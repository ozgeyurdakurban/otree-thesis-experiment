# Ag yapisi katki davranisini nasil etkiliyor? Duzey, siralama, kosullu isbirligi, bilgi kanali, dagilim, sure, akran etkisi
import pandas as pd, numpy as np, warnings
from scipy import stats
import statsmodels.formula.api as smf
warnings.filterwarnings('ignore')
D=pd.read_pickle('D117.pkl').sort_values(['pid','round_number']).reset_index(drop=True)
D['star']=(D.treatment=='star')*1
SG=np.random.default_rng(7).choice([1,-1],size=(100000,39))
def perm(v,lab):
    v=np.asarray(v,float); s=SG[:,:len(v)]; p=(np.abs((s*v).mean(1))>=abs(v.mean())-1e-12).mean(); print(f'  {lab}: {v.mean():+.3f}, perm p={p:.4f}, pozitif {int((v>0).sum())}/{len(v)}')
cl=lambda d:{'cov_type':'cluster','cov_kwds':{'groups':d.gid}}
print('### A. Duzey: Star blogu (centre+leaf) vs Control/Cycle')
G=D.groupby(['gid','treatment']).contribution.mean().unstack(); perm(G.star-G.control,'Star - Control'); perm(G.star-(G.control+G.cycle)/2,'Star - (Control+Cycle)/2')
print('\n### B. Gruplar arasi temiz karsilastirma: yalniz 1. blok (sira etkisi yok)')
b1=D[D.block_index==1].groupby(['gid','treatment']).contribution.mean().reset_index()
print('  ',b1.groupby('treatment').contribution.agg(['mean','std','count']).round(2).to_dict('index'))
print('   Kruskal p=%.3f'%stats.kruskal(*[g.contribution for _,g in b1.groupby('treatment')]).pvalue, '| Star vs Control MWU p=%.3f'%stats.mannwhitneyu(b1[b1.treatment=='star'].contribution,b1[b1.treatment=='control'].contribution).pvalue)
b1i=D[(D.block_index==1)&(D.adv_dec==0)]
m=smf.ols('contribution ~ C(treatment, Treatment("control"))+block_round+C(session_code)',b1i).fit(**cl(b1i)); print('   1. blok OLS (oturum FE):',{k.split('.')[-1][:-1]:(round(v,2),round(m.pvalues[k],3)) for k,v in m.params.items() if 'treatment' in k})
print('\n### C. Sira / yayilma: Star deneyimi sonraki Control/Cycle davranisini degistiriyor mu?')
D['after_star']=((D.star_order<D.block_index)&(D.star==0))*1
d=D[D.star==0]; m=smf.ols('contribution ~ after_star+C(block_index)+block_round+cyc+adv_dec+partner_adv+C(pid)',d).fit(**cl(d)); print(f'  Star sonrasi Control/Cycle: {m.params.after_star:+.3f} (se {m.bse.after_star:.3f}, p {m.pvalues.after_star:.3f}) [birey FE, blok sirasi kontrollu]')
m=smf.ols('contribution ~ C(treatment)*C(block_index)+block_round+adv_dec+partner_adv+C(pid)',D).fit(**cl(D))
print('  Tretman x blok sirasi etkilesimleri ortak test p =',round(float(m.f_test([k for k in m.params.index if ':' in k and 'treatment' in k]).pvalue),3))
for tr in ['control','cycle','star']:
    q=D[(D.treatment==tr)&(D.adv_dec==0)].groupby('block_index').contribution.mean(); print(f'   {tr}: blok 1/2/3 ortalamasi {q.round(2).tolist()}')
print('\n### D. Kosullu isbirligi: onceki turda GORULEN komsu ortalamasina tepki, tretmana gore (birey FE)')
D['obs_oth']=(D.neighborhood_total_contribution-D.contribution)/(D.neighborhood_size-1)
for c in ['obs_oth','contribution','adv_dec']: D['lag_'+c]=D.groupby('pid')[c].shift()
D['lag_grpoth']=D.groupby('pid').apply(lambda x:((x.group_total_contribution-x.contribution)/2).shift()).reset_index(level=0,drop=True)
dy=D[(D.block_round>1)&(D.adv_dec==0)&(D.lag_adv_dec==0)].copy()
m=smf.ols('contribution ~ lag_obs_oth+lag_obs_oth:star+star+lag_contribution+block_round+C(block_index)+partner_adv+C(pid)',dy).fit(**cl(dy))
print(f"  Control/Cycle egimi {m.params.lag_obs_oth:.3f} (se {m.bse.lag_obs_oth:.3f}); Star'da fark {m.params['lag_obs_oth:star']:+.3f} (se {m.bse['lag_obs_oth:star']:.3f}, p {m.pvalues['lag_obs_oth:star']:.3f})")
m=smf.ols('contribution ~ lag_grpoth+lag_grpoth:star+star+lag_contribution+block_round+C(block_index)+partner_adv+C(pid)',dy).fit(**cl(dy))
print(f"  (grup ortalamasi sinyaliyle) Control/Cycle {m.params.lag_grpoth:.3f}; Star'da fark {m.params['lag_grpoth:star']:+.3f} (p {m.pvalues['lag_grpoth:star']:.3f})")
print('\n### E. Bilgi kanali: leaf iken GORULEN (centre) ve GORULMEYEN (diger leaf) kisinin onceki katkisina tepki')
st=D[D.star==1][['gid','round_number','pid','network_role','contribution']]
rows=[]
for (g,t),x in st.groupby(['gid','round_number']):
    c=x[x.network_role=='center']; L=x[x.network_role=='periphery']
    for i in range(2):
        rows.append({'gid':g,'round_number':t+1,'pid':L.iloc[i].pid,'seen':c.contribution.iloc[0],'unseen':L.iloc[1-i].contribution})
S=pd.DataFrame(rows); E=D.merge(S,on=['gid','round_number','pid'],how='inner')
E=E[(E.adv_dec==0)&(E.lag_adv_dec==0)&(E.block_round>1)]
m=smf.ols('contribution ~ seen+unseen+lag_contribution+block_round+C(network_role)+C(pid)',E).fit(**cl(E))
t_=m.t_test('seen - unseen = 0'); print(f'  gorulen centre(t-1) {m.params.seen:+.3f} (p {m.pvalues.seen:.3f}); gorulmeyen leaf(t-1) {m.params.unseen:+.3f} (p {m.pvalues.unseen:.3f}); fark p={float(t_.pvalue):.3f}; n={int(m.nobs)}')
print('\n### F. Grup ici dagilim ve uyum (her grup-tur icin katkilarin sd ve max-min)')
D['gsd']=D.groupby(['gid','round_number']).contribution.transform('std'); D['grng']=D.groupby(['gid','round_number']).contribution.transform(lambda x:x.max()-x.min())
gg=D.groupby(['gid','treatment'])[['gsd','grng']].mean().unstack()
print('   ort grup ici sd:',gg.gsd.mean().round(2).to_dict()); perm(gg.gsd.star-gg.gsd.control,'grup ici sd: Star - Control')
print('\n### G. Blok ici azalma egimi tretmana gore')
m=smf.ols('contribution ~ block_round*C(treatment)+C(block_index)+adv_dec+partner_adv+C(pid)',D).fit(**cl(D))
b=m.params; print(f"  control {b.block_round:.3f}/tur; cycle fark {b['block_round:C(treatment)[T.cycle]']:+.3f} (p {m.pvalues['block_round:C(treatment)[T.cycle]']:.3f}); star fark {b['block_round:C(treatment)[T.star]']:+.3f} (p {m.pvalues['block_round:C(treatment)[T.star]']:.3f})")
print('\n### H. Karar suresi (log, birey FE), Control\'e gore')
d=D[D.adv_dec==0]; m=smf.ols('ldur ~ cyc+leaf+centre+C(block_index)+block_round+C(pid)',d).fit(**cl(d))
print('  ',{k:f'{np.exp(m.params[k])-1:+.1%} (p {m.pvalues[k]:.3f})' for k in ['cyc','leaf','centre']}, '| medyan sn:',d.groupby('pos').dur.median().round(1).to_dict())
print('\n### I. Partnerlerin prosocial weight\'inin (kompozit) etkisi: dC_i/dB_j > 0 (Prop. cd_net_general)')
pt=[f'pt_b{i}' for i in range(1,11)]; Q=D.groupby('pid').first(); Q=Q[Q.svy_invalid==0].copy()
z=lambda s:(s-s.mean())/s.std()
Q['comp']=pd.concat([z(Q[pt].mean(axis=1)),z((Q.alt_c1+Q.alt_c2)/2),z(Q[['svo_a1','svo_a2','svo_a3']].isin(['B','C']).sum(axis=1)),z(Q.charity_d1)],axis=1).mean(axis=1)
D=D.merge(Q[['comp']],left_on='pid',right_index=True,how='left')
D['comp_oth']=D.groupby(['gid','round_number']).comp.transform(lambda x:x.sum())-D.comp
D['n_oth']=D.groupby(['gid','round_number']).comp.transform('count')-D.comp.notna()
D['comp_othm']=D.comp_oth/D.n_oth
r=D[(D.star==0)&(D.adv_dec==0)].groupby(['pid','gid','session_code']).agg(c=('contribution','mean'),own=('comp','first'),oth=('comp_othm','first')).reset_index().dropna()
m=smf.ols('c ~ own+oth+C(session_code)',r).fit(**cl(r)); print(f'  Control/Cycle (kisi duzeyi): kendi B +1sd {m.params.own:+.3f} (p {m.pvalues.own:.3f}); partnerlerin ort B +1sd {m.params.oth:+.3f} (p {m.pvalues.oth:.3f}); n={len(r)}')
r1=D[(D.round_number==1)&(D.adv_dec==0)].dropna(subset=['comp','comp_othm'])
m=smf.ols('contribution ~ comp+comp_othm+C(session_code)',r1).fit(**cl(r1)); print(f'  1. tur (geri bildirimden once): partner B {m.params.comp_othm:+.3f} (p {m.pvalues.comp_othm:.3f}) -> beklenti kanali yoksa 0 olmali')
# Star: leaf icin centre'in B'si ile diger leaf'in B'si (birey FE: yalniz fark tanimli)
cB=D[D.network_role=='center'].set_index(['gid','round_number']).comp.rename('compC')
D=D.join(cB,on=['gid','round_number']); D['compL']=np.where(D.network_role=='periphery',D.comp_oth-D.compC,np.nan)
lf=D[(D.network_role=='periphery')&(D.adv_dec==0)].dropna(subset=['compC','compL']).assign(dCL=lambda x:x.compC-x.compL)
m=smf.ols('contribution ~ dCL+block_round+C(pid)',lf).fit(**cl(lf)); print(f"  Star leaf (birey FE): bagli partnerin (centre) B'si - bagsiz partnerin (diger leaf) B'si +1 -> {m.params.dCL:+.3f} (se {m.bse.dCL:.3f}, p {m.pvalues.dCL:.3f}); model: >0")
m=smf.ols('contribution ~ compC+compL+block_round+C(session_code)',lf).fit(**cl(lf)); print(f"  Star leaf (havuzlanmis): centre B {m.params.compC:+.3f} (p {m.pvalues.compC:.3f}); diger leaf B {m.params.compL:+.3f} (p {m.pvalues.compL:.3f})")
D.to_pickle('D117_ag.pkl')
