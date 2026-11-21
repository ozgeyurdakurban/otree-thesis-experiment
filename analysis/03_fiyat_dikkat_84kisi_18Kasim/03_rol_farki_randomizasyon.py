# Dogru randomizasyon nulli: Star'da centre turlari (1,4),(2,5),(3,6) semalarindan biri. Grup icinde semalar uyelere rassal atanmis.
# Null (rolun etkisi yok): ayni grupta semalari uyeler arasinda yer degistirmek (3! = 6) veriyi degistirmez.
# Istatistik: kisi duzeyi (leaf ort. - centre ort.) farklarinin varyansi ve |fark|>=3 orani.
import pandas as pd, numpy as np, itertools
D=pd.read_pickle('D84.pkl'); rng=np.random.default_rng(11)
def run(S,lab,col):
    S=S.copy()
    if col=='gr': S['y']=S.contribution-S.groupby(['gid','round_number']).contribution.transform('mean')   # grup x tur sabit etkisi
    else: S['y']=S.contribution
    Y={g:x.pivot(index='pid',columns='block_round',values='y') for g,x in S.groupby('gid')}
    sch={g:x[x.network_role=='center'].groupby('pid').block_round.min().reindex(Y[g].index).values for g,x in S.groupby('gid')}
    def stat(assign):
        gaps=[]
        for g,M in Y.items():
            for i,pid in enumerate(M.index):
                c=[assign[g][i]-1,assign[g][i]+2]; row=M.loc[pid].values
                gaps.append(np.delete(row,c).mean()-row[c].mean())
        gaps=np.array(gaps); return gaps.var(), (np.abs(gaps)>=3).mean(), gaps.mean()
    o=stat(sch); sims=[]
    perms=list(itertools.permutations(range(3)))
    for _ in range(5000):
        a={g:s[list(perms[rng.integers(6)])] for g,s in sch.items()}; sims.append(stat(a))
    sims=np.array(sims)
    print(f'{lab:44s} var gozlenen {o[0]:.2f} null {sims[:,0].mean():.2f} p={np.mean(sims[:,0]>=o[0]):.3f} | |gap|>=3 {o[1]:.3f} null {sims[:,1].mean():.3f} p={np.mean(sims[:,1]>=o[1]):.3f} | ort. gap {o[2]:+.2f} p(2-yonlu)={np.mean(np.abs(sims[:,2])>=abs(o[2])):.3f}')
S=D[D.treatment=='star']
run(S[S.veri_seti_3==1],'26 temiz grup, ham katki','raw')
run(S[S.veri_seti_3==1],'26 temiz grup, grup x tur etkisi cikarilmis','gr')
run(S,'28 grup (ilerletilenler dahil), ham','raw')
