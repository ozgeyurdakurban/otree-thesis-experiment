"""
SINIF DENEYI - YUK TESTI (sanal ogrenciler)            10 Kasim 2026

N sanal ogrenci, gercek bir ogrencinin yaptigi her seyi HTTP uzerinden yapar:
  1) /room/sinif adresine girer ("Basla"ya basar) ve odada bekler,
  2) siz yonetici panelinde oturumu olusturunca oyuna alinir,
  3) onam -> talimat -> katki -> bekleme -> sonuc (18 tur) -> anketler -> odeme
     sayfalarini gercek form gonderimleriyle doldurur.
Her ogrenci ayri cerez tasir (ayri telefon gibi). Bekleme sayfasinda 1 sn'de bir
sayfayi yeniden ister; bu, gercek tarayicilardan daha agir bir yuktur.

KULLANIM (proje klasorunde, venv etkinken; bir kez: pip install requests)
  Tunel uzerinden (onerilen prova):
    python ..\\deney_testleri\\yuk_testi.py https://ADRES.trycloudflare.com 27
  Yalnizca bilgisayarin kendisinde:
    python ..\\deney_testleri\\yuk_testi.py http://localhost:8000 27

  Script "N ogrenci odada" dedikten sonra panelde Rooms > Sinif Oturumu >
  Session config: network_within, Number of participants: N > Create.

  Secenekler:  --dusunme 2 8   (her sayfada 2-8 sn rastgele bekleme; varsayilan)
               --dusunme 0 0   (herkes aninda tiklar: en agir yuk)
               --oda demo      (demo odasini dener; config: DEMO)

ONEMLI: Bu bir test oturumudur. Gercek deneyden once baslat_sinif.ps1'de
veritabanini SIL ile sifirlayin ya da test oturumunu panelden silin.
"""
import argparse, re, time, random, threading, statistics, json
from collections import Counter
import requests

ap = argparse.ArgumentParser()
ap.add_argument('sunucu', help='ör. https://xxxx.trycloudflare.com veya http://localhost:8000')
ap.add_argument('n', type=int, help='sanal ogrenci sayisi (3un kati)')
ap.add_argument('--dusunme', nargs=2, type=float, default=[2, 8], metavar=('MIN', 'MAKS'))
ap.add_argument('--oda', default='sinif')
ap.add_argument('--rest-key', default=None, help='verilirse oturum otomatik olusturulur')
ap.add_argument('--config', default='network_within')
ap.add_argument('--yenile', type=int, default=0, help='baglanti hatasinda ayni istegi N kez yeniden dene (tarayiciyi yenileyen ogrenci gibi); 0 = hata ilk seferde ogrenciyi dusurur')
a = ap.parse_args()

BASE = a.sunucu.rstrip('/')
ROOM_URL = f'{BASE}/room/{a.oda}?welcome_page_ok=1'
TMIN, TMAX = a.dusunme
TIMEOUT = 30
lat, errors, lock = [], [], threading.Lock()
progress = {}
yenileme = []


def req(s, method, url, **kw):
    t0 = time.time()
    deneme = 0
    while True:
        try:
            r = s.request(method, url, timeout=TIMEOUT, **kw)
            break
        except Exception as e:
            with lock:
                errors.append(f'{time.strftime("%H:%M:%S")} {type(e).__name__} {url}')
            deneme += 1
            if deneme > a.yenile:
                raise
            with lock:
                yenileme.append(time.strftime("%H:%M:%S"))
            time.sleep(random.uniform(3, 8))      # ogrenci sayfayi yenilemeden once biraz bekler
    with lock:
        lat.append(time.time() - t0)
        if r.status_code >= 400:
            errors.append(f'{time.strftime("%H:%M:%S")} HTTP {r.status_code} {url}')
    return r


def hidden_inputs(html):
    return dict(re.findall(r'<input[^>]*type="hidden"[^>]*name="([^"]+)"[^>]*value="([^"]*)"', html))


def page_data(page):
    if page == 'Consent':
        return dict(consent_given='True')
    if page == 'Contribution':
        return dict(contribution=random.randint(0, 15))
    if page == 'Demographics':
        return dict(age="21–23", gender="Kadın", field_of_study="Sayısal (STEM)",
                    year_of_study="3. sınıf", cgpa="3.00–3.49",
                    monthly_income="10.001–30.000 TL", risk_attitude="Az risk alırım")
    if page == 'AltruismMeasure':
        d = {f'pt_b{i}': random.randint(1, 7) for i in range(1, 11)}
        d.update(charity_d1=random.randint(0, 100), alt_c1=5, alt_c2=6,
                 svo_a1='A', svo_a2='B', svo_a3='C')
        return d
    return {}


def student(i, result):
    s = requests.Session()
    try:
        r = req(s, 'GET', ROOM_URL)
        while '/p/' not in r.url:          # oturum acilana kadar odada bekle
            time.sleep(2)
            r = req(s, 'GET', ROOM_URL)
        stuck_since = time.time()
        while True:
            m = re.search(r'/p/\w+/\w+/(\w+)/(\d+)', r.url)
            if not m:
                result[i] = f'beklenmeyen adres {r.url}'; return
            page = m.group(1)
            progress[i] = page
            if page in ('WaitForAll',) or 'otree-wait-page' in r.text:
                if time.time() - stuck_since > 180:
                    result[i] = f'180 sn+ bekleme sayfasinda takildi'; return
                time.sleep(1)
                r = req(s, 'GET', r.url)
                continue
            stuck_since = time.time()
            time.sleep(random.uniform(TMIN, TMAX))
            data = hidden_inputs(r.text)
            data.update(page_data(page))
            r2 = req(s, 'POST', r.url, data=data)
            if page == 'ThankYou':
                result[i] = 'tamamladi'; return
            if r2.url == r.url:
                result[i] = f'form reddedildi: {page}'; return
            r = r2
    except Exception as e:
        result[i] = f'baglanti hatasi: {type(e).__name__}'


def main():
    result = {}
    ths = [threading.Thread(target=student, args=(i, result), daemon=True) for i in range(a.n)]
    for t in ths:
        t.start(); time.sleep(0.1)
    time.sleep(3)
    if a.rest_key:
        r = requests.post(f'{BASE}/api/sessions', headers={'otree-rest-key': a.rest_key}, timeout=60,
                          json=dict(session_config_name=a.config, num_participants=a.n, room_name=a.oda))
        r.raise_for_status()
        print('Oturum olusturuldu:', r.json()['code'])
    else:
        print(f'\n>>> {a.n} sanal ogrenci "{a.oda}" odasinda bekliyor.')
        print(f'>>> Panelde Rooms > oda > Create (config: {a.config}, katilimci: {a.n}).\n')
    t0 = time.time()
    while any(t.is_alive() for t in ths):
        time.sleep(15)
        c = Counter(progress.values())
        print(f'{time.strftime("%H:%M:%S")} | bitti: {sum(1 for v in result.values() if v=="tamamladi")}/{a.n} '
              f'| sayfalar: {dict(c)} | hata: {len(errors)}', flush=True)
    dur = time.time() - t0
    q = sorted(lat)
    print('\n================ SONUC ================')
    print(f'{a.n} ogrenci | dusunme {TMIN}-{TMAX} sn | toplam sure {dur/60:.1f} dk')
    print('Durum:', dict(Counter(result.values())))
    if q:
        print(f'Istek: {len(q)} | medyan {statistics.median(q)*1000:.0f} ms | '
              f'p95 {q[int(.95*len(q))]*1000:.0f} ms | en yavas {q[-1]*1000:.0f} ms')
    print(f'Hata sayisi: {len(errors)}')
    if a.yenile:
        print(f'Yenileme gereken istek sayisi: {len(yenileme)} (ilk/son: {yenileme[:1]} {yenileme[-1:]})')
    for e in errors[:15]:
        print('  ', e)
    out = f'yuk_testi_sonuc_{time.strftime("%Y%m%d_%H%M%S")}.json'
    json.dump(dict(result=result, errors=errors), open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('Ayrintilar:', out)


main()
