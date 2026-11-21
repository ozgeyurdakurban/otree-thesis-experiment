# 05_ces_bolumu_117kisi — CES genel model bölümü (taslak, 20 Kasım 2026)

Bölüm dosyası: `savunma/chapters/ces_general_model.tex` (şekiller `savunma/figures_ces/`).
Bölüm tezin içine henüz eklenmedi; yeri sonra kararlaştırılacak. Ön izleme: `savunma/ces_bolumu_onizleme.pdf`
(tez içinde derlenmiş hâlinden yalnız bu bölümün sayfaları; Ch2/Ch3'e yapılan atıflar çözülmüş durumda).

## Dosyalar
| Dosya | İçerik |
|---|---|
| `D117_kararlar.csv` | `04_analiz_117kisi_19Kasim/D117.pkl`'den alınmış karar düzeyi veri (117 kişi, 2.106 karar) |
| `katilimci_prososyal_ozet.csv` | Ch3 kompozit prososyal endeksi (04 klasöründen kopya) |
| `ces01_theory_checks.py` | bölümdeki yeni teorik iddiaların sembolik/sayısal kontrolü (C1–C16, 25 kontrol) → `ces01_log.txt` |
| `ces02_predictions.py` | tasarım parametrelerinde (sigma, lambda) öngörü tablosu, eta regular katkı 5,9'a kalibre; DGK parametrelerinin ağ oyununa taşınması → `ces02_predictions.csv`, `ces02_log.txt`, `fig_ces_predictions.png` |
| `ces03_data_analysis.py` | robust hipotez testleri (tek yönlü), parametrik hipotezler (D1, D2, Wald), yapısal censored likelihood (random intercept, sigma>=0, lambda>=0, sınır LR testleri, profile), eta_i, grup bootstrap → `ces03_results.json`, `ces03_profile.csv`, `ces03_bootstrap.csv`, `ces03_log.txt` |
| `ces04_figures.py` | profile likelihood şekli → `fig_ces_profile.png` |

## Çalıştırma
`pip install numpy scipy pandas statsmodels sympy matplotlib`, sonra bu klasörde:
`python ces01_theory_checks.py`, `python ces03_data_analysis.py 200` (yaklaşık 30 dk), `python ces02_predictions.py`, `python ces04_figures.py`.
Kalan oturumlar eklendiğinde: `D117_kararlar.csv` ve `katilimci_prososyal_ozet.csv` yeni veriyle yeniden üretilip aynı kod değiştirilmeden çalıştırılır.

## Temel sonuçlar (117 kişi)
- Robust hipotezlerin hiçbiri reddedilmiyor; leaf ≥ centre ve leaf ≥ regular eşitsizlikleri ±1 jeton içinde eşitlik olarak tutuyor.
- Cobb–Douglas reddediliyor (Wald 270; LR 240). Leontief (sigma = 0, lambda = 0) reddedilmiyor (P3 ortak p = 0,39); kısıtlı yapısal tahmin tam bu nokta; lambda <= 0,06.
- Kısıtsız sigma = -0,084 (bootstrap %95 [-0,27; 0,07]).
- Leaf'te Leontief oranı (X/c) regular'a göre %14 yüksek (p = 0,018); centre'ın katkısı prososyal yoğunlukla ilişkisiz — ikisi de CES ailesinin dışında.
