# veri_analizleri — Ch3 deney verisi analizleri

Her analiz turu ayrı bir alt klasörde birikir. Eski klasörler değiştirilmez.

| Klasör | Tarih | Örneklem | Rapor |
|---|---|---|---|
| 01_on_analiz_54kisi_12Kasim | 12 Kasım 2026 | Set 3: 54 kişi, 18 grup (4 oturum) | ch3_on_analiz_raporu_set3.md |
| 02_analiz_84kisi_17Kasim | 17 Kasım 2026 | Set 1: 84 kişi, 28 grup; Set 3: 78 kişi, 26 grup (5 oturum) | ch3_analiz_raporu_84kisi_17Kasim.md |
| 03_fiyat_dikkat_84kisi_18Kasim | 18 Kasım 2026 | 84 kişi (dummy'li) | OKUBENI_bulgular.md |
| 04_analiz_117kisi_19Kasim | 19–20 Kasım 2026 | 117 kişi, 39 grup (7 oturum), kimse çıkarılmadı, dummy'li; Set 3 (111) sağlamlık | **ch3_nihai_sonuclar_117kisi.md** (nihai sonuçlar), ch3_analiz_raporu_117kisi_19Kasim.md (teknik rapor) |

Ana örneklem (18 Kasım kararı): tüm katılımcılar, ilerletmeler dummy ile işaretli; Set 3 sağlamlık kontrolü. (17 Kasım ve öncesinde öneri Set 3 idi.) İlerletilen 4 kişinin katkı ve anket/bağış değerleri oTree varsayılanı olan 0 ile kayıtlı; 04 klasöründen itibaren bu anket/bağış değerleri eksik (NaN) kodlanıyor, katkı kararları dummy ile işaretli.

Veri kaynağı: ../experiment_data/tüm_veri.xlsx ve ../experiment_data/sessions/gerçek_*/otree_ciktilari/*PageTimes*.csv
Yeni oturum eklendiğinde: son klasörü kopyalayıp yeni adla (03_analiz_<N>kisi_<tarih>) çalıştırın; kodlar tüm_veri.xlsx'i doğrudan okur.
Raporların bir kopyası claude.ai "tez" Project'inde de var: tez/veri_analizleri/

Not: 01 klasoru arsivdir; icindeki kodlar ../tüm_veri.xlsx yolunu kullanir ve 54 kisilik sonucu uretmek icin yazilmistir. Yeniden calistirmak gerekirse orijinal klasor experiment_data/on_analiz_set3_12Kasim/ kullanilmali (tüm_veri.xlsx artik 84 kisiyi icerdigi icin sonuc 54 kisiyle birebir ayni cikmaz; 17Kasim oncesi yedek: experiment_data/sessions/ham_2026-11-17_tum_oturumlar/tüm_veri_17Kasim_oncesi_yedek.xlsx).
