# Sunum Rehberi — "Hocaya bunu ben sunacağım" (5-6 dakika)

> Bu metin konuşma diliyle yazılmıştır. Okuyarak da sunulabilir. Her adımda uygulamada neye tıklayacağıın da yazıyor.

---

## 1. Giriş (30 saniye)

**Söyle:**
> "NASA'nın bize verdiği görev şuydu: Ay'a veya Mars'a üs kurmayı düşündüğümüz yerlere benzeyen Dünya sahalarını, açık uydu verisiyle bulmak. Çünkü astronotlar Ay'a çıkmadan önce ekipmanlarını Dünya'da benzer yerlerde test ediyor. Ama hangi Dünya yeri gerçekten benzer? Biz bunu cevaplayan bir sistem yaptık."

---

## 2. Yaklaşım (1 dakika)

**Söyle:**
> "Önce görevin içindeki kritik cümleyi okuduk: 'Hiçbir Dünya yeri Ay'ı kusursuz yeniden üretemez.' Doğru — Dünya'da Ay'ın yerçekimi, vakumu ve radyasyonu yok. O yüzden 'en benzer TEK yer' diye aramadık. Her sahayı üç başlıklı çerçevede AYRI AYRI ele aldık:
> 1. **Arazi (Mobilite)** — eğim, pürüzlülük, yükseklik farkı (rover gidip gidemeyeceği; Ay `5 m/px` LOLA, Dünya `30 m/px` GLO-30 DEM) — **v1'de aktif**
> 2. **Yüzey** — geniş bant albedo / parlaklık (zemin malzemesinin ipucu) — **v1'de aktif**
> 3. **Sıcaklık (Termal)** — yüzey sıcaklık genliği (`Karar #30` gereği v1'de PDS tam-gün döngüsü hizalaması yapılana kadar **askıda / `NaN`**, sayısal skora katılmıyor)
>
> Aktif iki eksendeki her puana ölçüm hatasını da ekledik — yani sadece tek bir sayı demiyoruz, P5–P95 Monte Carlo belirsizlik aralığını da gösteriyoruz."

**Uygulamada:** Ayarlar paneli ve Eksen Grafikleri sekmesi gösterilir — Mobilite ve Yüzey aktif çubukları, Sıcaklık ise açıkça **askıda (`NaN`)** notuyla görünsün.

---

## 3. Canlı Demo (3 dakika)

### Adım 1 — Referansı seç
**Uygulamada:** Sol panelden **"Shackleton Krateri Kenarı"** seç. (Ay güney kutbu, NASA'nın Artemis görevinin iniş bölgesi.)

**Söyle:**
> "Referansımız Ay güney kutbundan gerçek NASA bölge adayları — Artemis III'ün iniş için incelediği ROI'ler. Yani Ay tarafı uydurma değil; NASA'nın kendisinin baktığı koordinatlar."

### Adım 2 — Skorlara, Görev Re-weighting'e ve Portföy Kartına bak
**Uygulamada:** **📊 Skor & Portföy** sekmesini aç. Dengeli modda en üst satırı ve tablonun hemen altındaki kompakt **Portföy Kartı**'nı göster; ardından sol panelden **Rover Hareket Testi**'ne geçirip sıranın değişimini göster.

**Söyle:**
> "Dengeli ağırlıkta 40 Dünya sahası içinde ilk sırada **Karapınar Meke Krateri (`0.528`, P5–P95: `0.406–0.569`)** var, ancak gücü esasen **Yüzey (`0.903`)** ekseninden geliyor, **Mobilite (`0.153`)** düşük. Sol menüden görevi **Rover Hareket Testi**'ne çektiğimizde ise **Hasandağı Keçikaleçik (`0.446`)** öne geçiyor — çünkü artık aynı sahaları seçtiğimiz ekipmanın ihtiyacına göre ağırlıklandırıyoruz. Tablonun hemen altındaki **Portföy Kartı** da tek bir yer yerine aktif eksenleri en az sahayla tamamlayan grubu ve Dünya'da kapatılamayan ya da v1'de askıda kalan (`Termal`) eksenleri açıkça simülasyon/laboratuvara yönlendiriyor."

### Adım 3 — Harita ve Gerçek 3D Arazi
**Uygulamada:** Önce **🗺️ Harita** sekmesine geç (mavi dış halka = 10 doğrulama sahası, yeşil–kırmızı dolgu = skor), ardından kısaca **⛰️ 3D Arazi** sekmesini aç.

**Söyle:**
> "40 Dünya sahasının tamamı haritada: mavi halkalı 10 saha literatürdeki bilinen analoglar, dolgu rengi ise aktif skoru gösteriyor. **3D Arazi** sekmesinde ise yapay örnek yüzey yerine doğrudan taahhüt edilmiş gerçek **5 m/px LOLA** Ay yükselti gridini ve **30 m/px Copernicus GLO-30** Dünya topografyasını (`~2.2 km` pencere) yan yana inceliyoruz."

### Adım 4 — Neden benzer / neden değil & Çevrimdışı Görsel Karşılaştırma
**Uygulamada:** **📡 Eksen Grafikleri** veya **⚠️ Analojinin Sınırları** sekmesinden sahayı (ör. **Karacadağ** veya **Karapınar Meke**) seç; 3 panelli görseli ve alttaki özellik fark tablosunu göster.

**Söyle:**
> "Bir sahanın hangi eksende güçlü, hangisinde zayıf kaldığını ayrı ayrı gösteriyoruz; termal eksen `Karar #30` ile v1'de bilinçli olarak **askıda (`NaN`)** bırakıldığı için uyumsuz gündüz–gece verilerini puanın içine zorla sokmuyoruz. Görsel inceleyicide ise internet kesilse bile çalışan yerel **5 m LOLA kabartma**, **LOLA eğim-tehlike haritası** ve **10 m Sentinel-2 L2A** uydu görüntüsünü bulutluluk ve çekim tarihiyle gösteriyoruz — görseller yalnızca nitel bağlamdır, asla sayısal skora girmez."

### Adım 5 — Analojinin Sınırları
**Uygulamada:** **⚠️ Analojinin Sınırları** sekmesinin alt bölümü.

**Söyle:**
> "Bu bölüm, Dünya'da sahadan ASLA test edilemeyecek şeyleri listeliyor: yerçekimi (1.62 m/s²), vakum, radyasyon, 29.5 günlük Ay gün–gece çevrimi ve nitel su buzu / lav tüpü / elektrostatik toz faktörleri. Yani sistemimiz 'burada test edin' dediği şeyi, 'burada test edemezsiniz' diye de sınırlıyor."

### Adım 6 — Betimsel Sıra Tanısı (Doğrulama sekmesi)
**Uygulamada:** **🧭 Sıra Tanısı (Doğrulama)** sekmesi — 10 doğrulama sahası için kaynaklı beklenen eksen, nitel E8 buz/permafrost durumu ve tıklanabilir DOI tablosu.

**Söyle:**
> "Burada literatürden bilinen 10 Dünya analogunu — Etna, Atacama, McMurdo, Haughton Krateri gibi — skorlayıcıya rol etiketi vermeden aynı 40 sahalık havuz içinde puanladık ve `docs/validation_expectations.md` içinde önceden kaydettiğimiz DOI kaynaklı beklenen eksenlerle karşılaştırdık. Örnek olarak Etna mobilitede **#3 / 40**, McMurdo Wright Vadisi yüzey parlaklığında **#2 / 40** çıkıyor. Önemli bir dürüstlük notu: 40 Dünya sahasının tamamı Z-ölçeklemesine katıldığı için bu ekran **bağımsız bir holdout doğrulaması değildir**; yöntemin bilinen sahaları beklendiği eksenlerde yukarı taşıyıp taşımadığını ve hangi fiziksel koşullarda kırıldığını gösteren bir **betimsel sıra tanısıdır**."

---

## 4. Güvenilirlik bölümü (1 dakika) — "gerçekten güvenilir mi?" sorusunun cevabı

**Söyle:**
> "Üç katmanlı şeffaflık:
> 1. **Her sayının kaynağı ve çözünürlüğü yazılı.** Eğim puanı hangi uydu DEM'inden (`5 m` LOLA vs `30 m` GLO-30), albedo hangi sensörden (`1000 m` LOLA vs `500 m` MODIS) — hepsi veri dosyasında `_src` ve `_res_m` sütunlarıyla etiketli.
> 2. **Sorumlu veri disiplini uyguladık.** Skorlama formüllerini çapraz doğruladık (`pytest` tüm birim ve uygulama testleri geçiyor) ve Ay `temp_amplitude` ürününde PDS `.lbl` etiketlerinden yakaladığımız tanım uyuşmazlığını zorlamak yerine `Karar #30` ile termal ekseni v1'de temiz şekilde `NaN` (askıda) bıraktık.
> 3. **Belirsizliği saklamıyoruz.** Ölçüm hatası olan her sayı P5–P95 Monte Carlo aralığı olarak gösteriliyor; verisi olmayan veya ortak tanımı henüz kurulmayan özelliklere (`thermal_inertia`, v1 Moon `temp_amplitude`) '0' yazmıyoruz, bilinçli olarak boş (`NaN`) bırakıyoruz.
>
> Kısacası: abartılı iddialar yerine sınırları bilinen, savunulabilir bir tarama aracı kurduk."

---

## 5. Kapanış (30 saniye)

**Söyle:**
> "Özet: Tek bir Dünya yeri Ay'ı temsil edemiyor — ama farklı Dünya sahaları farklı görev eksenlerini tamamlayan bir test portföyü oluşturabiliyor. Sistemimiz, bir görev planlayıcısına 'bu yeteneği hangi sahada, hangi sınırlar içinde test etmeliyim?' sorusunu veriyle cevaplıyor. 40 Dünya sahası, 5 Ay bölgesi, aktif Mobilite & Yüzey eksenleri, askıda olduğu dürüstçe işaretlenmiş Termal başlığı ve gerçek 3D/uydu bağlamıyla tüm sayılar kaynaklı ve belgeli. Teşekkürler."

---

## Olası sorular + hazır cevaplar

**S: Mars neden yok?**
> "Görev metni 'Ay VEYA Mars' diyor. v1'de Ay güney kutbunu seçtik çünkü NASA'nın Artemis verisi ve hazır ROI koordinatları açıkta; yöntemimiz cisim-bağımsız, Mars'a genişletme yolu raporda belgeli."

**S: Bu skorlar ne demek? Olasılık mı?**
> "Hayır, olasılık değil. 0–1 arası bir benzerlik indeksi: 1'e yakın 'bu eksende yakın', 0'a yakın 'farklı'. Görsel benzerlik değil; seçilmiş fiziksel ölçütlerden standartlaştırılmış hesap."

**S: Peki benzerlik eşiği kaç olmalı ki 'analog' diyelim?**
> "Evrensel bir 'analogdur / değildir' eşiği koymadık; sahaları eksen bazında sıralıyoruz ve her sınırı ayrıca belirtiyoruz. Skor Tablosu altındaki Portföy Kartı'nda gördüğünüz `0.70` değeri ise kalibre edilmiş fiziksel bir yeterlilik sınırı değil, eksen kapsamını özetlemek için kullanılan sezgisel bir indeks ayarıdır (`docs/data_notes.md`)."

**S: Veriler gerçek mi? Kendi verinizi mi kullandınız?**
> "Hepsi NASA ve ESA'nın açık arşivleri: LOLA (`5 m/px` Ay yüksekliği ve `1 km` albedo), Diviner (`240 m` Ay sıcaklık), Copernicus GLO-30 (`30 m` Dünya yüksekliği), MODIS (`1 km` Dünya sıcaklık, `500 m` albedo) ve Sentinel-2 L2A (`10 m` yalnızca görsel bağlam için; sayısal skora girmez). Çözünürlükler ve açık tanım sınırları `docs/data_notes.md` içinde belgeli."

**S: Sıcaklık puanları neden v1'de askıda (`NaN`) ve neden hesaplanmıyor?**
> "`docs/data_notes.md` (`Karar #30`) içinde belgelediğimiz üzere, mevcut PDS LRO Diviner `ltim` dilimi ile Dünya `MOD11A2.061` yıllık ortalama gündüz–gece sıcaklık farkı birebir aynı günlük çevrim tanımına oturmuyor. Yanlış ya da elmayla armutu kıyaslayan bir skor göstermek yerine Ay `temp_amplitude` ve `thermal_inertia` değerlerini v1'de temiz biçimde `NaN` (askıda) bıraktık; tam günlük Diviner TBOL entegrasyonu v2 yol haritasında."

**Uygulama açılmazsa (yedek plan):** `report/figures/` klasöründeki ekran görüntüleriyle aynı hikâyeyi anlat — sıra değişmez.
