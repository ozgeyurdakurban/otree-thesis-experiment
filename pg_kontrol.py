"""
PostgreSQL baglanti kontrolu (baslat_sinif.ps1 tarafindan cagrilir)   13 Kasim 2026

DATABASE_URL ortam degiskenindeki veritabanina baglanir ve tablo sayisini yazar.
Cikis kodu:  0 = baglandi, tablolar var (veri korunur)
             1 = baglandi, veritabani bos (ilk kurulum: otree resetdb gerekir)
             2 = baglanilamadi (servis kapali, sifre/adres yanlis vb.)
             3 = psycopg2 kurulu degil
Elle denemek icin (venv etkinken):
    $env:DATABASE_URL = (Get-Content .\veritabani_url.txt -TotalCount 1).Trim()
    python pg_kontrol.py
"""
import os
import sys

try:
    sys.stdout.reconfigure(errors='replace')
except Exception:
    pass

try:
    import psycopg2
except ImportError:
    print('HATA: psycopg2 kurulu degil.  pip install psycopg2-binary')
    sys.exit(3)

url = os.environ.get('DATABASE_URL', '')
if not url:
    print('HATA: DATABASE_URL tanimli degil.')
    sys.exit(2)

try:
    conn = psycopg2.connect(url, connect_timeout=10)
except Exception as exc:
    print('BAGLANTI HATASI: ' + str(exc).strip())
    sys.exit(2)

cur = conn.cursor()
cur.execute("select count(*) from information_schema.tables where table_schema = 'public'")
n = cur.fetchone()[0]
cur.execute('show server_version')
surum = cur.fetchone()[0]
conn.close()
print(f'PostgreSQL {surum} - baglanti tamam, tablo sayisi: {n}')
sys.exit(0 if n > 0 else 1)
