"""ces03: the experiment of Chapter 3 analysed in the terms of the general CES model (117 participants, 39 groups,
2,106 decisions; first seven sessions, 4-19 November 2026).  The analysis code is fixed and is re-run unchanged when
the remaining sessions are added.

Inputs : D117_kararlar.csv (decision level; exported from 04_analiz_117kisi_19Kasim/D117.pkl)
         katilimci_prososyal_ozet.csv (participant level; composite prosocial index of Chapter 3)
Outputs: ces03_results.json (every number quoted in the chapter), ces03_profile.csv, ces03_bootstrap.csv, ces03_log.txt

Sections
  A  group-level tables (positions: regular = mean of Control and Cycle, centre, leaf)
  B  robust hypotheses R1-R5 (one-sided randomization tests for the weak inequalities, TOST for equalities)
  C  parameter hypotheses: P1 sigma = 1, P2 lam = 0, P3 sigma = 0, joint (sigma, lam) = (0, 0), P4 token equality,
     P5 invariance of the private-consumption-to-giving ratio (the Leontief proportion) across positions
  D  structural interval-censored likelihood with random intercepts log eta_i ~ N(mu, tau^2):
        l*_it = log eta_i + (1 - sigma) log p_pos(lam) + controls + eps,  eps ~ N(0, s^2)
     unconstrained and constrained (sigma >= 0, lam >= 0) estimates, profile likelihoods, boundary LR tests
  E  prosocial intensity: eta_i = c/X in Control and Cycle (Leontief, lam = 0) and its correlation with the composite
  F  group bootstrap of the structural estimates
Usage: python3 ces03_data_analysis.py [nboot]
"""
import numpy as np, pandas as pd, json, os, sys, warnings
from scipy import stats
from scipy.optimize import minimize
from scipy.special import log_ndtr, logsumexp
import statsmodels.api as sm, statsmodels.formula.api as smf
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__)); nboot = int(sys.argv[1]) if len(sys.argv) > 1 else 200
R = {}   # results for the chapter
D = pd.read_csv(os.path.join(HERE, "D117_kararlar.csv")); Q = pd.read_csv(os.path.join(HERE, "katilimci_prososyal_ozet.csv"))
beta, e = 1.5, 15.0; L2 = np.log(2.0)
POS = {"control": (0.5, 2.0), "cycle": (0.5, 2.0), "center": (0.5, 2.5), "periphery": (0.25, 1.5)}   # (theta, Lambda)
D["theta"] = D.pos.map(lambda p: POS[p][0]); D["Lam"] = D.pos.map(lambda p: POS[p][1])
D["X"] = e - D.contribution + D.mp * D.neighborhood_total_contribution

# ---------------------------------------------------------------- A
def gtab(d, val):
    G = d.pivot_table(index="gid", columns="pos", values=val, aggfunc="mean"); G["reg"] = (G.control + G.cycle) / 2; return G
GC, GS = gtab(D, "contribution"), gtab(D, "share")
SIGNS = np.random.default_rng(7).choice([1, -1], size=(100000, len(GC)))
def perm(v, side="two"):
    v = np.asarray(v, float); m = v.mean(); dist = (SIGNS[:, :len(v)] * v).mean(1)
    if side == "two": return m, float((np.abs(dist) >= abs(m) - 1e-12).mean())
    if side == "less": return m, float((dist <= m + 1e-12).mean())     # H1: mean < 0
    return m, float((dist >= m - 1e-12).mean())
def tost(v, delta):
    v = np.asarray(v, float); n = len(v); se = v.std(ddof=1) / np.sqrt(n); m = v.mean(); t = stats.t.ppf(.95, n - 1)
    p = max(stats.t.sf((m + delta) / se, n - 1), stats.t.cdf((m - delta) / se, n - 1)); return p, m - t * se, m + t * se
print("== A. means by position (tokens, giving share)")
for p in ("reg", "center", "periphery"):
    print("  %-10s c = %.3f  share = %.4f" % (p, GC[p].mean(), GS[p].mean()))
R["means"] = {p: dict(c=GC[p].mean(), share=GS[p].mean()) for p in ("reg", "control", "cycle", "center", "periphery")}

# ---------------------------------------------------------------- B robust hypotheses
print("\n== B. robust hypotheses")
DD = D.merge(Q[["pid", "comp"]], on="pid", how="inner").dropna(subset=["comp"])
m = smf.ols("contribution ~ comp+leaf+centre+cyc+adv_dec+partner_adv+C(block_index)+block_round+C(session_code)", DD).fit(
    cov_type="cluster", cov_kwds={"groups": DD.gid})
R["R1_composite"] = dict(coef=m.params.comp, se=m.bse.comp, p=m.pvalues.comp, n=int(DD.pid.nunique()))
print("  R1 composite +1 sd: %+.3f (se %.3f, p %.4f), %d participants" % (m.params.comp, m.bse.comp, m.pvalues.comp, DD.pid.nunique()))
d = GC.cycle - GC.control; mm, p2 = perm(d); pt, lo, hi = tost(d, 0.5)
R["R2"] = dict(diff=mm, p_two=p2, tost05=pt, ci90=[lo, hi]); print("  R2 Cycle-Control %+.3f (p %.3f); TOST +-0.5 p %.3f, 90%% CI [%.2f, %.2f]" % (mm, p2, pt, lo, hi))
for key, a, b in (("R4_leaf_centre", "periphery", "center"), ("R5_leaf_regular", "periphery", "reg"), ("centre_regular", "center", "reg")):
    v = GC[a] - GC[b]; mm, p1 = perm(v, "less"); _, p2 = perm(v); pt1, lo, hi = tost(v, 1.0)
    R[key] = dict(diff=mm, p_one_less=p1, p_two=p2, tost1=pt1, ci90=[lo, hi], n_pos=int((v > 0).sum()))
    print("  %-16s %+.3f; one-sided p (H1: < 0) %.3f; two-sided %.3f; TOST +-1 p %.4f; 90%% CI [%.2f, %.2f]; positive %d/39"
          % (key, mm, p1, p2, pt1, lo, hi, (v > 0).sum()))

# ---------------------------------------------------------------- C parameter hypotheses
print("\n== C. parameter hypotheses")
R0 = D[D.adv_dec == 0]; zero = R0.groupby("pid").contribution.sum().loc[lambda s: s == 0].index; x = R0[~R0.pid.isin(zero)]
fl = smf.glm("share ~ leaf+centre+cyc+partner_adv+C(block_index)+block_round+C(pid)", x, family=sm.families.Binomial()).fit(
    cov_type="cluster", cov_kwds={"groups": x.gid})
D1, D2 = fl.params.centre, fl.params.leaf; V = fl.cov_params().loc[["centre", "leaf"], ["centre", "leaf"]].values
sD1, sD2 = np.sqrt(np.diag(V))
sig_hat = 1 + D2 / L2; se_sig = sD2 / L2
z_cd = (sig_hat - 1) / se_sig; z_le = sig_hat / se_sig
# joint test of (sigma, lam) = (0, 0): D1 = 0, D2 = -log 2
dv = np.array([D1 - 0.0, D2 + L2]); W00 = float(dv @ np.linalg.solve(V, dv))
# joint test of sigma = 1: D1 = D2 = 0
dv1 = np.array([D1, D2]); W1 = float(dv1 @ np.linalg.solve(V, dv1))
R["P"] = dict(D1=D1, se_D1=sD1, p_D1=float(2 * stats.norm.sf(abs(D1 / sD1))), D2=D2, se_D2=sD2, sigma_hat=sig_hat, se_sigma=se_sig,
              ci95_sigma=[sig_hat - 1.96 * se_sig, sig_hat + 1.96 * se_sig], z_sigma1=z_cd, z_sigma0=z_le,
              p_sigma0=float(2 * stats.norm.sf(abs(z_le))), wald_00=W00, p_00=float(stats.chi2.sf(W00, 2)), wald_cd=W1,
              p_cd=float(stats.chi2.sf(W1, 2)), n_part=int(x.pid.nunique()), n_dec=int(len(x)))
print("  FE fractional logit: D1 = %.3f (se %.3f), D2 = %.3f (se %.3f); sigma_hat = %.3f (se %.3f)" % (D1, sD1, D2, sD2, sig_hat, se_sig))
print("  P1 sigma = 1: z = %.2f; joint D1 = D2 = 0: Wald %.1f (p %.2g)" % (z_cd, W1, R["P"]["p_cd"]))
print("  P3 sigma = 0 (lam = 0): D2 + log 2 = %.3f, z = %.2f, p = %.3f" % (D2 + L2, z_le, R["P"]["p_sigma0"]))
print("  joint (sigma, lam) = (0, 0): Wald %.2f, p = %.3f" % (W00, R["P"]["p_00"]))
# P4 token equality (equivalence at +-1 already in B); P5 Leontief proportion X/c invariant across positions
P5 = R0.groupby(["pid", "gid", "pos"]).agg(X=("X", "sum"), c=("contribution", "sum")).reset_index()
P5["pos2"] = P5.pos.replace({"control": "reg", "cycle": "reg"})
P5 = P5.groupby(["pid", "gid", "pos2"]).agg(X=("X", "sum"), c=("c", "sum")).reset_index()
P5 = P5[P5.c > 0]; P5["lk"] = np.log(P5.X / P5.c)
W5 = P5.pivot_table(index=["pid", "gid"], columns="pos2", values="lk").dropna().reset_index()
for key, a in (("P5_leaf", "periphery"), ("P5_centre", "center")):
    v = (W5[a] - W5["reg"]).groupby(W5.gid).mean(); mm, p2 = perm(v.values)
    R[key] = dict(mean_log_ratio=mm, p_two=p2, n_part=int(len(W5)), ratio=float(np.exp(mm)))
    print("  %s: mean log(kappa_pos/kappa_reg) = %+.3f (ratio %.3f), group-level p = %.3f; %d participants" % (key, mm, np.exp(mm), p2, len(W5)))
# Cobb-Douglas counterpart: under sigma = 1 the leaf's kappa = X/c would be lower by the factor theta_L/theta_K adjusted for income
R["P5_note"] = "Leontief, lam=0: kappa = X/c invariant across positions"

# ---------------------------------------------------------------- D structural likelihood
print("\n== D. structural interval-censored likelihood")
S = R0.copy(); S["sid"] = pd.factorize(S.pid)[0]
cc = S.contribution.values.astype(float); th = S.theta.values; Wv = (e + S.mp * (S.neighborhood_total_contribution - S.contribution)).values
lo_c = np.maximum(cc - 0.5, 0); hi_c = np.minimum(cc + 0.5, e)
def lgt(v): return np.log(v) - np.log1p(-v)
LO = np.where(cc <= 0, -np.inf, lgt(np.clip(th * lo_c / Wv, 1e-12, 1 - 1e-12)))
HI = np.where(cc >= e, np.inf, lgt(np.clip(th * hi_c / Wv, 1e-12, 1 - 1e-12)))
Lm1 = (S.Lam.values - 1); lth = np.log(th)
Xc = np.column_stack([(S.block_index == 2).astype(float), (S.block_index == 3).astype(float), S.block_round.values - 3.5])
sid = S.sid.values; nsub = sid.max() + 1; allzero = S.groupby("sid").contribution.max().values == 0
GHX, GHW = np.polynomial.hermite.hermgauss(40)
def logp_int(lo, hi, mu, s):
    zl, zh = (lo - mu) / s, (hi - mu) / s; up = zl > 0
    a_, b_ = np.where(up, -zh, zl), np.where(up, -zl, zh)
    lb, la = log_ndtr(b_), log_ndtr(a_)
    with np.errstate(divide="ignore", invalid="ignore"): out = lb + np.log1p(-np.exp(np.minimum(la - lb, -1e-300)))
    return np.where(np.isfinite(out), out, -700.0)
NAMES = ["mu", "log_tau", "log_s", "logit_phi", "g_b2", "g_b3", "g_round", "sigma", "log_lam"]
def unpack(par, fix):
    q = dict(zip([n for n in NAMES if n not in fix], par)); q.update(fix); return q
def nll(par, fix, idx=None):
    q = unpack(par, fix); tau = np.exp(np.clip(q["log_tau"], -6, 3)); s = np.exp(np.clip(q["log_s"], -4, 3))
    lam = np.exp(np.clip(q["log_lam"], -30, 10)); sig = q["sigma"]
    mu = q["mu"] + (1 - sig) * (lth - np.log1p(lam * Lm1)) + Xc @ np.array([q["g_b2"], q["g_b3"], q["g_round"]])
    lp = logp_int(LO[:, None], HI[:, None], mu[:, None] + np.sqrt(2) * tau * GHX[None, :], s)
    Sm = np.zeros((nsub, len(GHX))); np.add.at(Sm, sid, lp)
    li = logsumexp(Sm + np.log(GHW / np.sqrt(np.pi))[None, :], axis=1)
    phi = 1 / (1 + np.exp(-q["logit_phi"]))
    li = np.logaddexp(np.log1p(-phi) + li, np.where(allzero, np.log(phi), -np.inf))
    if idx is not None: li = li[idx]
    v = -li.sum(); return v if np.isfinite(v) else 1e12
START = dict(mu=-1.2, log_tau=0.0, log_s=0.0, logit_phi=-4.0, g_b2=0.0, g_b3=0.0, g_round=0.0, sigma=0.5, log_lam=-1.0)
def fit(fix, bounds=None, idx=None, starts=None):
    free = [n for n in NAMES if n not in fix]; best = None
    for st in (starts or [{}]):
        x0 = np.array([st.get(n, START[n]) for n in free])
        if bounds:
            b = [bounds.get(n, (None, None)) for n in free]
            r = minimize(nll, x0, args=(fix, idx), method="L-BFGS-B", bounds=b)
        else:
            r = minimize(nll, x0, args=(fix, idx), method="BFGS", options=dict(maxiter=3000, gtol=1e-6))
        if best is None or r.fun < best.fun: best = r
    best.q = unpack(best.x, fix); best.ll = -best.fun; return best
LAM0 = {"log_lam": -30.0}
f_free = fit(dict(LAM0), starts=[{"sigma": -0.3}, {"sigma": 0.5}, {"sigma": 1.2}])                # sigma unrestricted, lam = 0
f_pos = fit(dict(LAM0), bounds={"sigma": (0.0, None)}, starts=[{"sigma": 0.2}, {"sigma": 1.0}])  # sigma >= 0, lam = 0
f_cd = fit(dict(LAM0, sigma=1.0))
f_le = fit(dict(LAM0, sigma=0.0))
f_sl = fit({}, bounds={"sigma": (0.0, None), "log_lam": (-30.0, 5.0)},
           starts=[{"sigma": 0.1, "log_lam": -3}, {"sigma": 0.5, "log_lam": 0.0}, {"sigma": 0.05, "log_lam": -8}])
f_sl_free = fit({}, bounds={"log_lam": (-30.0, 5.0)}, starts=[{"sigma": -0.2, "log_lam": -3}, {"sigma": 0.3, "log_lam": -1}])
def hess_se(r, fix):
    p = r.x; k = len(p); H = np.zeros((k, k)); h = 1e-4
    for i in range(k):
        for j in range(i, k):
            ei, ej = np.zeros(k), np.zeros(k); ei[i] = h; ej[j] = h
            H[i, j] = H[j, i] = (nll(p + ei + ej, fix) - nll(p + ei - ej, fix) - nll(p - ei + ej, fix) + nll(p - ei - ej, fix)) / (4 * h * h)
    return dict(zip([n for n in NAMES if n not in fix], np.sqrt(np.clip(np.diag(np.linalg.pinv(H)), 0, None))))
se_free = hess_se(f_free, dict(LAM0))
LR_cd = 2 * (f_free.ll - f_cd.ll); LR_le = 2 * (f_pos.ll - f_le.ll)
LR_lam = 2 * (f_sl.ll - f_pos.ll)
def chibar(lr, w=(0.5, 0.5)):   # p-value of 0.5 chi2_0 + 0.5 chi2_1
    return float(w[1] * stats.chi2.sf(max(lr, 0), 1)) if lr > 1e-10 else 1.0
q = f_free.q
R["D"] = dict(n_part=int(nsub), n_dec=int(len(S)),
              free=dict(sigma=q["sigma"], se_sigma=se_free["sigma"], mu=q["mu"], tau=float(np.exp(q["log_tau"])), s=float(np.exp(q["log_s"])),
                        phi=float(1 / (1 + np.exp(-q["logit_phi"]))), g_round=q["g_round"], ll=f_free.ll),
              constrained=dict(sigma=f_pos.q["sigma"], ll=f_pos.ll), cd=dict(ll=f_cd.ll), leontief=dict(ll=f_le.ll, mu=f_le.q["mu"],
              tau=float(np.exp(f_le.q["log_tau"])), s=float(np.exp(f_le.q["log_s"]))),
              joint=dict(sigma=f_sl.q["sigma"], lam=float(np.exp(f_sl.q["log_lam"])), ll=f_sl.ll),
              joint_free=dict(sigma=f_sl_free.q["sigma"], lam=float(np.exp(f_sl_free.q["log_lam"])), ll=f_sl_free.ll),
              LR_sigma1=LR_cd, p_sigma1=float(stats.chi2.sf(LR_cd, 1)), LR_sigma0=LR_le, p_sigma0_chibar=chibar(LR_le),
              LR_lam0=LR_lam, p_lam0_chibar=chibar(LR_lam))
print("  participants %d, decisions %d" % (nsub, len(S)))
print("  sigma unrestricted (lam = 0): %.3f (se %.3f); tau %.2f, s %.2f, phi %.3f, mu %.2f, round slope %.3f, logL %.2f"
      % (q["sigma"], se_free["sigma"], np.exp(q["log_tau"]), np.exp(q["log_s"]), 1 / (1 + np.exp(-q["logit_phi"])), q["mu"], q["g_round"], f_free.ll))
print("  sigma >= 0 (lam = 0): %.4f, logL %.2f | Leontief logL %.2f | CD logL %.2f" % (f_pos.q["sigma"], f_pos.ll, f_le.ll, f_cd.ll))
print("  joint sigma >= 0, lam >= 0: sigma %.4f, lam %.4f, logL %.2f | sigma free, lam >= 0: sigma %.3f, lam %.4f, logL %.2f"
      % (f_sl.q["sigma"], np.exp(f_sl.q["log_lam"]), f_sl.ll, f_sl_free.q["sigma"], np.exp(f_sl_free.q["log_lam"]), f_sl_free.ll))
print("  LR sigma = 1: %.1f (p %.2g) | LR sigma = 0 vs sigma >= 0: %.3f (chi-bar p %.3f) | LR lam = 0 at sigma >= 0: %.3f (chi-bar p %.3f)"
      % (LR_cd, R["D"]["p_sigma1"], LR_le, R["D"]["p_sigma0_chibar"], LR_lam, R["D"]["p_lam0_chibar"]))
# profiles
prof = []
for sg in np.round(np.arange(-0.4, 1.21, 0.1), 2):
    r = fit(dict(LAM0, sigma=float(sg))); prof.append(dict(kind="sigma|lam=0", value=float(sg), ll=r.ll))
for lm in (1e-4, 0.01, 0.03, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0):
    r = fit(dict(sigma=0.0, log_lam=float(np.log(lm)))); prof.append(dict(kind="lam|sigma=0", value=lm, ll=r.ll))
for lm in (1e-4, 0.01, 0.03, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0):
    r = fit(dict(log_lam=float(np.log(lm))), bounds={"sigma": (0.0, None)}, starts=[{"sigma": 0.05}, {"sigma": 0.5}])
    prof.append(dict(kind="lam|sigma>=0", value=lm, ll=r.ll, sigma=r.q["sigma"]))
prof = pd.DataFrame(prof); prof["dev"] = 2 * (prof.groupby("kind").ll.transform("max") - prof.ll)
prof.to_csv(os.path.join(HERE, "ces03_profile.csv"), index=False)
from scipy.optimize import brentq
c95, c90 = stats.chi2.ppf(.95, 1), stats.chi2.ppf(.90, 1)   # the one-sided (chi-bar) 95% bound at a boundary uses the 90% chi2_1 quantile
llmax = f_free.ll
dev_sigma = lambda sg: 2 * (llmax - fit(dict(LAM0, sigma=float(sg))).ll) - c95
s_lo = brentq(dev_sigma, -0.6, q["sigma"], xtol=1e-4); s_hi = brentq(dev_sigma, q["sigma"], 0.5, xtol=1e-4)
dev_lam = lambda ll_: 2 * (f_le.ll - fit(dict(sigma=0.0, log_lam=float(ll_))).ll) - c90
lam_ub = float(np.exp(brentq(dev_lam, np.log(1e-3), np.log(0.5), xtol=1e-4)))
R["D"]["profile_sigma_95"] = [float(s_lo), float(s_hi)]; R["D"]["lam_upper95_chibar"] = lam_ub
print("  profile 95%% interval for sigma (lam = 0): [%.3f, %.3f]; lam upper bound at sigma = 0 (chi-bar 95%%): %.3f" % (s_lo, s_hi, lam_ub))
print(prof.round(3).to_string(index=False))

# ---------------------------------------------------------------- E prosocial intensity
print("\n== E. prosocial intensity eta_i = c/X (Control and Cycle, Leontief with lam = 0)")
E = R0[R0.pos.isin(["control", "cycle"])].groupby("pid").agg(c=("contribution", "sum"), X=("X", "sum"))
E = E[E.c > 0]; E["eta"] = E.c / E.X; E["kappa"] = 1 / E.eta
EQ = E.join(Q.set_index("pid")[["comp"]], how="inner").dropna()
rho, prho = stats.spearmanr(EQ.eta, EQ.comp)
R["E"] = dict(n=int(len(E)), eta_median=float(E.eta.median()), eta_q25=float(E.eta.quantile(.25)), eta_q75=float(E.eta.quantile(.75)),
              kappa_median=float(E.kappa.median()), share_above_1_over_beta=float((E.eta > 1 / beta).mean()),
              rho_comp=float(rho), p_comp=float(prho), n_comp=int(len(EQ)))
print("  %d participants: eta median %.3f, IQR [%.3f, %.3f]; kappa median %.2f; eta > 1/beta (corner region) for %.3f"
      % (len(E), E.eta.median(), E.eta.quantile(.25), E.eta.quantile(.75), E.kappa.median(), (E.eta > 1 / beta).mean()))
print("  Spearman(eta, composite) = %.3f (p %.4f), n = %d" % (rho, prho, len(EQ)))

# ---------------------------------------------------------------- F bootstrap
print("\n== F. group bootstrap of the unrestricted sigma (lam = 0), B = %d" % nboot)
gids = S.gid.values; ug = np.unique(gids); rng = np.random.default_rng(20261120); bs = []
sub_of_gid = {g: np.unique(sid[gids == g]) for g in ug}
x0 = f_free.x
for b in range(nboot):
    draw = rng.choice(ug, len(ug))
    # weight subjects by the number of times their group is drawn (equivalent to resampling groups)
    w = np.zeros(nsub)
    for g in draw: w[sub_of_gid[g]] += 1
    def nll_w(par, fix=dict(LAM0)):
        q = unpack(par, fix); tau = np.exp(np.clip(q["log_tau"], -6, 3)); s = np.exp(np.clip(q["log_s"], -4, 3)); sig = q["sigma"]
        mu = q["mu"] + (1 - sig) * lth + Xc @ np.array([q["g_b2"], q["g_b3"], q["g_round"]])
        lp = logp_int(LO[:, None], HI[:, None], mu[:, None] + np.sqrt(2) * tau * GHX[None, :], s)
        Sm = np.zeros((nsub, len(GHX))); np.add.at(Sm, sid, lp)
        li = logsumexp(Sm + np.log(GHW / np.sqrt(np.pi))[None, :], axis=1); phi = 1 / (1 + np.exp(-q["logit_phi"]))
        li = np.logaddexp(np.log1p(-phi) + li, np.where(allzero, np.log(phi), -np.inf)); v = -(w * li).sum()
        return v if np.isfinite(v) else 1e12
    r = minimize(nll_w, x0, method="BFGS", options=dict(maxiter=2000, gtol=1e-5))
    qq = unpack(r.x, dict(LAM0)); bs.append(dict(sigma=qq["sigma"], s=np.exp(qq["log_s"]), tau=np.exp(qq["log_tau"])))
bs = pd.DataFrame(bs, columns=["sigma", "s", "tau"]); bs.to_csv(os.path.join(HERE, "ces03_bootstrap.csv"), index=False)
if nboot > 0: R["F"] = dict(B=nboot, sigma_se=float(bs.sigma.std()), sigma_ci95=[float(bs.sigma.quantile(.025)), float(bs.sigma.quantile(.975))])
if nboot > 0: print("  bootstrap sd of sigma %.3f; 95%% interval [%.3f, %.3f]" % (bs.sigma.std(), bs.sigma.quantile(.025), bs.sigma.quantile(.975)))
json.dump(R, open(os.path.join(HERE, "ces03_results.json"), "w"), indent=1, default=float)
