# Ch2/Ch3'te planlanan analizler -- 117 kisi, kimse cikarilmadi (ilerletme dummy'leri); Set 3 saglamlik
import pandas as pd, numpy as np, warnings, itertools
from scipy import stats, optimize
import statsmodels.api as sm, statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
warnings.filterwarnings('ignore')
pd.set_option('display.width',220); pd.set_option('display.max_columns',60); pd.set_option('display.float_format',lambda v:f'{v:.3f}')
D=pd.read_pickle('D117.pkl'); L2=np.log(0.5); rng=np.random.default_rng(2026)
D['reg']=D.pos.isin(['control','cycle'])*1
SIGNS={}
def perm(v,lab,ret=False):
    v=np.asarray(v,float); n=len(v)
    if n not in SIGNS: SIGNS[n]=np.random.default_rng(7).choice([1,-1],size=(100000,n))
    obs=v.mean(); p=(np.abs((SIGNS[n]*v).mean(axis=1))>=abs(obs)-1e-12).mean()
    pos=(v>0).sum(); print(f'  {lab}: fark {obs:+.3f} (grup sd {v.std(ddof=1):.2f}), permutasyon p={p:.4f}, pozitif grup {pos}/{n}')
    return (obs,p) if ret else None
def tost(v,delta,lab):
    v=np.asarray(v,float); n=len(v); se=v.std(ddof=1)/np.sqrt(n); m=v.mean()
    p=max(stats.t.sf((m+delta)/se,n-1),stats.t.cdf((m-delta)/se,n-1)); t=stats.t.ppf(.95,n-1)
    print(f'  TOST {lab} (+-{delta}): p={p:.4f}, %90 GA [{m-t*se:.2f}; {m+t*se:.2f}]')
def gtab(d,val='contribution'):
    G=d.pivot_table(index='gid',columns='pos',values=val,aggfunc='mean'); G['reg']=(G.control+G.cycle)/2; return G
samples={'117 (tum)':D,'Set 3 (111)':D[D.veri_seti_3==1]}

print('########## 1. H2: Control = Cycle (C3 = K3, yalniz cerceveleme farki)')
for k,d in samples.items():
    G=gtab(d); S=gtab(d,'share'); print(f' [{k}] {len(G)} grup')
    perm(G.cycle-G.control,'Cycle - Control (jeton)'); tost(G.cycle-G.control,1,'Cycle-Control'); tost(G.cycle-G.control,0.5,'Cycle-Control')
    perm(S.cycle-S.control,'Cycle - Control (giving share)')
m=smf.ols('contribution ~ cyc+leaf+centre+adv_dec+partner_adv+C(block_index)+block_round+C(pid)',D).fit(cov_type='cluster',cov_kwds={'groups':D.gid})
print(f" Birey FE OLS (dummy'li, 117): cycle {m.params.cyc:+.3f} (se {m.bse.cyc:.3f}, p {m.pvalues.cyc:.3f})")

print('\n########## 2. Referans spesifikasyonun (Cobb-Douglas, sigma=1) testi: giving share pozisyonlar arasi esit mi?')
for k,d in samples.items():
    S=gtab(d,'share'); print(f' [{k}]')
    perm(S.periphery-S.reg,'share: leaf - regular'); perm(S.center-S.reg,'share: centre - regular'); perm(S.periphery-S.center,'share: leaf - centre')
print(' Fractional logit (giving share), birey FE, grup kumelenmis SE; sigma_hat = 1 - D2/ln(0.5)  [lambda=0 altinda]')
# Not: adv_dec=1 kararlarin hepsi 0 oldugundan dogrusal olmayan modellerde (logit, PPML) bu dummy sifiri tam ongorur (MLE -> -inf);
# dummy'yi koymak bu kararlari tahminden dusmekle matematiksel olarak ayni. Bu yuzden bu modeller gercek kararlarla (adv_dec=0) kurulur.
R0=D[D.adv_dec==0]
zero=R0.groupby('pid').contribution.sum().loc[lambda s:s==0].index  # FE logit tum-sifir kisileri tahmin edemez (teknik)
print('  Gercek kararlarinin hepsi 0 olan kisi (FE logitte bilgi tasimaz):',len(zero),list(zero),'| hic gercek karari olmayan kisi:',D.pid.nunique()-R0.pid.nunique())
x=R0[~R0.pid.isin(zero)]
SIG={}
for lab,ctrl in [('kontrolsuz',''),('blok+tur+partner_adv','+partner_adv+C(block_index)+block_round')]:
    mm=smf.glm('share ~ leaf+centre+cyc'+ctrl+'+C(pid)',x,family=sm.families.Binomial()).fit(cov_type='cluster',cov_kwds={'groups':x.gid})
    b,se=mm.params,mm.bse; sig=1-b.leaf/L2; sse=se.leaf/abs(L2); SIG[lab]=sig
    print(f"  {lab}: D2(leaf)={b.leaf:.3f} (se {se.leaf:.3f}); D1(centre)={b.centre:.3f} (se {se.centre:.3f}, p {mm.pvalues.centre:.3f}); cycle={b.cyc:.3f} (p {mm.pvalues.cyc:.3f}) -> sigma_hat={sig:.3f} (se {sse:.3f}) %95 GA [{sig-1.96*sse:.3f}; {sig+1.96*sse:.3f}]; H0 sigma=1: z={(sig-1)/sse:.2f}")
x3=x[x.veri_seti_3==1]; mm=smf.glm('share ~ leaf+centre+cyc+C(block_index)+block_round+C(pid)',x3,family=sm.families.Binomial()).fit(cov_type='cluster',cov_kwds={'groups':x3.gid})
print(f"  Set 3: sigma_hat={1-mm.params.leaf/L2:.3f} (se {mm.bse.leaf/abs(L2):.3f}); D1={mm.params.centre:.3f} (p {mm.pvalues.centre:.3f})")
Gm=gtab(D[D.adv_dec==0],'share'); lo=lambda p:np.log(p/(1-p))
def sig_from(G): return 1-(lo(G.periphery.mean())-lo(G.reg.mean()))/L2, lo(G.center.mean())-lo(G.reg.mean())
bs=np.array([sig_from(Gm.iloc[rng.integers(0,len(Gm),len(Gm))]) for _ in range(5000)])
print(f'  Agregat log-odds: sigma={sig_from(Gm)[0]:.3f}, D1={sig_from(Gm)[1]:.3f}; grup bootstrap %95 GA sigma {np.percentile(bs[:,0],[2.5,97.5]).round(3)}, D1 {np.percentile(bs[:,1],[2.5,97.5]).round(3)}')
P=D[D.adv_dec==0].pivot_table(index='pid',columns='pos',values='share'); P['reg']=(P.control+P.cycle)/2
ok=P[(P.reg>0)&(P.periphery>0)]; si=1-(lo(ok.periphery)-lo(ok.reg))/L2
print(f'  Bireysel sigma_i (n={len(si)}): medyan {si.median():.3f}, IQR [{si.quantile(.25):.2f}; {si.quantile(.75):.2f}], sigma_i<1 orani {(si<1).mean():.3f}, sigma_i>=0.5 orani {(si>=.5).mean():.3f}')
mp=smf.glm('contribution ~ leaf+centre+cyc+partner_adv+C(block_index)+block_round+C(pid)',x,family=sm.families.Poisson()).fit(cov_type='cluster',cov_kwds={'groups':x.gid})
print(f"  PPML katkinin fiyat esnekligi d ln c/d ln theta = {mp.params.leaf/L2:.3f} (se {mp.bse.leaf/abs(L2):.3f}); CD ongorusu: pay sabit -> leaf katkisi yaklasik 2 kat (esneklik ~ -1)")

print('\n########## 3. H3 / H4: leaf > centre > regular (jeton)')
for k,d in samples.items():
    G=gtab(d); print(f' [{k}]')
    perm(G.periphery-G.center,'leaf - centre'); perm(G.periphery-G.reg,'leaf - regular'); perm(G.center-G.reg,'centre - regular')
    tost(G.periphery-G.center,1,'leaf-centre')
m=smf.ols('contribution ~ leaf+centre+cyc+adv_dec+partner_adv+C(block_index)+block_round+C(pid)',D).fit(cov_type='cluster',cov_kwds={'groups':D.gid})
lc=m.t_test('leaf - centre = 0')
print(f" Birey FE OLS (117, dummy'li): leaf {m.params.leaf:+.3f} (se {m.bse.leaf:.3f}), centre {m.params.centre:+.3f} (se {m.bse.centre:.3f}); leaf-centre {float(lc.effect):+.3f} (p {float(lc.pvalue):.3f}); adv_dec {m.params.adv_dec:+.2f}")
# Star dengesi ongorusu: CD ve CES, B_i regular paydan
Pr=P.reg.clip(1e-3,.999); rows=[]
for s_lab,s in [('CD (sigma=1)',1.0),('CES (sigma_hat)',SIG['blok+tur+partner_adv'])]:
    pred=[]
    for (g,t),dg in D[(D.treatment=='star')&(D.adv_dec==0)].groupby(['gid','round_number']):
        if len(dg)<3 or not all(p in Pr.index for p in dg.pid): continue
        pi={}
        for _,r in dg.iterrows():
            th=0.5 if r.network_role=='center' else 0.25; l=lo(Pr[r.pid])+(1-s)*(np.log(th)-np.log(.5)); pi[r.pid]=1/(1+np.exp(-l))
        c=dg[dg.network_role=='center'].iloc[0]; L=dg[dg.network_role=='periphery']
        # c_C = pi_C(15+0.5(cL1+cL2))/0.5 ; c_Lk = pi_Lk(15+0.75 c_C)/0.25
        A=np.array([[1,-pi[c.pid],-pi[c.pid]],[-3*pi[L.iloc[0].pid],1,0],[-3*pi[L.iloc[1].pid],0,1]]); bvec=np.array([30*pi[c.pid],60*pi[L.iloc[0].pid],60*pi[L.iloc[1].pid]])
        sol=np.clip(np.linalg.solve(A,bvec),0,15)
        pred+= [('center',c.contribution,sol[0]),('periphery',L.iloc[0].contribution,sol[1]),('periphery',L.iloc[1].contribution,sol[2])]
    pr=pd.DataFrame(pred,columns=['pos','obs','pred'])
    for p_,q in pr.groupby('pos'): print(f'  {s_lab} {p_}: gozlenen {q.obs.mean():.2f}, ongorulen {q.pred.mean():.2f}, RMSE {np.sqrt(((q.obs-q.pred)**2).mean()):.2f}')
    pv=pr.pivot_table(index=pr.index//3,columns='pos',values='pred',aggfunc='mean') if False else None

print('\n########## 4. H1: prosocial weight katkiyi artirir mi?')
first=lambda c:(c,'first')
pt=[f'pt_b{i}' for i in range(1,11)]
Q=D.groupby('pid').agg(gid=first('gid'),ses=first('session_code'),inv=first('svy_invalid'),charity=first('charity_d1'),alt1=first('alt_c1'),alt2=first('alt_c2'),gender=first('gender'),s1=first('svo_a1'),s2=first('svo_a2'),s3=first('svo_a3'),**{k:first(k) for k in pt})
R=D[D.adv_dec==0]
W=R.pivot_table(index='pid',columns='pos',values='contribution'); Sh=R.pivot_table(index='pid',columns='pos',values='share')
Q['c']=R.groupby('pid').contribution.mean(); Q['c_first']=R[R.round_number==1].set_index('pid').contribution
Q['Bhat_ctrl']=Sh.control; Q['Bhat']=(Sh.control+Sh.cycle)/2; Q['c_cyc']=W.cycle; Q['c_cen']=W.center; Q['c_leaf']=W.periphery; Q['c_reg']=(W.control+W.cycle)/2
Q=Q[Q.inv==0].copy()
Q['likert']=Q[pt].mean(axis=1); Q['anchor']=(Q.alt1+Q.alt2)/2; Q['svo']=Q[['s1','s2','s3']].isin(['B','C']).sum(axis=1); Q['dict']=Q.charity/100
z=lambda s:(s-s.mean())/s.std()
for v in ['likert','anchor','svo','dict']: Q['z_'+v]=z(Q[v])
Q['composite']=Q[['z_likert','z_anchor','z_svo','z_dict']].mean(axis=1)
sp=lambda a,b:stats.spearmanr(a,b,nan_policy='omit')
print(' 4a. Aciga cikmis B (yalniz Control payi) -> diger agdaki davranis (Spearman)')
for t in ['c_cyc','c_cen','c_leaf']: r_=sp(Q.Bhat_ctrl,Q[t]); print(f'   B_hat(Control) ~ {t}: rho={r_[0]:.3f} p={r_[1]:.4f}')
print(' 4b. Anket/bagis olculeri -> katki (Spearman, Holm duzeltmeli; n=%d)'%Q.c.notna().sum())
res=[]
for v in ['composite','likert','anchor','svo','dict']:
    for t in ['c','c_first','Bhat']:
        r_=sp(Q[v],Q[t]); res.append((v,t,r_[0],r_[1]))
res=pd.DataFrame(res,columns=['olcu','hedef','rho','p']); res['p_holm']=multipletests(res.p,method='holm')[1]; print(res.to_string(index=False))
DD=D.merge(Q[['composite','z_dict','z_likert']],left_on='pid',right_index=True,how='inner')
m=smf.ols('contribution ~ composite+leaf+centre+cyc+adv_dec+partner_adv+C(block_index)+block_round+C(session_code)',DD).fit(cov_type='cluster',cov_kwds={'groups':DD.gid})
print(f"  Panel OLS (oturum FE, grup kumeli): kompozit +1 sd -> {m.params.composite:+.3f} jeton (se {m.bse.composite:.3f}, p {m.pvalues.composite:.3f}); N kisi {DD.pid.nunique()}")
m=smf.ols('contribution ~ z_dict+z_likert+leaf+centre+cyc+adv_dec+partner_adv+C(block_index)+block_round+C(session_code)',DD).fit(cov_type='cluster',cov_kwds={'groups':DD.gid})
print(f"  Ayri ayri: bagis +1 sd {m.params.z_dict:+.3f} (p {m.pvalues.z_dict:.3f}); Likert +1 sd {m.params.z_likert:+.3f} (p {m.pvalues.z_likert:.3f})")

print('\n########## 5. H5: pozisyon x tercih etkilesimi (merkez yalnizca yuksek B esiginin uzerinde leaf\'i gecer)')
D2=D.merge(z(Q.Bhat_ctrl).rename('zB'),left_on='pid',right_index=True,how='left').merge(Q[['composite']],left_on='pid',right_index=True,how='left')
for bv in ['zB','composite']:
    d_=D2.dropna(subset=[bv]); m=smf.ols(f'contribution ~ leaf+centre+cyc+leaf:{bv}+centre:{bv}+adv_dec+partner_adv+C(block_index)+block_round+C(pid)',d_).fit(cov_type='cluster',cov_kwds={'groups':d_.gid})
    t_=m.t_test(f'leaf:{bv} - centre:{bv} = 0')
    print(f"  {bv}: leaf x B {m.params[f'leaf:{bv}']:+.3f} (p {m.pvalues[f'leaf:{bv}']:.3f}); centre x B {m.params[f'centre:{bv}']:+.3f} (p {m.pvalues[f'centre:{bv}']:.3f}); fark {float(t_.effect):+.3f} (p {float(t_.pvalue):.3f})  [H5: centre x B > leaf x B]")
Q['lc']=Q.c_leaf-Q.c_cen; r_=sp(Q.lc,Q.Bhat_ctrl); print(f'  Kisi duzeyi leaf-centre ~ B_hat(Control): rho={r_[0]:.3f} p={r_[1]:.3f}; ~ kompozit: rho={sp(Q.lc,Q.composite)[0]:.3f} p={sp(Q.lc,Q.composite)[1]:.3f}')
# odds esigi: odds(pi_C)/odds(pi_L) > theta_C/theta_L = 2  -> centre katkisi leaf'i gecer
oc=Sh.center/(1-Sh.center); ol=Sh.periphery/(1-Sh.periphery); orr=(oc/ol).replace([np.inf,-np.inf],np.nan).dropna()
above=orr>2; dd=(W.center-W.periphery).reindex(orr.index)
print(f'  Odds esigi (Ch2 eq. ces_threshold): odds orani >2 olan kisi {above.sum()}/{len(orr)}; bu kisilerde centre>leaf orani {(dd[above]>0).mean():.2f}, digerlerinde {(dd[~above]>0).mean():.2f} (mekanik iliski; yalniz tutarlilik kontrolu)')

print('\n########## 6. RQ3: social efficiency (SE) ag turune gore')
# SE kazanci: Control/Cycle her jeton 0,5; Star'da centre jetonu 1,0, leaf jetonu 0,25. Normalize: (SE-45)/22,5
def se_gain(r): return np.where(r.pos=='center',1.0,np.where(r.pos=='periphery',0.25,0.5))*r.contribution
D['seg']=se_gain(D); E=D.groupby(['gid','treatment','round_number']).seg.sum().div(22.5).groupby(['gid','treatment']).mean().unstack()
print('  Normalize etkinlik ortalamasi:',E.mean().round(3).to_dict())
perm(E.star-E.control,'Star - Control etkinlik'); perm(E.cycle-E.control,'Cycle - Control etkinlik')
print('  Friedman p =',round(stats.friedmanchisquare(E.control,E.cycle,E.star).pvalue,3))
st=D[D.treatment=='star']; tot=st.groupby(['gid','round_number']).contribution.sum()
cs=st[st.pos=='center'].set_index(['gid','round_number']).contribution
print(f'  Star: centre\'in grup katkisindaki payi {(cs/tot).mean():.3f} (esit dagilimda 1/3). Ayni toplam katki esit dagilsaydi etkinlik {(tot*(1+0.5)/3/22.5).groupby("gid").mean().mean():.3f}; tum katki centre\'da olsaydi {(tot.clip(upper=15)*1.0+(tot-15).clip(lower=0)*0.25).div(22.5).groupby("gid").mean().mean():.3f}')

print('\n########## 7. Strategic complementarity ve dinamik')
D=D.sort_values(['pid','round_number'])
D['obs_oth']=(D.neighborhood_total_contribution-D.contribution)/(D.neighborhood_size-1)
D['lag_obs']=D.groupby('pid').obs_oth.shift(); D['lag_c']=D.groupby('pid').contribution.shift(); D['lag_adv']=D.groupby('pid').adv_dec.shift()
dy=D[(D.block_round>1)]
for lab,f in [('FE (alt sinir)','contribution ~ lag_obs+lag_c+adv_dec+partner_adv+lag_adv+block_round+C(block_index)+C(pid)'),('Pooled OLS (ust sinir)','contribution ~ lag_obs+lag_c+adv_dec+partner_adv+lag_adv+block_round+C(block_index)')]:
    m=smf.ols(f,dy).fit(cov_type='cluster',cov_kwds={'groups':dy.gid}); print(f'  {lab}: gorulen komsu ort. (t-1) {m.params.lag_obs:.3f} (se {m.bse.lag_obs:.3f}, p {m.pvalues.lag_obs:.4f})')
for p_ in ['reg','center','periphery']:
    dq=dy[(dy.pos.isin(['control','cycle']) if p_=='reg' else dy.pos==p_)]
    m=smf.ols('contribution ~ lag_obs+adv_dec+partner_adv+lag_adv+block_round+C(pid)',dq).fit(cov_type='cluster',cov_kwds={'groups':dq.gid}); print(f'   pozisyon {p_}: egim {m.params.lag_obs:.3f} (se {m.bse.lag_obs:.3f}, p {m.pvalues.lag_obs:.3f})')
dy=dy.assign(dc=dy.contribution-dy.lag_c,gap=dy.lag_obs-dy.lag_c); dy=dy.assign(up=dy.gap.clip(lower=0),down=dy.gap.clip(upper=0))
m=smf.ols('dc ~ up+down+adv_dec+lag_adv+partner_adv',dy[(dy.adv_dec==0)&(dy.lag_adv==0)]).fit(cov_type='cluster',cov_kwds={'groups':dy[(dy.adv_dec==0)&(dy.lag_adv==0)].gid})
print(f'  Asimetrik tepki: digerleri fazla verdiyse artirma {m.params.up:.3f} (se {m.bse.up:.3f}); az verdiyse kisma {m.params.down:.3f} (se {m.bse.down:.3f}); esitlik p={float(m.t_test("up - down = 0").pvalue):.4f}')
Gr=D[D.adv_dec==0].groupby(['gid','block_index','block_round']).contribution.mean()
for k in [2,3]:
    v=(Gr.xs((k,1),level=[1,2])-Gr.xs((k-1,6),level=[1,2])); perm(v,f'Restart: {k}. blok basi - {k-1}. blok sonu')
mm=smf.mixedlm('contribution ~ leaf+centre+cyc+C(block_index)+block_round+adv_dec+partner_adv',D,groups='gid',re_formula='1',vc_formula={'pid':'0+C(pid)'}).fit()
vg=mm.cov_re.iloc[0,0]; vp=mm.vcomp[0]; ve=mm.scale; tot=vg+vp+ve
print(f'  Varyans ayristirmasi: gruplar arasi {vg/tot:.1%}, grup ici kisiler arasi {vp/tot:.1%}, artik {ve/tot:.1%}')

print('\n########## 8. Olcum eki: guvenilirlik ve yakinsak gecerlilik (anketi gecerli %d kisi)'%len(Q))
X=Q[pt]; k=10; alpha=k/(k-1)*(1-X.var().sum()/X.sum(axis=1).var()); ev=np.sort(np.linalg.eigvalsh(X.corr().values))[::-1]
print(f'  Likert Cronbach alfa {alpha:.3f}; ozdegerler {ev[:4].round(2)} (ilk bilesen payi {ev[0]/10:.3f}; Kaiser >1 olan {int((ev>1).sum())})')
C4=Q[['z_likert','z_anchor','z_svo','z_dict']]; a4=4/3*(1-C4.var().sum()/C4.sum(axis=1).var()); print(f'  4 kanalli kompozit alfa {a4:.3f}')
cv=[]
for a,b in itertools.combinations(['likert','anchor','svo','dict'],2):
    r_=sp(Q[a],Q[b]); cv.append((a,b,r_[0],r_[1]))
cv=pd.DataFrame(cv,columns=['a','b','rho','p']); cv['p_holm']=multipletests(cv.p,method='holm')[1]; print(cv.to_string(index=False))
ev4,vec4=np.linalg.eigh(C4.corr().values); pc1=C4.values@vec4[:,-1]; pc1*=np.sign(np.corrcoef(pc1,Q.composite)[0,1])
print(f'  Kompozit saglamligi (~ ort. katki): esit agirlik rho={sp(Q.composite,Q.c)[0]:.3f} (p {sp(Q.composite,Q.c)[1]:.3f}); PC1 rho={sp(pc1,Q.c)[0]:.3f} (p {sp(pc1,Q.c)[1]:.3f})', end='')
for drop in ['z_likert','z_anchor','z_svo','z_dict']:
    cc=C4.drop(columns=drop).mean(axis=1); print(f'; -{drop[2:]} rho={sp(cc,Q.c)[0]:.3f}',end='')
print()
print('  Tavan: bagis=100 orani %.3f; Likert ort %.2f/7; anchor ort %.2f/10; SVO 3/3 prosocial-veya-ustu orani %.3f'%((Q.charity==100).mean(),Q.likert.mean(),Q.anchor.mean(),(Q.svo==3).mean()))
print('  SVO secenek C (Siz 15 - Digeri 85 vb.) secilme sayisi:',int((Q[['s1','s2','s3']]=='C').sum().sum()),'(C altruistic secenek; tez metnindeki "competitive" ifadesiyle uyusmuyor)')

print('\n########## 9. Ornek disi replikasyon: 19 Kasim oturumlari (33 kisi, 11 grup) vs onceki 84 kisi')
for lab,d in [('onceki 84',D[D.new19==0]),('yeni 33 (19 Kasim)',D[D.new19==1])]:
    G=gtab(d); S=gtab(d,'share'); r=d[d.adv_dec==0]
    print(f' [{lab}] {len(G)} grup; ort katki {r.contribution.mean():.2f}; sifir {(r.contribution==0).mean():.3f}; cycle-control {(G.cycle-G.control).mean():+.2f}; leaf-centre {(G.periphery-G.center).mean():+.2f}; share leaf<regular {int((S.periphery<S.reg).sum())}/{len(S)}; ilk3->son3 {r[r.round_number<=3].contribution.mean():.2f}->{r[r.round_number>=16].contribution.mean():.2f}')
xn=x[x.new19==1]; mm=smf.glm('share ~ leaf+centre+cyc+C(block_index)+block_round+C(pid)',xn,family=sm.families.Binomial()).fit(cov_type='cluster',cov_kwds={'groups':xn.gid})
print(f'  Yeni oturumlarda sigma_hat = {1-mm.params.leaf/L2:.3f} (se {mm.bse.leaf/abs(L2):.3f})')
Go=gtab(D[D.new19==0]); Gn=gtab(D[D.new19==1])
for lab,f in [('ort katki',lambda G:G[['control','cycle','center','periphery']].mean(axis=1)),('leaf-centre',lambda G:G.periphery-G.center)]:
    print(f'  {lab} fark testi (grup duzeyi Mann-Whitney): p={stats.mannwhitneyu(f(Go),f(Gn)).pvalue:.3f}')

print('\n########## 10. Guc (39 grup, %80 guc, alfa 0,05, grup duzeyi eslestirilmis fark)')
G=gtab(D)
for lab,v in [('leaf-centre',G.periphery-G.center),('centre-regular',G.center-G.reg),('leaf-regular',G.periphery-G.reg),('cycle-control',G.cycle-G.control)]:
    sd=v.std(ddof=1); mde=lambda n:(stats.norm.ppf(.975)+stats.norm.ppf(.8))*sd/np.sqrt(n)
    need=lambda dlt:int(np.ceil(((stats.norm.ppf(.975)+stats.norm.ppf(.8))*sd/dlt)**2))
    print(f'  {lab}: gozlenen {v.mean():+.2f}, grup sd {sd:.2f}, MDE(39) {mde(39):.2f}, MDE(60) {mde(60):.2f}; 0,5 jeton icin {need(.5)} grup, 1 jeton icin {need(1)} grup')
print(f'  Korelasyon: n=113 ile %80 guc saptanabilir rho ~ {np.tanh((stats.norm.ppf(.975)+stats.norm.ppf(.8))/np.sqrt(113-3)):.3f}')
