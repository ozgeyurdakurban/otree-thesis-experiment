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
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
& .\venv\Scripts\Activate.ps1

$pw = Read-Host "Admin sifresi belirleyin (kullanici adi: eoy)"
if ([string]::IsNullOrWhiteSpace($pw)) { throw "Sifre bos olamaz." }
$env:OTREE_ADMIN_PASSWORD = $pw
$env:OTREE_SECRET_KEY = [guid]::NewGuid().ToString("N")
$env:OTREE_AUTH_LEVEL = "STUDY"      # demo baglantilari kapali, admin sifreli
$env:OTREE_PRODUCTION = "1"

$yedekKlasoru = Join-Path $PSScriptRoot "veri_yedekleri"
New-Item -ItemType Directory -Force -Path $yedekKlasoru | Out-Null

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

# Sunucu calisirken her 5 dakikada bir otomatik yedek
$yedekIsi = Start-Job -ScriptBlock {
    param($kok, $klasor)
    while ($true) {
        Start-Sleep -Seconds 300
        $kaynak = Join-Path $kok "db.sqlite3"
        if (Test-Path $kaynak) {
            $d = Get-Date -Format "yyyyMMdd_HHmmss"
            Copy-Item $kaynak (Join-Path $klasor ("db_canli_" + $d + ".sqlite3")) -ErrorAction SilentlyContinue
        }
    }
} -ArgumentList $PSScriptRoot, $yedekKlasoru
Write-Host "Her 5 dakikada bir otomatik yedek: veri_yedekleri klasoru"

try {
    otree prodserver 8000
}
finally {
    Stop-Job $yedekIsi -ErrorAction SilentlyContinue
    Remove-Job $yedekIsi -Force -ErrorAction SilentlyContinue
}
