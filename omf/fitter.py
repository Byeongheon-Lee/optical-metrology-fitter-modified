"""
omf.fitter -- the inverse problem: recover film thickness (and optionally index)
from measured reflectance.

Why this is not a trivial least-squares problem
-----------------------------------------------
For a transparent film on a substrate the reflectance is, to leading order,

    R(d) ~ A + B cos(2 delta),     delta = (2 pi / lam) n_f d cos(theta_f)

i.e. **periodic in d**.  A film that is thicker by one full order,

    Delta d = lam / (2 n_f cos theta_f)   (~139 nm for SiO2 at 405 nm, normal incidence)

produces an almost identical single-wavelength reflectance.  The cost function
therefore has a comb of near-degenerate local minima, and a gradient-based
optimiser started at an arbitrary guess will simply fall into whichever tooth of
the comb it happens to be nearest.  This is the classic **fringe-order
ambiguity** of thin-film metrology.

Two things break the degeneracy, and the code exposes both:

1. **Coarse grid pre-scan.**  Evaluate the cost on a dense grid spanning the
   plausible thickness range, take the global minimum as the starting point,
   then refine locally.  Cheap because the forward model is vectorised.
2. **Spectroscopic / angle-resolved data.**  The fringe spacing itself is
   wavelength-dependent (delta ∝ 1/lam), so a broadband measurement pins the
   absolute order.  A single-wavelength, single-angle measurement genuinely
   cannot -- no algorithm fixes that; it is an information-content limit, not an
   optimiser limit.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Sequence

import numpy as np
from scipy.optimize import least_squares

from .core import coh_tmm, psi_delta
from .materials import build_n_list

__all__ = ["FilmModel", "FitResult", "EllipsometryModel"]


@dataclass
class FitResult:
    """Outcome of a fit, with uncertainty propagated from the Jacobian."""
    params: np.ndarray                 # best-fit parameter vector
    names: list                        # parameter names
    sigma: np.ndarray                  # 1-sigma from the covariance diagonal
    cov: np.ndarray                    # parameter covariance matrix
    rms: float                         # RMS of the residual
    coarse_best: np.ndarray            # starting point from the grid pre-scan
    success: bool = True
    nfev: int = 0
    extra: dict = field(default_factory=dict)

    def __repr__(self):
        lines = [f"FitResult(rms={self.rms:.3e}, nfev={self.nfev})"]
        for nm, p, s in zip(self.names, self.params, self.sigma):
            lines.append(f"    {nm:>10s} = {p:12.5f}  +/- {s:.5f}")
        return "\n".join(lines)

    @property
    def correlation(self):
        d = np.sqrt(np.diag(self.cov))
        outer = np.outer(d, d)
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(outer > 0, self.cov / outer, np.nan)


class FilmModel:
    """A stack with one free-thickness film and an optional index offset.

    Parameters
    ----------
    materials : sequence, length N
        Entries are material names ('air', 'SiO2', 'Si'), callables f(lam_nm),
        or complex constants.  Index 0 = superstrate, index -1 = substrate.
    d_nm : sequence, length N
        Thicknesses in nm; d_nm[0] and d_nm[-1] must be np.inf.
    fit_layer : int
        Index of the layer whose thickness is a free parameter.
    fit_dn : bool
        If True, add a constant real offset `dn` to the fit layer's index.
        This is the standard remedy for the difference between bulk fused silica
        and thermal oxide -- but see the correlation analysis: `d` and `dn` are
        strongly anti-correlated for single-angle data, because the optical path
        n*d is what the fringes actually measure.
    pol : {'s', 'p', 'unpol'}
    """

    def __init__(self, materials: Sequence, d_nm: Sequence[float],
                 fit_layer: int = 1, fit_dn: bool = False, pol: str = "s"):
        self.materials = list(materials)
        self.d_nm = np.asarray(d_nm, dtype=float)
        self.fit_layer = fit_layer
        self.fit_dn = fit_dn
        self.pol = pol

        if pol not in ("s", "p", "unpol"):
            raise ValueError("pol must be 's', 'p' or 'unpol'")
        if not (np.isinf(self.d_nm[0]) and np.isinf(self.d_nm[-1])):
            raise ValueError("outer layers must have infinite thickness")
        if not np.isfinite(self.d_nm[fit_layer]):
            raise ValueError("fit_layer must be a finite-thickness film")

        self.names = ["d_nm"] + (["dn"] if fit_dn else [])

    # ------------------------------------------------------------------
    # forward model
    # ------------------------------------------------------------------
    def reflectance(self, params, lam_nm, theta_rad):
        """R(lam, theta) for the given parameter vector.

        `lam_nm` and `theta_rad` are broadcast against each other, so an
        (M,)-shaped lam with scalar theta costs one vectorised pass.
        """
        lam = np.asarray(lam_nm, dtype=float)
        n_list = build_n_list(self.materials, lam)
        return self._reflectance_with_n(params, n_list, lam, theta_rad)

    def _reflectance_with_n(self, params, n_list, lam, theta_rad):
        """Same as `reflectance`, but reuses a dispersion array the caller
        already built.  `n_list` depends only on wavelength, not on the fit
        parameters, so a caller sweeping many trial `d` values (coarse_scan,
        fit) builds it once and passes it in here instead of paying for
        build_n_list on every candidate.
        """
        params = np.atleast_1d(np.asarray(params, dtype=float))
        d = self.d_nm.copy()
        d[self.fit_layer] = params[0]

        if self.fit_dn:
            n_list = n_list.copy()
            n_list[..., self.fit_layer] += params[1]

        if self.pol == "unpol":
            rs = coh_tmm("s", n_list, d, theta_rad, lam)["R"]
            rp = coh_tmm("p", n_list, d, theta_rad, lam)["R"]
            return 0.5 * (rs + rp)
        return coh_tmm(self.pol, n_list, d, theta_rad, lam)["R"]

    # ------------------------------------------------------------------
    # coarse grid pre-scan
    # ------------------------------------------------------------------
    def coarse_scan(self, lam_nm, theta_rad, R_meas, d_grid, dn_grid=None):
        """Evaluate SSR on a grid and return the global minimiser.

        Complexity: len(d_grid) forward evaluations, each already vectorised
        over all data points.  For a 2000-point thickness grid and 400
        wavelengths this is ~8e5 TMM evaluations, well under a second.

        The dispersion array (build_n_list) depends only on wavelength, so it
        is built once here rather than once per grid point.
        """
        d_grid = np.asarray(d_grid, dtype=float)
        dn_grid = np.array([0.0]) if dn_grid is None else np.asarray(dn_grid, float)
        R_meas = np.asarray(R_meas, dtype=float)
        lam = np.asarray(lam_nm, dtype=float)
        n_list = build_n_list(self.materials, lam)

        ssr = np.empty((d_grid.size, dn_grid.size))
        for i, d in enumerate(d_grid):
            for j, dn in enumerate(dn_grid):
                p = (d, dn) if self.fit_dn else (d,)
                resid = self._reflectance_with_n(p, n_list, lam, theta_rad) - R_meas
                ssr[i, j] = float(np.sum(resid**2))

        i, j = np.unravel_index(np.argmin(ssr), ssr.shape)
        best = [d_grid[i]] + ([dn_grid[j]] if self.fit_dn else [])
        return np.array(best), ssr, d_grid, dn_grid

    # ------------------------------------------------------------------
    # full fit
    # ------------------------------------------------------------------
    def fit(self, lam_nm, theta_rad, R_meas, d_grid,
            dn_grid=None, sigma=None, bounds=None, verbose=False):
        """Coarse pre-scan followed by Levenberg-Marquardt-style refinement.

        Parameters
        ----------
        sigma : float or array or None
            Known 1-sigma measurement noise on R.  If given, the covariance is
            J^T J scaled by sigma^2 (an *a priori* estimate).  If None, the
            covariance is scaled by the reduced chi-squared of the fit
            (an *a posteriori* estimate), which is what you must use when the
            noise level is not independently known.
        """
        R_meas = np.asarray(R_meas, dtype=float)
        w = 1.0 if sigma is None else 1.0 / np.asarray(sigma, dtype=float)
        lam = np.asarray(lam_nm, dtype=float)
        n_list = build_n_list(self.materials, lam)

        p0, ssr_grid, dg, dng = self.coarse_scan(
            lam_nm, theta_rad, R_meas, d_grid, dn_grid)

        def resid(p):
            return (self._reflectance_with_n(p, n_list, lam, theta_rad) - R_meas) * w

        if bounds is None:
            lo = [float(np.min(d_grid))] + ([-0.5] if self.fit_dn else [])
            hi = [float(np.max(d_grid))] + ([+0.5] if self.fit_dn else [])
            bounds = (lo, hi)

        res = least_squares(resid, p0, bounds=bounds, method="trf",
                            xtol=1e-14, ftol=1e-14, gtol=1e-14,
                            verbose=2 if verbose else 0)

        m, npar = res.fun.size, res.x.size
        J = res.jac
        JTJ = J.T @ J
        try:
            cov = np.linalg.inv(JTJ)
        except np.linalg.LinAlgError:
            cov = np.full((npar, npar), np.nan)

        if sigma is None:
            dof = max(m - npar, 1)
            chi2_red = float(np.sum(res.fun**2)) / dof
            cov = cov * chi2_red
        # if sigma was supplied the residuals are already whitened, so
        # inv(J^T J) is directly the covariance.

        rms = float(np.sqrt(np.mean(
            (self._reflectance_with_n(res.x, n_list, lam, theta_rad) - R_meas) ** 2)))

        return FitResult(
            params=res.x, names=self.names,
            sigma=np.sqrt(np.abs(np.diag(cov))),
            cov=cov, rms=rms, coarse_best=p0,
            success=bool(res.success), nfev=int(res.nfev),
            extra={"ssr_grid": ssr_grid, "d_grid": dg, "dn_grid": dng},
        )


class EllipsometryModel:
    """A stack with one free-thickness layer, fit against ellipsometric
    (Psi, Delta) data instead of intensity reflectance.

    This exists for one reason: real instruments that report R directly
    (simple reflectometers) are common but their raw spectra are rarely
    published; real *ellipsometric* (Psi, Delta) measurements are more often
    shared, because most academic ellipsometry software (WVASE, CompleteEASE,
    ...) exports them as plain text.  The physics is the same fringe-order
    problem as `FilmModel` -- Psi/Delta are just as periodic in optical
    thickness as R is -- so the remedy is the same coarse-scan-then-refine
    pattern, only the observable and residual differ.

    Parameters
    ----------
    materials, d_nm, fit_layer : see `FilmModel`.
    fit_dn : bool
        If True, add a constant real offset `dn` to the fit layer's index,
        exactly as in `FilmModel.fit_dn`.  Needed whenever the tabulated
        index for the fit layer describes a *different physical state* of
        the material than what was actually measured -- e.g. a swollen,
        highly hydrated polymer brush fit with a table measured on the dry
        polymer.  In that case `dn` is not a small correction; it can be
        the dominant effect, so its bounds are set independently of
        `FilmModel`'s (see `fit`).
    """

    def __init__(self, materials: Sequence, d_nm: Sequence[float],
                 fit_layer: int = 1, fit_dn: bool = False):
        self.materials = list(materials)
        self.d_nm = np.asarray(d_nm, dtype=float)
        self.fit_layer = fit_layer
        self.fit_dn = fit_dn

        if not (np.isinf(self.d_nm[0]) and np.isinf(self.d_nm[-1])):
            raise ValueError("outer layers must have infinite thickness")
        if not np.isfinite(self.d_nm[fit_layer]):
            raise ValueError("fit_layer must be a finite-thickness film")

        self.names = ["d_nm"] + (["dn"] if fit_dn else [])

    def psi_delta(self, params, lam_nm, theta_rad):
        """(Psi, Delta) in degrees for the given parameter vector."""
        params = np.atleast_1d(np.asarray(params, dtype=float))
        d = self.d_nm.copy()
        d[self.fit_layer] = params[0]

        lam = np.asarray(lam_nm, dtype=float)
        n_list = build_n_list(self.materials, lam)
        if self.fit_dn:
            n_list = n_list.copy()
            n_list[..., self.fit_layer] += params[1]
        return psi_delta(n_list, d, theta_rad, lam)

    def coarse_scan(self, lam_nm, theta_rad, psi_meas, delta_meas, d_grid, dn_grid=None):
        """Evaluate SSR (Psi and Delta jointly) on a grid; return the global
        minimiser.  Same rationale as `FilmModel.coarse_scan`: Psi/Delta are
        periodic in optical thickness, so a local optimiser alone is not
        safe against the fringe-order ambiguity here either.
        """
        d_grid = np.asarray(d_grid, dtype=float)
        dn_grid = np.array([0.0]) if dn_grid is None else np.asarray(dn_grid, float)
        psi_meas = np.asarray(psi_meas, dtype=float)
        delta_meas = np.asarray(delta_meas, dtype=float)

        ssr = np.empty((d_grid.size, dn_grid.size))
        for i, d in enumerate(d_grid):
            for j, dn in enumerate(dn_grid):
                p = (d, dn) if self.fit_dn else (d,)
                psi, delta = self.psi_delta(p, lam_nm, theta_rad)
                ssr[i, j] = float(np.sum((psi - psi_meas) ** 2) + np.sum((delta - delta_meas) ** 2))

        i, j = np.unravel_index(np.argmin(ssr), ssr.shape)
        best = [d_grid[i]] + ([dn_grid[j]] if self.fit_dn else [])
        return np.array(best), ssr, d_grid, dn_grid

    def fit(self, lam_nm, theta_rad, psi_meas, delta_meas, d_grid,
            dn_grid=None, dn_bounds=(-0.5, 0.5), verbose=False):
        """Coarse pre-scan followed by Levenberg-Marquardt-style refinement,
        jointly on Psi and Delta residuals (both in degrees, so no relative
        weighting is applied between them -- a real analysis would weight by
        each instrument's actual Psi/Delta uncertainties).

        `dn_bounds` only matters when `fit_dn` is True; it defaults to the
        same +/-0.5 range as `FilmModel`, but pass a wider one if the fit
        layer's tabulated index describes a state (e.g. dry) far from the
        one actually measured (e.g. swollen) -- see the class docstring.
        """
        psi_meas = np.asarray(psi_meas, dtype=float)
        delta_meas = np.asarray(delta_meas, dtype=float)

        p0, ssr_grid, dg, dng = self.coarse_scan(
            lam_nm, theta_rad, psi_meas, delta_meas, d_grid, dn_grid)

        def resid(p):
            psi, delta = self.psi_delta(p, lam_nm, theta_rad)
            return np.concatenate([psi - psi_meas, delta - delta_meas])

        lo = [float(np.min(d_grid))] + ([dn_bounds[0]] if self.fit_dn else [])
        hi = [float(np.max(d_grid))] + ([dn_bounds[1]] if self.fit_dn else [])
        res = least_squares(resid, p0, bounds=(lo, hi), method="trf",
                            xtol=1e-14, ftol=1e-14, gtol=1e-14,
                            verbose=2 if verbose else 0)

        m, npar = res.fun.size, res.x.size
        J = res.jac
        try:
            cov = np.linalg.inv(J.T @ J)
        except np.linalg.LinAlgError:
            cov = np.full((npar, npar), np.nan)

        dof = max(m - npar, 1)
        chi2_red = float(np.sum(res.fun**2)) / dof
        cov = cov * chi2_red

        rms = float(np.sqrt(np.mean(res.fun ** 2)))

        return FitResult(
            params=res.x, names=self.names,
            sigma=np.sqrt(np.abs(np.diag(cov))),
            cov=cov, rms=rms, coarse_best=p0,
            success=bool(res.success), nfev=int(res.nfev),
            extra={"ssr_grid": ssr_grid, "d_grid": dg, "dn_grid": dng},
        )
