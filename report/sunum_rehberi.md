# Sunum Rehberi — "Hocaya bunu ben sunacağım" (5-6 dakika)

> Bu metin konuşma diliyle yazılmıştır. Okuyarak da sunulabilir. Her adımda uygulamada neye tıklayacağıın da yazıyor.

---

## 1. Giriş (30 saniye)

**Söyle:**
> "NASA'nın bize verdiği görev şuydu: Ay'a veya Mars'a üs kurmayı düşündüğümüz yerlere benzeyen Dünya sahalarını, açık uydu verisiyle bulmak. Çünkü astronotlar Ay'a çıkmadan önce ekipmanlarını Dünya'da benzer yerlerde test ediyor. Ama hangi Dünya yeri gerçekten benzer? Biz bunu cevaplayan bir sistem yaptık."

---

## 2. Yaklaşım (1 dakika)

**Söyle:**
> "Önce görevin içindeki kritik cümleyi okuduk: 'Hiçbir Dünya yeri Ay'ı kusursuz yeniden üretemez.' Doğru — Dünya'da Ay'ın yerçekimi, vakumu ve radyasyonu yok. O yüzden 'en benzer TEK yer' diye aramadık. Her sahayı üç konuda AYRI AYRI puanladık:
> 1. **Arazi** — eğim, pürüzlülük, yükseklik farkı (rover gidip gidemeyeceği; Ay 5 m/px, Dünya 30 m/px DEM)
> 2. **Sıcaklık** — yüzey sıcaklık genliği (*mevcut sürümde Ay tanımı PDS doğrulaması beklediği için geçici durumda*)
> 3. **Yüzey** — geniş bant albedo / parlaklık (zemin malzemesinin ipucu)
>
> Her puana ölçüm hatasını da ekledik — yani sadece tek bir sayı demiyoruz, belirsizlik aralığını da gösteriyoruz."

**Uygulamada:** Ayarlar paneli gösterilir — üç ölçütün listesi görünsün.

---

## 3. Canlı Demo (3 dakika)

### Adım 1 — Referansı seç
**Uygulamada:** Sol panelden **"Shackleton Krateri Kenarı"** seç. (Ay güney kutbu, NASA'nın Artemis görevinin iniş bölgesi.)

**Söyle:**
> "Referansımız Ay güney kutbundan gerçek NASA bölge adayları — Artemis III'ün iniş için incelediği ROI'ler. Yani Ay tarafı uydurmadır değil; NASA'nın kendisinin baktığı koordinatlardır."

### Adım 2 — Skorlara ve Portföy Kartına bak
**Uygulamada:** Skorlar tablosu aç. En üst satırı ve hemen altındaki kompakt Portföy Kartı'nı göster.

**Söyle:**
> "Mevcut taramada en üst satırda örneğin Bitlis'teki az bilinen bir volkanik saha olan **Süphan Dağı** (~0.37) öne çıkıyor; Etna ve Atacama gibi klasik sahalar da listede. Ancak burada iki şeye özellikle dikkat çekiyoruz: birincisi, mevcut sürümde Ay sıcaklık genliği tanımı doğrulama sürecinde olduğundan bunu kesinleşmiş 'en yakın Ay analogu' değil, daha yakından incelenecek aday havuzu çıktısı olarak okuyoruz. İkincisi, tablonun altındaki **Portföy Kartı** tek bir saha yerine farklı eksenleri tamamlayan kompakt saha grubunu gösteriyor; açıkta kalan koşullar ise laboratuvar/simülasyona bırakılıyor."

### Adım 3 — Harita
**Uygulamada:** Harita sekmesine geç.

**Söyle:**
> "40 Dünya sahası haritada. Nokta boyutu ve rengi mevcut görev ağırlıklı benzerlik indeksini yansıtıyor; aday havuzunda Anadolu volkanik sahaları ve Antarktika çevresi üst sıralarda öne çıkıyor."

### Adım 4 — Neden benzer / neden değil
**Uygulamada:** Görsel Karşılaştırma / Eksen çubuk kartlarını göster.

**Söyle:**
> "Bir sahanın hangi eksende güçlü, hangisinde zayıf kaldığını ayrı ayrı gösteriyoruz. Örneğin bu saha yüzey parlaklığında yüksek (0.85), arazi eğimi/pürüzlülüğünde orta, sıcaklıkta ise çok düşük çıkabiliyor. İki sınırımızı açıkça yazıyoruz: (1) Ay'daki DEM 5 m/px iken Dünya GLO-30 30 m/px çözünürlüktedir; (2) Ay sıcaklık genliği için PDS ürün dilimi doğrulaması sürdüğünden termal eksen şimdilik **geçici tanım** uyarısıyla sunuluyor."

### Adım 5 — Analojinin Sınırları
**Uygulamada:** "⚠️ Analojinin Sınırları" sekmesi.

**Söyle:**
> "Bu sekme, Dünya'da sahadan ASLA test edilemeyecek şeyleri listeliyor: yerçekimi (1.62 m/s²), vakum, radyasyon, 29 günlük Ay gün–gece çevrimi. Bunlar sahadan değil, laboratuvardan doğrulanır. Yani sistemimiz 'burada test edin' dediği şeyi, 'burada test edemezsiniz' diye de sınırlıyor."

### Adım 6 — Betimsel Sıra Tanısı (Doğrulama sekmesi)
**Uygulamada:** Betimsel Sıra Tanısı (Doğrulama) sekmesi — beklenen eksen, gerekçe ve kaynak tablosu.

**Söyle:**
> "Burada literatürden bilinen 10 Dünya analogunu — Etna, Atacama, Haughton Krateri gibi — skorlayıcıya rol etiketi vermeden aynı havuz içinde puanladık ve kaynaklı beklenen eksenleriyle karşılaştırdık. Önemli bir dürüstlük notu: 40 Dünya sahasının tamamı Z-ölçeklemesine katıldığı için bu ekran **bağımsız bir holdout doğrulaması değildir**; yöntemin bilinen sahaları beklendiği eksenlerde yukarı taşıyıp taşımadığını ve hangi fiziksel koşullarda kırıldığını gösteren bir **betimsel sıra tanısıdır**."

---

## 4. Güvenilirlik bölümü (1 dakika) — "gerçekten güvenilir mi?" sorusunun cevabı

**Söyle:**
> "Üç katmanlı şeffaflık:
> 1. **Her sayının kaynağı ve çözünürlüğü yazılı.** Eğim puanı hangi uydu DEM'inden (`5 m` LOLA vs `30 m` GLO-30), albedo ve sıcaklık hangi sensörden — hepsi veri dosyasında `_src` ve `_res_m` sütunlarıyla etiketli.
> 2. **Matematiksel formül ve kaynak denetimi yaptık.** Skorlama formüllerini elle 600'den fazla eşleşme üzerinde çapraz hesapladık (sapma: sıfır). Ayrıca Ay `temp_amplitude` ürününde PDS `.lbl` etiketlerinden yakaladığımız tanım farkını saklamak yerine `docs/data_notes.md` içinde açık engel olarak işaretledik.
> 3. **Belirsizliği saklamıyoruz.** Ölçüm hatası olan her sayı Monte Carlo aralığı olarak gösteriliyor; verisi olmayan veya ortak tanımı kurulmayan özelliğe (`thermal_inertia`) '0' yazmıyoruz, bilinçli olarak boş (`NaN`) bırakıyoruz.
>
> Kısacası: abartılı iddialar yerine sınırları bilinen, savunulabilir bir tarama aracı kurduk."

---

## 5. Kapanış (30 saniye)

**Söyle:**
> "Özet: Tek bir Dünya yeri Ay'ı temsil edemiyor — ama farklı Dünya sahaları farklı görev eksenlerini tamamlayan bir test portföyü oluşturabiliyor. Sistemimiz, bir görev planlayıcısına 'bu yeteneği hangi sahada, hangi sınırlar içinde test etmeliyim?' sorusunu veriyle cevaplıyor. 40 Dünya sahası, 5 Ay bölgesi, üç eksen; her sayı kaynaklı, belirsizliğiyle raporlanmış ve açık sınırlarıyla belgeli. Teşekkürler."

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

**S: Sıcaklık puanları neden düşük ve neden geçici uyarısı var?**
> "İki nedeni var. Fiziksel olarak Ay'da atmosfer olmadığı için kutup gündüz–gece termal döngüsü Dünya ortamlarından çok farklıdır. Teknik olarak da `docs/data_notes.md`'de belgelediğimiz üzere mevcut Ay `temp_amplitude` ürünü (`ltim` yerel saat dilimi seçimi) ile Dünya `MOD11A2.061` yıllık ortalama gündüz–gece farkı birebir aynı günlük döngü tanımına oturmuyor; PDS doğrulaması sürdüğü için termal ekseni şimdilik **geçici tanım** uyarısıyla sunuyoruz ve karar netleşene kadar bu eksene dayanarak kesin sıralama iddiası kurmuyoruz."

**Uygulama açılmazsa (yedek plan):** `report/figures/` klasöründeki ekran görüntüleriyle aynı hikâyeyi anlat — sıra değişmez.
