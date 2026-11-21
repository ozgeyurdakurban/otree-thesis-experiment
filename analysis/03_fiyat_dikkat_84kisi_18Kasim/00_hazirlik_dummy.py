# 84 kisi, kimse cikarilmadi; ilerletme dummy'leri turetiliyor
import pandas as pd, numpy as np, glob
D=pd.read_pickle('../02_analiz_84kisi_17Kasim/D.pkl').copy()
D['adv_dec']=D.contribution_advanced.astype(int)                 # karar ilerletildi (69)
D['adv_grp']=(1-D.veri_seti_3).astype(int)                         # ilerletilen grup (2 grup, 6 kisi)
D['partner_adv']=((D.groupby(['gid','round_number']).adv_dec.transform('sum')-D.adv_dec)>0).astype(int)
D['leaf']=(D.pos=='periphery')*1; D['centre']=(D.pos=='center')*1; D['cyc']=(D.pos=='cycle')*1
so=D[D.treatment=='star'].groupby('gid').block_index.first().rename('star_order'); D=D.join(so,on='gid')
# karar sureleri
fs=glob.glob('../../experiment_data/sessions/gerçek_*/otree_ciktilari/*PageTimes*.csv')
pt=pd.concat([pd.read_csv(f) for f in fs]).drop_duplicates().sort_values(['participant_code','epoch_time_completed'])
pt['dur']=pt.groupby('participant_code').epoch_time_completed.diff()
ct=pt[pt.page_name=='Contribution'][['session_code','participant_code','round_number','dur']]
D=D.merge(ct,on=['session_code','participant_code','round_number'],how='left')
D['ldur']=np.log(D.dur.clip(lower=1))
# kisinin Control+Cycle'daki ortalama log suresi (Star'dan once/bagimsiz olculen "dusunme tipi"), standartlastirilmis
reg=D[(D.treatment!='star')&(D.adv_dec==0)].groupby('pid').ldur.mean()
D=D.join(((reg-reg.mean())/reg.std()).rename('delib'),on='pid')
D.to_pickle('D84.pkl')
print('N',D.pid.nunique(),'grup',D.gid.nunique(),'karar',len(D),'| adv_dec',D.adv_dec.sum(),'adv_grp kisi',D[D.adv_grp==1].pid.nunique(),'partner_adv & gercek',((D.partner_adv==1)&(D.adv_dec==0)).sum(),'| sure eslesen',D.dur.notna().sum())
print('Star sirasi grup sayisi',D.groupby('gid').star_order.first().value_counts().sort_index().to_dict())
