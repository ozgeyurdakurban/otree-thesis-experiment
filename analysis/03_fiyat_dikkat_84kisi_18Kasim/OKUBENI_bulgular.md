# sigma ≈ 0 mı, fiyat dikkatsizliği mi? Dolaylı testler (18 Kasım 2026)

**Örneklem:** 84 katılımcı, 28 grup, 1512 karar. Kimse çıkarılmadı.
- `adv_dec`: karar ilerletildi (69 karar).
- `adv_grp`: ilerletilen grup (2 grup, 6 kişi).
- `partner_adv`: o tur komşulardan biri ilerletildi.

Set 3 (78 kişi) sağlamlık kontrolü olarak `01_cikti_set3.txt` dosyasında. Sonuçlar aynı.

**Mantık:** Fiyat dikkatsizliği, leaf'in fiyat avantajına tepkisinin deneyimle ve düşünmeyle artacağını öngörür. Saf tercih (σ ≈ 0) bunu öngörmez. Cobb–Douglas Star içinde leaf − centre farkını yaklaşık +3 jeton öngörüyor.

| Test | Sonuç (84 kişi) |
|---|---|
| A. Leaf − centre, Star'ın oynandığı bloğa göre (1/2/3) | −0,57 / +0,01 / −0,02 jeton. Hepsi anlamsız. Blok başına eğilim +0,27 (p = 0,50) |
| B. Star bloğu içinde turlarla değişim | Tur başına −0,04 (p = 0,84) |
| C. Düşünme tipi (Control/Cycle'daki ortalama log süre, 1 sd) × leaf | +0,34 jeton (p = 0,28) |
| D. σ̂, Star'ın oynandığı bloğa göre | −0,12 / 0,01 / 0,01. Üst güven sınırları 0,16 / 0,34 / 0,28 |
| D'. Düşünme tipi +1 sd → σ̂ değişimi | +0,15 (se 0,08, p = 0,068). Sınırda |
| E. Kişi düzeyinde leaf − centre dağılımı | Simetrik: +2 jeton ve üstü 15 kişi, −2 jeton ve altı 20 kişi (p = 0,50). Fiyata tepki veren bir sağ kuyruk yok |
| E'. \|leaf − centre\| ≥ 3 olanların oranı | **DÜZELTİLDİ (03 kodu).** Kişi içi serbest permütasyonla p = 0,027 bulunmuştu; ancak bu null yanlış. Doğru randomizasyon nulliyle (centre şemaları (1,4), (2,5), (3,6) grup içinde yer değiştirilerek) fazlalık yok: gözlenen %25,6, null %23,5, p = 0,33 |

**Okuma:**
1. Deneyimle ya da blok içinde öğrenilen bir fiyat tepkisi yok. Star'ı en son oynayanlarda bile σ ≤ 0,3; Cobb–Douglas (σ = 1) her koşulda dışlanıyor. Bu, deneyimle ya da çabayla giderilebilen bir dikkatsizlik açıklamasına karşı kanıt.
2. Tek zayıf işaret: Control ve Cycle'da yavaş karar verenler biraz daha fiyata duyarlı (p ≈ 0,07). Etki küçük: +1 sd düşünme tipi σ'yı yaklaşık 0,15 artırıyor.
3. (Düzeltildi) Kişi düzeyindeki leaf − centre farkları büyük ölçüde şansla uyumlu. Yalnızca farkların varyansında sınırda bir fazlalık var (grup × tur etkisi çıkarıldıktan sonra p = 0,054).
4. Ayrılamayan kısım: kalıcı bir sezgisel kural ("pozisyondan bağımsız olarak X ver") ile σ ≈ 0 gözlemsel olarak eşdeğer.

**Sınırlılıklar:**
- Star'ın oynandığı blok gruplar arası bir değişken (9 / 9 / 10 grup). Bu yüzden A ve D testlerinin gücü düşük.
- Düşünme tipi Star'dan önce ölçülüyor, ama dışsal değil.
- C'deki o tura ait süre endojen; yalnızca betimsel.

---

# Rol kanalı (02 ve 03 kodları)

**Ekrandaki bilgi yapısı:**
- Leaf yalnızca centre'ın katkısını görüyor; diğer leaf'i görmüyor.
- Centre iki leaf'in toplamını görüyor.
- Normal pozisyon diğer iki kişinin toplamını görüyor.
- Karar ekranında kazanç formülü (÷2 ya da ÷3) her turda açıkça yazılı. Bu yüzden fiyatın "hiç fark edilmemesi" pek olası değil; ancak hesaplanmaması mümkün.

| Test | Sonuç (84 kişi; Set 3 aynı) |
|---|---|
| Önceki turda görülen komşu ortalamasına tepki (birey FE) | Control/Cycle: +0,30 (p < 0,001). Star'da leaf: +0,12 (p = 0,06). Star'da centre: +0,06 (p = 0,59) |
| Plasebo: leaf'in görmediği diğer leaf'e tepki | −0,07 (p = 0,34). Sahte grup korelasyonu yok |
| Rol geçişi asimetrisi (centre → leaf −0,44; leaf → centre +0,11) | Önceki katkı ve görülen sinyal kontrol edilince kayboluyor (p = 0,46). Ortalamaya dönüş |
| Sosyal etki kanalı: bir jetonun diğerlerine getirisi centre'da 1,5, normalde 1,0, leaf'te 0,5 | Kişi düzeyi leaf − centre, centre − normal ve leaf − normal farkları B̂, Likert, bağış ve SVO ile ilişkisiz (en güçlüsü centre − normal ile Likert arasında ρ = −0,20, p = 0,08; beklenenin ters yönünde) |
| Rol farkının dağılımı (doğru randomizasyon nulli) | Ortalama fark yok (p = 0,65). \|fark\| ≥ 3 oranında fazlalık yok (p = 0,33). Varyansta sınırda fazlalık var (ham p = 0,014; grup × tur etkisi çıkarılınca p = 0,054) |

**Okuma:** Star pozisyonu katkıyı ne fiyat, ne sosyal etki, ne de bireysel prososyallik kanalıyla değiştiriyor. Star'ın verideki tek izi koşullu işbirliğinin zayıflaması: görülen komşu davranışına tepki Control/Cycle'daki 0,30'dan Star'da 0,06–0,12'ye düşüyor. Buna kararların yavaşlaması (karar süreleri) da ekleniyor.

Olası mekanizma: Roller her tur döndüğü için önceki turda görülen kişi ile bu turun komşusu çoğu zaman aynı değil. Referans grubu sabit olmadığında karşılıklılık zayıflıyor.

Bu bir hipotez; şu an önceden belirlenmiş değil, keşifsel olarak raporlanmalı.
