# Chapter 3 – Data analysis of the networked public good experiment

Python analysis of the classroom sessions of the experiment in this repository
(Control, Cycle and Star networks; within-subject, 3 blocks × 6 rounds; prosocial survey and an incentivised
dictator donation). Each folder is one analysis round; scripts are numbered in run order, and every script's
console output is kept next to it (`*_cikti.txt`, `*_log.txt`, `.json`, `.csv`, figures).

**The experimental data are not included.** Scripts expect the oTree exports under `experiment_data/`
at the repository root (`tüm_veri.xlsx`, `sessions/gerçek_*/otree_ciktilari/*.csv`), which is git-ignored.
Published outputs are aggregate; participant codes are masked.

| Folder | Sample | Content |
|---|---|---|
| `00_teorik_sinama_13Kasim2026/` | 60 participants, 20 groups | First test of the theory: data integrity checks, group-level sign-flip and t tests, individual fixed effects, dynamic (conditional-cooperation) regressions, Cobb–Douglas best response, CES `(σ, λ)` grid with leave-one-group-out validation, model RMSE |
| `03_fiyat_dikkat_84kisi_18Kasim/` | 84 participants | Price-attention and role-channel tests; randomisation inference for the leaf–centre gap |
| `04_analiz_117kisi_19Kasim/` | 117 participants, 39 groups, 2,106 decisions | Main analysis: descriptives; pre-planned hypotheses H1–H5 (individual FE OLS, group-clustered SE, TOST equivalence, fractional outcomes); network effects (first-block between-subject test, order effects, restart, information channel, response times); prosocial measurement (Spearman, VIF, Shapley R², factor analysis, ORIV); share-based identification of `(σ, λ)` with simulation and group-bootstrap bounds; Leontief and CES predictions; thesis figures |
| `05_ces_bolumu_117kisi/` | 117 participants | General CES chapter: symbolic/numerical checks of the propositions (SymPy), design-level predictions, structural censored likelihood with random intercepts and boundary LR tests (σ ≥ 0, λ ≥ 0), profile likelihood, group bootstrap |

Main packages: `pandas`, `numpy`, `scipy`, `statsmodels`, `linearmodels`, `factor_analyzer`, `sympy`, `matplotlib`, `openpyxl`.

Run order inside a folder: `00_*` (builds the analysis frame), then the remaining scripts in numerical order.
Folder notes in Turkish: `OKUBENI*.md/txt`.
