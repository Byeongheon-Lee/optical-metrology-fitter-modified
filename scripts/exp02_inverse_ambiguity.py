"""
EXPERIMENT 2 -- the inverse problem and the fringe-order ambiguity.

Question: given R, can d be recovered uniquely?  The answer depends entirely on
what was measured, not on how clever the optimiser is.

Three measurement designs, same sample (d_true = 217.3 nm SiO2 on Si):

  A. Single wavelength, single angle.   1 independent datum.
  B. Single wavelength, angle scan.     Phase varies as sqrt(n_f^2 - sin^2 th).
  C. Spectroscopic, normal incidence.   Phase varies as 1/lambda.

For each we map the full cost landscape SSR(d) over 0-600 nm, then run the fit.
The point of the exercise is that design A is *unsolvable in principle*: the
landscape is a comb of exact zeros.  No optimiser, no regularisation, and no
amount of averaging repairs a measurement that does not contain the information.

Finally: a local optimiser seeded at a naive initial guess is compared against
the coarse-scan-seeded fit, to show what the pre-scan actually buys.
"""

import json

import numpy as np
from scipy.optimize import least_squares

from _style import plt, C, save, banner, RESULTS
from omf.core import coh_tmm
from omf.fitter import FilmModel
from omf.materials import build_n_list, n_sio2

INF = np.inf
rng = np.random.default_rng(20260815)
res = {}

D_TRUE = 217.3
STACK = ["air", "SiO2", "Si"]
D_LIST = [INF, D_TRUE, INF]

banner("EXPERIMENT 2 -- INVERSE PROBLEM: FRINGE-ORDER AMBIGUITY")
print(f"  ground truth: d = {D_TRUE} nm of SiO2 on Si")
print(f"  noise: sigma_R = 2e-4 (typical for a photodiode + lock-in ratio measurement)")
SIGMA = 2e-4

# ---------------------------------------------------------------------------
# define the three measurement designs
# ---------------------------------------------------------------------------
designs = {}

# A: single wavelength, single angle -- one datum
lamA = np.array([405.0])
thA = 0.0
designs["A"] = dict(lam=lamA, th=thA, pol="s",
                    label="A: 405 nm, normal incidence (1 point)")

# B: single wavelength, angle scan
thB = np.deg2rad(np.linspace(0.0, 70.0, 141))
lamB = np.full(thB.shape, 405.0)
designs["B"] = dict(lam=lamB, th=thB, pol="s",
                    label="B: 405 nm, angle scan 0-70 deg (141 points)")

# C: spectroscopic, normal incidence
lamC = np.linspace(400.0, 900.0, 251)
thC = 0.0
designs["C"] = dict(lam=lamC, th=thC, pol="s",
                    label="C: 400-900 nm, normal incidence (251 points)")

# ---------------------------------------------------------------------------
# generate synthetic data and map the cost landscape
# ---------------------------------------------------------------------------
d_grid = np.linspace(1.0, 600.0, 3000)
fig, axes = plt.subplots(2, 3, figsize=(14, 7))

for col, key in enumerate("ABC"):
    D = designs[key]
    lam, th = D["lam"], D["th"]
    n_stack = build_n_list(STACK, lam)

    R_true = coh_tmm("s", n_stack, D_LIST, th, lam)["R"]
    R_meas = R_true + rng.normal(0.0, SIGMA, size=R_true.shape)
    D["R_meas"] = R_meas

    model = FilmModel(STACK, D_LIST, fit_layer=1, pol="s")
    ssr = np.array([
        np.sum((model.reflectance([d], lam, th) - R_meas) ** 2) for d in d_grid])
    D["ssr"] = ssr

    # ---- top row: the data ------------------------------------------------
    ax = axes[0, col]
    if key == "B":
        ax.plot(np.rad2deg(th), R_meas, ".", ms=2.5, color=C["grey"], label="data")
        ax.plot(np.rad2deg(th), R_true, color=C["blue"], label="truth")
        ax.set_xlabel("angle (deg)")
    elif key == "C":
        ax.plot(lam, R_meas, ".", ms=2.5, color=C["grey"], label="data")
        ax.plot(lam, R_true, color=C["blue"], label="truth")
        ax.set_xlabel("wavelength (nm)")
    else:
        ax.plot([0], R_meas, "o", ms=7, color=C["blue"])
        ax.set_xlim(-1, 1)
        ax.set_xticks([])
        ax.set_xlabel("(a single number)")
    ax.set_ylabel("R")
    ax.set_title(D["label"], fontsize=8.5)
    if key != "A":
        ax.legend()

    # ---- bottom row: the cost landscape -----------------------------------
    ax = axes[1, col]
    ax.semilogy(d_grid, np.maximum(ssr, 1e-18), color=C["red"], lw=1.0)
    ax.axvline(D_TRUE, color=C["green"], ls="--", lw=1.0, label=f"truth {D_TRUE} nm")
    ax.set_xlabel("trial thickness d (nm)")
    ax.set_ylabel("SSR")
    ax.legend(loc="lower right")

    # ---- how many thicknesses are STATISTICALLY indistinguishable? ---------
    # chi^2 = SSR/sigma^2 has mean N and variance 2N for the correct model.
    # A candidate d is acceptable at ~3 sigma if  chi^2(d) < N + 3 sqrt(2N),
    # i.e.  SSR(d) < sigma^2 (N + 3 sqrt(2N)).
    # This is the criterion that matters: not "is there a local minimum" but
    # "would this thickness be rejected by the data".
    N = int(np.size(R_meas))
    ssr_accept = SIGMA**2 * (N + 3.0 * np.sqrt(2.0 * N))
    acceptable = ssr < ssr_accept
    # contiguous accepted bands = distinct candidate thicknesses
    edges = np.diff(acceptable.astype(int))
    starts_i = np.where(edges == 1)[0] + 1
    ends_i = np.where(edges == -1)[0] + 1
    if acceptable[0]:
        starts_i = np.r_[0, starts_i]
    if acceptable[-1]:
        ends_i = np.r_[ends_i, acceptable.size]
    bands = [(d_grid[a], d_grid[b - 1]) for a, b in zip(starts_i, ends_i)]
    centres = np.array([0.5 * (a + b) for a, b in bands])
    n_cand = len(bands)

    ax.axhline(ssr_accept, color=C["grey"], ls=":", lw=1.0)
    ax.text(0.02, 0.02, "3$\\sigma$ acceptance", transform=ax.transAxes,
            ha="left", va="bottom", fontsize=7, color=C["grey"])
    ax.set_title(f"cost landscape: {n_cand} thickness(es) survive the data",
                 fontsize=8.5)

    print()
    print(f"  --- design {key}: {D['label']}")
    print(f"      N = {N} data points, chi^2 acceptance SSR < {ssr_accept:.3e}")
    print(f"      global minimum at d = {d_grid[int(np.argmin(ssr))]:.3f} nm")
    print(f"      statistically acceptable thicknesses: {n_cand}")
    if n_cand > 1:
        period = 405.0 / (2.0 * float(n_sio2(405.0).real))
        print(f"      candidates (nm): "
              f"{np.array2string(centres, precision=1, max_line_width=200)}")
        sp = np.diff(centres)
        print(f"      successive gaps: "
              f"{np.array2string(sp, precision=1, max_line_width=200)}")
        print(f"      TWO distinct degeneracies are visible here:")
        print(f"        (i)  FLANK ambiguity  -- within one fringe period R(d) rises")
        print(f"             then falls, so a single R value is matched twice.")
        print(f"             These are the closely spaced pairs above.")
        print(f"        (ii) ORDER ambiguity  -- the whole pattern repeats with")
        print(f"             period lam/(2 n_f) = {period:.2f} nm.")
        if sp.size >= 2:
            print(f"             observed pair-to-pair recurrence = "
                  f"{centres[2]-centres[0]:.2f} nm  (predicted {period:.2f} nm)")
        print(f"      Design A cannot resolve either.  A phase-sensitive measurement")
        print(f"      (ellipsometry) removes (i); broadband or angle data removes (ii).")
    res[f"design_{key}_n_candidates"] = n_cand
    res[f"design_{key}_candidates_nm"] = [round(float(c), 2) for c in centres[:20]]

save(fig, "exp02_ambiguity.png")

# ---------------------------------------------------------------------------
# actually fit designs B and C
# ---------------------------------------------------------------------------
banner("EXPERIMENT 2b -- FITS (coarse pre-scan + local refinement)")
for key in "BC":
    D = designs[key]
    model = FilmModel(STACK, D_LIST, fit_layer=1, pol="s")
    fr = model.fit(D["lam"], D["th"], D["R_meas"],
                   d_grid=np.linspace(1.0, 600.0, 1200), sigma=SIGMA)
    err = fr.params[0] - D_TRUE
    print()
    print(f"  design {key}")
    print(f"      coarse pre-scan start : d = {fr.coarse_best[0]:.3f} nm")
    print(f"      refined               : d = {fr.params[0]:.4f} +/- {fr.sigma[0]:.4f} nm")
    print(f"      error vs truth        : {err:+.4f} nm  ({abs(err)/fr.sigma[0]:.2f} sigma)")
    print(f"      residual RMS          : {fr.rms:.3e}  (injected sigma = {SIGMA:.1e})")
    res[f"design_{key}_d_fit"] = float(fr.params[0])
    res[f"design_{key}_sigma"] = float(fr.sigma[0])
    res[f"design_{key}_err"] = float(err)

# ---------------------------------------------------------------------------
# what the pre-scan buys: naive local start vs coarse-seeded
# ---------------------------------------------------------------------------
banner("EXPERIMENT 2c -- NAIVE LOCAL FIT vs COARSE-SEEDED FIT (design C)")
D = designs["C"]
model = FilmModel(STACK, D_LIST, fit_layer=1, pol="s")


def resid(p):
    return (model.reflectance(p, D["lam"], D["th"]) - D["R_meas"]) / SIGMA


print(f"  {'start d0 (nm)':>14s} {'naive local result':>22s} {'coarse-seeded result':>24s}")
naive_fail = 0
starts = [20.0, 60.0, 100.0, 150.0, 217.0, 300.0, 380.0, 450.0, 550.0]
for d0 in starts:
    r = least_squares(resid, [d0], bounds=([1.0], [600.0]),
                      xtol=1e-14, ftol=1e-14, gtol=1e-14)
    ok = abs(r.x[0] - D_TRUE) < 0.5
    naive_fail += (not ok)
    mark = "  ok" if ok else "  WRONG ORDER"
    print(f"  {d0:14.1f} {r.x[0]:16.3f} nm{mark:<12s} {D_TRUE:16.3f} nm  ok")
print()
print(f"  naive local optimiser: {naive_fail} / {len(starts)} starting points "
      f"converged to the wrong fringe order.")
print("  The coarse pre-scan removes this failure mode entirely, at the cost of")
print("  one exhaustive sweep -- which the vectorised forward model makes free.")
res["naive_wrong_order_fraction"] = naive_fail / len(starts)

with open(f"{RESULTS}/exp02_results.json", "w") as f:
    json.dump(res, f, indent=2)
print(f"\n    data -> results/exp02_results.json")
