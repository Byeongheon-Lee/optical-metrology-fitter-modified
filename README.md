# optical-metrology-fitter

A transfer-matrix forward model and inverse solver for thin-film optical
metrology, built to a standard where the uncertainty statement is defensible.

The headline result is deliberately two numbers, not one:

| | value | what it means |
|---|---|---|
| Algorithmic noise floor | **≈ 4 pm** | best case, model exactly correct (inverse crime) |
| Realistic accuracy | **≈ 1.3 nm** | model-form systematics included |

The gap between them is a factor of ~300 and is the entire point of the project.
A pipeline that reports only the first number is not measuring a thickness; it is
measuring its own self-consistency.

---

## 0. How this was built

The code and the validation scripts were written with AI coding tools. What I
contributed is the part that decides whether any of it can be believed: the
structure of the validation, the judgement of what each tier actually
guarantees, the systematic-error study in §4, and the limitations in §5.

That division is the right way to read §3. Thirty-four checks passing is not
the claim. The claim is that the three tiers carry different evidential
weight — Tier A catches coding mistakes but never a wrong convention, Tier B
tests the physics but is still self-consistency, and only Tier C is
external — and that even Tier C is not fully independent, since the author of
the `tmm` package wrote the paper this code follows. It establishes that the
method was transcribed correctly, and nothing beyond that.

---

## 1. Theory

### 1.1 Convention — fixed once, enforced everywhere

| choice | value |
|---|---|
| time dependence | $e^{-i\omega t}$ |
| complex index | $\tilde n = n + ik$, with $k \ge 0$ for a passive medium |
| forward wave | $e^{+ik_z z}$ |

These three are not independent. Given $e^{-i\omega t}$ and $\tilde n = n+ik$, a
wave travelling in $+z$ carries

$$e^{i k_z z} = e^{i\,\mathrm{Re}(k_z)z}\,e^{-\mathrm{Im}(k_z)z}$$

so physical decay requires $\mathrm{Im}(k_z)\ge 0$. That single inequality is the
**only** branch rule the code needs. Picking the other root describes a wave
that grows with distance — unphysical, and numerically fatal (overflow in
$e^{i k_z d}$ for thick absorbing layers).

The opposite convention $e^{+i\omega t}$ with $\tilde n = n - ik$ is equally valid
and appears in much of the ellipsometry literature. Mixing the two is the single
most common source of sign errors in TMM code, which is why the convention is
stated at the top of `core.py` and never revisited.

### 1.2 Snell's law as momentum conservation

The stack is translationally invariant in the plane, so the in-plane wavevector
is conserved across every interface:

$$k_x = n_0 k_0 \sin\theta_0 = \text{const}, \qquad
k_{z,j} = \sqrt{(\tilde n_j k_0)^2 - k_x^2}$$

This *is* Snell's law, written so that no complex angles ever appear. Total
internal reflection, absorbing media, and evanescent layers all fall out with no
special cases — $k_z$ simply becomes imaginary, and the branch rule handles it.
Writing the code in terms of $\theta_j = \arcsin(\cdot)$ instead would require
tracking which Riemann sheet each complex arcsine landed on.

### 1.3 Fresnel coefficients

Since $\tilde n_j\cos\theta_j = k_{z,j}/k_0$, the factor $k_0$ cancels from every
ratio:

$$
r^{s}_{ij}=\frac{k_{zi}-k_{zj}}{k_{zi}+k_{zj}},\qquad
t^{s}_{ij}=\frac{2k_{zi}}{k_{zi}+k_{zj}}
$$

$$
r^{p}_{ij}=\frac{\tilde n_j^2 k_{zi}-\tilde n_i^2 k_{zj}}{\tilde n_j^2 k_{zi}+\tilde n_i^2 k_{zj}},\qquad
t^{p}_{ij}=\frac{2\tilde n_i\tilde n_j k_{zi}}{\tilde n_j^2 k_{zi}+\tilde n_i^2 k_{zj}}
$$

The *sign* of $r^p$ is a genuine convention (it depends on how the positive
direction of $\mathbf{E}_p$ is defined after reflection). $|r^p|^2$ is not.

### 1.4 Transfer matrix

With layer 0 semi-infinite incident, layers $1\ldots N-2$ finite, layer $N-1$
semi-infinite exit, and $\delta_j = k_{zj} d_j$:

$$
M = D_{01}\prod_{j=1}^{N-2} P_j\,D_{j,j+1},\qquad
D_{ij}=\frac{1}{t_{ij}}\begin{pmatrix}1 & r_{ij}\\ r_{ij} & 1\end{pmatrix},\qquad
P_j=\begin{pmatrix}e^{-i\delta_j} & 0\\ 0 & e^{+i\delta_j}\end{pmatrix}
$$

$$r = \frac{M_{21}}{M_{11}},\qquad t = \frac{1}{M_{11}}$$

**Sanity check (done analytically, then in `test_core.py`).** For $N=3$:

$$M_{11}=\frac{e^{-i\delta}+r_{01}r_{12}e^{i\delta}}{t_{01}t_{12}},\quad
M_{21}=\frac{r_{01}e^{-i\delta}+r_{12}e^{i\delta}}{t_{01}t_{12}}$$

$$\Rightarrow\quad r=\frac{r_{01}+r_{12}e^{2i\delta}}{1+r_{01}r_{12}e^{2i\delta}}$$

which is exactly the Airy summation of the infinite geometric series of internal
reflections. The matrix formulation is that series, resummed.

### 1.5 Transmittance — the one place p differs from s

$$T_s=|t|^2\,\frac{\mathrm{Re}(\tilde n_f\cos\theta_f)}{\mathrm{Re}(\tilde n_0\cos\theta_0)},
\qquad
T_p=|t|^2\,\frac{\mathrm{Re}(\tilde n_f\cos^*\!\theta_f)}{\mathrm{Re}(\tilde n_0\cos^*\!\theta_0)}$$

The conjugation in the p case is not cosmetic. In $k_z$ form:

$$\mathrm{Re}(\tilde n\cos\theta)=\frac{\mathrm{Re}(k_z)}{k_0},\qquad
\mathrm{Re}(\tilde n\cos^*\!\theta)=\frac{\mathrm{Re}(\tilde n^2 k_z^*)}{k_0|\tilde n|^2}$$

They coincide for real $\tilde n$ but not otherwise. Using the s-form for p
breaks energy conservation, with an error that grows with angle and with
$\mathrm{Im}(\tilde n)$ — caught by test A3.

### 1.6 What "T" means for a semi-infinite absorber

A tempting error: bulk Si at 405 nm is opaque, so surely $T\to 0$? No. With a
semi-infinite exit medium there is no second interface, so $T$ is the Poynting
flux crossing *into* the substrate. That flux is absorbed over an infinite path,
but it has already entered. Hence $R+T=1$ exactly and $A=0$ by this bookkeeping.
Opacity is a property of a **finite** slab (test B13, Beer–Lambert).

### 1.7 The inverse problem is periodic

For a transparent film,

$$R(d)\simeq A+B\cos(2\delta),\qquad \delta=\frac{2\pi}{\lambda}n_f d\cos\theta_f$$

so $R$ is periodic in $d$ with period $\lambda/(2n_f\cos\theta_f)$ — 137.8 nm for
SiO₂ at 405 nm, normal incidence. **Two distinct degeneracies** follow, and they
are different problems requiring different fixes:

| degeneracy | origin | removed by |
|---|---|---|
| **flank** | within one period $R$ rises then falls, so one $R$ value matches two $d$ | phase-sensitive measurement (ellipsometry) |
| **order** | pattern repeats every $\lambda/2n_f$ | broadband or angle-resolved data |

Neither is an optimiser problem. A single-wavelength, single-angle reflectance
measurement cannot determine $d$, and no algorithm repairs that.

### 1.8 Precision: the Cramér–Rao bound

For independent Gaussian noise $\sigma_i$, the Fisher information is

$$F_{ab}=\sum_i \frac{1}{\sigma_i^2}\frac{\partial R_i}{\partial p_a}\frac{\partial R_i}{\partial p_b},
\qquad \mathrm{Cov}(\hat p)\succeq F^{-1}$$

For one parameter this reduces to

$$\sigma_d \ \ge\ \frac{\sigma_R}{\sqrt{\sum_i (\partial R_i/\partial d)^2}}$$

This bounds the **variance** — the random error. It says nothing whatsoever
about **bias** from a wrong model. A fit can sit exactly on the CRLB and still be
1 nm wrong. Random precision and systematic accuracy are separate budgets, and
§4 shows the second dominates by two orders of magnitude.

---

## 2. Structure

```
omf/core.py           TMM engine: kz branch, Fresnel, vectorised transfer matrix
omf/materials.py      Malitson SiO2, Green-2008 Si, Aspnes-1983 Si, N-BK7
omf/fitter.py         FilmModel: coarse grid pre-scan + least_squares + covariance
omf/uncertainty.py    Fisher information, CRLB, Monte Carlo
data/                 Si optical constants (refractiveindex.info, CC0)
tests/test_core.py    34 validation checks, three tiers
scripts/exp01..exp04  the four experiments below
results/              figures (PNG) and numerical output (JSON)
```

Run everything: `python run_all.py`

---

## 3. Validation — 34 / 34

Three tiers, in increasing order of evidential weight.

**Tier A — internal consistency** (catches coding errors, not wrong conventions)

| check | result |
|---|---|
| $R+T=1$, lossless, s and p, all angles | max err 1.6e-15 |
| $R+T+A=1$, absorbing film | exact |
| $\mathrm{Im}(k_z)\ge 0$ everywhere incl. frustrated TIR | holds |
| vectorised == looped | 0.0 |
| index-matched stack transparent | exact |

**Tier B — analytic limits** (tests the physics, derived independently)

| check | result |
|---|---|
| Fresnel $r_s$, $r_p$ at a single interface | 4.4e-15 |
| Brewster: $R_p=0$ at $\arctan(n_2/n_1)=56.659°$ | $R_p=4\times10^{-33}$ |
| TMM == Airy summation, complex film index | 2.2e-16 |
| half-wave film is absentee ($d_{1/2}=226.917$ nm) | 1.1e-16 |
| $d\to0$ == bare substrate | exact |
| quarter-wave AR, $n_f=\sqrt{n_0 n_s}$ | $R=1.3\times10^{-32}$ |
| total internal reflection $R=1$ | 8.9e-16 |
| $R_s=R_p$ at normal incidence | 4.4e-16 |
| periodicity in $d$ (period 192.37 nm at 546 nm, 20°) | 2.2e-16 |
| semi-infinite absorber: $R+T=1$ | exact |
| Beer–Lambert, 1–2 µm Si slab | ratio 1.003 |
| 1/e penetration depth at 405 nm | 124.3 nm |

**Tier C — external cross-validation** against `tmm` (S. J. Byrnes), the
reference implementation of the same paper this code follows. Independent
author, independent code path, same physics.

| check | result |
|---|---|
| $R$, 300 random stacks (2–5 layers, absorbing, 0–87°, 300–1600 nm) | max $|\Delta R| = 9.3\times10^{-15}$ |
| $T$, same | max $|\Delta T| = 1.1\times10^{-14}$ |
| dispersive SiO₂/Si spectrum, 300–1000 nm | $2.4\times10^{-15}$ |

---

## 4. Results

### exp01 — forward model

`results/exp01_forward_model.png`

- Bare Si at 633 nm: $R = 0.3476$
- Fringe period in $d$: 137.79 nm at 405 nm, 217.23 nm at 633 nm
- Peak sensitivity $|dR/dd| = 6.90\times10^{-3}$ nm⁻¹ at 405 nm (vs
  $3.90\times10^{-3}$ at 633 nm) — sensitivity scales as $1/\lambda$
- Dead zones where $dR/dd=0$ recur every half period (68.9 nm at 405 nm): at
  these thicknesses a reflectometer is locally blind

**Pseudo-Brewster on absorbing Si at 405 nm:** minimum at 79.644°, where
$\arctan(n)$ would give 79.640°. Crucially $R_{p,\min}=5.2\times10^{-4}\neq 0$.
For lossless BK7 the same calculation gives $4\times10^{-8}$. The non-vanishing
minimum is a direct measure of $k$ — this is the physical basis of ellipsometry.

**Vectorisation:** 2000 wavelengths, 3-layer stack — 2.75 ms vectorised vs
537 ms looped, **195.8×**. This is what makes an exhaustive global pre-scan
affordable, and hence what makes the fit fringe-order-safe.

### exp02 — the inverse problem

`results/exp02_ambiguity.png`

Ground truth $d = 217.3$ nm, $\sigma_R = 2\times10^{-4}$. Candidates counted by a
χ² acceptance test (a thickness survives if $\mathrm{SSR}<\sigma^2(N+3\sqrt{2N})$)
— i.e. "would the data reject it", not "is there a local minimum".

| design | N | surviving thicknesses |
|---|---|---|
| A: 405 nm, normal incidence | 1 | **8** |
| B: 405 nm, angle scan 0–70° | 141 | 1 |
| C: 400–900 nm, normal incidence | 251 | 1 |

Design A's candidates: `57.1, 79.5 | 194.9, 217.3 | 332.8, 355.1 | 470.4, 492.9`
nm. The **pair** structure (gap 22.4 nm) is the flank ambiguity; the
**pair-to-pair recurrence of 137.82 nm** is the order ambiguity, matching the
predicted 137.79 nm to 0.02%.

Fits (designs B and C):

| design | fitted $d$ | error vs truth | residual RMS |
|---|---|---|---|
| B | 217.2968 ± 0.0025 nm | −0.0032 nm (1.3σ) | 1.97e-4 |
| C | 217.2999 ± 0.0044 nm | −0.0001 nm (0.03σ) | 1.90e-4 |

**What the pre-scan buys:** a naive local optimiser converged to the *wrong
fringe order* from **6 of 9** starting points (landing on 47.0, 388.2, 506.2 nm).
The coarse-scan-seeded fit succeeded from all 9.

### exp03 — precision, CRLB vs Monte Carlo

`results/exp03_precision.png`

400 trials per noise level, design C:

| $\sigma_R$ | CRLB (nm) | MC std (nm) | efficiency |
|---|---|---|---|
| 1e-5 | 0.00022 | 0.00021 | 1.042 |
| 3e-5 | 0.00067 | 0.00069 | 0.971 |
| 1e-4 | 0.00222 | 0.00215 | 1.030 |
| 3e-4 | 0.00665 | 0.00646 | 1.030 |
| 1e-3 | 0.02218 | 0.02192 | 1.012 |
| 3e-3 | 0.06654 | 0.06406 | 1.039 |
| 1e-2 | 0.22181 | 0.22004 | 1.008 |

**Mean efficiency 1.019** across three decades of noise, bias < 0.005 nm
throughout. The estimator is efficient: it extracts essentially all the
information present. Further improvement requires a different *measurement*.

**Design comparison (random error only).** At $\sigma_R=2\times10^{-4}$:

| design | N | RMS $|dR/dd|$ | CRLB $\sigma_d$ |
|---|---|---|---|
| B (angle scan, 405 nm) | 141 | 6.67e-3 /nm | **0.00252 nm** |
| C (spectroscopic) | 251 | 2.85e-3 /nm | 0.00444 nm |

B wins despite fewer points, because $d\delta/dd\propto 1/\lambda$. But B pays
for it with a systematic C does not have — see S5.

**d–n degeneracy.** Fitting the film index simultaneously:

| design | ρ(d, Δn) | σ_d inflation |
|---|---|---|
| C | −0.930 | ×2.7 |
| B | −0.950 | ×3.2 |

ρ is not exactly −1 only because dispersion breaks the degeneracy: $n_{\rm SiO_2}(\lambda)$
varies while a constant offset does not. That residual difference in spectral
shape is the *only* thing separating the two parameters — which is why a
narrowband measurement cannot fit $n$ and $d$ together at all.

### exp04 — systematic error (inverse crime broken)

`results/exp04_systematics.png`

Data generated by a **different, more complete** model than the one fitted, one
perturbation at a time. The fit is always the simple air/SiO₂(Malitson)/Si(Green)
model.

| source | perturbation | bias (nm) | × random floor |
|---|---|---|---|
| S1 interfacial SiO_x ($n=2.5$) | 1 nm | +0.745 | 168 |
| S2 surface roughness (Bruggeman 50/50) | 2 nm | +0.876 | 197 |
| S3 film index (thermal oxide) | Δn = +0.004 | +0.627 | 141 |
| S4 Si reference data (Green ↔ Aspnes) | — | +0.166 | 37 |
| S5 incidence-angle calibration | 0.1° | −0.147 | 33 |
| **RSS combined** | | **1.33** | **299** |

Individual observations worth stating:

- **S1** scales linearly at ~0.75 nm of apparent oxide per nm of interfacial
  layer. Residual RMS stays at ~3e-4 — a good χ² does **not** certify the answer.
- **S2** transfer coefficient 0.438 nm apparent oxide per nm of 50 % rough layer.
  The fit reports the *volume-equivalent* thickness $d+f\,t_{\rm rough}$, not the
  physical top-surface position. Two instruments using different roughness
  conventions will disagree by $\sim f\,t_{\rm rough}$ **even if both are working
  perfectly**. This is a definition problem, not a measurement error.
- **S3** measured +0.3137 nm for Δn = +0.002 vs the predicted
  $+\Delta n\,d/n = +0.2984$ nm (5 %). Convention: $\Delta n = n_{\rm true}-n_{\rm assumed}$;
  since the fringes fix $nd$, an assumed index too low forces a fitted thickness
  too high. Confirms that the observable is optical thickness, not thickness.
- **S4** is irreducible without an independent measurement. Green 2008 and
  Aspnes 1983 are both peer-reviewed and neither is wrong; they differ by
  Δn = +0.034 at 405 nm and −0.009 at 633 nm. It must be *carried* as a
  systematic, not eliminated.
- **S5** is the price of design B's superior precision: 0.1° of angle error
  costs 0.147 nm, 58× that design's own random floor.

---

## 5. Limitations — read before quoting any number

1. **The 4 pm figure is an algorithmic noise floor, not an accuracy.** It comes
   from a study where the same model generates and fits the data. Every
   model-form error is invisible there by construction.
2. **No experimental data.** Every number in this repository is synthetic. The
   forward model is validated against an independent implementation and against
   analytic limits, but the *inverse* pipeline has never met a real sample.
   Validating it requires a reference-calibrated oxide wafer.
3. **Coherent layers only.** Thick incoherent substrates (backside reflection
   from a polished wafer, a glass slide) require incoherent averaging over the
   propagation phase, which is not implemented.
4. **Isotropic media only.** Anisotropy needs the 4×4 Berreman formalism.
5. **Ideal illumination.** No finite spectral bandwidth, no beam divergence, no
   finite spot size over a non-uniform film. Each of these adds bias in a real
   instrument.
6. **`n_si` is interpolated** from an 86-point table. Linear in $n$, logarithmic
   in $k$ (justified: $k$ spans five decades because Si's gap is indirect, so
   absorption is phonon-assisted and falls off smoothly).
7. **Thermal SiO₂ ≠ bulk fused silica.** Malitson is used as the film index
   throughout, which S3 shows is worth ~0.6 nm.

---

## 6. Defensible summary

> For a 217 nm SiO₂/Si film measured by spectroscopic reflectometry at
> $\sigma_R = 2\times10^{-4}$, the fitter is statistically efficient — the Monte
> Carlo spread sits at the Cramér–Rao bound to within 2 % over three decades of
> noise — giving a random uncertainty of 4 pm. Realistic accuracy is
> ~1.3 nm, dominated by model form: unmodelled interfacial layers, surface
> roughness convention, and film-index assumption each contribute several hundred
> times the random floor. Improving the result requires better *sample*
> knowledge, not a better optimiser.

---

## 7. References

- S. J. Byrnes, *Multilayer optical calculations*, arXiv:1603.02720 — matrix
  formulation, p-polarisation convention, transmittance prefactors. The `tmm`
  package by the same author is used for Tier C cross-validation.
- I. H. Malitson, *J. Opt. Soc. Am.* **55**, 1205 (1965) — fused silica Sellmeier.
- M. A. Green, *Sol. Energ. Mat. Sol. Cells* **92**, 1305 (2008) — Si optical
  constants, Kramers–Kronig consistent, 300 K.
- D. E. Aspnes and A. A. Studna, *Phys. Rev. B* **27**, 985 (1983) — independent
  Si determination by ellipsometry.
- Optical constant tables retrieved from the refractiveindex.info database
  (M. N. Polyanskiy), CC0 1.0 public domain.

## Requirements

`numpy`, `scipy`, `matplotlib`. Optional: `tmm` (Tier C cross-validation; the
suite skips it cleanly if absent).
