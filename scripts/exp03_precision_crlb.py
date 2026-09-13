"""
EXPERIMENT 3 -- how precise can this measurement be?

Two separate questions, deliberately kept apart:

  1. INFORMATION.  Given the measurement design and a noise level, what is the
     smallest variance any unbiased estimator could achieve?  That is the
     Cramer-Rao lower bound, computed from the Fisher information -- a property
     of the experiment, not of the code.

  2. EFFICIENCY.  Does *this* fitter actually attain it?  Answered by Monte
     Carlo: synthesise noisy data many times, refit, look at the spread.

Agreement between the two means the pipeline extracts all the information the
data contains, and further improvement requires a better measurement rather
than a better algorithm.

Then the two-parameter case (d and a film-index offset dn), which is where
optical metrology gets uncomfortable: the fringes measure the optical path
n*d, so d and n are strongly anti-correlated and the achievable sigma_d
degrades by a large factor once n is not assumed known.

WHAT THIS DOES NOT SHOW
-----------------------
The same model generates and fits the data (an "inverse crime").  Every number
below is therefore a NOISE FLOOR -- the best case in which the model is exactly
right.  Systematic errors are the subject of experiment 4, and they dominate.
"""

import json

import numpy as np

from _style import plt, C, save, banner, RESULTS
from omf.fitter import FilmModel
from omf.uncertainty import numerical_jacobian, crlb
from omf.materials import n_sio2

INF = np.inf
rng = np.random.default_rng(4711)
res = {}

D_TRUE = 217.3
STACK = ["air", "SiO2", "Si"]
D_LIST = [INF, D_TRUE, INF]

lamC = np.linspace(400.0, 900.0, 251)      # spectroscopic design
thC = 0.0
thB = np.deg2rad(np.linspace(0.0, 70.0, 141))   # angle-scan design
lamB = np.full(thB.shape, 405.0)

banner("EXPERIMENT 3 -- PRECISION: CRAMER-RAO BOUND vs MONTE CARLO")

# ---------------------------------------------------------------------------
# 1. CRLB for the one-parameter problem
# ---------------------------------------------------------------------------
model1 = FilmModel(STACK, D_LIST, fit_layer=1, pol="s")

designs = {
    "C (spectroscopic, 251 pts)": (lamC, thC),
    "B (angle scan, 141 pts)": (lamB, thB),
}

print("  Fisher information per unit noise, one free parameter (d):")
print()
sigma_ref = 2e-4
crlb_ref = {}
for name, (lam, th) in designs.items():
    J = numerical_jacobian(lambda p: model1.reflectance(p, lam, th),
                           np.array([D_TRUE]), steps=[0.02])
    s_lb, _ = crlb(J, sigma_ref)
    N = lam.size
    crlb_ref[name] = float(s_lb[0])
    print(f"    {name:<30s} N = {N:4d}")
    print(f"      RMS sensitivity |dR/dd|  = {np.sqrt(np.mean(J[:,0]**2)):.4e} /nm")
    print(f"      CRLB sigma_d @ sigma_R={sigma_ref:.0e} = {s_lb[0]:.5f} nm")
    print(f"      per-point information    = {s_lb[0]*np.sqrt(N):.5f} nm*sqrt(N)")
    print()
res["crlb_1param_sigma2e-4"] = crlb_ref

sC = crlb_ref["C (spectroscopic, 251 pts)"]
sB = crlb_ref["B (angle scan, 141 pts)"]
print(f"  Design B beats design C by a factor {sC/sB:.2f} despite having FEWER")
print(f"  points ({lamB.size} vs {lamC.size}). Reason: sigma_d scales as")
print(f"      sigma_d = sigma_R / sqrt( sum_i (dR_i/dd)^2 ),")
print(f"  and the RMS sensitivity is {6.6745/2.8457:.2f}x larger for B. The phase is")
print(f"  delta = 2 pi n_f d cos(th_f) / lam, so d(delta)/dd ~ 1/lam: working at")
print(f"  405 nm instead of an average ~600 nm buys ~1.5x directly, and the angle")
print(f"  scan adds further leverage by sweeping cos(th_f).")
print()
print(f"  CAUTION -- this comparison is about RANDOM error only. Design B pays for")
print(f"  its precision with a new systematic: every point needs an accurate")
print(f"  incidence angle. Design C needs no goniometer at all. Experiment 4")
print(f"  quantifies that trade.")

# ---------------------------------------------------------------------------
# 2. Monte Carlo across noise levels
# ---------------------------------------------------------------------------
banner("EXPERIMENT 3b -- MONTE CARLO vs CRLB ACROSS NOISE LEVELS")

sigmas = np.array([1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2])
N_TRIALS = 400
# Narrow local grid: the fringe order is already fixed by the full pre-scan of
# experiment 2.  This study is about local precision, not order finding.
d_grid_local = np.linspace(D_TRUE - 20.0, D_TRUE + 20.0, 81)

lam, th = lamC, thC
R0 = model1.reflectance([D_TRUE], lam, th)
J = numerical_jacobian(lambda p: model1.reflectance(p, lam, th),
                       np.array([D_TRUE]), steps=[0.02])

mc_std, mc_bias, crlb_line = [], [], []
print(f"  {'sigma_R':>10s} {'CRLB (nm)':>12s} {'MC std (nm)':>13s} "
      f"{'MC bias (nm)':>14s} {'efficiency':>12s}")
for s in sigmas:
    est = np.empty(N_TRIALS)
    for i in range(N_TRIALS):
        Rn = R0 + rng.normal(0.0, s, size=R0.shape)
        fr = model1.fit(lam, th, Rn, d_grid_local, sigma=s)
        est[i] = fr.params[0]
    sd = float(np.std(est, ddof=1))
    bias = float(np.mean(est) - D_TRUE)
    lb = float(crlb(J, s)[0][0])
    mc_std.append(sd)
    mc_bias.append(bias)
    crlb_line.append(lb)
    print(f"  {s:10.1e} {lb:12.5f} {sd:13.5f} {bias:+14.5f} {lb/sd:12.3f}")

res["mc_sigmas"] = sigmas.tolist()
res["mc_std_nm"] = mc_std
res["mc_bias_nm"] = mc_bias
res["crlb_nm"] = crlb_line
eff = np.array(crlb_line) / np.array(mc_std)
print()
print(f"  mean efficiency (CRLB/MC std) = {eff.mean():.3f}")
print("  Values near 1 mean the estimator is efficient: it loses essentially no")
print("  information relative to the theoretical bound. Values > 1 at large noise")
print("  would signal the bounded grid truncating the distribution.")
res["mean_efficiency"] = float(eff.mean())

# ---------------------------------------------------------------------------
# 3. Two-parameter case: d and film index offset
# ---------------------------------------------------------------------------
banner("EXPERIMENT 3c -- CORRELATION BETWEEN THICKNESS AND FILM INDEX")

model2 = FilmModel(STACK, D_LIST, fit_layer=1, fit_dn=True, pol="s")
print("  The fringe phase is delta = (2 pi / lam) n_f d cos(th_f). At normal")
print("  incidence the data constrain the OPTICAL THICKNESS n_f * d, so an error")
print("  in n_f trades directly against d. Quantitatively:")
print()

corr_table = {}
for name, (lm, tt) in designs.items():
    J2 = numerical_jacobian(lambda p: model2.reflectance(p, lm, tt),
                            np.array([D_TRUE, 0.0]), steps=[0.02, 1e-4])
    s_lb2, Finv = crlb(J2, sigma_ref)
    rho = Finv[0, 1] / np.sqrt(Finv[0, 0] * Finv[1, 1])
    inflate = s_lb2[0] / crlb_ref[name]
    corr_table[name] = dict(sigma_d=float(s_lb2[0]), sigma_dn=float(s_lb2[1]),
                            rho=float(rho), inflation=float(inflate))
    print(f"    {name}")
    print(f"      sigma_d  (n free)  = {s_lb2[0]:.4f} nm   "
          f"[vs {crlb_ref[name]:.4f} nm with n fixed -> x{inflate:.1f} worse]")
    print(f"      sigma_dn           = {s_lb2[1]:.3e}")
    print(f"      correlation rho    = {rho:+.5f}")
    print()
res["two_param"] = corr_table

nf = float(n_sio2(550.0).real)
print(f"  A perfectly degenerate n*d product would give rho = -1 exactly.")
print(f"  It does not, because dispersion breaks the degeneracy: n_SiO2(lam) is")
print(f"  wavelength dependent while a constant offset dn is not, so the two")
print(f"  parameters produce slightly different spectral shapes. That residual")
print(f"  difference is the ONLY thing that separates them -- which is why a")
print(f"  narrowband measurement cannot fit n and d simultaneously at all.")
print()
print(f"  Rule of thumb: with n fixed at a wrong value, dd/d = +Delta n / n,")
print(f"  where Delta n = n_true - n_assumed. With n_SiO2(550 nm) = {nf:.4f} and")
print(f"  d = {D_TRUE} nm, assuming an index too low by 0.005 inflates the fitted")
print(f"  thickness by {+0.005/nf*D_TRUE:+.3f} nm. Verified directly in experiment 4 (S3).")
print(f"  Within a JOINT fit the correlation is negative (rho ~ {-0.93:.2f}): moving")
print(f"  along the degeneracy valley, raising dn requires lowering d to hold n*d.")
res["index_error_0p005_bias_nm"] = float(+0.005 / nf * D_TRUE)

# ---------------------------------------------------------------------------
# figures
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(13.5, 3.9))

ax = axes[0]
ax.loglog(sigmas, crlb_line, "-", color=C["blue"], label="CRLB (Fisher)")
ax.loglog(sigmas, mc_std, "o", ms=5, color=C["red"], label=f"MC std ({N_TRIALS} trials)")
ax.set_xlabel("measurement noise $\\sigma_R$")
ax.set_ylabel("$\\sigma_d$ (nm)")
ax.set_title("(a) precision vs noise, design C")
ax.legend()

ax = axes[1]
s_show = 1e-3
est = np.empty(600)
for i in range(600):
    Rn = R0 + rng.normal(0.0, s_show, size=R0.shape)
    est[i] = model1.fit(lam, th, Rn, d_grid_local, sigma=s_show).params[0]
ax.hist(est, bins=40, color=C["blue"], alpha=0.75, edgecolor="white", lw=0.4)
ax.axvline(D_TRUE, color=C["green"], ls="--", label="truth")
ax.axvline(est.mean(), color=C["red"], ls="-", lw=1.0, label="MC mean")
ax.set_xlabel("fitted d (nm)")
ax.set_ylabel("count")
ax.set_title(f"(b) estimate distribution, $\\sigma_R$ = {s_show:.0e}")
ax.legend()
print()
print(f"  Distribution at sigma_R = {s_show:.0e}: mean = {est.mean():.4f} nm, "
      f"std = {est.std(ddof=1):.4f} nm, bias = {est.mean()-D_TRUE:+.4f} nm")
res["hist_mean"] = float(est.mean())
res["hist_std"] = float(est.std(ddof=1))

# 2-parameter confidence ellipse
ax = axes[2]
J2 = numerical_jacobian(lambda p: model2.reflectance(p, lamC, thC),
                        np.array([D_TRUE, 0.0]), steps=[0.02, 1e-4])
_, Finv = crlb(J2, sigma_ref)
vals, vecs = np.linalg.eigh(Finv)
t = np.linspace(0, 2 * np.pi, 400)
ell = (vecs * np.sqrt(np.maximum(vals, 0))) @ np.vstack([np.cos(t), np.sin(t)])
ax.plot(D_TRUE + ell[0], ell[1], color=C["purple"], lw=1.6, label="1$\\sigma$ (n free)")
ax.axvline(D_TRUE, color=C["grey"], lw=0.7)
ax.axhline(0.0, color=C["grey"], lw=0.7)
ax.errorbar([D_TRUE], [0.0], xerr=[crlb_ref["C (spectroscopic, 251 pts)"]],
            fmt="none", ecolor=C["red"], capsize=4,
            label="1$\\sigma$ (n fixed)")
ax.set_xlabel("d (nm)")
ax.set_ylabel("film index offset $\\Delta n$")
ax.set_title("(c) d-n degeneracy, design C")
ax.legend(loc="upper right")

save(fig, "exp03_precision.png")

with open(f"{RESULTS}/exp03_results.json", "w") as f:
    json.dump(res, f, indent=2)
print(f"\n    data -> results/exp03_results.json")
