# Katilimci adresinden QR kod PNG'si uretir ve acar.
# Kullanim:  python qr_olustur.py https://ADRES.trycloudflare.com/room/demo
#            python qr_olustur.py https://ADRES.trycloudflare.com/room/sinif
# Resmin ustune oda adi (DEMO / DENEY), altina adres yazilir.
# Dosya adlari: demo -> demo.png, sinif -> realex.png
import os, sys

try:
    import qrcode
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Once kurun:  pip install qrcode[pil]")

if len(sys.argv) < 2:
    sys.exit("Kullanim: python qr_olustur.py https://ADRES.trycloudflare.com/room/demo")

url = sys.argv[1].strip().rstrip("/")
if "ADRES" in url.upper().split("//")[-1].split(".")[0] or not url.lower().startswith("https://"):
    sys.exit(
        "HATA: Gercek tunel adresini yazmadiniz.\n"
        "  Tunel penceresindeki https://....trycloudflare.com adresini kopyalayip\n"
        "  'ADRES.trycloudflare.com' yerine yazin. Ornek:\n"
        "  python qr_olustur.py https://ornek-kelime-kelime.trycloudflare.com/room/demo"
    )
if "/room/" not in url:
    url += "/room/sinif"
oda = url.rsplit("/", 1)[-1]  # demo veya sinif

if oda == "demo":
    baslik, alt, renk = "DEMO", "3 tur - deneme oyunu", (230, 126, 34)
elif oda == "sinif":
    baslik, alt, renk = "DENEY", "18 tur - ödemeli deney", (39, 120, 60)
else:
    baslik, alt, renk = oda.upper(), "", (47, 95, 168)


def font(boyut, kalin=False):
    adaylar = (["arialbd.ttf", "calibrib.ttf"] if kalin else ["arial.ttf", "calibri.ttf"]) + [
        "DejaVuSans-Bold.ttf" if kalin else "DejaVuSans.ttf"]
    for ad in adaylar:
        try:
            return ImageFont.truetype(ad, boyut)
        except OSError:
            pass
    return ImageFont.load_default(boyut)  # Turkce harfler eksik cikabilir


qr = qrcode.make(url, box_size=14, border=2).convert("RGB")
W = max(qr.width + 80, 900)
ust, alt_h = 190, 150
img = Image.new("RGB", (W, ust + qr.height + alt_h), "white")
d = ImageDraw.Draw(img)
d.rectangle([0, 0, W, 150], fill=renk)


def ortala(metin, f, y, fill):
    sol, ustk, sag, alt = d.textbbox((0, 0), metin, font=f)
    d.text(((W - (sag - sol)) // 2 - sol, y), metin, font=f, fill=fill)


ortala(baslik, font(96, True), 22, "white")
if alt:
    ortala(alt, font(34), 155, (80, 80, 80))
img.paste(qr, ((W - qr.width) // 2, ust + 10))
ortala(url, font(26), ust + qr.height + 30, (40, 40, 40))
ortala("Telefonunuzun kamerasıyla okutun", font(28), ust + qr.height + 80, (110, 110, 110))

dosya_adi = {"demo": "demo.png", "sinif": "realex.png"}.get(oda, oda + ".png")
dosya = os.path.join(os.path.dirname(os.path.abspath(__file__)), dosya_adi)
img.save(dosya)
print("Adres :", url)
print("Dosya :", dosya)
try:
    os.startfile(dosya)  # Windows'ta resmi acar
except Exception:
    pass
