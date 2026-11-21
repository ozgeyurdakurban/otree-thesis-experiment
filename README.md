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
| `demo_network_within/` | 3-round demo of the main app (one round per block, fixed order; no surveys or payment pages). |
| `network_control/`, `network_cycle/`, `network_star/` | Stand-alone single-treatment apps for piloting. **Not loaded** since 10 Nov 2026 (removed from `INSTALLED_APPS`); folders kept on disk. |
| `settings.py`      | Session configurations, currency (`TRY`, points), participation fee, admin settings. |

Templates live under each app's `templates/` folder. The session run in the thesis
uses the `network_within` configuration in `settings.py`. Only two session configs remain:
`network_within` and `demo_network_within`.

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
(`network_within` for the main experiment, or `DEMO - Network Within (3 tur)`).

## Notes

- `beta = 1.5` is set as the constant `BETA` in each app's `models.py`
  (and in `network_within/__init__.py`). It satisfies the joint design constraint
  `6/5 < beta < 2` (socially productive at, yet privately costly for, the star
  periphery `d=2`).
- Before deploying to a real server, change `SECRET_KEY`, `ADMIN_USERNAME`, and
  `ADMIN_PASSWORD` in `settings.py`.
- Data are anonymous; no identifying information is collected (see the consent page).

## Ödeme, yuvarlama, odalar ve blok sırası (29 Ekim 2026 düzeltmeleri)

- `POINTS_DECIMAL_PLACES = 2`: tur payoff'ları yuvarlanmaz (0,25'in katları); ekranlarda hesaplanan değer gösterilir (18,5; 13,25).
- Yalnızca son sayfalarda (FinalResults, PaymentInfo) nihai toplam ödeme **tam liraya yukarı** yuvarlanır. `final_total_tl` bu yuvarlanmış tutardır.
- `participant.payoff` katılım ücretini **içermez**; oTree admin Payments sayfası ücreti kendisi ekler (aksi halde 2 kez sayılırdı).
- `ROOMS`: `itu_lab` ve `yeditepe_lab`; terminal etiketleri `_rooms/*.txt` içinde (ITU-01…18, YED-01…18; gerçek terminallere göre düzenle).
- Blok sırası dengeli atanır: 6 permütasyon karıştırılıp gruplara sırayla verilir. 18 kişilik oturumda (6 grup) her sıra tam bir kez çıkar. Sabit sıra gerekirse `network_within` config'indeki yorum satırı yapılmış `block_order` satırı açılır.
- Test: `deney_testleri/` altındaki `tests.py` (bot) ve `check_payoffs.py`. Eski dosyaların yedeği: `tez/otree/yedek_29Ekim_duzeltme_oncesi/`.

## Sınıf deneyi: sunucu, dayanıklılık ve prova (10–11 Kasım 2026)

- Sınıf oturumu `baslat_sinif.ps1` ile başlatılır (`prodserver`, Cloudflare tüneli); adım adım yönerge `Sinif_Deneyi_Teknik_Rehber.docx` içindedir. Eski betik `baslat_sinif_eski.ps1` olarak durur.
- Betik QuickEdit'i kapatır, uykuyu engeller, sunucu çıktısını `loglar/` altına yazar ve veritabanını her 5 dakikada SQLite yedekleme yöntemiyle `veri_yedekleri/` içine yedekler. Bu sürüm Windows'ta henüz denenmemiştir.
- `network_within` ve `demo_network_within` içindeki `templates/<app>/WaitForAll.html`, bekleme sayfasını 10–15 sn'de bir yeniler (websocket bildirimi kaybolursa takılmayı önler).
- `../deney_testleri/`: `tests.py` (bot testi; canlı veritabanı olan klasörde `otree test` çalıştırmayın, `db.sqlite3`'ü boşaltır), `yuk_testi.py` (sanal öğrenci yük testi; kullanım Rehber Bölüm 15), `check_payoffs.py`.
- Değişiklik öncesi dosyaların yedeği: `../yedekler/yedek_11Kasim_duzeltme_oncesi/`.
- **Oturum kurma (12 Kasım 2026):** Oturum panelden `Create` ile **değil**, `python oturum_olustur.py N` (N: 3'ün katı; demo için `--config demo_network_within --oda demo`) ile kurulur. Panelden kurulum, öğrenci istekleriyle çakışıp yarım oturum bırakabiliyor (provada 3 denemenin 2'si başarısız oldu). `baslat_sinif.ps1` her başlatmada rastgele bir REST anahtarını `rest_anahtari.txt` dosyasına yazar; `oturum_olustur.py` bunu kullanır. Bu dosyayı paylaşmayın.
- İki yük provası (27/30 sanal öğrenci, tünel üzerinden) 18 turu tamamladı; ikincisinde hata sayısı 0.

## PostgreSQL (13 Kasım 2026)

- Proje klasöründe `veritabani_url.txt` varsa `baslat_sinif.ps1` sunucuyu PostgreSQL ile başlatır (`DATABASE_URL`); dosya yoksa eskisi gibi SQLite (`db.sqlite3`) kullanılır. Dosyanın biçimi `veritabani_url_ORNEK.txt` içindedir; dosya `.gitignore` kapsamındadır, GitHub'a gitmez.
- Betik başlangıçta `pg_kontrol.py` ile bağlantıyı sınar; veritabanı boşsa tabloları kurar, doluysa `pg_dump` ile `veri_yedekleri/pg_baslangic_*.dump` yedeğini alır ve sunucu çalışırken 15 dakikada bir `pg_canli_*.dump` üretir.
- Geri yükleme (sunucu kapalıyken): `pg_restore --clean --if-exists --no-owner --dbname=<adres> <yedek.dump>`.
- 4–12 Kasım oturumlarının verisi `db.sqlite3` ve `veri_yedekleri/*.sqlite3` içinde kalır; PostgreSQL'e aktarılmamıştır.
- Bu sürüm Windows'ta henüz denenmemiştir; gerçek oturumdan önce `../deney_testleri/yuk_testi.py` ile prova yapılmalıdır.
## Data analysis (Chapter 3)

Python analysis of the classroom sessions (117 participants, 39 groups) is in [`analysis/`](analysis/README.md):
pre-planned hypothesis tests, network effects, prosocial measurement and structural estimation of the CES
parameters `(σ, λ)`. Data are not included.

## Lisans / License

Özgün kod katkılarım **MIT**, özgün metinlerim ve yaratıcı içeriklerim **CC BY 4.0** kapsamındadır. Üçüncü taraf içerikler kendi koşullarını korur. [Kapsam ve tam metinler](LICENSE.md).

My original code contributions are licensed under **MIT**; my original text and creative content under **CC BY 4.0**. Third-party material retains its own terms. See [scope and full texts](LICENSE.md).
