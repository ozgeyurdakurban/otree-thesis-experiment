"""
OTURUMU PANEL YERINE BU BETIKLE OLUSTURUN                      12 Kasim 2026

Neden: Panelden Create'e basinca oTree oturumu arka planda ayri bir is parcaciginda kurar.
Ayni anda ogrencilerin istekleri gelirse veritabani islemleri cakisabilir; kurulum
"invalid literal for int()" gibi bir hatayla yarim kalir ve yarim oturum kaydi birakir
(12 Kasim provasinda 3 denemenin 2'si boyle basarisiz oldu). Bu betik oturumu REST
uzerinden kurar; sunucu kurulum boyunca baska istek islemez, cakisma olmaz.

KULLANIM (proje klasorunde, venv etkinken, sunucu calisirken):
    python oturum_olustur.py 30          # 30 katilimci (3'un kati)
Secenekler:  --config demo_network_within   (demo icin; oda: --oda demo)
Anahtar, baslat_sinif.ps1 tarafindan her baslatmada rest_anahtari.txt dosyasina yazilir.
Bu dosyayi kimseyle paylasmayin.
"""
import argparse, sys, os, json
import requests

ap = argparse.ArgumentParser()
ap.add_argument('n', type=int, help='katilimci sayisi (3un kati)')
ap.add_argument('--config', default='network_within')
ap.add_argument('--oda', default='sinif')
ap.add_argument('--sunucu', default='http://localhost:8000')
a = ap.parse_args()

if a.n % 3 != 0 or a.n <= 0:
    sys.exit('HATA: katilimci sayisi 3un kati olmali (ornek: 27, 30).')
dosya = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rest_anahtari.txt')
try:
    anahtar = open(dosya, encoding='utf-8-sig').read().strip()
except OSError:
    sys.exit('HATA: rest_anahtari.txt yok. Sunucuyu baslat_sinif.ps1 ile baslattiniz mi?')
try:
    r = requests.post(a.sunucu.rstrip('/') + '/api/sessions', headers={'otree-rest-key': anahtar},
                      json=dict(session_config_name=a.config, num_participants=a.n, room_name=a.oda),
                      timeout=300)
except requests.RequestException as e:
    sys.exit(f'HATA: sunucuya ulasilamadi ({type(e).__name__}). Pencere 1 acik mi?')
if r.status_code != 200:
    sys.exit(f'HATA {r.status_code}: {r.text[:500]}')
d = r.json()
print(f'Oturum olusturuldu. Kod: {d["code"]}  |  {a.n} katilimci  |  config: {a.config}  |  oda: {a.oda}')
print('Izleme: http://localhost:8000/SessionMonitor/' + d['code'])
