# =====================================================================
# SINIF OTURUMU - SUNUCUYU BASLAT (PowerShell)
# Calistirma:  powershell -ExecutionPolicy Bypass -File .\baslat_sinif.ps1
# Bu pencere oturum boyunca ACIK kalmali. Tuneli ayri bir pencerede baslatin:
#   cloudflared tunnel --url http://localhost:8000
# Ogrenci adresi:  <tunel adresi>/room/sinif
# Admin paneli:    <tunel adresi>/rooms  (kullanici: eoy, sifre: asagida belirlediginiz)
#
# VERI GUVENLIGI
#  - Veritabani (db.sqlite3) asla otomatik silinmez.
#  - Her baslangicta mevcut veritabani veri_yedekleri\ klasorune YEDEKLENIR.
#  - Sunucu calisirken her 5 dakikada bir yeni yedek alinir.
#  - Sifirlama ancak iki kez SIL yazarsaniz yapilir (bos birakirsaniz veriler korunur).
#  - Yedeklerden birini geri yuklemek icin: sunucuyu kapatin, secilen dosyayi
#    db.sqlite3 adiyla proje klasorune kopyalayin.
# =====================================================================
#
# 10 KASIM 2026 EKLERI (5 Kasim donmasindan sonra)
#  - Bu pencerede "Hizli Duzenleme" (QuickEdit) otomatik kapatilir: pencereye yanlislikla
#    tiklamak sunucunun ekrana yazmasini, dolayisiyla TUM istekleri durdurur.
#  - Bilgisayarin uykuya gecmesi script calistigi surece engellenir.
#  - Sunucu ciktisi ekranla birlikte loglar\sunucu_<tarih>.txt dosyasina da yazilir
#    (5 Kasim'da hata ciktisi kaydedilmedigi icin neden belirlenemedi).
#  - 5 dakikalik yedek, SQLite'in kendi yedekleme yontemiyle alinir (dosya kopyasi yerine):
#    sunucu yazarken dosyayi kilitlemez ve tutarli bir kopya uretir.
#
# 13 KASIM 2026 EKI: PostgreSQL
#  - Proje klasorunde veritabani_url.txt varsa sunucu PostgreSQL ile calisir
#    (tek satir: postgresql://kullanici:sifre@localhost:5432/veritabani).
#  - Dosya yoksa eskisi gibi SQLite (db.sqlite3) kullanilir; geri donus icin dosyanin adini degistirin.
#  - PostgreSQL yedekleri pg_dump ile alinir: veri_yedekleri\pg_baslangic_*.dump ve pg_canli_*.dump
#  - Yedekten geri yukleme (sunucu kapaliyken):
#      pg_restore --clean --if-exists --no-owner --dbname=<veritabani_url.txt icindeki adres> <yedek.dump>
# =====================================================================
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
& .\venv\Scripts\Activate.ps1

# --- QuickEdit kapat + uykuyu engelle (basarisiz olursa script durmaz, yalnizca uyari verir) ---
try {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class SinifKonsol {
    [DllImport("kernel32.dll")] static extern IntPtr GetStdHandle(int n);
    [DllImport("kernel32.dll")] static extern bool GetConsoleMode(IntPtr h, out uint m);
    [DllImport("kernel32.dll")] static extern bool SetConsoleMode(IntPtr h, uint m);
    [DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint f);
    public static bool QuickEditKapat() {
        IntPtr h = GetStdHandle(-10); uint m;
        if (!GetConsoleMode(h, out m)) return false;
        m &= ~0x0040u;  // ENABLE_QUICK_EDIT_MODE kapali
        m |= 0x0080u;   // ENABLE_EXTENDED_FLAGS
        return SetConsoleMode(h, m);
    }
}
'@
    if ([SinifKonsol]::QuickEditKapat()) {
        Write-Host "Hizli Duzenleme (QuickEdit) bu pencerede kapatildi."
    } else {
        Write-Host "UYARI: QuickEdit kapatilamadi; pencere ozelliklerinden elle kapatin." -ForegroundColor Yellow
    }
    # ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    [void][SinifKonsol]::SetThreadExecutionState([uint32]2147483651)
    Write-Host "Script calistigi surece bilgisayar uykuya gecmeyecek."
} catch {
    Write-Host "UYARI: QuickEdit/uyku ayari yapilamadi: $($_.Exception.Message)" -ForegroundColor Yellow
}

$pw = Read-Host "Admin sifresi belirleyin (kullanici adi: eoy)"
if ([string]::IsNullOrWhiteSpace($pw)) { throw "Sifre bos olamaz." }
$env:OTREE_ADMIN_PASSWORD = $pw
$env:OTREE_SECRET_KEY = [guid]::NewGuid().ToString("N")
$env:OTREE_AUTH_LEVEL = "STUDY"      # demo baglantilari kapali, admin sifreli
$env:OTREE_PRODUCTION = "1"
# REST anahtari: oturum, panel yerine oturum_olustur.py ile kurulur (panelden kurulum, ogrenci istekleriyle cakisabiliyor)
$env:OTREE_REST_KEY = [guid]::NewGuid().ToString("N")
Set-Content -Path (Join-Path $PSScriptRoot "rest_anahtari.txt") -Value $env:OTREE_REST_KEY -Encoding ASCII

$yedekKlasoru = Join-Path $PSScriptRoot "veri_yedekleri"
New-Item -ItemType Directory -Force -Path $yedekKlasoru | Out-Null

# --- VERITABANI SECIMI (13 Kasim 2026) ---
# veritabani_url.txt VARSA PostgreSQL, YOKSA eskisi gibi SQLite (db.sqlite3) kullanilir.
# SQLite'a donmek icin veritabani_url.txt dosyasinin adini degistirmek yeterlidir.
$urlDosyasi = Join-Path $PSScriptRoot "veritabani_url.txt"
$pgUrl = $null
$pgDump = $null
$yedekIsi = $null
if (Test-Path $urlDosyasi) {
    $pgUrl = Get-Content $urlDosyasi | ForEach-Object { $_.Trim() } |
        Where-Object { $_ -and -not $_.StartsWith("#") } | Select-Object -First 1
    if (-not $pgUrl -or $pgUrl -notmatch '^postgres(ql)?://') {
        throw "veritabani_url.txt gecersiz. Beklenen bicim: postgresql://kullanici:sifre@localhost:5432/veritabani"
    }
}

if ($pgUrl) {
    # ================= PostgreSQL =================
    $env:DATABASE_URL = $pgUrl
    Write-Host ""
    Write-Host "Veritabani: PostgreSQL" -ForegroundColor Cyan
    $py = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
    & $py (Join-Path $PSScriptRoot "pg_kontrol.py")
    $pgDurum = $LASTEXITCODE
    if ($pgDurum -ge 2) {
        throw "PostgreSQL'e baglanilamadi. Servis calisiyor mu (services.msc > postgresql)? veritabani_url.txt icindeki kullanici/sifre/veritabani adi dogru mu?"
    }

    # pg_dump'i bul (yedekler icin)
    $komut = Get-Command pg_dump -ErrorAction SilentlyContinue
    if ($komut) {
        $pgDump = $komut.Source
    } else {
        $aday = Get-ChildItem "C:\Program Files\PostgreSQL\*\bin\pg_dump.exe" -ErrorAction SilentlyContinue |
            Sort-Object FullName -Descending | Select-Object -First 1
        if ($aday) { $pgDump = $aday.FullName }
    }
    if (-not $pgDump) {
        Write-Host "UYARI: pg_dump bulunamadi; OTOMATIK YEDEK ALINMAYACAK." -ForegroundColor Yellow
        $devam = Read-Host "Yedeksiz devam etmek icin DEVAM yazin (bos birakirsaniz script durur)"
        if ($devam -cne "DEVAM") { throw "pg_dump bulunamadigi icin durduruldu." }
    }

    if ($pgDurum -eq 1) {
        Write-Host "Veritabani bos: tablolar ilk kez olusturuluyor."
        otree resetdb --noinput
    } else {
        if ($pgDump) {
            $damga = Get-Date -Format "yyyyMMdd_HHmmss"
            $hedef = Join-Path $yedekKlasoru ("pg_baslangic_" + $damga + ".dump")
            & $pgDump --format=custom "--file=$hedef" "--dbname=$pgUrl"
            if ($LASTEXITCODE -ne 0 -or -not (Test-Path $hedef)) {
                throw "Baslangic yedegi alinamadi (pg_dump hata verdi). Veriler guvende, ancak yedeksiz devam edilmiyor."
            }
            Write-Host ""
            Write-Host "Mevcut veritabani yedeklendi: veri_yedekleri\pg_baslangic_$damga.dump"
        }
        Write-Host "Veriler KORUNACAK. Veritabani varsayilan olarak SIFIRLANMAZ."
        Write-Host ""
        $a = Read-Host "Sifirlamak istiyorsaniz tam olarak SIL yazin (bos birakirsaniz veriler korunur)"
        if ($a -ceq "SIL") {
            $b = Read-Host "Emin misiniz? Canli veritabani silinecek. Onaylamak icin tekrar SIL yazin"
            if ($b -ceq "SIL") {
                otree resetdb --noinput
                Write-Host "Veritabani sifirlandi (onceki veriler veri_yedekleri klasorunde)."
            } else {
                Write-Host "Iptal edildi, veriler korundu."
            }
        } else {
            Write-Host "Veriler korundu."
        }
    }
    Write-Host "Not: db.sqlite3 (onceki oturumlarin verisi) kullanilmiyor ve oldugu gibi duruyor."

    # Sunucu calisirken her 15 dakikada bir otomatik yedek (pg_dump, sunucuyu durdurmaz)
    if ($pgDump) {
        $yedekIsi = Start-Job -ScriptBlock {
            param($pgDump, $url, $klasor)
            while ($true) {
                Start-Sleep -Seconds 900
                $d = Get-Date -Format "yyyyMMdd_HHmmss"
                $hedef = Join-Path $klasor ("pg_canli_" + $d + ".dump")
                & $pgDump --format=custom "--file=$hedef" "--dbname=$url" 2>$null
            }
        } -ArgumentList $pgDump, $pgUrl, $yedekKlasoru
        Write-Host "Her 15 dakikada bir otomatik yedek: veri_yedekleri klasoru (pg_canli_*.dump)"
    }
} else {
    # ================= SQLite (eski davranis) =================
    Write-Host ""
    Write-Host "Veritabani: SQLite (db.sqlite3) - veritabani_url.txt bulunamadi" -ForegroundColor Yellow
    if (Test-Path ".\db.sqlite3") {
        $damga = Get-Date -Format "yyyyMMdd_HHmmss"
        Copy-Item ".\db.sqlite3" (Join-Path $yedekKlasoru ("db_baslangic_" + $damga + ".sqlite3"))
        Write-Host ""
        Write-Host "Mevcut veritabani yedeklendi: veri_yedekleri\db_baslangic_$damga.sqlite3"
        Write-Host "Veriler KORUNACAK. Veritabani varsayilan olarak SIFIRLANMAZ."
        Write-Host ""
        $a = Read-Host "Sifirlamak istiyorsaniz tam olarak SIL yazin (bos birakirsaniz veriler korunur)"
        if ($a -ceq "SIL") {
            $b = Read-Host "Emin misiniz? Canli veritabani silinecek (yedek alindi). Onaylamak icin tekrar SIL yazin"
            if ($b -ceq "SIL") {
                otree resetdb --noinput
                Write-Host "Veritabani sifirlandi (onceki veriler veri_yedekleri klasorunde)."
            } else {
                Write-Host "Iptal edildi, veriler korundu."
            }
        } else {
            Write-Host "Veriler korundu."
        }
    } else {
        otree resetdb --noinput
    }

    # Sunucu calisirken her 15 dakikada bir otomatik yedek (SQLite online backup API)
    $yedekIsi = Start-Job -ScriptBlock {
        param($kok, $klasor)
        $py = Join-Path $kok "venv\Scripts\python.exe"
        while ($true) {
            Start-Sleep -Seconds 900
            $kaynak = Join-Path $kok "db.sqlite3"
            if (Test-Path $kaynak) {
                $d = Get-Date -Format "yyyyMMdd_HHmmss"
                $hedef = Join-Path $klasor ("db_canli_" + $d + ".sqlite3")
                & $py -c "import sqlite3,sys; s=sqlite3.connect(sys.argv[1], timeout=30); t=sqlite3.connect(sys.argv[2]); s.backup(t); t.close(); s.close()" $kaynak $hedef 2>$null
            }
        }
    } -ArgumentList $PSScriptRoot, $yedekKlasoru
    Write-Host "Her 15 dakikada bir otomatik yedek: veri_yedekleri klasoru"
}

# Sunucu ciktisini hem ekrana hem log dosyasina yaz
$logKlasoru = Join-Path $PSScriptRoot "loglar"
New-Item -ItemType Directory -Force -Path $logKlasoru | Out-Null
$logDosyasi = Join-Path $logKlasoru ("sunucu_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".txt")
Write-Host "Sunucu logu: $logDosyasi"
$env:PYTHONUNBUFFERED = "1"

try {
    # cmd /c ... 2>&1 : hata akisini cmd icinde birlestirir; PowerShell 5.1'in
    # native stderr'i hata sayip scripti durdurmasini onler.
    $ErrorActionPreference = "Continue"
    cmd /c "otree prodserver 8000 2>&1" | Tee-Object -FilePath $logDosyasi -Append
}
finally {
    if ($yedekIsi) {
        Stop-Job $yedekIsi -ErrorAction SilentlyContinue
        Remove-Job $yedekIsi -Force -ErrorAction SilentlyContinue
    }
}
