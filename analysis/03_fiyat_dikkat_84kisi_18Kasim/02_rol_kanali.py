# Rol farki hangi kanaldan geliyor? Bilgi yapisi (ekran): leaf yalnizca centre'in katkisini (toplam olarak) gorur;
# centre iki leaf'in TOPLAMINI gorur; normal pozisyon diger iki kisinin toplamini gorur. Karar ekraninda kazanc formulu acik yazili.
import pandas as pd, numpy as np, warnings, os
import statsmodels.formula.api as smf
from scipy import stats
warnings.filterwarnings('ignore')
SET=os.environ.get('SET','84')
D=pd.read_pickle('D84.pkl'); d=(D if SET=='84' else D[D.veri_seti_3==1]).copy()
adv='+adv_dec' if SET=='84' else ''
print('##### ORNEKLEM',SET,'N',d.pid.nunique())
cl=lambda x:{'cov_type':'cluster','cov_kwds':{'groups':x.gid}}
def r(m,k): return f"{m.params[k]:+.3f} (se {m.bse[k]:.3f}, p {m.pvalues[k]:.3f})"
d=d.sort_values(['pid','round_number'])
d['nb']=d.neighborhood_size-1
d['obs']=(d.neighborhood_total_contribution-d.contribution)/d.nb          # gordugu komsu ortalamasi (bu tur)
d['unobs']=np.where(d.pos=='periphery',d.group_total_contribution-d.neighborhood_total_contribution,np.nan)  # leaf'in gormedigi diger leaf
for v in ['obs','unobs','pos','contribution']: d[v+'_l']=d.groupby(['pid','block_index'])[v].shift()
d['grpoth_l']=d.groupby(['pid','block_index']).group_total_contribution.shift()-d.contribution_l
d['grpoth_l']=d.grpoth_l/2
L=d[d.block_round>=2].copy()

print('\n### 1. Tepki fonksiyonu: bu turun katkisi ~ onceki turda GORDUGU komsu ortalamasi (birey FE)')
for lab,q in [('tum',L),('normal (Control+Cycle)',L[L.treatment!='star']),('Star: simdi leaf',L[L.pos=='periphery']),('Star: simdi centre',L[L.pos=='center'])]:
    m=smf.ols('contribution ~ obs_l+block_round'+adv+'+C(pid)',q).fit(**cl(q)); print(f'  {lab:28s} n={len(q):4d}  gordugu: {r(m,"obs_l")}')

print('\n### 2. Plasebo: onceki turda leaf iken GORMEDIGI diger leaf\'e tepki (Star)')
q=L[(L.treatment=='star')&(L.pos_l=='periphery')].dropna(subset=['unobs_l'])
m=smf.ols('contribution ~ obs_l+unobs_l+block_round'+adv+'+C(pid)',q).fit(**cl(q)); print('  gordugu centre:',r(m,'obs_l'),'| gormedigi leaf:',r(m,'unobs_l'),' n',len(q))

print('\n### 3. Rol farki bilgi/karsiliklilik dinamigiyle aciklaniyor mu? (Star, kisi duzeyi leaf-centre dagilimi)')
S=L[(L.treatment=='star')&(L.adv_dec==0)].copy()
def gaps(x,col):
    q=x.groupby(['pid','pos'])[col].mean().unstack().dropna(); return q.periphery-q.center
rng=np.random.default_rng(7)
def excess(x,col,B=2000):
    g=gaps(x,col); obs=(g.abs()>=3).mean() if col=='contribution' else g.var()
    sims=[]
    for _ in range(B):
        y=x[['pid','pos',col]].copy(); y['pos']=y.groupby('pid').pos.transform(lambda v:rng.permutation(v.values))
        gg=gaps(y,col); sims.append((gg.abs()>=3).mean() if col=='contribution' else gg.var())
    return obs,np.mean(sims),np.mean(np.array(sims)>=obs)
o,s,p=excess(S,'contribution'); print(f'  ham katki (2.-6. turlar): |gap|>=3 orani {o:.3f} vs rastgele {s:.3f}, p={p:.3f}')
m=smf.ols('contribution ~ obs_l+block_round+C(pid)',S).fit(); S['res']=m.resid
o,s,p=excess(S,'res'); print(f'  gordugu komsu + tur etkisi cikarildiktan sonra: gap varyansi {o:.2f} vs rastgele {s:.2f}, p={p:.3f}')
S0=S.copy(); o0,s0,p0=excess(S0,'contribution'); 
m=smf.ols('contribution ~ block_round+C(pid)',S).fit(); S['res2']=m.resid
o,s,p=excess(S,'res2'); print(f'  yalnizca tur etkisi cikarildiktan sonra:        gap varyansi {o:.2f} vs rastgele {s:.2f}, p={p:.3f}')

print('\n### 4. Rol gecisleri: onceki tur rolune gore degisim, gordugu sinyal kontrollu')
q=L[L.treatment=='star'].copy(); q['tr']=q.pos_l.str[0]+'>'+q.pos.str[0]; q['dc']=q.contribution-q.contribution_l
print('  ham ortalama degisim:',q.groupby('tr').dc.agg(['mean','size']).round(2).to_dict('index'))
m=smf.ols('dc ~ C(tr)+obs_l+contribution_l+block_round'+adv,q).fit(**cl(q)); print('  regresyon (ref c>p):',{k:f"{m.params[k]:+.2f} p{m.pvalues[k]:.2f}" for k in m.params.index if 'tr' in k})

print('\n### 5. Sosyal etki kanali: kisinin bir jetonu digerlerine centre\'da 1,5, normalde 1,0, leaf\'te 0,5 getiriyor')
print('    Baskalarini onemseyen (yuksek B) kisi centre\'da fazla, leaf\'te az vermeli; fiyat ise ters yonu ongoruyor.')
x=d[(d.adv_dec==0)]
P=x.pivot_table(index='pid',columns='pos',values='contribution',aggfunc='mean')
P['norm']=P[['control','cycle']].mean(1); P['gap']=P.periphery-P.center; P['c_n']=P.center-P.norm; P['l_n']=P.periphery-P.norm
Bh=x[x.treatment!='star'].groupby('pid').share.mean(); P=P.join(Bh.rename('Bhat'))
sv=d.groupby('pid').first()
okp=~sv.index.isin(D[D.n_rounds_advanced>=14].pid.unique())     # ilerletilen 4 kisinin anketi eksik kabul
lik=sv[[f'pt_b{i}' for i in range(1,11)]].mean(1).where(okp); don=sv.charity_d1.where(okp)
svo=(sv[['svo_a1','svo_a2','svo_a3']]=='B').sum(1).astype(float).where(okp)   # prosocial (B) secim sayisi
P=P.join(lik.rename('likert')).join(don.rename('bagis')).join(svo.rename('svo'))
for y in ['gap','c_n','l_n']:
    out=[]
    for z in ['Bhat','likert','bagis','svo']:
        qq=P[[y,z]].dropna(); rho,p=stats.spearmanr(qq[y],qq[z]); out.append(f'{z} rho={rho:+.2f} (p {p:.2f}, n {len(qq)})')
    print(f'  {y:4s}:',' | '.join(out))
print('  (gap=leaf-centre, c_n=centre-normal, l_n=leaf-normal; kisi duzeyi)')
