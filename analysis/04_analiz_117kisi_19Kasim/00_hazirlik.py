# 117 katilimci, kimse cikarilmadi (18 Kasim karari); ilerletme dummy'leri ile isaretli
import pandas as pd, numpy as np, glob, warnings
warnings.filterwarnings('ignore')
pd.set_option('display.width',220); pd.set_option('display.max_columns',60); pd.set_option('display.float_format',lambda v:f'{v:.3f}')
D=pd.read_excel('../../experiment_data/tüm_veri.xlsx',sheet_name=0)
D['gid']=D.session_code+'_'+D.group_no.astype(str); D['pid']=D.session_code+'_'+D.participant_code
D['pos']=np.where(D.treatment=='star',D.network_role,D.treatment)
beta,e=1.5,15
D['S']=D.neighborhood_total_contribution-D.contribution
D['mp']=beta/D.neighborhood_size
print('Getiri formulu max |fark|:',(e-D.contribution+D.mp*D.neighborhood_total_contribution-D.round_payoff_points).abs().max())
g=D.groupby(['gid','round_number']).contribution.sum().rename('gs'); D=D.join(g,on=['gid','round_number'])
print('Grup toplami uyumsuz satir:',(D.gs!=D.group_total_contribution).sum())
cen=D[D.network_role=='center'].set_index(['gid','round_number']).contribution.rename('cc'); D=D.join(cen,on=['gid','round_number'])
bad=((D.network_role!='periphery')&(D.neighborhood_total_contribution!=D.gs))|((D.network_role=='periphery')&(D.neighborhood_total_contribution!=D.contribution+D.cc))
print('Komsuluk toplami uyumsuz satir:',bad.sum())
print('Kisi basi centre tur sayisi:',D[D.network_role=='center'].groupby('pid').size().value_counts().to_dict())
print('Grup-tur basina centre sayisi:',D[D.treatment=='star'].groupby(['gid','round_number']).apply(lambda x:(x.network_role=='center').sum()).value_counts().to_dict())
D['W']=e+D.mp*D.S; D['share']=(1-D.mp)*D.contribution/D.W
# dummy'ler
D['adv_dec']=D.contribution_advanced.fillna(0).astype(int)
D['adv_person']=(D.groupby('pid').adv_dec.transform('sum')>0).astype(int)
D['adv_grp']=(D.groupby('gid').adv_dec.transform('sum')>0).astype(int)
D['partner_adv']=((D.groupby(['gid','round_number']).adv_dec.transform('sum')-D.adv_dec)>0).astype(int)
D['leaf']=(D.pos=='periphery')*1; D['centre']=(D.pos=='center')*1; D['cyc']=(D.pos=='cycle')*1
so=D[D.treatment=='star'].groupby('gid').block_index.first().rename('star_order'); D=D.join(so,on='gid')
D['new19']=D.session_date.astype(str).str.contains('2026-11-19').astype(int)
# Anket: ilerletilen 4 kisinin anket/bagis degerleri oTree varsayilani 0 -> gercek cevap degil, eksik (NaN) kodlanir
svy=[f'pt_b{i}' for i in range(1,11)]+['alt_c1','alt_c2','charity_d1']
D['svy_invalid']=(D.veri_kalite=='ilerletilmis_ardisik').astype(int)
D.loc[D.svy_invalid==1,svy]=np.nan
# karar sureleri
fs=glob.glob('../../experiment_data/sessions/gerçek_*/otree_ciktilari/*PageTimes*.csv')
pt=pd.concat([pd.read_csv(f) for f in fs]).drop_duplicates().sort_values(['participant_code','epoch_time_completed'])
pt['dur']=pt.groupby('participant_code').epoch_time_completed.diff()
ct=pt[pt.page_name=='Contribution'][['session_code','participant_code','round_number','dur']].drop_duplicates(['session_code','participant_code','round_number'])
D=D.merge(ct,on=['session_code','participant_code','round_number'],how='left')
D['ldur']=np.log(D.dur.clip(lower=1))
D.to_pickle('D117.pkl')
print('\nN katilimci',D.pid.nunique(),'| grup',D.gid.nunique(),'| karar',len(D),'| oturum',D.session_code.nunique())
print(D.groupby(['session_date','session_code']).pid.nunique())
print('anketi gecersiz (ilerletilmis_ardisik) kisi',D[D.svy_invalid==1].pid.nunique()); print('ilerletilen karar',D.adv_dec.sum(),'| ilerletilen kisi',D[D.adv_person==1].pid.nunique(),'| ilerletilen grup',D[D.adv_grp==1].gid.nunique(),'| sure eslesen',D.dur.notna().sum())
print('onam=0 kisi:',D[D.consent_given!=1].groupby('pid').size().index.tolist())
print('Star sirasi grup sayisi',D.groupby('gid').star_order.first().value_counts().sort_index().to_dict())
print('blok sirasi dagilimi:',D.groupby('gid').block_order.first().value_counts().to_dict())
