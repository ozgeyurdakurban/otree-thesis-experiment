"""ces01: symbolic and numerical checks of the statements of the CES chapter that are not already verified by the
Chapter 2 scripts (thesis-algebrics/ch2, s01-s12).  Every check prints PASS/FAIL; the script exits with an error
if any check fails.

Notation.  Material payoff X = W - theta c, moral good Y = Lt c, Lt = 1 + lam (Lambda - 1), p = theta / Lt.
CES utility in the prosocial-intensity parametrization  eta = (B/(1-B))^sigma:
        U = [ X^rho + eta^(1-rho) Y^rho ]^(1/rho),   sigma = 1/(1-rho).
Claims checked:
  C1  interior share: odds(pi) = eta p^(1-sigma), pi = theta c / W            (any sigma != 1; sigma = 1 separately)
  C2  equivalence with the B-parametrization of Ch2: eta = (B/(1-B))^sigma gives the same share
  C3  limits: sigma -> 1 gives B = eta/(1+eta); sigma -> 0 gives the Leontief best response of min{X, Y/eta}
  C4  comparative statics of the log odds: d/dlog eta = 1, d/dsigma|eta = -log p, d/dlam = (sigma-1)(Lambda-1)/Lt
  C5  network comparative static dc_i/deta_j = M_ij c_j (1-pi_j)/eta_j   (finite differences, random networks)
  C6  K_n interiority ceiling in eta: interior iff eta < (theta/beta) p^(sigma-1)
  C7  Leontief topology invariance (sigma = 0, lam = 0, common eta <= 1/beta): c* = eta e/(1 - eta(beta - 1)) on any network
  C8  sigma = 0, lam > 0, common eta: leaf > regular > centre in tokens (n = 3, beta = 1.5)
  C9  positional log-odds differences at the design: D1 = (sigma-1) log(Lt_C/Lt_K), D2 = (sigma-1) log(p_K/p_L);
      at sigma = 0, lam = 0: D1 = 0 and D2 = -log 2
  C10 interior contributions are proportional to the endowment (any network, any sigma, lam)
  C11 best response by direct maximization of U over [0, e] (random parameters, sigma in [0.05, 4])
  C12 star closed form with a common eta (Ch2 eq. ces_star_hom) against best-response iteration
"""
import numpy as np, sympy as sp, sys
from scipy.optimize import minimize_scalar
rng = np.random.default_rng(20261120)
FAIL = []
def check(name, ok, info=""):
    print(("PASS " if ok else "FAIL ") + name + ("  " + info if info else "")); (None if ok else FAIL.append(name))

# ------------------------------------------------------------------ symbolic C1-C4
X, Y, W, th, Lt, c, eta, rho, B, lam, Lam, sig = sp.symbols('X Y W theta Lt c eta rho B lam Lambda sigma', positive=True)
U = (X**rho + eta**(1 - rho) * Y**rho)  # monotone transform of the CES utility (rho in (0,1); rho < 0 flips the sign, same FOC)
Uc = U.subs({X: W - th * c, Y: Lt * c})
foc = sp.diff(Uc, c)
# solve FOC for the ratio r = c/X: (1) theta X^(rho-1) = eta^(1-rho) Lt^rho c^(rho-1)
r = sp.symbols('r', positive=True)
lhs = th * (1) ; rhs = eta**(1 - rho) * Lt**rho * r**(rho - 1)   # dividing both sides by X^(rho-1)
r_sol = sp.solve(sp.Eq(lhs, rhs), r)[0]
# pi = theta c / W with c = r X and X = W - theta c  =>  pi = theta r / (1 + theta r);  odds = theta r
odds = sp.simplify(th * r_sol)
p = th / Lt
target = eta * p**(1 - 1 / (1 - rho))
check("C1 odds(pi) = eta p^(1-sigma)", sp.simplify(sp.log(odds) - sp.log(target)) == 0 or abs(float((odds / target).subs({th: .37, Lt: 1.9, eta: .41, rho: -.6}) - 1)) < 1e-12)
# numerical confirmation of C1 directly from the FOC
vals = {W: 21.0, th: 0.5, Lt: 1.7, eta: 0.3, rho: -0.8}
cstar = sp.nsolve(foc.subs(vals), c, 5.0)
pi_num = float(0.5 * cstar / 21.0); s_ = 1 / (1 + 0.8)
pi_formula = (0.3 * (0.5 / 1.7) ** (1 - s_)) / (1 + 0.3 * (0.5 / 1.7) ** (1 - s_))
check("C1 numerical FOC", abs(pi_num - pi_formula) < 1e-10, f"pi={pi_num:.8f} formula={pi_formula:.8f}")
# C2: B-parametrization of Ch2: odds = (B/(1-B))^sigma p^(1-sigma)
oddsB = (B / (1 - B))**sig * p**(1 - sig)
check("C2 eta=(B/(1-B))^sigma reproduces Ch2 share", sp.simplify(oddsB - (eta * p**(1 - sig)).subs(eta, (B / (1 - B))**sig)) == 0)
# C3 limits
pi_eta = lambda e_, p_, s__: e_ * p_**(1 - s__) / (1 + e_ * p_**(1 - s__))
check("C3 sigma=1: pi = eta/(1+eta)", abs(pi_eta(0.25, 0.3, 1.0) - 0.25 / 1.25) < 1e-14)
# Leontief: U = min{X, Y/eta} => X = Y/eta => W - theta c = Lt c / eta => pi = theta c / W = theta eta/(eta theta + Lt) = eta p/(1+eta p)
for e_, p_ in [(0.3, 0.25), (0.8, 0.5), (2.0, 0.2)]:
    cL = 21.0 / (0.5 + 1.7 / e_) if False else None
check("C3 sigma->0: pi -> eta p/(1+eta p) (Leontief min{X, Y/eta})", all(abs(pi_eta(e_, p_, 1e-9) - e_ * p_ / (1 + e_ * p_)) < 1e-8 for e_, p_ in [(0.3, .25), (.8, .5), (2, .2)]))
# Leontief best response from the kink, compared with the CES utility maximized at small sigma
def br_direct(eta_, theta_, Lt_, W_, sigma_, e_=15.0):
    rho_ = 1 - 1 / sigma_
    def negU(cc):
        Xv = W_ - theta_ * cc; Yv = Lt_ * cc
        if Xv <= 0 or Yv <= 0: return 1e9
        if abs(rho_) < 1e-9: return -(np.log(Xv) + eta_ * np.log(Yv)) / (1 + eta_)   # Cobb-Douglas
        z = (Xv**rho_ + eta_**(1 - rho_) * Yv**rho_)
        return -(np.log(z) / rho_)
    r_ = minimize_scalar(negU, bounds=(1e-9, e_), method="bounded", options=dict(xatol=1e-10))
    return r_.x
# (a) direct maximization of the Leontief utility min{X, Y/eta}; (b) CES optimum converges to it as sigma -> 0
rL = minimize_scalar(lambda cc: -min(21.0 - 0.5 * cc, 1.0 * cc / 0.33), bounds=(0, 15), method="bounded", options=dict(xatol=1e-10))
check("C3 Leontief kink: argmax min{X, Y/eta} = W/(theta + Lt/eta)", abs(rL.x - 21.0 / (0.5 + 1.0 / 0.33)) < 1e-6, f"{rL.x:.6f}")
gaps = [abs(br_direct(0.33, 0.5, 1.0, 21.0, s__) - 21.0 / (0.5 + 1.0 / 0.33)) for s__ in (0.2, 0.1, 0.05, 0.02)]
check("C3 CES optimum -> Leontief optimum as sigma -> 0 (monotone convergence)", all(np.diff(gaps) < 0), "gaps " + ", ".join(f"{g:.4f}" for g in gaps))
# C4
lo = sp.log(eta) + (1 - sig) * (sp.log(th) - sp.log(1 + lam * (Lam - 1)))
check("C4 dlog-odds/dlog eta = 1", sp.simplify(sp.diff(lo, eta) * eta - 1) == 0)
check("C4 dlog-odds/dsigma|eta = -log p", sp.simplify(sp.diff(lo, sig) + (sp.log(th) - sp.log(1 + lam * (Lam - 1)))) == 0)
check("C4 dlog-odds/dlam = (sigma-1)(Lambda-1)/Lt", sp.simplify(sp.diff(lo, lam) - (sig - 1) * (Lam - 1) / (1 + lam * (Lam - 1))) == 0)

# ------------------------------------------------------------------ numerical machinery
def random_connected(n, pr=0.5):
    while True:
        A = (rng.random((n, n)) < pr).astype(float); A = np.triu(A, 1); A = A + A.T
        # connectivity
        seen = {0}; stack = [0]
        while stack:
            k = stack.pop()
            for j in np.where(A[k] > 0)[0]:
                if j not in seen: seen.add(j); stack.append(j)
        if len(seen) == n: return A
def prices(A, beta, lam):
    d = A.sum(1) + 1; theta = 1 - beta / d
    Lam = 1 + A @ (beta / d); Lt = 1 + lam * (Lam - 1)
    return d, theta, Lam, Lt
def shares(eta_v, theta, Lt, sigma):
    o = eta_v * (theta / Lt) ** (1 - sigma); return o / (1 + o)
def equilibrium(A, beta, e, pi, tol=1e-13, it=200000, start=0.0):
    d = A.sum(1) + 1; theta = 1 - beta / d
    c = np.full(len(pi), start)
    for _ in range(it):
        S = A @ c; cn = np.minimum(e, pi * (e + beta / d * S) / theta)
        if np.max(np.abs(cn - c)) < tol: return cn
        c = cn
    return c
def interior(c, e): return np.all(c < e - 1e-9)

# C5 network comparative static in eta
ok = True; nchk = 0; worst = 0
for _ in range(300):
    n = rng.integers(3, 8); A = random_connected(n); beta = rng.uniform(1.05, min(1.95, (A.sum(1) + 1).min() - 0.05))
    if beta <= 1: continue
    lam = rng.uniform(0, 3); sigma = rng.uniform(0.05, 3); e = 15.0
    d, theta, Lam, Lt = prices(A, beta, lam)
    eta_v = rng.uniform(0.01, 0.3, n); pi = shares(eta_v, theta, Lt, sigma)
    G = np.diag(pi * beta / (d - beta)) @ A
    if np.max(np.abs(np.linalg.eigvals(G))) >= 1: continue
    cst = equilibrium(A, beta, e, pi)
    if not interior(cst, e): continue
    M = np.linalg.inv(np.eye(n) - G); j = rng.integers(n); h = 1e-6 * eta_v[j]
    ep = eta_v.copy(); ep[j] += h; c2 = equilibrium(A, beta, e, shares(ep, theta, Lt, sigma))
    fd = (c2 - cst) / h; an = M[:, j] * cst[j] * (1 - pi[j]) / eta_v[j]
    worst = max(worst, np.max(np.abs(fd - an) / (np.abs(an) + 1e-12))); nchk += 1
check("C5 dc_i/deta_j = M_ij c_j (1-pi_j)/eta_j", worst < 1e-4 and nchk > 50, f"{nchk} interior draws, max rel. error {worst:.2e}")

# C6 K_n ceiling
okc = True; cnt = 0
for _ in range(4000):
    n = rng.integers(3, 9); beta = rng.uniform(1.05, n - 0.05); lam = rng.uniform(0, 3); sigma = rng.uniform(0.05, 4)
    theta = 1 - beta / n; Lam = 1 + (n - 1) * beta / n; Lt = 1 + lam * (Lam - 1); p_ = theta / Lt
    eta_ = 10 ** rng.uniform(-3, 1); pi = shares(eta_, theta, Lt, sigma)
    A = np.ones((n, n)) - np.eye(n); cst = equilibrium(A, beta, 15.0, np.full(n, pi))
    pred_int = eta_ < (theta / beta) * p_ ** (sigma - 1)
    if abs(eta_ / ((theta / beta) * p_ ** (sigma - 1)) - 1) < 1e-6: continue
    okc &= (pred_int == interior(cst, 15.0)); cnt += 1
check("C6 K_n interior iff eta < (theta/beta) p^(sigma-1)", okc, f"{cnt} draws")

# C7 Leontief invariance on random networks (sigma -> 0 limit implemented exactly: pi = eta theta/(1+eta theta) at lam=0)
okv = True; cnt = 0; worst = 0
for _ in range(500):
    n = rng.integers(3, 9); A = random_connected(n, rng.uniform(0.3, 0.9)); dmin = (A.sum(1) + 1).min()
    beta = rng.uniform(1.05, min(1.95, dmin - 0.05)) if dmin > 2 else rng.uniform(1.05, 1.95)
    if beta >= dmin: continue
    eta_ = rng.uniform(0.02, 1 / beta * 0.999); d, theta, Lam, Lt = prices(A, beta, 0.0)
    pi = eta_ * theta / (1 + eta_ * theta)
    cst = equilibrium(A, beta, 15.0, pi); pred = eta_ * 15.0 / (1 - eta_ * (beta - 1))
    worst = max(worst, np.max(np.abs(cst - pred))); cnt += 1
check("C7 Leontief, lam=0, common eta: c* = eta e/(1-eta(beta-1)) on any network", worst < 1e-8, f"{cnt} networks, max |dev| {worst:.1e}")
# and the full-contribution corner when eta > 1/beta
A = np.ones((3, 3)) - np.eye(3); d, theta, Lam, Lt = prices(A, 1.5, 0.0); eta_ = 0.7
check("C7 corner: eta > 1/beta gives c* = e", np.allclose(equilibrium(A, 1.5, 15.0, eta_ * theta / (1 + eta_ * theta)), 15.0))

# design networks
K3 = np.ones((3, 3)) - np.eye(3)
S3 = np.array([[0, 1, 1], [1, 0, 0], [1, 0, 0]], float)   # node 0 = centre
def design_eq(eta_, sigma, lam, beta=1.5, e=15.0):
    out = {}
    for name, A in (("K", K3), ("S", S3)):
        d, theta, Lam, Lt = prices(A, beta, lam)
        if sigma == 0: pi = eta_ * (theta / Lt) / (1 + eta_ * (theta / Lt))
        else: pi = shares(np.full(3, eta_), theta, Lt, sigma)
        out[name] = (equilibrium(A, beta, e, pi), pi, theta, Lt, d)
    return out

# C8 sigma = 0, lam > 0: leaf > regular > centre
ok8 = True
for lam in (0.05, 0.25, 0.5, 1, 2, 4):
    for eta_ in (0.05, 0.15, 0.3):
        r_ = design_eq(eta_, 0.0, lam); cK = r_["K"][0][0]; cC, cL = r_["S"][0][0], r_["S"][0][1]
        if max(cK, cC, cL) < 15 - 1e-9: ok8 &= (cL > cK > cC)
check("C8 sigma=0, lam>0: leaf > regular > centre", ok8)

# C9 positional log-odds differences
s_, l_ = sp.symbols('s l', nonnegative=True)
LtK, LtC, LtL = 1 + l_ * sp.Rational(3, 2) * sp.Rational(2, 3) * 1, 1 + l_ * sp.Rational(3, 2), 1 + l_ * sp.Rational(1, 2)
# Lambda_K = 1 + 2(beta/3) = 2, Lambda_C = 1 + 2(beta/2) = 2.5, Lambda_L = 1 + beta/3 = 1.5 at beta = 1.5
LtK, LtC, LtL = 1 + l_ * 1, 1 + l_ * sp.Rational(3, 2), 1 + l_ * sp.Rational(1, 2)
thK, thC, thL = sp.Rational(1, 2), sp.Rational(1, 2), sp.Rational(1, 4)
lo_ = lambda thv, Ltv: sp.log(eta) + (1 - s_) * (sp.log(thv) - sp.log(Ltv))
D1 = sp.simplify(lo_(thC, LtC) - lo_(thK, LtK)); D2 = sp.simplify(lo_(thL, LtL) - lo_(thK, LtK))
check("C9 D1 = (sigma-1) log(Lt_C/Lt_K)", sp.simplify(D1 - (s_ - 1) * sp.log(LtC / LtK)) == 0)
check("C9 D2 = (sigma-1) log(p_K/p_L) = (sigma-1) log((2+lam)/(1+lam))", sp.simplify(sp.expand_log(D2 - (s_ - 1) * sp.log((2 + l_) / (1 + l_)), force=True)) == 0)
check("C9 sigma=0, lam=0: D1 = 0, D2 = -log 2", D1.subs({s_: 0, l_: 0}) == 0 and sp.simplify(D2.subs({s_: 0, l_: 0}) + sp.log(2)) == 0)

# C10 proportionality to e
okp = True
for _ in range(200):
    n = rng.integers(3, 7); A = random_connected(n); dmin = (A.sum(1) + 1).min()
    beta = rng.uniform(1.05, min(1.95, dmin - 0.05)) if dmin > 2 else 1.5
    if beta >= dmin: continue
    d, theta, Lam, Lt = prices(A, beta, rng.uniform(0, 2)); pi = shares(rng.uniform(.01, .15, n), theta, Lt, rng.uniform(.1, 3))
    c1 = equilibrium(A, beta, 1e6, pi); c2 = equilibrium(A, beta, 2e6, pi)
    if np.all(c1 < 1e6 * 0.999): okp &= np.allclose(c2, 2 * c1, rtol=1e-9)
check("C10 interior contributions proportional to e", okp)

# C11 best response by direct maximization
worst = 0
for _ in range(400):
    sigma = rng.uniform(0.05, 4); eta_ = 10 ** rng.uniform(-2, 0.3); theta = rng.uniform(.2, .8); Lt_ = rng.uniform(1, 3)
    W_ = rng.uniform(15, 30); pi = shares(eta_, theta, Lt_, sigma); cf = min(15.0, pi * W_ / theta)
    cd = br_direct(eta_, theta, Lt_, W_, sigma)
    worst = max(worst, abs(cf - cd))
check("C11 closed-form best response = direct maximization", worst < 1e-3, f"max |dev| {worst:.1e} tokens")

# C12 star closed form (Ch2 eq. ces_star_hom) with common eta
worst = 0; cnt = 0
for _ in range(2000):
    sigma = rng.uniform(0.05, 4); lam = rng.uniform(0, 3); eta_ = 10 ** rng.uniform(-3, 0)
    r_ = design_eq(eta_, sigma, lam); cS, pi, theta, Lt, d = r_["S"]
    if not interior(cS, 15.0): continue
    n, beta, e = 3, 1.5, 15.0; piC, piL = pi[0], pi[1]
    DS = (n - beta) * (2 - beta) - (n - 1) * piC * piL * beta**2
    cC = piC * e * (n * (2 - beta) + 2 * (n - 1) * piL * beta) / DS; cL = piL * e * (2 * (n - beta) + n * piC * beta) / DS
    worst = max(worst, abs(cC - cS[0]), abs(cL - cS[1])); cnt += 1
check("C12 star closed form = iteration", worst < 1e-8, f"{cnt} interior draws")

# C13/C14 positional orderings across networks with a common eta, including the Leontief limit sigma = 0
# (Ch2 Prop. ces_star_order (iii)-(iv) are established on sigma in [0.1, 20]; here sigma in [0, 4], lam in [0, 4])
ok13 = True; ok14 = True; ok15 = True; cnt = 0
for sigma in np.concatenate([[0.0], np.linspace(0.02, 4, 60)]):
    for lam in np.linspace(0, 4, 41):
        for eta_ in np.geomspace(1e-3, 3, 40):
            r_ = design_eq(eta_, sigma, lam); cK = r_["K"][0][0]; cC, cL = r_["S"][0][0], r_["S"][0][1]
            if max(cK, cC, cL) >= 15 - 1e-9: continue
            cnt += 1
            ok13 &= (cL >= cK - 1e-9)                                        # leaf >= regular, every sigma, lam
            if sigma == 0.0 and lam == 0.0: ok13 &= abs(cL - cK) < 1e-8
            if lam <= 2: ok15 &= ((cL > cC) if not (sigma == 0.0 and lam == 0.0) else abs(cL - cC) < 1e-8)  # leaf > centre for lam <= 2, except (0,0)
            if sigma >= 1 or lam == 0: ok14 &= (cC >= cK - 1e-9)              # centre >= regular if sigma >= 1 or lam = 0
            if sigma == 0.0 and lam > 0: ok14 &= (cC < cK)                    # centre < regular at the Leontief limit with lam > 0
check("C13 leaf >= regular for every sigma in [0,4], lam in [0,4]; equality at (0,0)", ok13, f"{cnt} interior points")
check("C14 centre >= regular if sigma >= 1 or lam = 0; centre < regular at sigma = 0, lam > 0", ok14)
check("C15 leaf > centre for lam <= 2 and every sigma in [0,4], except equality at sigma = 0, lam = 0", ok15)

# C16 position-preference threshold with heterogeneous intensity on S3: centre (eta_C) out-contributes the leaves (eta_P)
#     iff eta_C/eta_P > T(sigma, lam) = (theta_C/theta_L)^sigma (Lt_C/Lt_L)^(1-sigma)   [= 2^sigma ((1+1.5 lam)/(1+0.5 lam))^(1-sigma)]
ok16 = True; cnt = 0
for _ in range(20000):
    sigma = rng.choice([0.0, rng.uniform(0.02, 3)]); lam = rng.uniform(0, 3)
    etaP = 10 ** rng.uniform(-2.5, -0.3); etaC = etaP * 10 ** rng.uniform(-1, 1)
    d, theta, Lam, Lt = prices(S3, 1.5, lam); eta_v = np.array([etaC, etaP, etaP])
    pi = eta_v * (theta / Lt) ** (1 - sigma); pi = pi / (1 + pi)
    cS = equilibrium(S3, 1.5, 15.0, pi)
    if not interior(cS, 15.0): continue
    T = 2 ** sigma * ((1 + 1.5 * lam) / (1 + 0.5 * lam)) ** (1 - sigma)
    if abs(etaC / etaP / T - 1) < 1e-6: continue
    ok16 &= ((cS[0] > cS[1]) == (etaC / etaP > T)); cnt += 1
check("C16 centre > leaf iff eta_C/eta_P > 2^sigma ((1+1.5lam)/(1+0.5lam))^(1-sigma)", ok16, f"{cnt} interior draws")

print("\n%d checks failed" % len(FAIL)); sys.exit(1 if FAIL else 0)
