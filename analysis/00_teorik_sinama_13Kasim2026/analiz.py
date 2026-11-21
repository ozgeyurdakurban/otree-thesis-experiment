"""Independent, read-only theory checks. Requires bundled numpy/pandas/openpyxl.
Run from any working directory. Inputs are never overwritten.
Inference unit is session x group. This is exploratory, not preregistered.
"""
from pathlib import Path
import json, math, itertools
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
rng = np.random.default_rng(20261113)
SIGN_CACHE={}

def save_json(obj, name):
    (OUT/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2,
        default=lambda x: x.item() if isinstance(x,np.generic) else str(x)), encoding='utf-8')

# Student t CDF via continued fraction for regularized incomplete beta.
def betacf(a,b,x):
    qab=a+b; qap=a+1; qam=a-1; c=1.; d=1-qab*x/qap
    d=1/max(d,1e-300); h=d
    for m in range(1,301):
        aa=m*(b-m)*x/((qam+2*m)*(a+2*m))
        d=1+aa*d; d=d if abs(d)>1e-300 else 1e-300
        c=1+aa/c; c=c if abs(c)>1e-300 else 1e-300
        d=1/d; h*=d*c
        aa=-(a+m)*(qab+m)*x/((a+2*m)*(qap+2*m))
        d=1+aa*d; d=d if abs(d)>1e-300 else 1e-300
        c=1+aa/c; c=c if abs(c)>1e-300 else 1e-300
        d=1/d; delta=d*c; h*=delta
        if abs(delta-1)<3e-14: break
    return h

def ibeta(a,b,x):
    if x<=0: return 0.
    if x>=1: return 1.
    bt=math.exp(math.lgamma(a+b)-math.lgamma(a)-math.lgamma(b)+a*math.log(x)+b*math.log1p(-x))
    return bt*betacf(a,b,x)/a if x<(a+1)/(a+b+2) else 1-bt*betacf(b,a,1-x)/b

def tcdf(t,df):
    q=.5*ibeta(df/2,.5,df/(df+t*t))
    return 1-q if t>=0 else q

def tq(p,df):
    lo,hi=-100.,100.
    for _ in range(80):
        m=(lo+hi)/2
        if tcdf(m,df)<p: lo=m
        else: hi=m
    return (lo+hi)/2

assert abs(tcdf(1,1)-.75)<1e-10
assert abs(tq(.975,17)-2.1098155778)<1e-7

def paired(v):
    v=np.asarray(v,float); n=len(v); mean=v.mean(); se=v.std(ddof=1)/np.sqrt(n)
    t=mean/se if se else 0.; crit=tq(.975,n-1)
    if n not in SIGN_CACHE:
        SIGN_CACHE[n]=(2*((np.arange(2**n,dtype=np.uint32)[:,None]>>np.arange(n,dtype=np.uint32))&1).astype(np.int8)-1)
    signs=SIGN_CACHE[n]
    sf=float((np.abs(signs@v/n)>=abs(mean)-1e-12).mean())
    nz=v[v!=0]; k=int((nz>0).sum()); nn=len(nz)
    signp=min(1.,2*sum(math.comb(nn,j) for j in range(min(k,nn-k)+1))/2**nn)
    return dict(n=n,mean=mean,se=se,ci_low=mean-crit*se,ci_high=mean+crit*se,
                p_t=2*tcdf(-abs(t),n-1),p_signflip=sf,p_sign=signp,positive=k,negative=nn-k)

def prep(df):
    d=df.copy(); d['pid']=d.session_code+'_'+d.participant_code
    d['gid']=d.session_code+'_'+d.group_no.astype(str)
    d['pos']=np.where(d.treatment=='star',d.network_role,d.treatment)
    d['S']=d.neighborhood_total_contribution-d.contribution
    d['mp']=1.5/d.neighborhood_size; d['theta']=1-d.mp
    d['W']=15+d.mp*d.S; d['share']=d.theta*d.contribution/d.W
    return d

sets={k:prep(v) for k,v in pd.read_excel(ROOT/'tüm_veri.xlsx',sheet_name=None).items()}
all_d=list(sets.values())[0]; d=list(sets.values())[2]
summary={}; tests=[]
for name,x in sets.items():
    summary[name]=dict(rows=len(x),people=x.pid.nunique(),groups=x.gid.nunique(),
        zero=(x.contribution==0).mean(),full=(x.contribution==15).mean(),
        duplicate_person_round=int(x.duplicated(['pid','round_number']).sum()),
        max_payoff_error=float((15-x.contribution+x.mp*x.neighborhood_total_contribution-x.round_payoff_points).abs().max()))
    for field in ['contribution','share']:
        g=x.pivot_table(index='gid',columns='pos',values=field); g['regular']=(g.control+g.cycle)/2
        for a,b in [('cycle','control'),('periphery','center'),('periphery','regular'),('center','regular')]:
            tests.append(dict(sample=name,field=field,contrast=a+'-'+b,**paired(g[a]-g[b])))
pd.DataFrame(tests).to_csv(OUT/'grup_testleri.csv',index=False,encoding='utf-8-sig')
desc=d.groupby('pos').agg(n=('contribution','size'),mean=('contribution','mean'),sd=('contribution','std'),share=('share','mean'))
desc.to_csv(OUT/'betimsel.csv',encoding='utf-8-sig')

# Verify source rows against all four actual-session oTree exports.
raw_checks=[]
for f in (ROOT/'sessions').glob('gerçek_*/otree_ciktilari/*_network_within.csv'):
    raw=pd.read_csv(f)
    rr=raw.rename(columns={'session.code':'session_code','participant.code':'participant_code',
        'subsession.round_number':'round_number','player.contribution':'raw_contribution',
        'player.payoff':'raw_payoff'})
    joined=all_d.merge(rr[['session_code','participant_code','round_number','raw_contribution','raw_payoff']],
        on=['session_code','participant_code','round_number'],how='inner',validate='one_to_one')
    raw_checks.append(dict(file=f.name,rows=len(raw),matched=len(joined),
        contribution_mismatch=int((joined.contribution!=joined.raw_contribution).sum()),
        max_payoff_difference=float((joined.round_payoff_points-joined.raw_payoff).abs().max())))
summary['raw_exports']=raw_checks
summary['set3_integrity']=dict(group_round_sizes=d.groupby(['gid','round_number']).size().value_counts().to_dict(),
    rounds_per_person=d.groupby('pid').size().value_counts().to_dict(),
    center_rounds=d[d.pos=='center'].groupby('pid').size().value_counts().to_dict(),
    advanced=int(d.contribution_advanced.sum()))

# Fixed-person-effects OLS, group CR1, t inference with G-1 df.
def fe_fit(x,ycol,additional=None):
    labels=['leaf','center','cycle','block2','block3','block_round']
    X=np.column_stack([(x.pos=='periphery')*1.,(x.pos=='center')*1.,(x.pos=='cycle')*1.,
            (x.block_index==2)*1.,(x.block_index==3)*1.,x.block_round.astype(float)])
    if additional:
        for key in additional: X=np.column_stack([X,x[key].values]); labels.append(key)
    y=x[ycol].to_numpy(dtype=float,copy=True)
    pids=x.pid.to_numpy(); gids=x.gid.to_numpy()
    for p in np.unique(pids):
        z=pids==p; X[z]-=X[z].mean(axis=0); y[z]-=y[z].mean()
    inv=np.linalg.pinv(X.T@X); b=inv@X.T@y; resid=y-X@b
    meat=np.zeros((X.shape[1],X.shape[1])); ug=np.unique(gids)
    for g in ug:
        z=gids==g; score=X[z].T@resid[z]; meat+=np.outer(score,score)
    n=len(x); k=len(labels)+x.pid.nunique()
    V=inv@meat@inv*len(ug)/(len(ug)-1)*(n-1)/(n-k)
    se=np.sqrt(np.maximum(0,np.diag(V))); crit=tq(.975,len(ug)-1)
    return [dict(outcome=ycol,term=l,beta=b[j],se=se[j],ci_low=b[j]-crit*se[j],ci_high=b[j]+crit*se[j],
        p=2*tcdf(-abs(b[j]/se[j]),len(ug)-1)) for j,l in enumerate(labels)]

fe=[]
for label,x in [('all',d),('last3_per_block',d[d.block_round>=4]),('interior_only',d[d.contribution.between(1,14)])]:
    for y in ['contribution','share']:
        fe.extend([dict(sample=label,**r) for r in fe_fit(x,y)])
pd.DataFrame(fe).to_csv(OUT/'birey_sabit_etki.csv',index=False,encoding='utf-8-sig')

# Sensitivity of share restrictions to assumed information/beliefs.
# Current realized neighbour contributions are not information available at choice time.
sens=[]
for label,x in [('all',d),('late',d[d.block_round>=4]),('first_block_star',d[d.block_index==1])]:
    gp=x.pivot_table(index='gid',columns='pos',values='share')
    if {'control','cycle','periphery'}.issubset(gp.columns):
        gp['regular']=gp[['control','cycle']].mean(axis=1)
        v=(gp.periphery-gp.regular).dropna()
        if len(v): sens.append(dict(spec=label,**paired(v)))
lag=d.sort_values(['pid','round_number']).copy()
lag['S_lag']=lag.groupby(['pid','block_index']).S.shift(1)
lag['own_lag']=lag.groupby(['pid','block_index']).contribution.shift(1)
lag['lag_group_total']=lag.groupby(['gid','round_number']).own_lag.transform('sum')
lagcenter=lag[lag.pos=='center'].set_index(['gid','round_number']).own_lag
lag['lag_current_center']=pd.MultiIndex.from_frame(lag[['gid','round_number']]).map(lagcenter)
lag['S_current_neighbors_lag']=np.where(lag.pos=='periphery',lag.lag_current_center,lag.lag_group_total-lag.own_lag)
lag.loc[lag.block_round==1,'S_current_neighbors_lag']=np.nan
lag['others_mean_lag']=lag.groupby(['pid','block_index']).apply(
    lambda q:(q.S/(q.neighborhood_size-1)).shift(1),include_groups=False).reset_index(level=[0,1],drop=True)
for name,S in [('previous_neighborhood_total',lag.S_lag),('current_neighbors_previous_contributions',lag.S_current_neighbors_lag),('lag_mean_times_current_degree',lag.others_mean_lag*(lag.neighborhood_size-1)),('zero_expected_inflow',pd.Series(0.,index=lag.index))]:
    q=lag[S.notna()].copy(); q['share_alt']=q.theta*q.contribution/(15+q.mp*S.loc[q.index])
    g=q.pivot_table(index='gid',columns='pos',values='share_alt'); g['regular']=(g.control+g.cycle)/2
    sens.append(dict(spec=name,**paired(g.periphery-g.regular)))
pd.DataFrame(sens).to_csv(OUT/'pay_duyarlilik.csv',index=False,encoding='utf-8-sig')
lag['neighbor_mean_lag']=lag.S_current_neighbors_lag/(lag.neighborhood_size-1)
dyn=lag[lag.own_lag.notna() & lag.neighbor_mean_lag.notna()].copy()
dynamic=fe_fit(dyn,'contribution',['own_lag','neighbor_mean_lag'])
pd.DataFrame(dynamic).to_csv(OUT/'dinamik_iliskiler.csv',index=False,encoding='utf-8-sig')

# Out-of-group validation of constrained CES, calibrated only on each person's
# Control/Cycle share. Structural sigma/lambda selected using OTHER groups' Star.
# B is not held equal to the CD share when sigma != 1: invert CES share instead.
P=d.pivot_table(index='pid',columns='pos',values='share'); pref=((P.control+P.cycle)/2).clip(1e-5,1-1e-5)
preg=d[d.treatment!='star'].groupby('pid').contribution.mean()
pids=sorted(d.pid.unique()); piidx={p:i for i,p in enumerate(pids)}
logodds=np.log(pref.loc[pids].values/(1-pref.loc[pids].values))
configs=[]
for (gid,r),q in d[d.treatment=='star'].groupby(['gid','round_number']):
    q=q.sort_values('id_in_group'); idx=np.array([piidx[p] for p in q.pid]); center=(q.pos=='center').values
    configs.append((gid,idx,center,q.contribution.to_numpy(float)))
idx=np.stack([q[1] for q in configs]); center=np.stack([q[2] for q in configs]); cg=np.array([q[0] for q in configs])
theta=np.where(center,.5,.25); mp=1-theta
A=np.zeros((len(configs),3,3))
for k in range(len(configs)):
    for i in range(3):
        for j in range(3): A[k,i,j]=int(i!=j and (center[k,i] or center[k,j]))
obs=np.stack([q[3] for q in configs]); groupids=np.unique(cg)
weights=np.ones_like(obs)
paircode=(idx*2+center.astype(int)).ravel()
paircount=np.bincount(paircode,minlength=len(pids)*2)
assert np.all(paircount>0)
obsavg=np.bincount(paircode,weights=obs.ravel(),minlength=len(pids)*2)/paircount
person_group=d.drop_duplicates('pid').set_index('pid').gid.loc[pids].to_numpy()
pairgroup=np.repeat(person_group,2)

def equilibrium(shares):
    c=np.zeros_like(shares)
    for _ in range(2500):
        nc=np.minimum(15,shares/theta*(15+mp*np.einsum('kij,kj->ki',A,c)))
        if np.max(np.abs(nc-c))<1e-10: break
        c=nc
    residual=np.max(np.abs(nc-np.minimum(15,shares/theta*(15+mp*np.einsum('kij,kj->ki',A,nc)))))
    if residual>1e-7: raise ValueError('Equilibrium not converged')
    return nc

def shares_for(sig,lam):
    pK=.5/(1+lam); ppos=theta/(1+lam*np.where(center,1.5,.5))
    eta=logodds[idx]+(1-sig)*np.log(ppos/pK)
    return 1/(1+np.exp(-np.clip(eta,-700,700)))

# Independent analytical benchmarks for the bounded solver.
bench=equilibrium(np.full_like(theta,.1))
assert np.max(np.abs(bench[center]-4.468085106382979))<1e-7
assert np.max(np.abs(bench[~center]-7.340425531914893))<1e-7
assert np.max(np.abs(equilibrium(np.full_like(theta,.9))-15))<1e-7

sigmas=np.array([.001,.005,.01,.025,.05,.1,.2,.35,.5,.75,1.,1.25,1.5,2.,3.,5.])
lambdas=np.array([0.,.1,.25,.5,1.,2.,4.,10.,100.])
grid=[]; predictions=[]; scores=[]
for sig in sigmas:
    for lam in lambdas:
        pred=equilibrium(shares_for(sig,lam)); predictions.append(pred)
        predavg=np.bincount(paircode,weights=pred.ravel(),minlength=len(pids)*2)/paircount
        loss=np.array([np.mean((predavg[pairgroup==g]-obsavg[pairgroup==g])**2) for g in groupids])
        scores.append(loss); grid.append(dict(sigma=sig,lambda_=lam,rmse=np.sqrt(loss.mean())))
grid=pd.DataFrame(grid); predictions=np.stack(predictions); scores=np.stack(scores)
grid.to_csv(OUT/'ces_profil.csv',index=False,encoding='utf-8-sig')
best=int(np.argmin(scores.mean(axis=1))); cvpred=np.zeros_like(obs); selected=[]
for j,g in enumerate(groupids):
    train=np.arange(len(groupids))!=j; pick=int(np.argmin(scores[:,train].mean(axis=1)))
    cvpred[cg==g]=predictions[pick,cg==g]
    selected.append(dict(heldout_group=g,**grid.iloc[pick].to_dict()))
pd.DataFrame(selected).to_csv(OUT/'ces_disarida_birakilan_grup.csv',index=False,encoding='utf-8-sig')
cd=equilibrium(shares_for(1.,0.)); baseline=preg.loc[np.array(pids)[idx].ravel()].values.reshape(idx.shape)
models={'CD':cd,'CES_group_holdout':cvpred,'CES_in_sample':predictions[best],'same_own_regular_contribution':baseline}
predrows=[]; modelrows=[]
for model,pred in models.items():
    for k,(gid,ii,cc,_) in enumerate(configs):
        for j,p in enumerate(ii): predrows.append(dict(model=model,gid=gid,pid=pids[p],role='center' if cc[j] else 'periphery',observed=obs[k,j],predicted=pred[k,j]))
pr=pd.DataFrame(predrows); pp=pr.groupby(['model','gid','pid','role'])[['observed','predicted']].mean().reset_index()
for model,q in pp.groupby('model'):
    for role,z in [('all',q),*list(q.groupby('role'))]:
        modelrows.append(dict(model=model,role=role,n=len(z),rmse=np.sqrt(np.mean((z.predicted-z.observed)**2)),mae=np.mean(np.abs(z.predicted-z.observed)),predicted_mean=z.predicted.mean(),observed_mean=z.observed.mean()))
pd.DataFrame(modelrows).to_csv(OUT/'model_ongoru.csv',index=False,encoding='utf-8-sig')
pp.to_csv(OUT/'bireysel_ongoru.csv',index=False,encoding='utf-8-sig')
losses=pp.assign(sq=lambda q:(q.predicted-q.observed)**2).groupby(['gid','model']).sq.mean().unstack()
modeltests={}
for a,b in [('CD','same_own_regular_contribution'),('CD','CES_group_holdout'),('CES_group_holdout','same_own_regular_contribution')]:
    modeltests[a+' minus '+b]=paired(losses[a]-losses[b])

# Proper one-step best response: compare out-of-treatment calibrated CD against
# choices using either realized contemporaneous inflows or lagged beliefs.
brrows=[]
for inflow,q,S in [('realized',d,d.S),('lagged_current_neighbors',lag[lag.S_current_neighbors_lag.notna()],lag.loc[lag.S_current_neighbors_lag.notna(),'S_current_neighbors_lag'])]:
    star=q[q.treatment=='star'].copy(); star['pred']=np.minimum(15,pref.loc[star.pid].values/star.theta*(15+star.mp*S.loc[star.index]))
    v=star.groupby('gid').apply(lambda z:(z.pred-z.contribution).mean(),include_groups=False)
    brrows.append(dict(inflow=inflow,**paired(v)))
pd.DataFrame(brrows).to_csv(OUT/'cd_en_iyi_tepki.csv',index=False,encoding='utf-8-sig')

# External preference proxy and time dynamics: descriptive associations only.
people=d.drop_duplicates('pid').set_index('pid'); mean_c=d.groupby('pid').contribution.mean()
def spearman(a,b): return float(pd.Series(np.asarray(a)).rank().corr(pd.Series(np.asarray(b)).rank()))
proxy=dict(charity_mean=float(people.charity_d1.mean()),charity_full=float((people.charity_d1==100).mean()),
    charity_contribution_spearman=spearman(people.charity_d1,mean_c.loc[people.index]),
    dictator_minus_regular_share=float((people.charity_d1/100-pref.loc[people.index]).mean()))
proxy['charity_individuals']=int(len(people))
time=dict(first3=d[d.round_number<=3].contribution.mean(),last3=d[d.round_number>=16].contribution.mean(),
    zero_first=(d[d.round_number==1].contribution==0).mean(),zero_last=(d[d.round_number==18].contribution==0).mean())

# Compare each group's early and late contributions, and efficiency differences.
early=d[d.round_number<=3].groupby('gid').contribution.mean(); late=d[d.round_number>=16].groupby('gid').contribution.mean()
time['late_minus_early']=paired(late-early)
gt=d.groupby(['gid','round_number','treatment']).round_payoff_points.sum().reset_index()
gt['efficiency']=(gt.round_payoff_points-45)/22.5
ef=gt.pivot_table(index='gid',columns='treatment',values='efficiency')
efficiency={'means':ef.mean().to_dict(),'star_minus_control':paired(ef.star-ef.control)}
regdiff=d.pivot_table(index='gid',columns='pos',values='contribution')
v=regdiff.cycle-regdiff.control; se=v.std(ddof=1)/np.sqrt(len(v))
tost=max(1-tcdf((v.mean()+1)/se,len(v)-1),tcdf((v.mean()-1)/se,len(v)-1))

# Inversion diagnostics: small sigma implies extreme B, not a literal sigma=0 fit.
bdiagnostics=[]
for sig in [.001,.01,.05,.1,.5,1.]:
    eta=(logodds-(1-sig)*np.log(.5))/sig
    B=1/(1+np.exp(-np.clip(eta,-700,700)))
    bdiagnostics.append(dict(sigma=sig,median_B=float(np.median(B)),min_B=float(B.min()),max_B=float(B.max())))
save_json(dict(sample=summary,tests=tests,fe=fe,sensitivity=sens,dynamic=dynamic,model_comparison=modelrows,
    model_loss_tests=modeltests,grid_best=grid.iloc[best].to_dict(),proxy=proxy,time=time,
    efficiency=efficiency,tost_margin_1=float(tost),B_inversion=bdiagnostics,
    limitations=['Exploratory; no preregistration','18 independent groups; individuals and rounds are dependent',
    'Sign-flip p values assume symmetric paired differences, not design-exact randomization inference',
    'CES comparison assumes common sigma/lambda and invariant person-specific preferences',
    'Control/Cycle realized shares calibrate person preferences; they are not independently elicited preferences',
    'Current realized inflows assume equilibrium/perfect expectations; lagged inflows are only a sensitivity case',
    'Grid minima at boundaries do not identify the boundary as a true parameter',
    'CES leave-one-group-out predicts held-out Star using that group\u2019s own regular behavior',
    'Prediction-loss tests are descriptive for CES because group-held-out training sets overlap']), 'sonuclar.json')
print('SET3',summary[list(sets)[2]])
print(desc.to_string())
print('GROUP TESTS',pd.DataFrame(tests).query('sample==@list(sets)[2]') if False else pd.DataFrame(tests).tail(8).to_string(index=False))
print('FE',pd.DataFrame(fe).query("sample=='all'").to_string(index=False))
print('MODEL',pd.DataFrame(modelrows).to_string(index=False))
print('BEST GRID',grid.iloc[best].to_dict())
print('MODEL LOSS TESTS',modeltests)
print('SENSITIVITY',sens)
print('PROXY',proxy,'TIME',time,'EFFICIENCY',efficiency,'TOST',tost)
print('B INVERSION',bdiagnostics)
print('SAVED',OUT)
