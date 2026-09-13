"""
EXPERIMENT 1 -- the forward model.

Question: given a known SiO2/Si stack, what does the reflectance look like, and
which features carry thickness information?

Three panels:
  (a) Spectral reflectance at normal incidence for several oxide thicknesses.
      The interference fringes are the signal.  Their *spacing* encodes n*d;
      their *absolute position* encodes it too, but only modulo one order.
  (b) Angle-resolved reflectance at 405 nm (the wavelength of the lab's CW
      laser), s and p, showing the pseudo-Brewster dip.
  (c) Sensitivity dR/dd -- the quantity that actually determines how precisely a
      thickness can be measured.  Where this vanishes, the measurement is blind.

Also benchmarks the vectorised implementation against a per-point Python loop.
"""

import json
import time

import numpy as np

from _style import plt, C, save, banner, RESULTS
from omf.core import coh_tmm
from omf.materials import build_n_list, n_sio2, n_si

INF = np.inf
out = {}

banner("EXPERIMENT 1 -- FORWARD MODEL: SiO2 on Si")

# ---------------------------------------------------------------------------
# (a) spectral reflectance
# ---------------------------------------------------------------------------
lam = np.linspace(400.0, 900.0, 1001)
thicknesses = [50.0, 100.0, 200.0, 400.0]
n_stack = build_n_list(["air", "SiO2", "Si"], lam)

fig, axes = plt.subplots(1, 3, figsize=(13.5, 3.9))
ax = axes[0]
spectra = {}
for d, col in zip(thicknesses, [C["blue"], C["green"], C["orange"], C["red"]]):
    R = coh_tmm("s", n_stack, [INF, d, INF], 0.0, lam)["R"]
    spectra[d] = R
    ax.plot(lam, R, color=col, label=f"d = {d:.0f} nm")
R_bare = coh_tmm("s", build_n_list(["air", "Si"], lam), [INF, INF], 0.0, lam)["R"]
ax.plot(lam, R_bare, color=C["grey"], ls="--", lw=1.0, label="bare Si")
ax.set_xlabel("wavelength (nm)")
ax.set_ylabel("R")
ax.set_title("(a) normal-incidence reflectance")
ax.legend(ncol=2)
ax.set_ylim(0, 0.65)

print(f"  bare Si at 633 nm : R = {np.interp(633.0, lam, R_bare):.4f}")
for d in thicknesses:
    R = spectra[d]
    print(f"  d = {d:5.0f} nm      : R(405 nm) = {np.interp(405.0, lam, R):.4f}, "
          f"R(633 nm) = {np.interp(633.0, lam, R):.4f}")
out["R_bare_633"] = float(np.interp(633.0, lam, R_bare))
out["R_vs_d_633"] = {str(d): float(np.interp(633.0, lam, spectra[d])) for d in thicknesses}

# extrema count -> fringe order, a useful cross-check on the fit
R400 = spectra[400.0]
sign = np.diff(np.sign(np.diff(R400)))
n_extrema = int(np.count_nonzero(sign))
print(f"  d = 400 nm shows {n_extrema} extrema over 400-900 nm "
      f"(more fringes = more independent order information)")
out["n_extrema_400nm_film"] = n_extrema

# ---------------------------------------------------------------------------
# (b) angle-resolved reflectance at 405 nm
# ---------------------------------------------------------------------------
th = np.deg2rad(np.linspace(0.0, 89.5, 900))
L405 = np.full(th.shape, 405.0)
ax = axes[1]

n3 = build_n_list(["air", "SiO2", "Si"], L405)
n2 = build_n_list(["air", "Si"], L405)

for pol, col, ls in (("s", C["blue"], "-"), ("p", C["red"], "-")):
    Rf = coh_tmm(pol, n3, [INF, 217.0, INF], th, L405)["R"]
    Rb = coh_tmm(pol, n2, [INF, INF], th, L405)["R"]
    ax.plot(np.rad2deg(th), Rf, color=col, ls=ls, label=f"{pol}-pol, 217 nm SiO$_2$")
    ax.plot(np.rad2deg(th), Rb, color=col, ls=":", lw=1.0, label=f"{pol}-pol, bare Si")

Rp_bare = coh_tmm("p", n2, [INF, INF], th, L405)["R"]
i_min = int(np.argmin(Rp_bare))
th_pB = float(np.rad2deg(th[i_min]))
nSi405 = n_si(405.0)
th_B_ideal = float(np.rad2deg(np.arctan(nSi405.real / 1.000293)))
ax.axvline(th_pB, color=C["grey"], lw=0.8, ls="--")
ax.set_xlabel("incidence angle (deg)")
ax.set_ylabel("R")
ax.set_title("(b) angle scan at 405 nm")
ax.legend(loc="upper left")

print()
print(f"  Si index at 405 nm            : n = {nSi405.real:.4f}, k = {nSi405.imag:.5f}")
print(f"  pseudo-Brewster minimum (bare): {th_pB:.3f} deg,  R_p,min = {Rp_bare[i_min]:.5f}")
print(f"  lossless arctan(n) would give : {th_B_ideal:.3f} deg")
print(f"  --> absorption both shifts the minimum and lifts it off zero;")
print(f"      R_p,min = {Rp_bare[i_min]:.5f} != 0 is a direct measure of k.")
out["pseudo_brewster_deg"] = th_pB
out["arctan_n_deg"] = th_B_ideal
out["Rp_min_bare_Si_405"] = float(Rp_bare[i_min])

# a genuinely lossless case for contrast: BK7 coverslip
from omf.materials import n_bk7                                    # noqa: E402
n_bk = build_n_list(["air", "BK7"], L405)
Rp_bk = coh_tmm("p", n_bk, [INF, INF], th, L405)["R"]
i2 = int(np.argmin(Rp_bk))
print(f"  BK7 (k=0) at 405 nm           : minimum at {np.rad2deg(th[i2]):.3f} deg, "
      f"arctan(n) = {np.rad2deg(np.arctan(float(n_bk7(405.0).real))):.3f} deg, "
      f"R_p,min = {Rp_bk[i2]:.2e}")
out["bk7_brewster_deg"] = float(np.rad2deg(th[i2]))
out["bk7_arctan_n_deg"] = float(np.rad2deg(np.arctan(float(n_bk7(405.0).real))))

# ---------------------------------------------------------------------------
# (c) thickness sensitivity dR/dd
# ---------------------------------------------------------------------------
ax = axes[2]
d_scan = np.linspace(0.0, 500.0, 2001)
for lam0, col in ((405.0, C["purple"]), (633.0, C["orange"])):
    L = np.array([lam0])
    n = build_n_list(["air", "SiO2", "Si"], L)
    R = np.array([coh_tmm("s", n, [INF, d, INF], 0.0, L)["R"][0] for d in d_scan])
    dRdd = np.gradient(R, d_scan)
    ax.plot(d_scan, dRdd * 1e3, color=col, label=f"$\\lambda$ = {lam0:.0f} nm")
    nf = float(n_sio2(lam0).real)
    period = lam0 / (2.0 * nf)
    print()
    print(f"  lambda = {lam0:.0f} nm : n_SiO2 = {nf:.4f}, fringe period in d = {period:.2f} nm")
    print(f"                   max |dR/dd| = {np.max(np.abs(dRdd))*1e3:.3f} x 10^-3 /nm")
    print(f"                   dead zones (dR/dd = 0) every {period/2:.2f} nm")
    out[f"fringe_period_d_{int(lam0)}"] = float(period)
    out[f"max_dRdd_{int(lam0)}"] = float(np.max(np.abs(dRdd)))

ax.axhline(0.0, color=C["black"], lw=0.7)
ax.set_xlabel("SiO$_2$ thickness d (nm)")
ax.set_ylabel("dR/dd  ($10^{-3}$ nm$^{-1}$)")
ax.set_title("(c) thickness sensitivity, normal incidence")
ax.legend()

save(fig, "exp01_forward_model.png")

# ---------------------------------------------------------------------------
# vectorisation benchmark
# ---------------------------------------------------------------------------
banner("EXPERIMENT 1b -- VECTORISATION BENCHMARK")
lam_b = np.linspace(400.0, 900.0, 2000)
n_b = build_n_list(["air", "SiO2", "Si"], lam_b)

t0 = time.perf_counter()
for _ in range(20):
    coh_tmm("s", n_b, [INF, 217.0, INF], 0.0, lam_b)
t_vec = (time.perf_counter() - t0) / 20

t0 = time.perf_counter()
for L in lam_b:
    La = np.array([L])
    coh_tmm("s", build_n_list(["air", "SiO2", "Si"], La), [INF, 217.0, INF], 0.0, La)
t_loop = time.perf_counter() - t0

print(f"  {lam_b.size} wavelengths, 3-layer stack")
print(f"    vectorised : {t_vec*1e3:8.3f} ms   ({t_vec/lam_b.size*1e6:.3f} us/point)")
print(f"    Python loop: {t_loop*1e3:8.3f} ms   ({t_loop/lam_b.size*1e6:.3f} us/point)")
print(f"    speed-up   : {t_loop/t_vec:.1f}x")
print()
print("  Why this matters: the coarse grid pre-scan in the fitter evaluates the")
print("  forward model on the order of 1e3 times.  At loop speed that is minutes;")
print("  vectorised it is well under a second, which is what makes an exhaustive")
print("  global scan -- and hence a fringe-order-safe fit -- practical at all.")
out["bench_vec_ms"] = t_vec * 1e3
out["bench_loop_ms"] = t_loop * 1e3
out["bench_speedup"] = t_loop / t_vec

with open(f"{RESULTS}/exp01_results.json", "w") as f:
    json.dump(out, f, indent=2)
print(f"\n    data -> results/exp01_results.json")
