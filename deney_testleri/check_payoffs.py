"""
Kullanım:
    cd public_goods_networked
    otree test network_within 12 --export=../test_out
    python check_payoffs.py ../test_out/network_within.csv

Export edilen veriyi, ödeme formülünden BAĞIMSIZ olarak yeniden hesaplar:
  pi_i = 15 - c_i + 1.5 * (kapalı komşuluk katkı toplamı) / |N[i]|
ve şunları kontrol eder: payoff, rol/komşuluk büyüklüğü, star merkez rotasyonu,
blok sırası, toplam ödeme alanları.
"""
import sys
import math
import pandas as pd

E, BETA, RPB = 15, 1.5, 6
d = pd.read_csv(sys.argv[1])
d = d.rename(columns={'participant.payoff': 'ppayoff', 'participant.code': 'code',
                      'group.id_in_subsession': 'g'})
d.columns = [c.split('.', 1)[1] if c.startswith(('player.', 'group.', 'subsession.')) else c
             for c in d.columns]

# POINTS_DECIMAL_PLACES=2 ile payoff'lar yuvarlanmaz: formulle birebir ayni olmali
TOL = 1e-9
bad, rounded = 0, 0
for (g, r), x in d.groupby(['g', 'round_number']):
    x = x.set_index('id_in_group'); c = x.contribution
    t = x.treatment.iloc[0]
    order = x.block_order.iloc[0].split(',')
    assert t == order[(r - 1) // RPB], ('blok sirasi', g, r)
    for i in x.index:
        if t in ('control', 'cycle'):
            nb = [1, 2, 3]
        else:
            ctr = int(x.star_center_order.iloc[0].split(',')[((r - 1) % RPB) % 3])
            nb = [1, 2, 3] if i == ctr else [i, ctr]
            if x.network_role[i] != ('center' if i == ctr else 'periphery') or x.neighborhood_size[i] != len(nb):
                bad += 1; print('rol/komsuluk hatasi', g, r, i)
        exp = E - c[i] + BETA * sum(c[k] for k in nb) / len(nb)
        diff = abs(x.payoff[i] - exp)
        if diff > 1e-9: rounded += 1
        if diff > TOL:
            bad += 1; print('payoff hatasi', g, r, i, t, x.payoff[i], exp)

for g, x in d.groupby('g'):
    cnt = x[x.treatment == 'star'].groupby('id_in_group').apply(lambda y: (y.network_role == 'center').sum())
    assert (cnt == 2).all(), ('star merkez dagilimi', g, cnt.to_dict())

last = d[d.round_number == d.round_number.max()].set_index('code')
tot = d.groupby('code').payoff.sum()
FEE = 100
assert ((last.game_total_tl - tot).abs() < 1e-9).all(), 'game_total_tl != tur payoff toplami'
exact = tot + (100 - last.charity_d1) + FEE
payable = exact.apply(lambda v: math.ceil(round(v, 6)))
assert ((last.final_total_tl - payable).abs() < 1e-9).all(), 'final_total_tl: tam liraya yukari yuvarlanmis olmali'
assert ((last.ppayoff - (payable - FEE)).abs() < 1e-9).all(), 'participant.payoff katilim ucretini icermemeli (admin ucreti ayrica ekler)'
print(f'{d.g.nunique()} grup, {len(d)} satir | hata: {bad} | yuvarlanan payoff satiri: {rounded}')
print('final_total_tl yukari yuvarlanmis, participant.payoff ucret haric: OK')
print('Blok siralari (grup sayisi):', d[d.round_number == 1].drop_duplicates('g').block_order.value_counts().to_dict())
