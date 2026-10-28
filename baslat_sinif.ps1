# =====================================================================
# SINIF OTURUMU - SUNUCUYU BASLAT (PowerShell)
# Calistirma:  sag tik > "PowerShell ile calistir"  veya
#   powershell -ExecutionPolicy Bypass -File .\baslat_sinif.ps1
# Bu pencere oturum boyunca ACIK kalmali. Tuneli ayri bir pencerede baslatin:
#   cloudflared tunnel --url http://localhost:8000
# Ogrenci adresi:  <tunel adresi>/room/sinif
# Admin paneli:    <tunel adresi>/rooms  (kullanici: eoy, sifre: asagida belirlediginiz)
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

if (-not (Test-Path .\db.sqlite3)) {
    otree resetdb --noinput
} else {
    Write-Host ""
    Write-Host "UYARI: Sifirlama onceki tum oturum verilerini siler. Once Data sekmesinden export alin."
    $a = Read-Host "Veritabani sifirlansin mi? (E/H)  [ilk kez veya yeni oturum icin E; ara verdiyseniz H]"
    if ($a -eq "E" -or $a -eq "e") { otree resetdb --noinput }
}

otree prodserver 8000
