"""
Validation suite for omf.core.

Three tiers, in increasing order of evidential weight:

  A. Internal consistency -- energy conservation, branch selection, broadcasting.
     Catches coding errors but cannot catch a wrong *convention*.
  B. Analytic limits -- Fresnel, Airy, Brewster, absentee layer, quarter-wave AR,
     total internal reflection.  These have closed forms derived independently of
     the matrix machinery, so agreement tests the physics, not just the code.
  C. External cross-check -- against `tmm` (S. J. Byrnes), the reference
     implementation of the same paper this code follows.  This is the strongest
     single test: an independent author, independent code path, same physics.

Run:  python tests/test_core.py      (or: pytest tests/test_core.py)
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from omf.core import coh_tmm, fresnel_rt, kz_from_index          # noqa: E402
from omf.materials import n_si, n_sio2, build_n_list             # noqa: E402

INF = np.inf
_RESULTS = []


def check(name, condition, detail=""):
    _RESULTS.append((name, bool(condition), detail))
    flag = "PASS" if condition else "FAIL"
    print(f"  [{flag}] {name}" + (f"   {detail}" if detail else ""))
    assert condition, f"{name}: {detail}"


def run(test_fn):
    """Run one test function, keeping the batch alive if it fails.

    `check()` still asserts, so `pytest tests/test_core.py` correctly flags
    the individual failing test.  But a failure inside one test function must
    not abort the rest of the suite when driven from `main()` -- otherwise a
    single failing check silently prevents every check after it (and the
    final "N / 34 passed" summary) from ever running.
    """
    try:
        test_fn()
    except AssertionError:
        pass


# ============================================================================
# TIER A -- internal consistency
# ============================================================================
def test_energy_conservation_lossless():
    """R + T = 1 for a lossless stack, both polarisations, all angles."""
    lam = np.linspace(400.0, 800.0, 41)
    th = np.linspace(0.0, np.deg2rad(85.0), 18)
    LAM, TH = np.meshgrid(lam, th, indexing="ij")
    n = build_n_list(["air", "SiO2", 1.60], LAM)
    for pol in ("s", "p"):
        out = coh_tmm(pol, n, [INF, 217.0, INF], TH, LAM)
        err = np.max(np.abs(out["R"] + out["T"] - 1.0))
        check(f"A1 energy conservation, lossless, {pol}-pol",
              err < 1e-12, f"max|R+T-1| = {err:.2e}")


def test_energy_conservation_absorbing_film():
    """R + T + A = 1 with an absorbing film and a lossless substrate.

    This is where a wrong p-polarisation transmittance prefactor shows up: using
    the s-form Re(n cos th) instead of Re(n cos th*) leaves a residual that grows
    with angle and with Im(n).
    """
    lam = np.linspace(450.0, 750.0, 31)
    th = np.linspace(0.0, np.deg2rad(80.0), 15)
    LAM, TH = np.meshgrid(lam, th, indexing="ij")
    n = build_n_list(["air", 2.10 + 0.35j, 1.52], LAM)
    for pol in ("s", "p"):
        out = coh_tmm(pol, n, [INF, 95.0, INF], TH, LAM)
        A = out["A"]
        check(f"A2 absorbed fraction non-negative, {pol}-pol",
              np.min(A) > -1e-12, f"min A = {np.min(A):.2e}")
        check(f"A3 R+T+A = 1 by construction, {pol}-pol",
              np.max(np.abs(out["R"] + out["T"] + A - 1.0)) < 1e-12)


def test_branch_selection():
    """Im(k_z) >= 0 in every layer, including evanescent and absorbing ones."""
    lam = np.array([405.0])
    th = np.deg2rad(np.linspace(0.0, 89.0, 90))
    n = build_n_list([1.52, 1.00, "Si"], np.broadcast_to(lam, th.shape))
    kx = 1.52 * (2 * np.pi / 405.0) * np.sin(th)
    kz = kz_from_index(n, np.broadcast_to(lam, th.shape), kx)
    check("A4 Im(k_z) >= 0 everywhere (incl. frustrated TIR)",
          np.min(kz.imag) > -1e-10, f"min Im(kz) = {np.min(kz.imag):.2e}")


def test_broadcasting_matches_loop():
    """A vectorised call reproduces an element-by-element loop exactly."""
    lam = np.linspace(400.0, 700.0, 25)
    th = np.deg2rad(30.0)
    n = build_n_list(["air", "SiO2", "Si"], lam)
    vec = coh_tmm("p", n, [INF, 180.0, INF], th, lam)["R"]
    loop = np.array([
        coh_tmm("p", build_n_list(["air", "SiO2", "Si"], np.array(L)),
                [INF, 180.0, INF], th, np.array(L))["R"]
        for L in lam])
    check("A5 vectorised == looped", np.max(np.abs(vec - loop)) < 1e-14,
          f"max diff = {np.max(np.abs(vec - loop)):.2e}")


def test_no_interface():
    """Identical index throughout -> R = 0, T = 1 (no spurious interfaces)."""
    lam = np.array([550.0])
    n = build_n_list([1.5, 1.5, 1.5], lam)
    for pol in ("s", "p"):
        out = coh_tmm(pol, n, [INF, 333.0, INF], np.deg2rad(41.0), lam)
        check(f"A6 index-matched stack is transparent, {pol}-pol",
              abs(out["R"][0]) < 1e-14 and abs(out["T"][0] - 1.0) < 1e-14)


# ============================================================================
# TIER B -- analytic limits
# ============================================================================
def test_single_interface_fresnel():
    """Two-layer stack must reproduce the textbook Fresnel coefficients."""
    n1, n2 = 1.0, 1.52
    th1 = np.deg2rad(np.linspace(0.0, 89.0, 90))
    th2 = np.arcsin(n1 * np.sin(th1) / n2)
    lam = np.full(th1.shape, 589.3)
    n = build_n_list([n1, n2], lam)

    rs_a = (n1 * np.cos(th1) - n2 * np.cos(th2)) / (n1 * np.cos(th1) + n2 * np.cos(th2))
    rp_a = (n2 * np.cos(th1) - n1 * np.cos(th2)) / (n2 * np.cos(th1) + n1 * np.cos(th2))

    rs = coh_tmm("s", n, [INF, INF], th1, lam)["r"]
    rp = coh_tmm("p", n, [INF, INF], th1, lam)["r"]
    check("B1 s-pol reproduces Fresnel r_s",
          np.max(np.abs(rs - rs_a)) < 1e-13, f"max diff = {np.max(np.abs(rs - rs_a)):.2e}")
    check("B2 p-pol reproduces Fresnel r_p",
          np.max(np.abs(rp - rp_a)) < 1e-13, f"max diff = {np.max(np.abs(rp - rp_a)):.2e}")


def test_brewster_angle():
    """R_p vanishes at theta_B = arctan(n2/n1)."""
    n1, n2 = 1.0, 1.52
    thB = np.arctan(n2 / n1)
    lam = np.array([589.3])
    n = build_n_list([n1, n2], lam)
    Rp = coh_tmm("p", n, [INF, INF], np.array([thB]), lam)["R"][0]
    Rs = coh_tmm("s", n, [INF, INF], np.array([thB]), lam)["R"][0]
    check("B3 R_p = 0 at Brewster angle",
          Rp < 1e-25, f"theta_B = {np.rad2deg(thB):.3f} deg, R_p = {Rp:.2e}")
    check("B4 R_s != 0 at Brewster angle", Rs > 0.1, f"R_s = {Rs:.4f}")


def test_airy_single_film():
    """Three-layer stack must reproduce the Airy summation exactly.

        r = (r01 + r12 e^{2i delta}) / (1 + r01 r12 e^{2i delta})

    Tested with a *complex* film index so the geometric-series bookkeeping is
    exercised, not just the real case.
    """
    lam = np.linspace(400.0, 900.0, 51)
    th0 = np.deg2rad(37.0)
    nlist = build_n_list(["air", 2.05 + 0.02j, "Si"], lam)
    d = 240.0

    k0 = 2 * np.pi / lam
    kx = 1.000293 * k0 * np.sin(th0)
    kz = kz_from_index(nlist, lam, kx)
    delta = kz[..., 1] * d

    for pol in ("s", "p"):
        r01, _ = fresnel_rt(pol, nlist[..., 0], nlist[..., 1], kz[..., 0], kz[..., 1])
        r12, _ = fresnel_rt(pol, nlist[..., 1], nlist[..., 2], kz[..., 1], kz[..., 2])
        ph = np.exp(2j * delta)
        r_airy = (r01 + r12 * ph) / (1.0 + r01 * r12 * ph)
        r_tmm = coh_tmm(pol, nlist, [INF, d, INF], th0, lam)["r"]
        err = np.max(np.abs(r_tmm - r_airy))
        check(f"B5 TMM == Airy summation, {pol}-pol", err < 1e-13,
              f"max diff = {err:.2e}")


def test_absentee_layer():
    """A half-wave film is optically invisible: R equals the bare substrate.

    delta = pi  =>  e^{2i delta} = 1  =>  the Airy expression collapses to
    (r01 + r12)/(1 + r01 r12) = r02.  A classic exam identity and a sharp test of
    the phase factor's sign and magnitude.
    """
    lam = 632.8
    nf = float(n_sio2(lam).real)
    th0 = np.deg2rad(25.0)
    kx_over_k0 = 1.000293 * np.sin(th0)
    cos_f = np.sqrt(1.0 - (kx_over_k0 / nf) ** 2)
    d_half = lam / (2.0 * nf * cos_f)

    L = np.array([lam])
    n3 = build_n_list(["air", "SiO2", "Si"], L)
    n2 = build_n_list(["air", "Si"], L)
    for pol in ("s", "p"):
        R_film = coh_tmm(pol, n3, [INF, d_half, INF], th0, L)["R"][0]
        R_bare = coh_tmm(pol, n2, [INF, INF], th0, L)["R"][0]
        check(f"B6 half-wave layer is absentee, {pol}-pol",
              abs(R_film - R_bare) < 1e-12,
              f"d_1/2 = {d_half:.3f} nm, dR = {abs(R_film - R_bare):.2e}")


def test_zero_thickness():
    """d -> 0 must return the bare-substrate result."""
    lam = np.linspace(400.0, 800.0, 21)
    th0 = np.deg2rad(55.0)
    n3 = build_n_list(["air", "SiO2", "Si"], lam)
    n2 = build_n_list(["air", "Si"], lam)
    for pol in ("s", "p"):
        R3 = coh_tmm(pol, n3, [INF, 0.0, INF], th0, lam)["R"]
        R2 = coh_tmm(pol, n2, [INF, INF], th0, lam)["R"]
        check(f"B7 zero-thickness film == bare substrate, {pol}-pol",
              np.max(np.abs(R3 - R2)) < 1e-14)


def test_quarter_wave_ar():
    """Perfect single-layer AR coating: n_f = sqrt(n0 ns), d = lam/(4 n_f) -> R = 0."""
    lam = 550.0
    n0, ns = 1.0, 2.25
    nf = np.sqrt(n0 * ns)
    d = lam / (4.0 * nf)
    L = np.array([lam])
    n = build_n_list([n0, nf, ns], L)
    R = coh_tmm("s", n, [INF, d, INF], 0.0, L)["R"][0]
    check("B8 quarter-wave AR gives R = 0 at design wavelength",
          R < 1e-25, f"n_f = {nf:.4f}, d = {d:.3f} nm, R = {R:.2e}")


def test_total_internal_reflection():
    """Beyond the critical angle: R = 1 exactly, T = 0."""
    n1, n2 = 1.52, 1.00
    thc = np.arcsin(n2 / n1)
    th = np.linspace(thc + 1e-4, np.deg2rad(89.0), 40)
    lam = np.full(th.shape, 633.0)
    n = build_n_list([n1, n2], lam)
    for pol in ("s", "p"):
        out = coh_tmm(pol, n, [INF, INF], th, lam)
        check(f"B9 total internal reflection R = 1, {pol}-pol",
              np.max(np.abs(out["R"] - 1.0)) < 1e-13,
              f"theta_c = {np.rad2deg(thc):.3f} deg, max|R-1| = {np.max(np.abs(out['R'] - 1.0)):.2e}")


def test_normal_incidence_pol_degenerate():
    """At theta = 0 the s/p distinction is meaningless: R_s must equal R_p."""
    lam = np.linspace(300.0, 1000.0, 71)
    n = build_n_list(["air", "SiO2", "Si"], lam)
    Rs = coh_tmm("s", n, [INF, 150.0, INF], 0.0, lam)["R"]
    Rp = coh_tmm("p", n, [INF, 150.0, INF], 0.0, lam)["R"]
    check("B10 R_s == R_p at normal incidence",
          np.max(np.abs(Rs - Rp)) < 1e-14, f"max diff = {np.max(np.abs(Rs - Rp)):.2e}")


def test_thickness_periodicity():
    """R is periodic in d with period lam/(2 n_f cos th_f) for a lossless film."""
    lam = 546.1
    nf = float(n_sio2(lam).real)
    th0 = np.deg2rad(20.0)
    cos_f = np.sqrt(1.0 - (1.000293 * np.sin(th0) / nf) ** 2)
    period = lam / (2.0 * nf * cos_f)
    L = np.array([lam])
    n = build_n_list(["air", "SiO2", "Si"], L)
    d0 = 173.0
    Ra = coh_tmm("s", n, [INF, d0, INF], th0, L)["R"][0]
    Rb = coh_tmm("s", n, [INF, d0 + period, INF], th0, L)["R"][0]
    Rc = coh_tmm("s", n, [INF, d0 + 3 * period, INF], th0, L)["R"][0]
    check("B11 R periodic in d (fringe-order degeneracy is real)",
          abs(Ra - Rb) < 1e-12 and abs(Ra - Rc) < 1e-12,
          f"period = {period:.3f} nm, |dR| = {abs(Ra - Rc):.2e}")


def test_semi_infinite_absorber_flux():
    """What `T` means for a semi-infinite absorbing substrate.

    A tempting but WRONG expectation is T -> 0 for bulk silicon at 405 nm, on the
    grounds that the wafer is opaque.  It is not what this quantity is.  With a
    semi-infinite exit medium there is no second interface, so `T` is the
    time-averaged Poynting flux crossing *into* the substrate at its front face.
    That flux is subsequently absorbed over an infinite path, but it has already
    entered.  Hence R + T = 1 exactly, and the absorbed fraction A is zero by the
    bookkeeping of this function -- absorption inside a semi-infinite medium is
    not counted as "A", it is counted as "T".

    Opacity is a property of a *finite* slab, and is tested separately below.
    """
    lam = np.array([405.0])
    n = build_n_list(["air", "Si"], lam)
    out = coh_tmm("s", n, [INF, INF], np.deg2rad(15.0), lam)
    check("B12 semi-infinite absorber: R + T = 1 (T = flux entering substrate)",
          abs(out["R"][0] + out["T"][0] - 1.0) < 1e-13,
          f"R = {out['R'][0]:.4f}, T = {out['T'][0]:.4f}")


def test_beer_lambert_thick_slab():
    """A finite absorbing slab obeys Beer-Lambert in the single-pass limit.

        T ~ (1 - R_01)^2 exp(-alpha d),   alpha = 4 pi k / lam

    When exp(-alpha d) << 1 the multiple-reflection terms of the Airy series are
    suppressed by an extra factor exp(-2 alpha d) and the single-pass estimate
    becomes exact.  Agreement here validates that Im(k_z) enters the propagation
    phase with the right sign and magnitude -- the branch rule, end to end.
    """
    lam_nm = 405.0
    lam = np.array([lam_nm])
    nSi = n_si(lam_nm)
    alpha = 4.0 * np.pi * nSi.imag / lam_nm          # 1/nm
    R01 = abs((1.0 - nSi) / (1.0 + nSi)) ** 2
    n = build_n_list(["air", "Si", "air"], lam)

    for d in (1000.0, 2000.0):
        T = coh_tmm("s", n, [INF, d, INF], 0.0, lam)["T"][0]
        est = (1.0 - R01) ** 2 * np.exp(-alpha * d)
        check(f"B13 Beer-Lambert, {d:.0f} nm Si slab",
              abs(T / est - 1.0) < 0.03,
              f"T = {T:.4e}, single-pass = {est:.4e}, ratio = {T/est:.4f}")
    check("B13b 1/e penetration depth at 405 nm",
          120.0 < 1.0 / alpha < 130.0, f"1/alpha = {1.0/alpha:.1f} nm")


# ============================================================================
# TIER C -- external cross-validation against Byrnes' reference implementation
# ============================================================================
def test_against_reference_tmm():
    try:
        import tmm as ref
    except ImportError:
        print("  [SKIP] C1-C3: reference `tmm` package not installed")
        return

    rng = np.random.default_rng(20260815)
    worst = {"s": 0.0, "p": 0.0}
    worst_t = {"s": 0.0, "p": 0.0}

    # 300 random stacks: random layer count, indices (some absorbing),
    # thicknesses, angles and wavelengths.
    for _ in range(300):
        nlayer = int(rng.integers(2, 6))
        n = [1.0]
        for _ in range(nlayer - 1):
            n.append(float(rng.uniform(1.2, 4.5)) + 1j * float(rng.uniform(0.0, 0.8)))
        n[-1] = complex(n[-1].real, float(rng.uniform(0.0, 0.5)))
        d = [INF] + [float(rng.uniform(5.0, 900.0)) for _ in range(nlayer - 2)] + [INF]
        th = float(rng.uniform(0.0, np.deg2rad(87.0)))
        lam = float(rng.uniform(300.0, 1600.0))

        narr = np.array(n, dtype=complex)[None, :]
        for pol in ("s", "p"):
            mine = coh_tmm(pol, narr, d, np.array([th]), np.array([lam]))
            theirs = ref.coh_tmm(pol, n, d, th, lam)
            worst[pol] = max(worst[pol], abs(mine["R"][0] - theirs["R"]))
            worst_t[pol] = max(worst_t[pol], abs(mine["T"][0] - theirs["T"]))

    for pol in ("s", "p"):
        check(f"C1 R matches Byrnes reference tmm, {pol}-pol (300 random stacks)",
              worst[pol] < 1e-12, f"max |dR| = {worst[pol]:.2e}")
        check(f"C2 T matches Byrnes reference tmm, {pol}-pol (300 random stacks)",
              worst_t[pol] < 1e-12, f"max |dT| = {worst_t[pol]:.2e}")

    # Realistic SiO2/Si stack across a spectrum, dispersive indices
    lam = np.linspace(300.0, 1000.0, 141)
    th = np.deg2rad(65.0)
    narr = build_n_list(["air", "SiO2", "Si"], lam)
    err = 0.0
    for pol in ("s", "p"):
        mine = coh_tmm(pol, narr, [INF, 312.0, INF], th, lam)["R"]
        theirs = np.array([
            ref.coh_tmm(pol, [complex(narr[i, 0]), complex(narr[i, 1]), complex(narr[i, 2])],
                        [INF, 312.0, INF], th, float(lam[i]))["R"]
            for i in range(lam.size)])
        err = max(err, float(np.max(np.abs(mine - theirs))))
    check("C3 dispersive SiO2/Si spectrum matches reference",
          err < 1e-12, f"max |dR| = {err:.2e}")


# ============================================================================
def main():
    print("=" * 74)
    print("TIER A -- internal consistency")
    print("=" * 74)
    run(test_energy_conservation_lossless)
    run(test_energy_conservation_absorbing_film)
    run(test_branch_selection)
    run(test_broadcasting_matches_loop)
    run(test_no_interface)

    print()
    print("=" * 74)
    print("TIER B -- analytic limits")
    print("=" * 74)
    run(test_single_interface_fresnel)
    run(test_brewster_angle)
    run(test_airy_single_film)
    run(test_absentee_layer)
    run(test_zero_thickness)
    run(test_quarter_wave_ar)
    run(test_total_internal_reflection)
    run(test_normal_incidence_pol_degenerate)
    run(test_thickness_periodicity)
    run(test_semi_infinite_absorber_flux)
    run(test_beer_lambert_thick_slab)

    print()
    print("=" * 74)
    print("TIER C -- external cross-validation")
    print("=" * 74)
    run(test_against_reference_tmm)

    npass = sum(1 for _, ok, _ in _RESULTS if ok)
    print()
    print("=" * 74)
    print(f"  {npass} / {len(_RESULTS)} checks passed")
    print("=" * 74)
    return 0 if npass == len(_RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
