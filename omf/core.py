"""
omf.core -- Isotropic 2x2 transfer-matrix method (TMM) for multilayer thin films.

Sign / phase convention
-----------------------
Time dependence          : exp(-i omega t)
Complex refractive index : n_tilde = n + i k,  with k >= 0 for an absorbing medium
Forward-propagating wave : exp(+i k_z z)

With this pair of choices a wave travelling in +z inside an absorbing medium
carries the factor exp(i Re(k_z) z) * exp(-Im(k_z) z), so physical decay requires
Im(k_z) >= 0.  That single inequality is the *only* branch rule needed and it is
enforced explicitly in `kz_from_index` (see `_fix_branch`).

Reference
---------
S. J. Byrnes, "Multilayer optical calculations", arXiv:1603.02720.
The layer-matrix construction, the p-polarisation Fresnel convention and the
transmittance prefactors below follow that paper.

Layer indexing
--------------
Layer 0     : semi-infinite incident (superstrate) medium
Layer 1..N-2: finite-thickness films
Layer N-1   : semi-infinite exit (substrate) medium

Thicknesses of layers 0 and N-1 must be np.inf.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "kz_from_index",
    "fresnel_rt",
    "coh_tmm",
    "snell_angles",
    "psi_delta",
]

# Branch-selection tolerance.  Values of |Im(k_z)| below this are treated as
# exactly zero (a lossless propagating wave), for which we instead require
# Re(k_z) > 0.
_BRANCH_TOL = 1e-10


# ----------------------------------------------------------------------------
# 1.  Transverse wavevector and branch selection
# ----------------------------------------------------------------------------
def _fix_branch(kz: np.ndarray) -> np.ndarray:
    """Force Im(k_z) >= 0; for the marginal lossless case force Re(k_z) > 0.

    Physics: with exp(-i omega t) and exp(+i k_z z), the amplitude of the
    forward wave is exp(-Im(k_z) z).  Choosing the root with Im(k_z) < 0 would
    describe a wave that *grows* with propagation distance -- unphysical for a
    passive medium, and numerically catastrophic for thick absorbing layers
    (overflow in exp(+i k_z d)).
    """
    kz = np.asarray(kz, dtype=complex)
    bad = (kz.imag < -_BRANCH_TOL) | (
        (np.abs(kz.imag) <= _BRANCH_TOL) & (kz.real < 0.0)
    )
    return np.where(bad, -kz, kz)


def kz_from_index(n: np.ndarray, lam_vac: np.ndarray, kx: np.ndarray) -> np.ndarray:
    """Normal component of the wavevector.

    Parameters
    ----------
    n       : complex refractive index, shape (..., N)
    lam_vac : vacuum wavelength (same length unit as thicknesses), shape (...)
    kx      : conserved in-plane wavevector, shape (...)

    Returns
    -------
    k_z of shape (..., N), branch-corrected.

    Note
    ----
    k_x is conserved across every interface (translational invariance in the
    plane).  This *is* Snell's law -- writing it as k_x conservation rather than
    n1 sin(th1) = n2 sin(th2) avoids all complex-angle bookkeeping and handles
    total internal reflection and absorbing media without special cases.
    """
    n = np.asarray(n, dtype=complex)
    k0 = 2.0 * np.pi / np.asarray(lam_vac, dtype=float)
    kz2 = (n * k0[..., None]) ** 2 - np.asarray(kx, dtype=complex)[..., None] ** 2
    return _fix_branch(np.sqrt(kz2))


def snell_angles(n: np.ndarray, lam_vac: np.ndarray, kx: np.ndarray) -> np.ndarray:
    """Complex propagation angles, provided for reporting only.

    The solver never needs these -- it works directly with k_z.
    """
    n = np.asarray(n, dtype=complex)
    k0 = 2.0 * np.pi / np.asarray(lam_vac, dtype=float)
    return np.arcsin(np.asarray(kx, dtype=complex)[..., None] / (n * k0[..., None]))


# ----------------------------------------------------------------------------
# 2.  Interface (Fresnel) coefficients
# ----------------------------------------------------------------------------
def fresnel_rt(pol: str, n_i, n_j, kz_i, kz_j):
    """Amplitude reflection / transmission coefficients for interface i -> j.

    Written in terms of k_z instead of cos(theta):  n_m cos(theta_m) = k_zm / k0,
    so the common factor k0 cancels from every ratio below.

    s-polarisation (TE, E parallel to the interface):
        r = (kz_i - kz_j) / (kz_i + kz_j)
        t = 2 kz_i       / (kz_i + kz_j)

    p-polarisation (TM, H parallel to the interface):
        r = (n_j^2 kz_i - n_i^2 kz_j) / (n_j^2 kz_i + n_i^2 kz_j)
        t = 2 n_i n_j kz_i            / (n_j^2 kz_i + n_i^2 kz_j)

    The p-polarisation forms follow Byrnes' convention, in which r_p > 0 below
    the Brewster angle.  The *sign* convention for r_p is a genuine convention
    (it depends on how the positive direction of E_p is defined after
    reflection); |r_p|^2 and hence R_p is convention independent.
    """
    n_i = np.asarray(n_i, dtype=complex)
    n_j = np.asarray(n_j, dtype=complex)

    if pol == "s":
        denom = kz_i + kz_j
        r = (kz_i - kz_j) / denom
        t = 2.0 * kz_i / denom
    elif pol == "p":
        denom = n_j**2 * kz_i + n_i**2 * kz_j
        r = (n_j**2 * kz_i - n_i**2 * kz_j) / denom
        t = 2.0 * n_i * n_j * kz_i / denom
    else:
        raise ValueError("pol must be 's' or 'p'")
    return r, t


# ----------------------------------------------------------------------------
# 3.  Coherent transfer matrix
# ----------------------------------------------------------------------------
def _matmul(a, b):
    """Batched 2x2 matrix product over trailing axes."""
    return np.einsum("...ij,...jk->...ik", a, b)


def coh_tmm(pol, n_list, d_list, th_0, lam_vac, want_fields=False):
    """Fully coherent TMM for a stack of isotropic layers.

    Parameters
    ----------
    pol     : 's' or 'p'
    n_list  : complex index array, shape (..., N) -- broadcasts against the
              batch shape implied by `th_0` and `lam_vac`
    d_list  : thickness array, shape (N,); d_list[0] and d_list[-1] must be inf
    th_0    : incidence angle in the (real, lossless) medium 0, radians, shape (...)
    lam_vac : vacuum wavelength, same length unit as d_list, shape (...)

    Returns
    -------
    dict with keys r, t, R, T, A (A = 1 - R - T, the total absorbed fraction)

    Vectorisation
    -------------
    Everything is broadcast: a call with lam_vac of shape (M,) and th_0 of shape
    (1,) evaluates M wavelengths in a single pass.  The only Python-level loop
    runs over layers (N is small, typically 3-5), never over data points.
    """
    d_list = np.asarray(d_list, dtype=float)
    n_list = np.asarray(n_list, dtype=complex)
    N = d_list.size

    if n_list.shape[-1] != N:
        raise ValueError(f"n_list last axis ({n_list.shape[-1]}) != len(d_list) ({N})")
    if not (np.isinf(d_list[0]) and np.isinf(d_list[-1])):
        raise ValueError("d_list[0] and d_list[-1] must be np.inf (semi-infinite media)")
    if N >= 3 and not np.all(np.isfinite(d_list[1:-1])):
        raise ValueError("interior thicknesses must be finite")

    th_0 = np.asarray(th_0, dtype=float)
    lam_vac = np.asarray(lam_vac, dtype=float)

    # ---- broadcast batch shape ------------------------------------------------
    batch = np.broadcast_shapes(th_0.shape, lam_vac.shape, n_list.shape[:-1])
    th_0 = np.broadcast_to(th_0, batch)
    lam_vac = np.broadcast_to(lam_vac, batch)
    n_list = np.broadcast_to(n_list, batch + (N,))

    k0 = 2.0 * np.pi / lam_vac
    n0 = n_list[..., 0]
    if np.max(np.abs(n0.imag)) > 1e-12:
        raise ValueError("the incident medium must be lossless (real n) for R/T to be well defined")

    # In-plane wavevector: conserved through the whole stack.
    kx = (n0.real * k0) * np.sin(th_0)

    kz = kz_from_index(n_list, lam_vac, kx)              # (..., N)

    # ---- propagation phases for interior layers -------------------------------
    # delta_j = k_zj d_j.  Im(delta) >= 0 guaranteed by the branch rule, so
    # exp(+i delta) never overflows.
    delta = kz[..., 1:-1] * d_list[1:-1]                 # (..., N-2)

    # ---- interface coefficients ----------------------------------------------
    r_if, t_if = fresnel_rt(pol, n_list[..., :-1], n_list[..., 1:],
                            kz[..., :-1], kz[..., 1:])   # (..., N-1)

    # ---- assemble  M = D_01 * (P_1 D_12) * (P_2 D_23) * ... -------------------
    def D(idx):
        """Interface matrix (1/t)[[1, r],[r, 1]] for interface `idx`."""
        r = r_if[..., idx]
        t = t_if[..., idx]
        m = np.empty(batch + (2, 2), dtype=complex)
        m[..., 0, 0] = 1.0
        m[..., 0, 1] = r
        m[..., 1, 0] = r
        m[..., 1, 1] = 1.0
        return m / t[..., None, None]

    def P(j):
        """Propagation matrix diag(exp(-i delta), exp(+i delta)) for film `j`."""
        dl = delta[..., j]
        m = np.zeros(batch + (2, 2), dtype=complex)
        m[..., 0, 0] = np.exp(-1j * dl)
        m[..., 1, 1] = np.exp(+1j * dl)
        return m

    M = D(0)
    for j in range(N - 2):                # one propagation + one interface each
        M = _matmul(M, P(j))
        M = _matmul(M, D(j + 1))

    # [E0+, E0-]^T = M [Ef+, 0]^T   ->   t = 1/M11,  r = M21/M11
    r = M[..., 1, 0] / M[..., 0, 0]
    t = 1.0 / M[..., 0, 0]

    R = np.abs(r) ** 2

    # ---- transmittance: needs the ratio of longitudinal Poynting flux ---------
    # s-pol :  T = |t|^2 Re(n_f cos th_f)   / Re(n_0 cos th_0)
    # p-pol :  T = |t|^2 Re(n_f cos th_f^*) / Re(n_0 cos th_0^*)
    # The conjugation in the p case is NOT cosmetic: for an absorbing exit medium
    # the two prefactors differ, and using the s-form for p violates energy
    # conservation.  Rewritten with n cos th = k_z / k0:
    #     Re(n cos th)   = Re(k_z)/k0
    #     Re(n cos th^*) = Re(n^2 k_z^*) / (k0 |n|^2)
    nf, kzf = n_list[..., -1], kz[..., -1]
    if pol == "s":
        num, den = kzf.real, kz[..., 0].real
    else:
        num = (nf**2 * np.conj(kzf)).real / np.abs(nf) ** 2
        den = (n0**2 * np.conj(kz[..., 0])).real / np.abs(n0) ** 2
    T = np.abs(t) ** 2 * (num / den)

    out = {"r": r, "t": t, "R": R, "T": T, "A": 1.0 - R - T, "kz": kz, "kx": kx}
    if want_fields:
        out["M"] = M
    return out


# ----------------------------------------------------------------------------
# 4.  Ellipsometry: Psi/Delta from the same stack
# ----------------------------------------------------------------------------
def psi_delta(n_list, d_list, th_0, lam_vac):
    """Ellipsometric (Psi, Delta) in degrees, via rho = r_p / r_s.

    rho = tan(Psi) * exp(i Delta) is the standard ellipsometric definition
    (Azzam & Bashara).  Both polarisations see the same stack and angle, so
    this is just two `coh_tmm` calls sharing all the branch/interface
    machinery above -- reflectometry (R) and ellipsometry (Psi, Delta) are
    the same physics read out two different ways.

    Delta is returned wrapped to [0, 360) degrees, matching the convention
    most ellipsometers (e.g. WVASE) report.  Because r_p's *sign* is a
    convention (see `fresnel_rt`), Delta from a different sign convention
    would come out as its 360-Delta mirror image; a caller comparing against
    a real instrument should check both if the fit looks wrong.
    """
    rs = coh_tmm("s", n_list, d_list, th_0, lam_vac)["r"]
    rp = coh_tmm("p", n_list, d_list, th_0, lam_vac)["r"]
    rho = rp / rs
    psi = np.degrees(np.arctan(np.abs(rho)))
    delta = np.degrees(np.angle(rho)) % 360.0
    return psi, delta
