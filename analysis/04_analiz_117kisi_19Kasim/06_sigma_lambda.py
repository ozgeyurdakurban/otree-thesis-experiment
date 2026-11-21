# Prop. identification (i): sigma != 1 iken (D1, D2) -> (sigma, lambda). Veri sigma ~ 0 verdigi icin lambda tanimlanabilir hale geliyor.
import pandas as pd, numpy as np, warnings
from scipy import optimize
import statsmodels.api as sm, statsmodels.formula.api as smf
warnings.filterwarnings('ignore')
D=pd.read_pickle('D117.pkl'); R=D[D.adv_dec==0]
zero=R.groupby('pid').contribution.sum().loc[lambda s:s==0].index; x=R[~R.pid.isin(zero)]
g1=lambda l:np.log((1+1.5*l)/(1+l)); g2=lambda l:np.log((2+l)/(1+l))   # n=3, beta=1.5
def invert(D1,D2):
    r=D1/D2
    if D2>=0: return np.nan,np.nan
    if r<=0: lam=0.0
    else:
        f=lambda l:g1(l)/g2(l)-r
        lam=optimize.brentq(f,1e-9,1e4) if f(1e4)>0 else np.inf
    return 1+D2/g2(lam), lam
m=smf.glm('share ~ leaf+centre+cyc+partner_adv+C(block_index)+block_round+C(pid)',x,family=sm.families.Binomial()).fit(cov_type='cluster',cov_kwds={'groups':x.gid})
D1,D2=m.params.centre,m.params.leaf; V=m.cov_params().loc[['centre','leaf'],['centre','leaf']].values
s,l=invert(D1,D2); print(f'FE logit: D1={D1:.3f}, D2={D2:.3f} -> sigma_hat={s:.3f}, lambda_hat={l:.3f} (D1>0 oldugu icin lambda sinirda: 0)')
rng=np.random.default_rng(1); draws=rng.multivariate_normal([D1,D2],V,20000); inv=np.array([invert(a,b) for a,b in draws])
print(f'Delta yerine parametrik simulasyon (20000): sigma %95 [{np.nanpercentile(inv[:,0],2.5):.3f}; {np.nanpercentile(inv[:,0],97.5):.3f}], lambda medyan {np.nanmedian(inv[:,1]):.3f}, %90 ust sinir {np.nanpercentile(inv[:,1],90):.3f}, %95 ust sinir {np.nanpercentile(inv[:,1],95):.3f}; P(lambda=0)={np.mean(inv[:,1]==0):.3f}')
# grup bootstrap (agregat log-odds)
lo=lambda p:np.log(p/(1-p)); G=R.pivot_table(index='gid',columns='pos',values='share'); G['reg']=(G.control+G.cycle)/2
out=[]
for _ in range(5000):
    b=G.iloc[rng.integers(0,len(G),len(G))]; out.append(invert(lo(b.center.mean())-lo(b.reg.mean()),lo(b.periphery.mean())-lo(b.reg.mean())))
out=np.array(out); print(f'Grup bootstrap: lambda %95 ust sinir {np.nanpercentile(out[:,1],95):.3f}; P(lambda=0)={np.mean(out[:,1]==0):.3f}')
print('Yorum: lambda <= ~ust sinir -> impact weight act motivinin kucuk bir kesri; altruism katsayisi zeta = lambda B/(1-B) ~ 0. H3 lambda<=2 icin saglam oldugundan H3\'un basarisizligi lambda ile aciklanamaz.')
