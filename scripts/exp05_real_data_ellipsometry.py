"""
EXPERIMENT 5 -- fitting REAL measured data (not synthetic).

Every other experiment in this repo generates its own data with the same
model it then fits (an inverse crime, see uncertainty.py).  This script
breaks that pattern: the (Psi, Delta) values below come from an actual
spectroscopic ellipsometer (J.A. Woollam WVASE), measuring a real PNIPAM
polymer brush swollen in water on a Si wafer with a thin native SiO2 layer,
at 15 C, single angle (65 deg), 400-800 nm.

Source: refnx/refellips (github.com/refnx/refellips), demos/
        WVASE_example_2nmSiO2_100nmPNIPAM_MultiWavelength_Water.dat
        (MIT licensed).  Nominal dry PNIPAM thickness per the filename: ~100 nm.

Stack fit here: water / PNIPAM (free thickness) / SiO2 (fixed 2 nm) / Si.
Free parameter: swollen PNIPAM brush thickness.

Convention check
-----------------
r_p's sign is a genuine convention (see omf/core.py docstring): flipping it
shifts Delta by 180 deg without changing Psi at all.  Real instruments don't
all agree with this project's Byrnes-style convention, so this script fits
BOTH the data as given and the 180-deg-shifted version, and reports which one
the model actually likes -- this is an empirical way to resolve a convention
question, not a theoretical one.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from omf.fitter import EllipsometryModel  # noqa: E402
from omf.materials import n_water, build_n_list  # noqa: E402

DATA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data",
    "WVASE_2nmSiO2_PNIPAM_water_real.dat",
)


def n_water_incident(lam_nm):
    """Water's k is ~1e-9 to 4e-7 across 400-800 nm -- real but far below
    anything that matters for phase/kx here.  `coh_tmm` requires the
    incident (superstrate) medium to be exactly lossless (see its
    docstring: R/T are only well-defined flux ratios for a non-absorbing
    incidence side), so the tiny imaginary part is dropped only for water's
    role as layer 0.  This has no measurable effect at these thicknesses.
    """
    return n_water(lam_nm).real.astype(complex)


INF = np.inf
STACK = [n_water_incident, "PNIPAM_swollen", "SiO2", "Si"]
SIO2_NM = 2.0
NOMINAL_DRY_NM = 100.0


def load_real_data(path):
    lam, angle, psi, delta = [], [], [], []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            a, b, c, d = (float(x) for x in line.split(","))
            lam.append(a)
            angle.append(b)
            psi.append(c)
            delta.append(d)
    return (np.array(lam), np.array(angle), np.array(psi), np.array(delta))


def run_fit(model, lam, theta, psi_meas, delta_meas, d_grid, dn_grid, label):
    fr = model.fit(lam, theta, psi_meas, delta_meas, d_grid, dn_grid=dn_grid)
    dn_str = f"  dn = {fr.params[1]:+.4f} +/- {fr.sigma[1]:.4f}" if model.fit_dn else ""
    print(f"  [{label}] d = {fr.params[0]:8.3f} +/- {fr.sigma[0]:.3f} nm{dn_str}   "
          f"rms = {fr.rms:.3f} deg")
    return fr


def main():
    lam, angle_deg, psi_meas, delta_meas = load_real_data(DATA_PATH)
    theta = np.deg2rad(angle_deg[0])
    assert np.allclose(angle_deg, angle_deg[0]), "expected a single fixed angle"

    print("=" * 78)
    print("EXPERIMENT 5 -- REAL DATA: PNIPAM brush in water, spectroscopic ellipsometry")
    print("=" * 78)
    print(f"  {len(lam)} wavelengths, {angle_deg[0]:.0f} deg incidence, "
          f"{lam.min():.0f}-{lam.max():.0f} nm")
    print(f"  stack: water / PNIPAM (free) / SiO2 ({SIO2_NM} nm, fixed) / Si")
    print(f"  nominal DRY PNIPAM thickness (from sample label): ~{NOMINAL_DRY_NM:.0f} nm")
    print(f"  (measured in water, below PNIPAM's LCST -- brush should be swollen,")
    print(f"   so a fitted thickness well above {NOMINAL_DRY_NM:.0f} nm is physically expected)")
    print()

    d_nm = [INF, 100.0, SIO2_NM, INF]
    # fit_dn=True: pnipam.csv is the DRY polymer's tabulated index (n~1.50-1.52,
    # confirmed by inspection).  A brush swollen in water below its LCST is
    # mostly water by volume, so its effective index should sit much closer
    # to n_water (~1.33-1.34) -- dn absorbs that difference (see class docstring).
    model = EllipsometryModel(STACK, d_nm, fit_layer=1, fit_dn=True)
    d_grid = np.linspace(5.0, 900.0, 1500)
    dn_grid = np.linspace(-0.30, 0.05, 36)

    print("  convention check (r_p sign is a convention -- see core.py):")
    fr_asis = run_fit(model, lam, theta, psi_meas, delta_meas, d_grid, dn_grid, "as measured")
    delta_flipped = (delta_meas + 180.0) % 360.0
    fr_flipped = run_fit(model, lam, theta, psi_meas, delta_flipped, d_grid, dn_grid, "delta+180")
    print()

    best_label, fr = (("as measured", fr_asis) if fr_asis.rms <= fr_flipped.rms
                       else ("delta+180 convention", fr_flipped))
    print(f"  -> lower-residual convention: {best_label}")
    print()

    n_dry_600 = float(np.real(build_n_list(["PNIPAM_swollen"], np.array([600.0]))[0, 0]))
    n_eff_600 = n_dry_600 + fr.params[1]
    print("  final fit:")
    print(f"    swollen PNIPAM thickness = {fr.params[0]:.2f} +/- {fr.sigma[0]:.2f} nm")
    print(f"    index offset dn          = {fr.params[1]:+.4f} +/- {fr.sigma[1]:.4f}")
    print(f"    -> effective n @600nm     = {n_eff_600:.4f}  "
          f"(dry table: {n_dry_600:.4f}, water: {float(np.real(n_water(np.array([600.0]))[0])):.4f})")
    print(f"    residual RMS              = {fr.rms:.3f} deg")
    if fr.params[0] > NOMINAL_DRY_NM:
        ratio = fr.params[0] / NOMINAL_DRY_NM
        print(f"    swelling ratio vs nominal dry thickness: {ratio:.2f}x")
    print()

    psi_fit, delta_fit = model.psi_delta(fr.params, lam, theta)
    delta_compare = delta_flipped if best_label != "as measured" else delta_meas
    print(f"  {'lam (nm)':>9s} {'Psi meas':>9s} {'Psi fit':>9s} "
          f"{'Delta meas':>11s} {'Delta fit':>10s}")
    for i in range(len(lam)):
        print(f"  {lam[i]:9.0f} {psi_meas[i]:9.3f} {psi_fit[i]:9.3f} "
              f"{delta_compare[i]:11.3f} {delta_fit[i]:10.3f}")

    print()
    print("  NOTE: this is a real measurement, not synthetic data -- there is no")
    print("  known ground-truth swollen thickness to check the fit against (that is")
    print("  exactly the point: no inverse crime).  What CAN be checked is internal")
    print("  consistency -- residual RMS in the sub-degree range for real ellipsometer")
    print("  noise, and a swollen thickness that makes physical sense relative to the")
    print("  nominal dry value.")


if __name__ == "__main__":
    sys.exit(main())
