"""
omf.uncertainty -- how well *can* a thickness be determined, and how well *is* it?

The distinction matters, and it is the part of a metrology project that a
fitting routine alone does not answer.

Cramer-Rao lower bound (CRLB)
-----------------------------
For measurements R_i with independent Gaussian noise of standard deviation
sigma_i, and a model R_i(p) depending on parameters p, the Fisher information
matrix is

    F_ab = sum_i (1/sigma_i^2) (dR_i/dp_a)(dR_i/dp_b)

and *any* unbiased estimator obeys  Cov(p) >= F^{-1}  (matrix inequality).  So

    sigma_d >= sqrt( (F^{-1})_dd ).

This is a statement about the *experiment*, not the algorithm: it says how much
information about d is physically present in the data.  If the measured spread
sits at the CRLB, the estimator is efficient and the only way to do better is to
change the measurement (more points, lower noise, wider spectral range, a
different angle).  If the measured spread is far above it, the estimator is
wasteful.

Note the crucial asymmetry: the CRLB bounds the *variance*, i.e. the random
error.  It says nothing at all about **bias** from a wrong model.  A fit can sit
exactly at the CRLB and still be 3 nm wrong because the true sample has a native
oxide the model omits.  Random precision and systematic accuracy are separate
budgets (see scripts/exp04).
"""

from __future__ import annotations

import numpy as np

__all__ = ["numerical_jacobian", "fisher_information", "crlb", "monte_carlo_fit"]


def numerical_jacobian(f, p, steps):
    """Central-difference Jacobian dF_i/dp_a of a vector-valued model.

    `steps` sets the finite-difference step per parameter.  Central differences
    give O(h^2) truncation error; with h chosen ~ 1e-4 of the parameter scale the
    total error is comfortably below the noise levels considered here.
    """
    p = np.asarray(p, dtype=float)
    steps = np.atleast_1d(np.asarray(steps, dtype=float))
    cols = []
    for a in range(p.size):
        h = steps[a]
        pp, pm = p.copy(), p.copy()
        pp[a] += h
        pm[a] -= h
        cols.append((np.asarray(f(pp)) - np.asarray(f(pm))) / (2.0 * h))
    return np.stack(cols, axis=-1)          # (M, npar)


def fisher_information(J, sigma):
    """F = J^T W J with W = diag(1/sigma^2)."""
    sigma = np.broadcast_to(np.asarray(sigma, dtype=float), (J.shape[0],))
    Jw = J / sigma[:, None]
    return Jw.T @ Jw


def crlb(J, sigma):
    """Return (sigma_lower_bound_vector, inverse Fisher matrix)."""
    F = fisher_information(J, sigma)
    Finv = np.linalg.inv(F)
    return np.sqrt(np.abs(np.diag(Finv))), Finv


def monte_carlo_fit(model, lam_nm, theta_rad, p_true, sigma, n_trials,
                    d_grid, dn_grid=None, rng=None, use_known_sigma=True):
    """Synthesise noisy data `n_trials` times and refit; return the estimates.

    This is the empirical counterpart of the CRLB.  Comparing the two is the
    single most informative validation a fitting pipeline can carry:

      * spread == CRLB  -> estimator efficient, measurement-limited
      * spread >  CRLB  -> optimiser or parameterisation is losing information
      * mean   != truth -> bias; with the same model on both sides this can only
                           come from the estimator (nonlinearity, bounds), since
                           the model is exact by construction

    IMPORTANT (inverse crime): because `model` generates the data *and* fits it,
    the only error sources present are the injected noise and the optimiser.
    Every model-form error -- wrong dispersion, ignored native oxide, roughness,
    finite beam divergence -- is invisible here.  The resulting sigma is a
    *noise floor*, i.e. an upper bound on achievable performance, never a
    validated accuracy.
    """
    rng = np.random.default_rng() if rng is None else rng
    p_true = np.atleast_1d(np.asarray(p_true, dtype=float))

    R0 = model.reflectance(p_true, lam_nm, theta_rad)
    out = np.empty((n_trials, p_true.size))

    for i in range(n_trials):
        R_noisy = R0 + rng.normal(0.0, sigma, size=np.shape(R0))
        fr = model.fit(lam_nm, theta_rad, R_noisy, d_grid, dn_grid=dn_grid,
                       sigma=sigma if use_known_sigma else None)
        out[i] = fr.params
    return out
