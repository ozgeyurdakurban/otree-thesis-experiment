# Ch2 hipotezlerinin buyuklugu sigma'ya ve lambda'ya gore (n=3, beta=1.5, e=15); regular katki gozlenen 5.9'a kalibre
import numpy as np
from scipy.optimize import brentq
e,cK=15,5.9
piK=cK/(30+2*cK); oK=piK/(1-piK)
print('### A. CES, lambda=0: pozisyon farklari sigma ile nasil kuculuyor (ortak B, regular=5.9)')
def star_ces(s):
    w=oK/0.5**(1-s); oL=w*0.25**(1-s); piL=oL/(1+oL); piC=piK
    cC,cL=np.linalg.solve(np.array([[1,-2*piC],[-3*piL,1]]),[30*piC,60*piL]); B=w**(1/s)/(1+w**(1/s)); return cL,cC,B
for s in [1,0.75,0.5,0.25,0.1,0.05,0.01]:
    cL,cC,B=star_ces(s); print(f'  sigma={s:<5}: B={B:.2e} leaf={cL:.2f} centre={cC:.2f} | leaf-centre {cL-cC:+.2f}, leaf-regular {cL-cK:+.2f}, centre-regular {cC-cK:+.2f}')
for g in [0.16,0.5]: print(f'  leaf-centre farki {g} jeton olan sigma: {brentq(lambda s:star_ces(s)[0]-star_ces(s)[1]-g,1e-6,1):.3f}')
print('  (gozlenen leaf-centre %90 GA ust ucu +0.16 -> sigma <~ 0.05)')
print('\n### B. Leontief U=min{X, kappa*Y}, X = kappa*Lambda_tilde*c: pozisyon farklari lambda ile (regular=5.9)')
def star_leo(lam):
    k=(e/cK+0.5)/(1+lam)
    cC,cL=np.linalg.solve(np.array([[k*(1+1.5*lam)+0.5,-1],[-0.75,k*(1+0.5*lam)+0.25]]),[e,e]); return cL,cC,k
for lam in [0,0.05,0.1,0.25,0.5,1.0]:
    cL,cC,k=star_leo(lam); print(f'  lambda={lam:<5}: kappa={k:.2f} leaf={cL:.2f} centre={cC:.2f} | leaf-centre {cL-cC:+.2f}, leaf-regular {cL-cK:+.2f}, centre-regular {cC-cK:+.2f}')
print(f'  leaf-centre farki 0.16 jeton olan lambda (Leontief): {brentq(lambda l:star_leo(l)[0]-star_leo(l)[1]-0.16,1e-9,5):.3f}')
print('\n### C. Ch2 normalizasyonunda Leontief limiti (lambda=0): pi -> theta/(1+theta), B_i duser')
for th,lab in [(0.5,'regular/centre'),(0.25,'leaf')]: print(f'  {lab}: pi = {th/(1+th):.3f}')
print('  K3 dengesi: c = 2*pi*(15+c) -> pi=1/3 icin c = 30 > 15 -> herkes tam katki (c=15); veri %39 -> bu normalizasyonda Leontief limiti reddedilir')
