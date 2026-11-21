"""
IZLEME PROBE - yuk testi sirasinda sistemi her 2 sn olcer              16 Kasim 2026

Amac: kopma/yavaslama oldugunda NEREDE oldugunu ayirmak:
  yerel   = sunucunun kendisi (localhost)          -> yavaslarsa SUNUCU/PostgreSQL
  tunel   = tunel adresi uzerinden                 -> yerel iyi, tunel kotuyse TUNEL
  internet= 1.1.1.1:443'e TCP baglanti suresi      -> yavaslar/kopar ise INTERNET (Wi-Fi/ISS)
  cpu/ram, python ve postgres islemlerinin CPU'su, 8000 portundaki baglanti sayisi

KULLANIM (yeni bir PowerShell penceresi, proje klasorunde):
  .\\venv\\Scripts\\pip install psutil
  .\\venv\\Scripts\\python ..\\deney_testleri\\izleme_probe.py https://TUNEL-ADRESI
Testi bitirince bu pencerede Ctrl+C: ozet ekrana yazilir, ham veri loglar\\izleme_<tarih>.csv'ye kaydedilir.
"""
import sys, time, csv, socket, statistics, threading, os, datetime
import requests
try:
    import psutil
except ImportError:
    psutil = None

if len(sys.argv) < 2:
    sys.exit('Kullanim: python izleme_probe.py https://TUNEL-ADRESI [yerel_adres]')
TUNEL = sys.argv[1].rstrip('/')
YEREL = (sys.argv[2] if len(sys.argv) > 2 else 'http://127.0.0.1:8000').rstrip('/')
ARALIK = 2.0
YOL = '/room/sinif'          # parametresiz: yalnizca karsilama sayfasi, katilimci olusturmaz
kok = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public_goods_networked', 'loglar')
os.makedirs(kok, exist_ok=True)
dosya = os.path.join(kok, 'izleme_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.csv')

def get_ms(url, timeout=15):
    t = time.perf_counter()
    try:
        r = requests.get(url + YOL, timeout=timeout)
        return r.status_code, (time.perf_counter() - t) * 1000
    except Exception as e:
        return type(e).__name__, (time.perf_counter() - t) * 1000

def net_ms(timeout=5):
    t = time.perf_counter()
    try:
        s = socket.create_connection(('1.1.1.1', 443), timeout=timeout); s.close()
        return 'ok', (time.perf_counter() - t) * 1000
    except Exception as e:
        return type(e).__name__, (time.perf_counter() - t) * 1000

def kaynak():
    if not psutil:
        return '', '', '', '', ''
    py = pg = 0.0
    for p in psutil.process_iter(['name', 'cpu_percent']):
        n = (p.info['name'] or '').lower()
        if n.startswith('python'): py += p.info['cpu_percent'] or 0
        elif n.startswith('postgres'): pg += p.info['cpu_percent'] or 0
    try:
        con = sum(1 for c in psutil.net_connections('tcp') if c.laddr and c.laddr.port == 8000 and c.status == 'ESTABLISHED')
    except Exception:
        con = ''
    return psutil.cpu_percent(), psutil.virtual_memory().percent, round(py), round(pg), con

if psutil:
    psutil.cpu_percent(); [p.cpu_percent() for p in psutil.process_iter()]
rows = []
son_k = ('', '', '', '', '')
sayac = 0
print(f'Izleme basladi. Yerel: {YEREL}  Tunel: {TUNEL}\nCSV: {dosya}\nBitirmek icin Ctrl+C.\n')
f = open(dosya, 'w', newline='', encoding='utf-8-sig'); w = csv.writer(f)
w.writerow(['saat', 'yerel_durum', 'yerel_ms', 'tunel_durum', 'tunel_ms', 'internet_durum', 'internet_ms', 'cpu_pct', 'ram_pct', 'python_cpu', 'postgres_cpu', 'baglanti_8000'])
try:
    while True:
        t0 = time.time()
        res = {}
        def calis(k, fn): res[k] = fn()
        th = [threading.Thread(target=calis, args=('y', lambda: get_ms(YEREL))),
              threading.Thread(target=calis, args=('t', lambda: get_ms(TUNEL))),
              threading.Thread(target=calis, args=('n', net_ms))]
        [x.start() for x in th]; [x.join() for x in th]
        if sayac % 15 == 0:      # agir olcum: 30 sn'de bir (psutil Windows'ta CPU yer)
            son_k = kaynak()
        sayac += 1
        k = son_k
        row = [time.strftime('%H:%M:%S'), res['y'][0], round(res['y'][1]), res['t'][0], round(res['t'][1]), res['n'][0], round(res['n'][1])] + list(k)
        w.writerow(row); f.flush(); rows.append(row)
        if len(rows) % 5 == 0:
            print(row[0], 'yerel', row[1], row[2], 'ms | tunel', row[3], row[4], 'ms | internet', row[5], row[6], 'ms | cpu', row[7], 'py', row[9], 'pg', row[10])
        time.sleep(max(0, ARALIK - (time.time() - t0)))
except KeyboardInterrupt:
    pass
f.close()

def ozet(ad, durum_i, ms_i, esik):
    ok = [r[ms_i] for r in rows if str(r[durum_i]) in ('200', 'ok')]
    bad = [r for r in rows if str(r[durum_i]) not in ('200', 'ok')]
    yavas = [r for r in rows if str(r[durum_i]) in ('200', 'ok') and r[ms_i] > esik]
    s = f'{ad:9s} olcum {len(rows)} | hata {len(bad)} | yavas(>{esik} ms) {len(yavas)}'
    if ok:
        ok.sort(); s += f' | medyan {statistics.median(ok):.0f} ms | p95 {ok[int(len(ok)*0.95)-1]:.0f} ms | en yavas {ok[-1]:.0f} ms'
    print(s)
    return bad, yavas
print('\n=========== OZET ===========')
yb, yy = ozet('yerel', 1, 2, 1000)
tb, ty = ozet('tunel', 3, 4, 3000)
nb, ny = ozet('internet', 5, 6, 300)
yt = {r[0] for r in yb + yy}; tt = {r[0] for r in tb + ty}; nt = {r[0] for r in nb + ny}
print('\nYORUM (otomatik, kaba):')
print(f'  sunucu yavas/hatali olculer           : {len(yt)}')
print(f'  tunel yavas, ama sunucu iyi           : {len(tt - yt)}   -> tunel veya internet')
print(f'  internet de ayni anda yavas/kopuk     : {len((tt - yt) & nt)}   -> sorun buyuk olasilikla INTERNET/Wi-Fi')
print(f'  tunel yavas, internet iyi, sunucu iyi : {len((tt - yt) - nt)}   -> sorun TUNEL (cloudflare)')
print(f'  sunucu yavas                          : {len(yt)}   -> CPU/PostgreSQL (csv\'de cpu, python_cpu, postgres_cpu sutunlarina bak)')
