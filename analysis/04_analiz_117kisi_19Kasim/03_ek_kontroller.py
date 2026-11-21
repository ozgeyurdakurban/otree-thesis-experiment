# Ek kontroller: H5 marjinal etkileri ve saglamlik, cinsiyet (kesifsel), dictator payi vs oyun payi
import pandas as pd, numpy as np, warnings
from scipy import stats
import statsmodels.formula.api as smf
warnings.filterwarnings('ignore')
D=pd.read_pickle('D117.pkl'); R=D[D.adv_dec==0]
pt=[f'pt_b{i}' for i in range(1,11)]
Q=D.groupby('pid').first(); Q=Q[Q.svy_invalid==0].copy()
z=lambda s:(s-s.mean())/s.std()
Q['likert']=Q[pt].mean(axis=1); Q['anchor']=(Q.alt_c1+Q.alt_c2)/2; Q['svo']=Q[['svo_a1','svo_a2','svo_a3']].isin(['B','C']).sum(axis=1); Q['dict']=Q.charity_d1/100
Q['composite']=pd.concat([z(Q[v]) for v in ['likert','anchor','svo','dict']],axis=1).mean(axis=1)
Q['composite_nodict']=pd.concat([z(Q[v]) for v in ['likert','anchor','svo']],axis=1).mean(axis=1)
print('### H5 marjinal etkiler (birey FE; kompozit -1/0/+1 sd)')
for lab,dd in [('117',D),('Set 3',D[D.veri_seti_3==1])]:
    for bv in ['composite','composite_nodict']:
        d=dd.merge(Q[[bv]],left_on='pid',right_index=True)
        m=smf.ols(f'contribution ~ leaf+centre+cyc+leaf:{bv}+centre:{bv}+adv_dec+partner_adv+C(block_index)+block_round+C(pid)',d).fit(cov_type='cluster',cov_kwds={'groups':d.gid})
        out=[]
        for zz in [-1,0,1]:
            t=m.t_test(f'leaf + {zz}*leaf:{bv} - centre - {zz}*centre:{bv} = 0'); c=m.t_test(f'centre + {zz}*centre:{bv} = 0'); l=m.t_test(f'leaf + {zz}*leaf:{bv} = 0')
            out.append(f'z={zz:+d}: leaf-centre {float(t.effect):+.2f} (p {float(t.pvalue):.3f}), centre-reg {float(c.effect):+.2f}, leaf-reg {float(l.effect):+.2f}')
        print(f' [{lab}, {bv}]',' | '.join(out))
# kompozitin her pozisyondaki egimi (pooled, oturum FE)
d=D.merge(Q[['composite']],left_on='pid',right_index=True); d=d[d.adv_dec==0]
for p_ in ['control','cycle','center','periphery']:
    q=d[d.pos==p_].groupby(['pid','gid','session_code']).agg(c=('contribution','mean'),comp=('composite','first')).reset_index()
    m=smf.ols('c ~ comp+C(session_code)',q).fit(cov_type='cluster',cov_kwds={'groups':q.gid}); print(f'  {p_}: kompozit egimi {m.params.comp:+.3f} (se {m.bse.comp:.3f}, p {m.pvalues.comp:.3f})')
print('\n### Cinsiyet (kesifsel)')
P=R.groupby('pid').agg(c=('contribution','mean'),gid=('gid','first'),ses=('session_code','first')).join(Q[['gender','composite','dict']],how='inner')
f,m_=P[P.gender=='Kadın'],P[P.gender=='Erkek']
print(f'  kadin {f.c.mean():.2f} (n={len(f)}), erkek {m_.c.mean():.2f} (n={len(m_)}); MWU p={stats.mannwhitneyu(f.c,m_.c).pvalue:.3f}')
pp=P[P.gender.isin(['Kadın','Erkek'])].assign(female=lambda x:(x.gender=='Kadın')*1)
for f_ in ['c ~ female+C(ses)','c ~ female+composite+C(ses)']:
    mm=smf.ols(f_,pp).fit(cov_type='cluster',cov_kwds={'groups':pp.gid}); print(f'  {f_}: kadin {mm.params.female:+.2f} (se {mm.bse.female:.2f}, p {mm.pvalues.female:.3f})'+(f'; kompozit {mm.params.composite:+.2f} (p {mm.pvalues.composite:.3f})' if 'composite' in f_ else ''))
print(f'  kompozit: kadin {f.composite.mean():+.2f}, erkek {m_.composite.mean():+.2f} (MWU p={stats.mannwhitneyu(f.composite,m_.composite).pvalue:.3f}); bagis kadin {f.dict.mean()*100:.1f}, erkek {m_.dict.mean()*100:.1f}')
print('\n### Dictator payi ile oyundaki giving share (CD altinda ikisi de B_i)')
S=R[R.pos.isin(['control','cycle'])].groupby('pid').share.mean()
x=pd.concat([S.rename('g'),Q.dict],axis=1).dropna()
print(f'  ort dictator payi {x.dict.mean():.3f}, ort oyun payi {x.g.mean():.3f}; dictator payi > oyun payi olan kisi {(x.dict>x.g).mean():.3f}; Wilcoxon p={stats.wilcoxon(x.dict,x.g).pvalue:.1e}')
print(f'  Spearman {stats.spearmanr(x.dict,x.g)[0]:.3f} (p {stats.spearmanr(x.dict,x.g)[1]:.3f}); bagis<100 olanlarda Spearman {stats.spearmanr(x[x.dict<1].dict,x[x.dict<1].g)[0]:.3f} (p {stats.spearmanr(x[x.dict<1].dict,x[x.dict<1].g)[1]:.3f}, n={int((x.dict<1).sum())})')
print('\n### Oturum/sinif heterojenligi (gercek kararlar)')
print(R.groupby('session_code').agg(ort=('contribution','mean'),ilk3=('contribution',lambda s:s[R.loc[s.index,'round_number']<=3].mean()),son3=('contribution',lambda s:s[R.loc[s.index,'round_number']>=16].mean()),sifir=('contribution',lambda s:(s==0).mean())).round(2))
