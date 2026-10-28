# otree-thesis-experiment

oTree implementation of the laboratory experiment for the doctoral thesis
*Altruism in Networked Public Good Games*. A within-subject networked
public-goods game with three treatments, followed by a battery of prosocial-weight
measures.

## Design

- **Groups of 3**, fixed partner matching across the whole session.
- **3 treatments × 6 rounds = 18 rounds.** Block order randomized per group.
  - **Control** — fully connected group (`d=3`).
  - **Cycle** — ring; with `n=3`, `C_3 = K_3`, so payoff-equivalent to Control (differs only in framing).
  - **Star** — center (`d=3`) and two leaves (`d=2`); the central role rotates so each member is center twice.
- Per-round endowment `e = 15` tokens; pool productivity `beta = 1.5`.
- Payoff: `pi_i = e - c_i + beta * (1/d_i) * sum_{k in N[i]} c_k`.
- Post-game measures: incentivized charity dictator game, Carlo–Randall prosocial
  Likert items, Falk et al. general-altruism items, and a Murphy et al. SVO module,
  plus demographics.
- All rounds paid; payment = participation fee + token earnings + charity amount retained.

## Apps

| Folder | Role |
|--------|------|
| `network_within/`  | **Main app** used for data collection: all three treatments within one session (`__init__.py` holds the full model, pages, and payoff logic). |
| `network_control/` | Stand-alone Control treatment (`models.py`, `pages.py`) — for piloting a single arm. |
| `network_cycle/`   | Stand-alone Cycle treatment. |
| `network_star/`    | Stand-alone Star treatment. |
| `settings.py`      | Session configurations, currency (`TRY`, points), participation fee, admin settings. |

Templates live under each app's `templates/` folder. The session run in the thesis
uses the `network_within` configuration in `settings.py`.

## Requirements

```
python >= 3.9
otree
```
```
pip install -r requirements.txt
```

## Run locally

```bash
otree devserver
```
Then open `http://localhost:8000` and start a session
(`Control Treatment`, `Cycle Treatment`, `Star Treatment`, or the within-subject
`network_within` configuration).

## Notes

- `beta = 1.5` is set as the constant `BETA` in each app's `models.py`
  (and in `network_within/__init__.py`). It satisfies the joint design constraint
  `6/5 < beta < 2` (socially productive at, yet privately costly for, the star
  periphery `d=2`).
- Before deploying to a real server, change `SECRET_KEY`, `ADMIN_USERNAME`, and
  `ADMIN_PASSWORD` in `settings.py`.
- Data are anonymous; no identifying information is collected (see the consent page).

## Ödeme, yuvarlama, odalar, blok sırası ve sınıf oturumu (29 Ekim 2026)

- `POINTS_DECIMAL_PLACES = 2`: tur payoff'ları yuvarlanmaz (0,25'in katları); ekranlarda hesaplanan değer gösterilir (18,5; 13,25).
- Yalnızca son sayfalarda (FinalResults, PaymentInfo) nihai toplam ödeme **tam liraya yukarı** yuvarlanır; `final_total_tl` bu yuvarlanmış tutardır.
- `participant.payoff` katılım ücretini **içermez**; oTree admin Payments sayfası ücreti kendisi ekler (aksi halde 2 kez sayılırdı).
- `ROOMS`: `itu_lab`, `yeditepe_lab` (terminal etiketleri `_rooms/*.txt`: ITU-01…18, YED-01…18; gerçek terminallere göre düzenle) ve `sinif` (etiketsiz; herkes `/room/sinif` adresiyle girer).
- Blok sırası dengeli atanır: 6 permütasyon karıştırılıp gruplara sırayla verilir; 18 kişilik oturumda (6 grup) her sıra tam bir kez çıkar. Sabit sıra için `block_order` session config'i hâlâ geçerli.
- Admin şifresi ve `SECRET_KEY` ortam değişkenlerinden okunur (`OTREE_ADMIN_PASSWORD`, `OTREE_SECRET_KEY`); `baslat_sinif.ps1` sunucuyu güvenli modda (`OTREE_AUTH_LEVEL=STUDY`, `prodserver`) başlatır. Sınıfta tünel için: `cloudflared tunnel --url http://localhost:8000`.
- Testler: `deney_testleri/tests.py` (bot testi; `network_within/` içine kopyalayıp `otree test network_within 18 --export=../test_out`) ve `deney_testleri/check_payoffs.py` (export edilen veriyi ödeme formülünden bağımsız olarak kontrol eder).

## Lisans / License

Özgün kod katkılarım **MIT**, özgün metinlerim ve yaratıcı içeriklerim **CC BY 4.0** kapsamındadır. Üçüncü taraf içerikler kendi koşullarını korur. [Kapsam ve tam metinler](LICENSE.md).

My original code contributions are licensed under **MIT**; my original text and creative content under **CC BY 4.0**. Third-party material retains its own terms. See [scope and full texts](LICENSE.md).
