# Güncel tez modelinin deney verisiyle bağımsız sınanması

13 Kasım 2026. Ana örneklem: Set 3, 54 katılımcı, 18 bağımsız grup, 972 kişi-tur gözlemi. Bu çalışma keşifseldir; ön kayıtlı bir doğrulama analizi değildir. Önceki YZ'nin hesaplamaları yeniden kullanılmadan veri dosyasından hesaplanmıştır. Tez ve kaynak veriler değiştirilmemiştir.

**Sonuç:** Veri, pozitif ve çoğunlukla ara düzeyde katkıyı ve bireysel davranışın sürekliliğini gösteriyor. Buna karşılık sabit bireysel prososyal ağırlık ve denge varsayımları altındaki Cobb–Douglas referans modelinin konumlar arası eşit katkı payı kısıtı güçlü biçimde desteklenmiyor. İzin verilen parametrelerle incelenen CES seçenekleri referans modelden daha iyi öngörü veriyor; ancak kişinin düzenli ağdaki katkısını Star'da da sürdürmesi şeklindeki basit alternatifi geçemiyor. Dolayısıyla bu veriye dayanarak etki temelli CES mekanizmasının doğrulandığı söylenemez. Genel CES ailesinin bütün heterojen biçimlerinin reddedildiği de söylenemez.

**1. Sınanan teori ve kapsam**

Dayanak, `savunma/chapters/ch2_theory.tex` içindeki genel en iyi tepki, ağ oyunu, heterojen ağırlıklar, konumsal sıralamalar, tanımlama ve H1–H5 özetidir. Güncel genel model CES'tir; Cobb–Douglas sigma=1 referans durumudur. B_i prososyal ağırlık, lambda_i etki ağırlığıdır. Altruizm bu parametrelerden türetilir; B_i tek başına altruizm değildir.

Modelin içsel en iyi tepkisi:

    c_i = min(15, pi_i W_i / theta_i)
    W_i = 15 + (1.5/d_i) S_i
    theta_i = 1 - 1.5/d_i
    odds(pi_i) = odds(B_i)^sigma [theta_i / (1+lambda_i(Lambda_i-1))]^(1-sigma)

S_i açık komşuluğun katkı toplamıdır; kişinin kendi katkısını içermez. Düzenli ağ/merkez/çevre için theta sırasıyla 0.50/0.50/0.25, Lambda ise 2/2.5/1.5'tir.

Sigma=1 durumunda pi_i=B_i olur ve lambda davranıştan çıkar. Sabit B_i ve doğru beklentiler/denge altında aynı kişinin katkı payı konumlar arasında aynı olmalıdır. Eşit B varsayımı altındaki çevre-merkez sıralaması ile heterojen B_i'lerle kurulmuş oyunun öngörüsü aynı sınama değildir. Bu yüzden ortalama karşılaştırmasına ek olarak bireysel ağırlıklarla model öngörüsü hesaplandı.

**2. Veri ve çıkarım**

Ana dosya `tüm_veri.xlsx`; üç sayfa sırasıyla 60/56/54 katılımcı ve 1080/1008/972 satır içeriyor. Set 3, yönetici tarafından ardışık ilerletilen kişilerin bulunduğu grupları bütünüyle dışlıyor. Set 2 tamamlanmamış gruplar içerdiğinden yalnız duyarlılık analizi olarak ele alındı.

Dört gerçek oturumun ham oTree dışa aktarımlarındaki 1080 katkı ve tur getirisi, birleştirilmiş dosyayla birebir eşleşti. Set 3'te:

- Her kişi 18 tur, her grup-tur 3 kişi içeriyor; yinelenen kişi-tur kaydı yok.
- Her kişi Star'da iki tur merkezde. İlerletilmiş katkı kaydı yok.
- Getiri formülünün azami mutlak hatası sıfır.
- Katkıların %13.58'i sıfır, %3.19'u 15; %83.23'ü iki sınırın arasında.

Bağımsız çıkarım birimi 18 gruptur; 972 satır bağımsız örneklem sayılmadı. Eşleştirilmiş grup farkları için Student-t güven aralıkları (17 serbestlik derecesi), iki taraflı işaret testi ve işaret çevirme testi hesaplandı. İşaret çevirme, simetrik farklar varsayımına dayanır; deneyin atama mekanizmasından türetilmiş kesin bir randomizasyon testi değildir. Birey sabit etkili regresyonlar blok sırası ve blok içi turu kontrol eder; standart hatalar grupta kümelenir, CR1 düzeltmesi ve G-1 serbestlik derecesi kullanılır.

**3. Doğrudan konum ve ağ karşılaştırmaları**

| Konum/koşul | Ortalama katkı | Ortalama katkı payı |
|---|---:|---:|
| Control | 5.741 | 0.13745 |
| Cycle | 5.719 | 0.13501 |
| Star merkez | 6.231 | 0.14956 |
| Star çevre | 5.801 | 0.07374 |

| Grup düzeyinde katkı farkı | Fark | %95 güven aralığı | İki taraflı p |
|---|---:|---:|---:|
| Cycle - Control | -0.022 | [-0.993, 0.950] | 0.963 |
| Çevre - merkez | -0.431 | [-1.156, 0.295] | 0.227 |
| Çevre - düzenli | 0.071 | [-0.691, 0.833] | 0.846 |
| Merkez - düzenli | 0.502 | [-0.408, 1.411] | 0.261 |

“Düzenli”, Control ve Cycle ortalamalarının eşit ağırlıklı ortalamasıdır. Control-Cycle farkı için sonradan seçilen +/-1 jetonluk eşdeğerlik sınırı kullanılırsa TOST p=0.0243. Bu yalnızca bu genişlikteki farkların dışlanmasını destekler; tam eşitlik kanıtı değildir. Üç kişide C3=K3 olduğundan karşılaştırma esas olarak çerçeve/görsel sunum farkını inceler.

Çevrenin merkezden daha fazla vermesi mevcut örneklemde desteklenmiyor. Ancak güven aralığı küçük pozitif farkları içeriyor. Bu yüzden tüm CES ailesindeki her pozitif çevre priminin reddedildiği söylenemez. Ayrıca teorideki eşit B koşulunun örneklemde sağlandığı varsayılmamalıdır.

**4. Referans modelin en açık sınaması: katkı payı eşitliği**

Çevre-düzenli katkı payı farkı -0.06249; %95 güven aralığı [-0.07475, -0.05023]. 18 grubun tamamında negatif. İki taraflı işaret testi p=0.00000763. Çevre-merkez pay farkı da 18 grubun tamamında negatif: ortalama -0.07582.

Birey sabit etkisi, blok sırası ve blok içi tur kontrol edildiğinde çevre-Control pay farkı -0.06454; %95 güven aralığı [-0.08029, -0.04879]. Katkı miktarında aynı çevre-Control katsayısı 0.012 jeton; güven aralığı [-0.928, 0.952]. Yani konum değişimi esas olarak teorinin beklediği miktar artışına dönüşmüyor; buna karşılık düşük fiyatla hesaplanan pay düşüyor.

Duyarlılık kontrolleri:

- Her bloğun yalnız son üç turunda çevre-düzenli pay farkı -0.05976; güven aralığı [-0.07800, -0.04152].
- Yalnız 1–14 katkıları tutulduğunda, birey sabit etkili çevre-Control pay katsayısı -0.07295. Bu seçim katkı sonucuna göre yapıldığı için ana tahmin değil, duyarlılıktır.
- Set 1 ve Set 2'de çevre-düzenli pay farkı sırasıyla -0.05832 ve -0.06226; her iki sette de 20 grubun tamamında negatif.
- Bugünkü komşuların önceki tur katkıları beklenen S_i yerine konduğunda fark -0.05893; güven aralığı [-0.07310, -0.04477]. Bu yalnız bir olası beklenti kuralıdır, ölçülmüş beklenti değildir.

Bu sonuç Cobb–Douglas + sabit tercihler + kullanılan bilgi/denge yorumunun ortak kısıtına güçlü biçimde aykırıdır. Sadece tercih fonksiyonunu, beklentiler ve denge davranışından bağımsız olarak reddeden bir deney değildir. Pay farkı düşük theta nedeniyle benzer miktarlarda mekanik olarak oluşabilir; bu mekaniklik bulgunun teorik önemini ortadan kaldırmaz, çünkü teori miktarın bu fiyat farkını telafi edecek yönde değişmesini gerektirir.

**5. Heterojen tercihlerle öngörü sınaması ve basit alternatif**

Her kişinin Control/Cycle katkı payı yalnız bu koşullardaki verilerle hesaplandı. Cobb–Douglas'ta bu B_i kalibrasyonu oldu. CES'te aynı pay doğrudan B_i sayılmadı; her sigma/lambda için CES denkleminden uygun tercih terimi geri çıkarıldı. Böylece sigma=1 dışındayken B_i=pay hatası yapılmadı.

Her gerçek Star rol ataması için üç kişilik denge, sınırlı en iyi tepki iterasyonu ile çözüldü. Sınırsız çözüm sonradan kırpılmadı. Çözücü ortak B=0.10 için analitik merkez=4.468085, çevre=7.340426 değerlerini ve yüksek paydaki tam katkı köşesini yeniden üretti; hesaplanan dengelerin en iyi tepki kalıntısı 1e-7'nin altında tutuldu.

CES karşılaştırması ortak sigma ve ortak lambda, fakat bireysel B_i varsayıyor. Sigma için 0.001–5 arasında 16, lambda için 0–100 arasında 9 değer tarandı. Bu bir kısıtlı öngörü taramasıdır; bütün CES ailesi için maksimum olabilirlik tahmini veya güven aralığı değildir. Her grup sırayla dışarıda bırakıldı: sigma/lambda kalan 17 grubun Star sonuçlarından seçildi; dışarıda kalan grubun Star'ı yalnız kendi Control/Cycle davranışı ve diğer gruplardan seçilen parametrelerle öngörüldü. Bu nedenle kişiler tamamen yeni değildir; ağlar arası aktarım sınanır.

Hata, 54 kişinin merkez ve çevre ortalamaları üzerinden, 108 kişi-konum değeri eşit ağırlıkla hesaplandı. Düşük RMSE daha iyi öngörüdür.

| Öngörü | Toplam RMSE | Merkez RMSE | Çevre RMSE | Öngörülen çevre ortalaması |
|---|---:|---:|---:|---:|
| Cobb–Douglas | 4.499 | 3.264 | 5.461 | 10.360 |
| Grup dışarıda bırakmalı CES | 2.608 | 2.834 | 2.360 | 5.809 |
| Kişinin Control/Cycle katkısını aynen sürdürmesi | 2.530 | 2.772 | 2.262 | 5.730 |
| Gözlenen çevre | — | — | — | 5.801 |

Cobb–Douglas, özellikle çevrede fazla katkı öngörüyor. Bireysel heterojenliğin kalibrasyona dahil edilmesi bu sorunu çözmüyor. CES daha iyi uyuyor; fakat basit katkı sürekliliği alternatifi daha düşük hata veriyor. Bu son farkın küçük olması ve 18 küme nedeniyle basit alternatifin evrensel üstünlüğü iddia edilmemeli; temel sonuç CES için ek öngörü üstünlüğü gösterilememesidir. CES'in grup dışarıda bırakma eğitim kümeleri örtüştüğünden model kayıp farklarının testleri de keşifsel okunmalıdır.

Tarama her dışarıda bırakılan grupta alt sınıra, sigma=0.001 ve lambda=0'a yöneldi. Alt sınırı 0.01'den 0.001'e düşürmek toplam RMSE'yi yalnız 2.610'dan 2.608'e indirdi. Bu bir iç optimum veya kesin sigma tahmini değildir. Negatif sigma kullanılmadı.

Önemli yorum: “Sigma sıfıra yakın, öyleyse Leontief tercihler doğrulandı” denemez. Aynı düzenli ağ payını korumak için B_i de sigma ile değiştiriliyor; örneğin sigma=0.01, lambda=0 altında ortanca geri çıkarılan B yaklaşık 8.8e-51 oluyor. Bu, sabit ve sonlu B ile alınmış basit Leontief limiti değildir. Çok küçük sigma ile aşırı küçük B değerleri benzer payları açıklayabilir. Veri düşük sigma yönünde esneklik sağlıyor; parametrelerin davranışsal yorumunu tek başına sabitlemiyor.

**6. Diğer temel öncüller**

Katkılar çoğunlukla sınırların arasında. Bu, ara düzeyde ve heterojen katkıyı modelleme ihtiyacını destekler; CES'i başka eğrisel tercihlerden, eşitsizlik kaygısından veya davranış kurallarından ayırt etmez. %13.58 sıfır katkı, pozitif B'li deterministik sürekli modelde doğrudan üretilmez; tamsayılaştırma, karar hatası veya sıfır B kütlesi gibi bir gözlem modeli gerekir.

Bağış ortalaması %81.15, tam bağış oranı %61.11; bağışla ortalama katkı arasındaki Spearman ilişki -0.0436. Düzenli ağdaki pay ise yaklaşık %13.62. Aynı B'nin doğrudan bağışta da gözlendiği güçlü proxy varsayımı desteklenmiyor. Bu, kişinin hiçbir prososyal tercihi olmadığı anlamına gelmez; ölçümün bağlamlar arasında aynı parametreyi yakaladığı gösterilemiyor. H1 ve H5 için bağımsız B ölçümünün zayıflığı sürüyor. Control/Cycle katkısından çıkarılan parametreyle Star katkısı arasındaki ilişki tek başına H1'in nedensel doğrulaması değildir. H5'i yalnız “B ile çevre-merkez farkının korelasyonu”na indirgemek de tezin eşik önermesinin doğrudan testi değildir; heterojen denge öngörü karşılaştırması bu çalışma içinde daha uygun bir kontrol sağlar.

Katkı ilk üç turda 6.815, son üç turda 4.772; grup düzeyinde azalma -2.043 jeton, güven aralığı [-3.141, -0.946]. Blok/tur kontrollerinde azalma sürüyor. Dolayısıyla statik denge yorumuna dinamik bir sınırlama var.

Kendi gecikmeli katkısı ve aynı turda bağlı olduğu komşuların önceki tur ortalamasıyla kurulan birey sabit etkili modelde komşu katsayısı 0.128; güven aralığı [0.0015, 0.2547], p=0.0476. Bu yön, tamamlayıcılıkla uyumlu bir ilişki gösteriyor. Kısa panelde gecikmeli bağımlı değişken yanlılığı ve ortak şoklar nedeniyle nedensel stratejik tamamlayıcılığın kanıtı veya yapısal en iyi tepki eğiminin tahmini sayılmadı.

Gerçekleşen maddi etkinlik, sıfır katkı ve tam katkı kıyasları arasında normalize edildiğinde Control=0.383, Cycle=0.381, Star=0.406. Star-Control farkı 0.023; güven aralığı [-0.044, 0.090]. Maddi etkinlik farkı saptanmadı; sıfır etki kanıtlanmadı. Buradaki “sıfır katkı kıyası”, prososyal modelin Nash dengesi değil, tamamen maddi oyunun sıfır katkı kıyasıdır.

**7. Tezin sorularına cevap ve sınırlar**

RQ1: Bu üç kişilik uygulamada Control/Cycle sunumu ve Star yapısı arasında belirgin ortalama katkı farkı görünmüyor. Sonuç diğer ağ büyüklüklerine genellenemez.

RQ2: Fiyatı düşen çevrede referans modelin beklediği büyüklükte katkı artışı oluşmuyor. Bireysel heterojenlik kullanılarak üretilen Cobb–Douglas öngörüleri de özellikle çevrede fazla yüksek kalıyor. Bu, referans açıklama açısından gerçek bir öngörü sorunudur.

RQ3: Davranışın bireysel sürekliliği mevcut olsa da B'nin bağımsız ölçümü ve konum-tercih mekanizmasının ayrılması eksik. Maddi etkinlik farkı belirsiz. Modeldeki altruizm katsayısı veya etki ağırlığı bu analizde güvenilir biçimde tanımlanmış kabul edilmedi.

Olası açıklamalar: dengeye ulaşmama ve öğrenme; konumun maddi sonuçlarının yeterince kullanılmaması; katkı miktarını sabit tutan karar kuralları; bağlama göre değişen tercihler; modelde olmayan eşitsizlik/karşılıklılık güdüleri. Karar süreleri tek başına teşviklerin anlaşıldığını kanıtlamaz. Nakit yerine ders puanı kullanıldığı önceki konuşmada belirtilmişti; bu çalışma fiili ödeme/teşvik protokolünü bağımsız belgelemediğinden bunu doğrulanmış veri özelliği olarak kabul etmiyor. Protokol tezde yazılırken ayrıca doğrulanmalı.

Bu analiz, “tercihler mutlaka Leontief'tir”, “etki ağırlığı kesin sıfırdır”, “konumun hiçbir etkisi yoktur” veya “yeni veri sonucu değiştiremez” sonuçlarını desteklemiyor. Daha fazla bağımsız grup hassasiyeti artırabilir; beklentilerin ölçülmemesi ve mekanizmaların ayrıştırılamaması ise yalnız örneklem büyüterek çözülmez.

Yeniden üretim: Aynı klasördeki `analiz.py` birleştirilmiş dosyayı ve dört ham gerçek oturum dışa aktarımını okur; sonuçları `sonuclar.json` ve konu bazlı CSV dosyalarına yazar. Pandas/numpy/openpyxl gerekir. `model_ongoru.csv` öngörü hatalarını, `grup_testleri.csv` üç örneklemdeki karşılaştırmaları, `birey_sabit_etki.csv` kontrolleri, `pay_duyarlilik.csv` alternatif bilgi varsayımlarını içerir. Kaynak dosyalara yazmaz.
