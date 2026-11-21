# Prosocial weight olculeri: hangisi katkiyla iliskili? Ayri mi, olcek mi? Kismi etkiler, VIF, Shapley R2, faktor yapisi, ORIV (olcum hatasi)
import pandas as pd, numpy as np, warnings, itertools, math
from scipy import stats
import statsmodels.formula.api as smf, statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from linearmodels.iv import IV2SLS
from factor_analyzer import FactorAnalyzer
warnings.filterwarnings('ignore')
D=pd.read_pickle('D117.pkl'); R=D[D.adv_dec==0]
pt=[f'pt_b{i}' for i in range(1,11)]
Q=D.groupby('pid').first(); Q=Q[Q.svy_invalid==0].copy()
Sh=R.pivot_table(index='pid',columns='pos',values='share')
Q['c']=R.groupby('pid').contribution.mean(); Q['c1']=R[R.round_number==1].set_index('pid').contribution; Q['Bhat']=(Sh.control+Sh.cycle)/2
Q['likert']=Q[pt].mean(axis=1); Q['anchor']=(Q.alt_c1+Q.alt_c2)/2; Q['svo']=Q[['svo_a1','svo_a2','svo_a3']].isin(['B','C']).sum(axis=1); Q['dict']=Q.charity_d1
Q['dict_full']=(Q.charity_d1==100)*1; Q['female']=(Q.gender=='Kadın')*1
z=lambda s:(s-s.mean())/s.std()
M=['likert','anchor','svo','dict']
for v in M+['alt_c1','alt_c2']: Q['z_'+v]=z(Q[v])
Q['comp']=Q[['z_'+v for v in M]].mean(axis=1); Q['comp3']=Q[['z_likert','z_anchor','z_svo']].mean(axis=1)
Q=Q.dropna(subset=['c']); n=len(Q); print('N =',n)
cl={'cov_type':'cluster','cov_kwds':{'groups':Q.gid}}
print('\n### 1. Ikili iliskiler (Pearson / Spearman) - hedefler: ort. katki, 1. tur katkisi (geri bildirimden once), B_hat (Control+Cycle share)')
rows=[]
for v in M+['alt_c1','alt_c2','comp','comp3']:
    for t in ['c','c1','Bhat']:
        rows.append((v,t,stats.pearsonr(Q[v],Q[t])[0],stats.spearmanr(Q[v],Q[t])[0],stats.spearmanr(Q[v],Q[t])[1]))
print(pd.DataFrame(rows,columns=['olcu','hedef','pearson','spearman','p']).pivot(index='olcu',columns='hedef',values=['spearman','p']).round(3))
print('\n### 2. Coklu regresyon: dort olcu birlikte (kismi etkiler), oturum FE, grup kumelenmis SE')
X=Q[['z_'+v for v in M]]; print('  VIF:',{c:round(variance_inflation_factor(sm.add_constant(X).values,i+1),2) for i,c in enumerate(X.columns)})
print('  Olculer arasi Pearson:'); print(Q[M].corr().round(2))
for t in ['c','c1','Bhat']:
    yv=z(Q[t]) if t=='Bhat' else Q[t]
    m=smf.ols(f'{t} ~ z_likert+z_anchor+z_svo+z_dict+C(session_code)',Q).fit(**cl)
    jt=m.f_test('z_likert=0, z_anchor=0, z_svo=0, z_dict=0').pvalue
    print(f'  {t}: '+'; '.join(f"{v} {m.params['z_'+v]:+.3f} (se {m.bse['z_'+v]:.3f}, p {m.pvalues['z_'+v]:.3f})" for v in M)+f' | ortak test p={float(jt):.4f}, R2={m.rsquared:.3f}')
    m2=smf.ols(f'{t} ~ comp+C(session_code)',Q).fit(**cl); m0=smf.ols(f'{t} ~ C(session_code)',Q).fit()
    print(f'      kompozit tek basina: {m2.params.comp:+.3f} (se {m2.bse.comp:.3f}, p {m2.pvalues.comp:.4f}), R2 artisi {m2.rsquared-m0.rsquared:.3f} (4 ayri olcu: {m.rsquared-m0.rsquared:.3f})')
print('\n### 3. Shapley (dominance) R2 ayristirmasi - ort. katki ve B_hat (oturum FE sabit tutularak)')
def r2(cols,t):
    f=f'{t} ~ '+('+'.join(cols)+'+' if cols else '')+'C(session_code)'; return smf.ols(f,Q).fit().rsquared
for t in ['c','Bhat']:
    base=r2([],t); zc=['z_'+v for v in M]; sh={}
    for v in zc:
        others=[o for o in zc if o!=v]; tot=0
        for k in range(len(others)+1):
            for S in itertools.combinations(others,k):
                w=math.factorial(k)*math.factorial(len(zc)-k-1)/math.factorial(len(zc)); tot+=w*(r2(list(S)+[v],t)-r2(list(S),t))
        sh[v[2:]]=tot
    T=sum(sh.values()); print(f'  {t}: toplam R2 artisi {T:.3f};',{k:f'{v:.3f} (%{100*v/T:.0f})' for k,v in sh.items()})
print('\n### 4. Madde duzeyi: GPS anchor maddeleri ve Likert faktor yapisi')
for v in ['alt_c1','alt_c2']:
    m=smf.ols(f'c ~ z_{v}+C(session_code)',Q).fit(**cl); print(f'  {v}: +1sd -> {m.params["z_"+v]:+.3f} (p {m.pvalues["z_"+v]:.3f})')
m=smf.ols('c ~ z_alt_c1+z_alt_c2+C(session_code)',Q).fit(**cl); print(f'  birlikte: alt_c1 {m.params.z_alt_c1:+.3f} (p {m.pvalues.z_alt_c1:.3f}), alt_c2 {m.params.z_alt_c2:+.3f} (p {m.pvalues.z_alt_c2:.3f})')
fa=FactorAnalyzer(n_factors=2,rotation='varimax',method='ml'); fa.fit(Q[pt]); L=pd.DataFrame(fa.loadings_,index=pt,columns=['F1','F2']); print('  Likert 2 faktor (ML, varimax) yukleri:'); print(L.round(2).T)
F=pd.DataFrame(fa.transform(Q[pt]),index=Q.index,columns=['F1','F2']); Q=Q.join(F)
m=smf.ols('c ~ F1+F2+C(session_code)',Q).fit(**cl); print(f'  Faktor skorlari -> ort katki: F1 {m.params.F1:+.3f} (p {m.pvalues.F1:.3f}), F2 {m.params.F2:+.3f} (p {m.pvalues.F2:.3f})')
for it in pt:
    r_=stats.spearmanr(Q[it],Q.c); print(f'   {it}: rho={r_[0]:+.2f} (p {r_[1]:.3f})',end='')
print()
fa1=FactorAnalyzer(n_factors=1,rotation=None,method='ml'); C4=Q[['z_'+v for v in M]]; fa1.fit(C4); print('  4 kanalli tek faktor yukleri:',dict(zip(M,fa1.loadings_[:,0].round(2))))
Q['fscore']=fa1.transform(C4)[:,0]; Q['fscore']*=np.sign(np.corrcoef(Q.fscore,Q.comp)[0,1])
m=smf.ols('c ~ fscore+C(session_code)',Q).fit(**cl); print(f'  Faktor skoru (latent B) -> ort katki: {m.params.fscore/Q.fscore.std():+.3f} jeton/sd (p {m.pvalues.fscore:.4f})')
print('\n### 5. Bagisin dogrusal olmamasi (tavan: %%%.0f tam bagis)'%(100*Q.dict_full.mean()))
m=smf.ols('c ~ dict_full+C(session_code)',Q).fit(**cl); print(f'  tam bagis yapan vs yapmayan: {m.params.dict_full:+.3f} (p {m.pvalues.dict_full:.3f})')
q=Q[Q.dict<100]; r_=stats.spearmanr(q.dict,q.c); print(f'  bagis<100 olanlarda bagis ~ katki: rho={r_[0]:.3f} (p {r_[1]:.3f}, n={len(q)})')
print('\n### 6. Olcum hatasi: ORIV mantigi (Gillen, Snowberg ve Yariv 2019) - bir olcu digerleriyle araclanir')
for endo,inst in [('z_likert',['z_anchor','z_svo']),('z_anchor',['z_likert','z_svo']),('z_svo',['z_likert','z_anchor']),('comp3','z_dict')]:
    inst=inst if isinstance(inst,list) else [inst]
    f=f'c ~ 1 + C(session_code) + [{endo} ~ {"+".join(inst)}]'
    r=IV2SLS.from_formula(f,Q).fit(cov_type='clustered',clusters=Q.gid)
    ols=smf.ols(f'c ~ {endo}+C(session_code)',Q).fit(**cl)
    fs=smf.ols(f'{endo} ~ {"+".join(inst)}+C(session_code)',Q).fit(); Fst=fs.f_test(', '.join(f'{i}=0' for i in inst)).fvalue
    print(f'  {endo} | arac {inst}: OLS {ols.params[endo]:+.3f} -> IV {r.params[endo]:+.3f} (se {r.std_errors[endo]:.3f}, p {r.pvalues[endo]:.3f}); 1. asama F={float(Fst):.1f}')
print('\n### 7. Kompozitin belirleyicileri ve cinsiyet aracilik (kesifsel)')
pp=Q[Q.gender.isin(['Kadın','Erkek'])]
a=smf.ols('comp ~ female+C(session_code)',pp).fit(cov_type='cluster',cov_kwds={'groups':pp.gid}); b=smf.ols('c ~ female+comp+C(session_code)',pp).fit(cov_type='cluster',cov_kwds={'groups':pp.gid}); c=smf.ols('c ~ female+C(session_code)',pp).fit(cov_type='cluster',cov_kwds={'groups':pp.gid})
print(f'  toplam etki {c.params.female:+.2f} (p {c.pvalues.female:.3f}); kadin -> kompozit {a.params.female:+.2f} (p {a.pvalues.female:.3f}); kompozit -> katki {b.params.comp:+.2f} (p {b.pvalues.comp:.3f}); dolayli {a.params.female*b.params.comp:+.2f}, dogrudan {b.params.female:+.2f} (p {b.pvalues.female:.3f})')
Q[['gid','session_code','c','c1','Bhat']+M+['comp','comp3','fscore','F1','F2','female']].to_csv('katilimci_prososyal_ozet.csv')
