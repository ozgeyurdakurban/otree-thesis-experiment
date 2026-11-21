# sigma -> 0, lambda = 0 (Leontief: X_i = k_i * c_i) altinda Star ongorusu. k_i kisinin Control/Cycle davranisindan.
# Analitik gozlem: herkes ayni c verdiginde X_i = e - c + (beta/d_i)*d_i*c = e + (beta-1)c, d_i'den bagimsiz -> ortak k icin denge her pozisyonda ayni c.
import pandas as pd, numpy as np
D=pd.read_pickle('D117.pkl'); R=D[D.adv_dec==0]
reg=R[R.pos.isin(['control','cycle'])]
X=(reg.W-(1-reg.mp)*reg.contribution).groupby(reg.pid).mean(); C=reg.groupby('pid').contribution.mean()
k=(X/C).replace(np.inf,1e6)
print('k_i (X/c, Control+Cycle): medyan %.2f, ceyrekler %.2f-%.2f'%(k.median(),k.quantile(.25),k.quantile(.75)))
out=[]
for (g,t),dg in R[R.treatment=='star'].groupby(['gid','round_number']):
    if len(dg)<3 or not all(p in k.index for p in dg.pid): continue
    c=dg[dg.network_role=='center'].iloc[0]; L=dg[dg.network_role=='periphery']
    kc,k1,k2=k[c.pid],k[L.iloc[0].pid],k[L.iloc[1].pid]
    # c_C(0.5+kc) = 15 + 0.5(c1+c2) ; c_j(0.25+kj) = 15 + 0.75 c_C
    A=np.array([[0.5+kc,-0.5,-0.5],[-0.75,0.25+k1,0],[-0.75,0,0.25+k2]]); s=np.clip(np.linalg.solve(A,[15,15,15]),0,15)
    out+=[('center',c.contribution,s[0],(0.5*s[0])/(15+0.5*(s[1]+s[2]))),('periphery',L.iloc[0].contribution,s[1],0.25*s[1]/(15+0.75*s[0])),('periphery',L.iloc[1].contribution,s[2],0.25*s[2]/(15+0.75*s[0]))]
o=pd.DataFrame(out,columns=['pos','obs','pred','pred_share'])
obs_share=R[R.treatment=='star'].groupby('pos').share.mean()
for p,q in o.groupby('pos'): print(f'Leontief {p}: gozlenen {q.obs.mean():.2f}, ongorulen {q.pred.mean():.2f}, RMSE {np.sqrt(((q.obs-q.pred)**2).mean()):.2f} | share gozlenen {obs_share[p]:.3f}, ongorulen {q.pred_share.mean():.3f}')
print('Karsilastirma (02_cikti): CD RMSE centre 4.22 / leaf 6.12; CES(sigma_hat) RMSE centre 3.66 / leaf 3.13')
