# sigma~0 (tercih) mi, fiyat dikkatsizligi mi? Dolayli testler. 84 kisi + ilerletme dummy'leri.
# Dikkatsizlik ongorusu: fiyata tepki (leaf'in fazla vermesi) deneyimle / dusunmeyle ARTAR. Saf tercih (sigma~0): artmaz.
import pandas as pd, numpy as np, warnings, os
import statsmodels.api as sm, statsmodels.formula.api as smf
from scipy import stats
warnings.filterwarnings('ignore')
SET=os.environ.get('SET','84')
D=pd.read_pickle('D84.pkl'); d=D if SET=='84' else D[D.veri_seti_3==1]
print('##### ORNEKLEM',SET,'N',d.pid.nunique(),'grup',d.gid.nunique())
L2=np.log(0.5); cl=lambda x:{'cov_type':'cluster','cov_kwds':{'groups':x.gid}}
def r(m,k): return f"{m.params[k]:+.3f} (se {m.bse[k]:.3f}, p {m.pvalues[k]:.3f})"
adv='+adv_dec' if SET=='84' else ''
S=d[d.treatment=='star'].copy(); S['delib']=S.delib.fillna(0)

print('\n### A. Star icinde leaf - centre (jeton), birey FE. CD ongorusu ~ +3 jeton, sigma~0 ongorusu ~0')
m=smf.ols('contribution ~ leaf+block_round'+adv+'+C(pid)',S).fit(**cl(S)); print('ortalama leaf-centre:',r(m,'leaf'))
for k in [1,2,3]: S[f'leaf_o{k}']=S.leaf*(S.star_order==k)
m=smf.ols('contribution ~ leaf_o1+leaf_o2+leaf_o3+block_round'+adv+'+C(pid)',S).fit(**cl(S))
print('Star 1. blokta:',r(m,'leaf_o1')); print('Star 2. blokta:',r(m,'leaf_o2')); print('Star 3. blokta:',r(m,'leaf_o3'))
S['so']=S.star_order-1; S['leaf_so']=S.leaf*S.so
m=smf.ols('contribution ~ leaf+leaf_so+block_round'+adv+'+C(pid)',S).fit(**cl(S)); print('egilim (her ek blok deneyimi):',r(m,'leaf_so'))

print('\n### B. Star blogu icinde ogrenme: leaf - centre turlarla buyuyor mu?')
S['br']=S.block_round-1; S['leaf_br']=S.leaf*S.br
m=smf.ols('contribution ~ leaf+leaf_br+br'+adv+'+C(pid)',S).fit(**cl(S)); print('1. turda leaf-centre:',r(m,'leaf'),'| tur basina degisim:',r(m,'leaf_br'))
S['late']=(S.block_round>=4)*1; S['leaf_late']=S.leaf*S.late
m=smf.ols('contribution ~ leaf+leaf_late+late'+adv+'+C(pid)',S).fit(**cl(S)); print('ilk 3 tur:',r(m,'leaf'),'| son 3 turda ek:',r(m,'leaf_late'))

print('\n### C. Dusunme: Control/Cycle\'da yavas karar verenler leaf\'te daha cok fiyata tepki veriyor mu?')
S['leaf_delib']=S.leaf*S.delib
m=smf.ols('contribution ~ leaf+leaf_delib+block_round'+adv+'+C(pid)',S).fit(**cl(S)); print('leaf x dusunme tipi (1 sd):',r(m,'leaf_delib'))
S['ldur_c']=S.ldur-S.groupby('pid').ldur.transform('mean'); S['leaf_ldur']=S.leaf*S.ldur_c
m=smf.ols('contribution ~ leaf+ldur_c+leaf_ldur+block_round'+adv+'+C(pid)',S).fit(**cl(S)); print('leaf x o turun suresi (kisi ici, endojen):',r(m,'leaf_ldur'))

print('\n### D. sigma_hat (pay log-odds, fractional logit, birey FE) Star sirasina gore. CD: 1, Leontief: 0')
x=d[~d.pid.isin(d.groupby('pid').contribution.sum().loc[lambda s:s==0].index)].copy()
for k in [1,2,3]: x[f'leaf_o{k}']=x.leaf*(x.star_order==k)
m=smf.glm('share ~ leaf_o1+leaf_o2+leaf_o3+centre+cyc+C(block_index)+block_round'+adv+'+C(pid)',x,family=sm.families.Binomial()).fit(**cl(x))
for k in [1,2,3]:
    b,se=m.params[f'leaf_o{k}'],m.bse[f'leaf_o{k}']; s=1-b/L2; ss=se/abs(L2)
    print(f'Star {k}. blokta: sigma_hat {s:.3f}  %95GA [{s-1.96*ss:.3f}; {s+1.96*ss:.3f}]')
x['delib_leaf']=x.leaf*x.delib.fillna(0)
m=smf.glm('share ~ leaf+delib_leaf+centre+cyc+C(block_index)+block_round'+adv+'+C(pid)',x,family=sm.families.Binomial()).fit(**cl(x))
print('dusunme tipi +1 sd -> sigma degisimi:',f"{-m.params['delib_leaf']/L2:+.3f} (se {m.bse['delib_leaf']/abs(L2):.3f}, p {m.pvalues['delib_leaf']:.3f})")

print('\n### E. Fiyata tepki veren alt grup var mi? Kisi duzeyi: kendi leaf ort. - kendi centre ort.')
q=S[S.adv_dec==0].groupby(['pid','pos']).contribution.mean().unstack().dropna(); g=q.periphery-q.center
print('n',len(g),'| ortalama',round(g.mean(),2),'medyan',round(g.median(),2),'sd',round(g.std(),2))
for t in [2,3]: print(f'  leaf >= centre+{t}: {(g>=t).sum()} kisi | leaf <= centre-{t}: {(g<=-t).sum()} kisi | isaret testi p={stats.binomtest(int((g>=t).sum()),int((g>=t).sum()+(g<=-t).sum())).pvalue:.3f}')
print('  dagilim:',pd.cut(g,[-16,-4,-2,-0.5,0.5,2,4,16]).value_counts().sort_index().to_dict())
# permutasyon: kisi icinde rol etiketlerini karistir, |gap|>=3 olanlarin orani sansla ne kadar?
rng=np.random.default_rng(1); s2=S[S.adv_dec==0][['pid','pos','contribution']]
obs=((g.abs()>=3).mean()); sims=[]
for _ in range(2000):
    s2p=s2.copy(); s2p['pos']=s2p.groupby('pid').pos.transform(lambda v:rng.permutation(v.values))
    qq=s2p.groupby(['pid','pos']).contribution.mean().unstack().dropna(); gg=qq.periphery-qq.center; sims.append((gg.abs()>=3).mean())
print(f'  |leaf-centre|>=3 olanlarin orani: gozlenen {obs:.3f}, rol etiketleri rastgele olsaydi {np.mean(sims):.3f} (p={np.mean(np.array(sims)>=obs):.3f})')
