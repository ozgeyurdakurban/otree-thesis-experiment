"""
network_asymmetric_derivations.py
=================================
Symbolic verification of the ASYMMETRIC (heterogeneous prosocial-weight)
Nash equilibria on the cycle C_n and the star S_n, for the impact-based
Cobb-Douglas model.

Model recap
-----------
Interior first-order condition on a general network:
    c_i = kappa_i * X_i,    X_i = e - theta_i c_i + (beta/d_i) * sum_{j in G_i} c_j
with
    theta_i = 1 - beta/d_i,     kappa_i = B_i / (A_i * theta_i),   A_i = 1 - B_i.
This yields the linear best-response system
    c_i = alpha_i + gamma_i * sum_{j in G_i} c_j,
    alpha_i = kappa_i e / (1 + kappa_i theta_i),
    gamma_i = (kappa_i beta/d_i) / (1 + kappa_i theta_i),
i.e.  c = alpha + (Gamma A) c,  with Gamma = diag(gamma_i), A the adjacency.
The interior equilibrium is c* = (I - Gamma A)^{-1} alpha, unique when the
best-response map is a contraction, rho(Gamma A) < 1.

Topology conventions (closed neighborhood size d_i = |N[i]|):
  - cycle  C_n : every node has 2 neighbors, so d_i = 3 for all n>=3
                 (hence C_3 = K_3); theta = 1 - beta/3.
  - star   S_n : center has d_C = n (center + (n-1) leaves);
                 each leaf has d_L = 2; theta_C = 1 - beta/n, theta_L = 1 - beta/2.

All checks below print PASS/FAIL and the script asserts at the end.
"""

import sympy as sp

PASS = []


def record(name, ok):
    PASS.append(ok)
    print(("PASS" if ok else "FAIL"), name)


# ============================================================
# 1. CYCLE: direct solver and closed forms
# ============================================================
def cycle_direct(n, alpha, gamma):
    """Solve the cyclic best-response system c_i = alpha_i + gamma_i (c_{i-1}+c_{i+1})."""
    c = sp.symbols(f'c1:{n + 1}')
    eqs = []
    for i in range(n):
        eqs.append(sp.Eq(c[i], alpha[i] + gamma[i] * (c[(i - 1) % n] + c[(i + 1) % n])))
    return sp.solve(eqs, c, dict=True)[0], c


# ---- Cycle n = 3 (= complete graph K_3): aggregate closed form ----
a = sp.symbols('a1 a2 a3')
g = sp.symbols('g1 g2 g3')
sol3, c3 = cycle_direct(3, a, g)

# Claim: with p_i = g_i/(1+g_i), q_i = a_i/(1+g_i),
#        C* = (sum q_i)/(1 - sum p_i),   c_i* = q_i + p_i C*.
p = [g[i] / (1 + g[i]) for i in range(3)]
q = [a[i] / (1 + g[i]) for i in range(3)]
Cstar = sum(q) / (1 - sum(p))
c3_mine = [sp.simplify(q[i] + p[i] * Cstar) for i in range(3)]
record("Cycle n=3 (=K_3) aggregate closed form",
       all(sp.simplify(c3_mine[i] - sol3[c3[i]]) == 0 for i in range(3)))

# ---- Cycle n = 4: bipartite (even/odd) closed form ----
a4 = sp.symbols('a1 a2 a3 a4')
g4 = sp.symbols('g1 g2 g3 g4')
sol4, c4 = cycle_direct(4, a4, g4)
# Odd sublattice {1,3} responds to even sum S24 = c2+c4; even {2,4} to S13 = c1+c3.
A_, B_ = a4[0] + a4[2], a4[1] + a4[3]
G_, H_ = g4[0] + g4[2], g4[1] + g4[3]
S13 = (A_ + G_ * B_) / (1 - G_ * H_)
S24 = (B_ + H_ * A_) / (1 - G_ * H_)
c4_mine = [a4[0] + g4[0] * S24, a4[1] + g4[1] * S13,
           a4[2] + g4[2] * S24, a4[3] + g4[3] * S13]
record("Cycle n=4 bipartite closed form",
       all(sp.simplify(c4_mine[i] - sol4[c4[i]]) == 0 for i in range(4)))


# ============================================================
# 2. STAR: direct solver and closed form (general number of leaves)
# ============================================================
def star_check(num_leaves):
    """Verify the star closed form for a center with `num_leaves` leaves."""
    L = num_leaves
    cC = sp.Symbol('cC')
    cs = sp.symbols(f'cL1:{L + 1}')
    aC, gC = sp.symbols('aC gC')
    aL = sp.symbols(f'aL1:{L + 1}')
    gL = sp.symbols(f'gL1:{L + 1}')

    eqs = [sp.Eq(cC, aC + gC * sum(cs))]
    for j in range(L):
        eqs.append(sp.Eq(cs[j], aL[j] + gL[j] * cC))
    sol = sp.solve(eqs, (cC,) + cs, dict=True)[0]

    # Closed form: c_C* = (aC + gC * sum aL) / (1 - gC * sum gL),  c_j* = aL_j + gL_j c_C*.
    cC_mine = (aC + gC * sum(aL)) / (1 - gC * sum(gL))
    cs_mine = [aL[j] + gL[j] * cC_mine for j in range(L)]
    ok = (sp.simplify(cC_mine - sol[cC]) == 0
          and all(sp.simplify(cs_mine[j] - sol[cs[j]]) == 0 for j in range(L)))
    return ok


for L in (2, 3, 4):
    record(f"Star with {L} leaves (n={L + 1}) closed form", star_check(L))


# ---- Star spectral radius: rho(Gamma A) = sqrt(gC * sum gL) ----
gC = sp.Symbol('gC', positive=True)
gL1, gL2 = sp.symbols('gL1 gL2', positive=True)
A_star = sp.Matrix([[0, 1, 1], [1, 0, 0], [1, 0, 0]])      # center 0, leaves 1,2
Gam = sp.diag(gC, gL1, gL2)
eig = (Gam * A_star).eigenvals()
nonzero = [k for k in eig if sp.simplify(k) != 0]
record("Star rho(Gamma A) = sqrt(gC (gL1+gL2))",
       any(sp.simplify(k**2 - gC * (gL1 + gL2)) == 0 for k in nonzero))


# ============================================================
# 3. Numerical sanity at experimental parameters (beta=1.5, e=15, n=3)
#    Ordering by B and strategic complementarity.
# ============================================================
beta = sp.Rational(3, 2)
e = 15
theta_cyc = 1 - beta / 3
theta_C = 1 - beta / 3       # star center, n=3
theta_L = 1 - beta / 2       # star leaf


def alpha_gamma(B, theta, d):
    A = 1 - B
    k = B / (A * theta)
    return k * e / (1 + k * theta), k * (beta / d) / (1 + k * theta)


def cycle3(Bs):
    ag = [alpha_gamma(B, theta_cyc, 3) for B in Bs]
    a_, g_ = [x[0] for x in ag], [x[1] for x in ag]
    p_ = [g_[i] / (1 + g_[i]) for i in range(3)]
    q_ = [a_[i] / (1 + g_[i]) for i in range(3)]
    C = sum(q_) / (1 - sum(p_))
    return [float(q_[i] + p_[i] * C) for i in range(3)], float(sum(p_))


def star3(BC, B1, B2):
    aC, gC_ = alpha_gamma(BC, theta_C, 3)
    a1, g1 = alpha_gamma(B1, theta_L, 2)
    a2, g2 = alpha_gamma(B2, theta_L, 2)
    cC = (aC + gC_ * (a1 + a2)) / (1 - gC_ * (g1 + g2))
    return float(cC), float(a1 + g1 * cC), float(a2 + g2 * cC), float(gC_ * (g1 + g2))


cyc, sp_sum = cycle3([sp.Rational(2, 10), sp.Rational(3, 10), sp.Rational(45, 100)])
record("Cycle n=3 ordered by B (asc)", cyc[0] < cyc[1] < cyc[2] and sp_sum < 1)

base = star3(sp.Rational(3, 10), sp.Rational(3, 10), sp.Rational(3, 10))
record("Star homogeneous: periphery > center", base[1] > base[0] and base[2] > base[0])
hi_leaf = star3(sp.Rational(3, 10), sp.Rational(35, 100), sp.Rational(3, 10))
record("Star: own-B up raises own leaf", hi_leaf[1] > base[1])
hi_cent = star3(sp.Rational(35, 100), sp.Rational(3, 10), sp.Rational(3, 10))
record("Star: center-B up raises center", hi_cent[0] > base[0])
record("Star: center-B up raises leaves (complementarity)", hi_cent[1] > base[1])


# ============================================================
print("-" * 56)
assert all(PASS), "Some checks FAILED."
print(f"ALL {len(PASS)} CHECKS PASSED.")
