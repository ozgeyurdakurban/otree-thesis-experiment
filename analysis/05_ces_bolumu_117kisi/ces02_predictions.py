"""ces02: equilibrium predictions at the experimental parameters (n = 3, e = 15, beta = 1.5) as functions of
(sigma, lam), with a common prosocial intensity eta calibrated so that a regular member (Control/Cycle) contributes
the observed mean of 5.9 tokens.  The eta-parametrization keeps the Leontief limit sigma = 0 well defined.
Outputs: ces02_predictions.csv, ces02_log.txt (printed), fig_ces_predictions.png
"""
import numpy as np, pandas as pd, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
beta, e, n, CREG = 1.5, 15.0, 3, 5.9
K3 = np.ones((3, 3)) - np.eye(3); S3 = np.array([[0, 1, 1], [1, 0, 0], [1, 0, 0]], float)

def prices(A, lam):
    d = A.sum(1) + 1; theta = 1 - beta / d; Lam = 1 + A @ (beta / d); Lt = 1 + lam * (Lam - 1)
    return d, theta, Lam, Lt
def eq(A, pi):
    d = A.sum(1) + 1; theta = 1 - beta / d; c = np.zeros(3)
    for _ in range(100000):
        cn = np.minimum(e, pi * (e + beta / d * (A @ c)) / theta)
        if np.max(np.abs(cn - c)) < 1e-13: return cn
        c = cn
    return c
def share(eta, p, sigma):
    o = eta * p ** (1 - sigma); return o / (1 + o)

# calibration: regular member interior on K3: c = 3 pi e / (3 - beta - 2 pi beta) = CREG
piK = CREG * (3 - beta) / (3 * e + 2 * beta * CREG); oddsK = piK / (1 - piK)
rows = []
SIGMAS = [0.0, 0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
LAMS = [0.0, 0.1, 0.25, 0.5, 1.0, 2.0]
for lam in LAMS:
    for sigma in SIGMAS:
        dK, thK, LamK, LtK = prices(K3, lam); dS, thS, LamS, LtS = prices(S3, lam)
        pK = thK[0] / LtK[0]
        eta = oddsK / pK ** (1 - sigma)
        cK = eq(K3, share(eta, thK / LtK, sigma)); piS = share(eta, thS / LtS, sigma); cS = eq(S3, piS)
        cC, cL = cS[0], cS[1]
        WK = e + beta / 3 * 2 * cK[0]; WC = e + beta / 3 * 2 * cL; WL = e + beta / 2 * cC
        shK, shC, shL = thK[0] * cK[0] / WK, thS[0] * cC / WC, thS[1] * cL / WL
        seK = (0.5 * 3 * cK[0]) / 22.5; seS = (1.0 * cC + 0.25 * 2 * cL) / 22.5
        B = eta ** (1 / sigma) / (1 + eta ** (1 / sigma)) if sigma > 0 else np.nan
        rows.append(dict(sigma=sigma, lam=lam, eta=eta, kappa=1 / eta, B=B, c_regular=cK[0], c_centre=cC, c_leaf=cL,
                         leaf_minus_centre=cL - cC, leaf_minus_regular=cL - cK[0], centre_minus_regular=cC - cK[0],
                         share_regular=shK, share_centre=shC, share_leaf=shL, SE_control=seK, SE_star=seS,
                         SE_star_minus_control=seS - seK, corner=bool(max(cK.max(), cS.max()) >= e - 1e-9),
                         D1=(sigma - 1) * np.log(LtS[0] / LtK[0]), D2=(sigma - 1) * np.log(pK / (thS[1] / LtS[1]))))
P = pd.DataFrame(rows); P.to_csv(os.path.join(HERE, "ces02_predictions.csv"), index=False)
pd.set_option("display.width", 200)
print("eta calibrated to a regular contribution of %.1f tokens: pi_K = %.4f, odds = %.4f" % (CREG, piK, oddsK))
print(P[["sigma", "lam", "eta", "B", "c_leaf", "c_centre", "leaf_minus_centre", "leaf_minus_regular", "centre_minus_regular",
         "share_leaf", "share_centre", "share_regular", "SE_star_minus_control", "corner"]].round(3).to_string(index=False))

# figure: predicted token gaps against sigma, by lam, with the observed gaps (90% CIs from Ch3)
# observed group-level means and 90% CIs (from ces03_results.json when available; values of Chapter 3 otherwise)
OBS = {"leaf_minus_centre": (-0.297, -0.75, 0.16), "centre_minus_regular": (0.125, -0.42, 0.67)}
jf = os.path.join(HERE, "ces03_results.json")
if os.path.exists(jf):
    import json; RR = json.load(open(jf))
    OBS = {"leaf_minus_centre": (RR["R4_leaf_centre"]["diff"], *RR["R4_leaf_centre"]["ci90"]),
           "centre_minus_regular": (RR["centre_regular"]["diff"], *RR["centre_regular"]["ci90"])}
INK, MUTED = "#0b0b0b", "#52514e"; COL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#6250d6"]
sg = np.linspace(0, 2, 81); fig, ax = plt.subplots(1, 2, figsize=(10, 3.9))
plt.rcParams.update({"font.size": 10})
for k, (key, title) in enumerate([("leaf_minus_centre", "(a) Leaf $-$ centre"), ("centre_minus_regular", "(b) Centre $-$ regular member")]):
    a = ax[k]
    for j, lam in enumerate([0.0, 0.25, 0.5, 1.0, 2.0]):
        ys = []
        for sigma in sg:
            dK, thK, LamK, LtK = prices(K3, lam); dS, thS, LamS, LtS = prices(S3, lam)
            pK = thK[0] / LtK[0]; eta = oddsK / pK ** (1 - sigma)
            cK = eq(K3, share(eta, thK / LtK, sigma)); cS = eq(S3, share(eta, thS / LtS, sigma))
            ys.append(cS[1] - cS[0] if key == "leaf_minus_centre" else cS[0] - cK[0])
        a.plot(sg, ys, color=COL[j], lw=2, label=r"$\lambda=%g$" % lam)
    o, lo_, hi_ = OBS[key]
    if lo_ is not None: a.axhspan(lo_, hi_, color="#d9d8d3", alpha=0.6, lw=0, label="observed, 90% CI")
    a.axhline(o, color=INK, lw=1, ls=":", label="observed mean")
    a.axhline(0, color=MUTED, lw=0.6)
    a.set_xlabel(r"elasticity of substitution $\sigma$"); a.set_ylabel("tokens")
    a.set_title(title, loc="left", fontsize=10); a.grid(axis="y", color="#e6e5e1", lw=0.8)
    for s_ in ("top", "right"): a.spines[s_].set_visible(False)
ax[0].legend(frameon=False, fontsize=8.5, loc="upper left", ncol=2)
fig.tight_layout(); fig.savefig(os.path.join(HERE, "fig_ces_predictions.png"), dpi=200)

# transport of the charitable-giving calibration (Ch2, Deb-Gazzale-Kotchen panel: sigma = 1.4, lam bounded below) to the design
print("\nTransport: sigma = 1.4, eta calibrated to a regular contribution of 5.9 tokens")
for lam in (0.5, 1, 2, 10, 100, 1e4):
    dK, thK, LamK, LtK = prices(K3, lam); dS, thS, LamS, LtS = prices(S3, lam)
    pK = thK[0] / LtK[0]; eta = oddsK / pK ** (1 - 1.4)
    cK = eq(K3, share(eta, thK / LtK, 1.4)); cS = eq(S3, share(eta, thS / LtS, 1.4))
    print("  lam = %-7g regular %.2f centre %.2f leaf %.2f  leaf/regular %.2f" % (lam, cK[0], cS[0], cS[1], cS[1] / cK[0]))
