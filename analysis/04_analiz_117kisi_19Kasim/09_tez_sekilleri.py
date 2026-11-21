"""Ch3 tez sekilleri (117 katilimci). Cikti: savunma/figures_ch3/*.png
Calistirma: python3 09_tez_sekilleri.py  (00_hazirlik.py'nin urettigi D117.pkl gerekir)"""
import os, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "..", "savunma", "figures_ch3"); os.makedirs(OUT, exist_ok=True)
d = pd.read_pickle(os.path.join(HERE, "D117.pkl"))
BLUE, ORANGE, AQUA, YEL = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.family": "serif", "font.size": 10, "axes.edgecolor": INK2,
    "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.axisbelow": True, "legend.frameon": False})
def gci(df, key):  # grup duzeyi ortalama ve %95 GA (gruplar bagimsiz birim)
    g = df.groupby(["gid", key])["contribution"].mean().unstack()
    m = g.mean(); se = g.std(ddof=1) / np.sqrt(g.notna().sum()); return m, 1.96 * se
# Sekil 1: tur dinamigi
fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"width_ratios": [1.5, 1]})
m, h = gci(d, "round_number")
ax[0].fill_between(m.index, m - h, m + h, color=BLUE, alpha=0.15, lw=0)
ax[0].plot(m.index, m.values, color=BLUE, lw=2, marker="o", ms=4)
for b in (6.5, 12.5): ax[0].axvline(b, color=INK2, lw=0.8, ls=":")
for x, t in ((3.5, "Block 1"), (9.5, "Block 2"), (15.5, "Block 3")):
    ax[0].text(x, 8.6, t, ha="center", color=INK2, fontsize=9)
ax[0].set(xlabel="Round", ylabel="Mean contribution (tokens)", ylim=(3, 9), xticks=[1, 6, 12, 18])
ax[0].set_title("(a) All groups, by round", fontsize=10, loc="left")
for tr, col, mk, ls in (("control", BLUE, "o", "-"), ("cycle", ORANGE, "s", "--"), ("star", AQUA, "^", "-.")):
    s = d[d["treatment"] == tr]; mm, hh = gci(s, "block_round")
    ax[1].plot(mm.index, mm.values, color=col, lw=2, marker=mk, ms=5, ls=ls, label=tr.capitalize())
ax[1].set(xlabel="Round within block", ylim=(3, 9), xticks=range(1, 7))
ax[1].set_title("(b) By treatment", fontsize=10, loc="left"); ax[1].legend(loc="lower left", fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig_ch3_dynamics.png"), dpi=300); plt.close(fig)
# Sekil 2: pozisyon, gozlenen ve model ongoruleri (jeton ve giving share)
d["P"] = d["pos"].replace({"control": "Regular", "cycle": "Regular", "center": "Centre", "periphery": "Leaf"})
order = ["Regular", "Centre", "Leaf"]
gc = d.groupby(["gid", "P"])["contribution"].mean().unstack()[order]
gs = d.groupby(["gid", "P"])["share"].mean().unstack()[order]
creg = gc["Regular"].mean()
th = {"Regular": 0.5, "Centre": 0.5, "Leaf": 0.25}
W = {"Regular": 15 + creg, "Centre": 15 + creg, "Leaf": 15 + 0.75 * creg}  # herkes ayni c verdiginde full income
leo_s = [th[p] * creg / W[p] for p in order]
cd_c = [creg, 7.52, 11.66]          # 08_cikti.txt A, sigma=1, regular=5.9'a kalibre
cd_s = [gs["Regular"].mean()] * 3   # CD: share her pozisyonda B
fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0))
x = np.arange(3); w = 0.26
for k, (lab, col, hatch, vc, vs) in enumerate((
        ("Observed", BLUE, "", gc.mean().values, gs.mean().values),
        ("Cobb–Douglas (σ = 1)", ORANGE, "///", cd_c, cd_s),
        ("Leontief (σ = 0, λ = 0)", AQUA, "\\\\\\", [creg] * 3, leo_s))):
    er_c = 1.96 * gc.std(ddof=1).values / np.sqrt(len(gc)) if k == 0 else None
    er_s = 1.96 * gs.std(ddof=1).values / np.sqrt(len(gs)) if k == 0 else None
    for a, v, er in ((ax[0], vc, er_c), (ax[1], vs, er_s)):
        a.bar(x + (k - 1) * w, v, w - 0.03, color=col, hatch=hatch, edgecolor="white", lw=0, label=lab,
              yerr=er, error_kw={"ecolor": INK, "lw": 1, "capsize": 3})
for a, yl, t in ((ax[0], "Contribution (tokens)", "(a) Contributions"), (ax[1], "Giving share  θc/W", "(b) Giving shares")):
    a.set_xticks(x, order); a.set_ylabel(yl); a.set_title(t, fontsize=10, loc="left"); a.grid(axis="x", visible=False)
ax[0].set_ylim(0, 13); ax[1].set_ylim(0, 0.2)
h_, l_ = ax[0].get_legend_handles_labels()
fig.legend(h_, l_, loc="lower center", ncol=3, fontsize=9, bbox_to_anchor=(0.5, -0.02))
fig.tight_layout(rect=(0, 0.08, 1, 1)); fig.savefig(os.path.join(OUT, "fig_ch3_positions.png"), dpi=300); plt.close(fig)
print("regular c", round(creg, 3), "obs c", gc.mean().round(3).to_dict(), "obs share", gs.mean().round(3).to_dict(),
      "Leontief share", [round(v, 3) for v in leo_s])
