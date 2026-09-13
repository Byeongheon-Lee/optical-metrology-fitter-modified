"""
omf.materials -- dispersion models.

All functions take wavelength in **nanometres** and return the complex index
n_tilde = n + i k consistent with the exp(-i omega t) convention of omf.core.

Two classes of model are used, for a reason worth stating explicitly:

* **Sellmeier** (SiO2, BK7): a physically-motivated closed form derived from a
  sum of Lorentz oscillators in the limit of negligible damping,
      n^2 - 1 = sum_j B_j lam^2 / (lam^2 - C_j),
  valid only in the transparency window between the UV and IR absorption
  bands.  It gives k = 0 by construction, which is an excellent approximation
  for fused silica in the visible (alpha < 1e-4 /cm).

* **Tabulated n,k** (Si): silicon has strong interband absorption (E1 at 3.4 eV,
  E2 at 4.25 eV) in the visible/UV, so no low-order analytic form works.  We
  interpolate a Kramers-Kronig-consistent measured data set.
"""

from __future__ import annotations

import os
import numpy as np

__all__ = [
    "n_air", "n_vacuum", "n_sio2", "n_bk7", "n_si", "n_si_aspnes", "n_constant",
    "n_pnipam_swollen", "n_water",
    "MATERIALS",
]

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


# ----------------------------------------------------------------------------
# Sellmeier models
# ----------------------------------------------------------------------------
def _sellmeier(lam_nm, B, C):
    """n^2 = 1 + sum_j B_j lam^2/(lam^2 - C_j), with lam in micrometres."""
    lam_um2 = (np.asarray(lam_nm, dtype=float) / 1000.0) ** 2
    n2 = 1.0
    for b, c in zip(B, C):
        n2 = n2 + b * lam_um2 / (lam_um2 - c)
    return np.sqrt(n2).astype(complex)


def n_sio2(lam_nm):
    """Fused silica, 20 C.  Malitson, J. Opt. Soc. Am. 55, 1205 (1965).

    Valid 210 nm - 3.71 um.  k is taken as exactly zero.

    Caveat for metrology: *thermal* SiO2 grown on Si is not identical to bulk
    fused silica.  Densification and stress typically raise n by ~0.002-0.006 in
    the visible.  Treating n_film as a free fit parameter (see fitter.py) is one
    way to absorb this; assuming Malitson exactly is a systematic error source.
    """
    B = (0.6961663, 0.4079426, 0.8974794)
    C = (0.0684043**2, 0.1162414**2, 9.896161**2)
    return _sellmeier(lam_nm, B, C)


def n_bk7(lam_nm):
    """N-BK7 borosilicate crown (SCHOTT).  Valid 300 nm - 2.5 um.

    Used here as a stand-in for a microscope coverslip.  Real coverslips are
    usually D263 or B270 (n_d ~ 1.5230 vs 1.5168 for N-BK7), so this is a ~0.4%
    index approximation -- acceptable for a Brewster-angle demonstration, not
    for absolute thickness metrology.
    """
    B = (1.03961212, 0.231792344, 1.01046945)
    C = (0.00600069867, 0.0200179144, 103.560653)
    return _sellmeier(lam_nm, B, C)


def n_air(lam_nm):
    """Air at STP, treated as non-dispersive.

    n_air = 1.000293 at 589 nm; the dispersion across the visible is ~3e-6,
    far below any effect we can resolve, so a constant is used.
    """
    return np.full(np.shape(lam_nm), 1.000293, dtype=complex)


def n_vacuum(lam_nm):
    return np.full(np.shape(lam_nm), 1.0, dtype=complex)


def n_constant(value):
    """Factory for a dispersionless material of given complex index."""
    def f(lam_nm):
        return np.full(np.shape(lam_nm), complex(value), dtype=complex)
    return f


# ----------------------------------------------------------------------------
# Tabulated silicon
# ----------------------------------------------------------------------------
def _load_si_table(fname="Si_Green2008.csv"):
    path = os.path.join(_DATA_DIR, fname)
    rows = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or line[0].isalpha():
                continue          # skip provenance comments and the column header
            rows.append([float(x) for x in line.split(",")])
    arr = np.asarray(rows, dtype=float)
    lam, n, k = arr[:, 0], arr[:, 1], arr[:, 2]
    order = np.argsort(lam)
    return lam[order], n[order], k[order]


_SI_LAM, _SI_N, _SI_K = _load_si_table()
SI_RANGE_NM = (float(_SI_LAM[0]), float(_SI_LAM[-1]))


def n_si(lam_nm):
    """Intrinsic crystalline silicon at 300 K.

    Data: M. A. Green, Sol. Energ. Mat. Sol. Cells 92, 1305 (2008), a
    Kramers-Kronig-consistent compilation.  Retrieved from the
    refractiveindex.info database (CC0 1.0).  Range 250-1100 nm.

    Interpolation: n linearly, k in log space.  k spans five decades over this
    range (3.7 at 250 nm down to 3e-5 at 1100 nm) because silicon's gap is
    indirect -- near the band edge absorption requires phonon assistance and
    falls off smoothly by orders of magnitude.  Linear interpolation of such a
    quantity between sparse grid points is badly wrong; log interpolation is the
    correct choice for an exponential-like tail.
    """
    lam = np.asarray(lam_nm, dtype=float)
    if np.any(lam < _SI_LAM[0] - 1e-9) or np.any(lam > _SI_LAM[-1] + 1e-9):
        raise ValueError(
            f"n_si: wavelength outside tabulated range {SI_RANGE_NM} nm"
        )
    n = np.interp(lam, _SI_LAM, _SI_N)
    floor = 1e-12
    logk = np.interp(lam, _SI_LAM, np.log(np.maximum(_SI_K, floor)))
    k = np.exp(logk)
    return (n + 1j * k).astype(complex)


_ASP_LAM, _ASP_N, _ASP_K = _load_si_table("Si_Aspnes1983.csv")


def n_si_aspnes(lam_nm):
    """Crystalline silicon, D. E. Aspnes & A. A. Studna, PRB 27, 985 (1983).

    An *independent* determination (spectroscopic ellipsometry on chemically
    stripped surfaces), valid 206-826 nm.  Provided deliberately as a second
    opinion: the difference between this and Green-2008 is not numerical noise
    but a genuine reference-data disagreement, and propagating that difference
    through the fit is the honest way to quote a systematic uncertainty on
    thickness.  See scripts/exp04_systematics.py.
    """
    lam = np.asarray(lam_nm, dtype=float)
    if np.any(lam < _ASP_LAM[0] - 1e-9) or np.any(lam > _ASP_LAM[-1] + 1e-9):
        raise ValueError(
            f"n_si_aspnes: outside tabulated range "
            f"({_ASP_LAM[0]}, {_ASP_LAM[-1]}) nm")
    n = np.interp(lam, _ASP_LAM, _ASP_N)
    k = np.exp(np.interp(lam, _ASP_LAM, np.log(np.maximum(_ASP_K, 1e-12))))
    return (n + 1j * k).astype(complex)


# ----------------------------------------------------------------------------
# Real measured tables: PNIPAM brush (hydrated) and water
# ----------------------------------------------------------------------------
# Unlike SiO2/BK7 (Sellmeier, k=0 by construction) or Si (Kramers-Kronig
# compiled from many groups' work), these two come from a single real
# spectroscopic-ellipsometry measurement (refnx/refellips), tabulated as-is.
_PNIPAM_LAM, _PNIPAM_N, _PNIPAM_K = _load_si_table("PNIPAM_swollen.csv")
PNIPAM_RANGE_NM = (float(_PNIPAM_LAM[0]), float(_PNIPAM_LAM[-1]))


def n_pnipam_swollen(lam_nm):
    """Hydrated PNIPAM (poly(N-isopropylacrylamide)) polymer brush.

    Tabulated n, k from real spectroscopic ellipsometry (refnx/refellips,
    materials/pnipam.csv), not an analytic model.  Both n and k vary
    smoothly here (no band-edge falloff like Si), so plain linear
    interpolation of k is fine -- the log-interpolation trick used for
    n_si is unnecessary.
    """
    lam = np.asarray(lam_nm, dtype=float)
    if np.any(lam < _PNIPAM_LAM[0] - 1e-6) or np.any(lam > _PNIPAM_LAM[-1] + 1e-6):
        raise ValueError(
            f"n_pnipam_swollen: wavelength outside tabulated range {PNIPAM_RANGE_NM} nm"
        )
    n = np.interp(lam, _PNIPAM_LAM, _PNIPAM_N)
    k = np.interp(lam, _PNIPAM_LAM, _PNIPAM_K)
    return (n + 1j * k).astype(complex)


_WATER_LAM, _WATER_N, _WATER_K = _load_si_table("water.csv")
WATER_RANGE_NM = (float(_WATER_LAM[0]), float(_WATER_LAM[-1]))


def n_water(lam_nm):
    """Water at room temperature, tabulated n, k (refnx/refellips,
    materials/water.csv).  k is <1e-7 across the visible, so this is
    effectively lossless there; still returned as complex for API
    consistency with every other material function.
    """
    lam = np.asarray(lam_nm, dtype=float)
    if np.any(lam < _WATER_LAM[0] - 1e-6) or np.any(lam > _WATER_LAM[-1] + 1e-6):
        raise ValueError(
            f"n_water: wavelength outside tabulated range {WATER_RANGE_NM} nm"
        )
    n = np.interp(lam, _WATER_LAM, _WATER_N)
    k = np.interp(lam, _WATER_LAM, _WATER_K)
    return (n + 1j * k).astype(complex)


MATERIALS = {
    "air": n_air,
    "vacuum": n_vacuum,
    "SiO2": n_sio2,
    "BK7": n_bk7,
    "Si": n_si,
    "Si_Aspnes": n_si_aspnes,
    "PNIPAM_swollen": n_pnipam_swollen,
    "water": n_water,
}


def build_n_list(names_or_values, lam_nm):
    """Assemble an (..., N) index array from a list of material names/values.

    Each entry may be a string key of MATERIALS, a callable f(lam_nm), or a
    complex constant.
    """
    lam = np.asarray(lam_nm, dtype=float)
    cols = []
    for item in names_or_values:
        if isinstance(item, str):
            cols.append(np.broadcast_to(MATERIALS[item](lam), lam.shape))
        elif callable(item):
            cols.append(np.broadcast_to(item(lam), lam.shape))
        else:
            cols.append(np.full(lam.shape, complex(item), dtype=complex))
    return np.stack(cols, axis=-1)
