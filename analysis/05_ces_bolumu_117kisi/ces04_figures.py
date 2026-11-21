"""ces04: profile-likelihood figure for the structural estimates of ces03 (run after ces03).
Output: fig_ces_profile.png"""
import numpy as np, pandas as pd, json, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__))
P = pd.read_csv(os.path.join(HERE, "ces03_profile.csv")); R = json.load(open(os.path.join(HERE, "ces03_results.json")))
INK, MUTED, BLUE, ORANGE = "#0b0b0b", "#52514e", "#2a78d6", "#eb6834"
plt.rcParams.update({"font.size": 10})
fig, ax = plt.subplots(1, 2, figsize=(10, 3.7))
a = ax[0]; s = P[P.kind == "sigma|lam=0"].sort_values("value")
a.plot(s.value, s.dev, color=BLUE, lw=2, marker="o", ms=4)
a.axhline(stats.chi2.ppf(.95, 1), color=MUTED, ls="--", lw=1); a.text(0.62, stats.chi2.ppf(.95, 1) + 6, r"$\chi^2_1$ 95%", color=MUTED, fontsize=9)
a.axvline(0, color=ORANGE, lw=1.5); a.text(0.02, 250, "Leontief\n" r"($\sigma=0$)", color=INK, fontsize=9)
a.axvline(1, color=INK, lw=1, ls=":"); a.text(0.97, 285, "Cobb–Douglas\n" r"($\sigma=1$)", color=INK, fontsize=9, ha="right")
lo, hi = R["D"]["profile_sigma_95"]; a.axvspan(lo, hi, color="#d9d8d3", alpha=0.7, lw=0)
a.set_xlabel(r"elasticity of substitution $\sigma$ ($\lambda=0$)"); a.set_ylabel(r"deviance $2(\log L_{\max}-\log L)$")
a.set_title(r"(a) Profile likelihood of $\sigma$", loc="left", fontsize=10)
b = ax[1]; l = P[P.kind == "lam|sigma=0"].sort_values("value")
b.plot(l.value, l.dev, color=BLUE, lw=2, marker="o", ms=4)
b.axhline(stats.chi2.ppf(.90, 1), color=MUTED, ls="--", lw=1); b.text(0.55, stats.chi2.ppf(.90, 1) + 3, r"$\bar\chi^2$ 95% (one-sided)", color=MUTED, fontsize=9)
b.axvline(R["D"]["lam_upper95_chibar"], color=ORANGE, lw=1.5)
b.text(R["D"]["lam_upper95_chibar"] + 0.02, 55, r"upper bound $%.2f$" % R["D"]["lam_upper95_chibar"], color=INK, fontsize=9)
b.set_xlabel(r"impact weight $\lambda$ ($\sigma=0$)"); b.set_ylabel(r"deviance")
b.set_title(r"(b) Profile likelihood of $\lambda$", loc="left", fontsize=10)
for x in ax:
    x.grid(axis="y", color="#e6e5e1", lw=0.8)
    for sp_ in ("top", "right"): x.spines[sp_].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(HERE, "fig_ces_profile.png"), dpi=200)
