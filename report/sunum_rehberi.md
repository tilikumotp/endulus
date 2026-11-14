# Sunum Rehberi — "Hocaya / Jüriye Bunu Ben Sunacağım" (5–6 Dakika)

> Bu metin doğrudan konuşma diliyle yazılmıştır. Okuyarak da sunulabilir. Her adımda uygulamada (`streamlit run app/main.py`) neye tıklayacağın da yazıyor.

---

## 1. Giriş (30 saniye)

**Söyle:**
> "NASA'nın bize verdiği görev şuydu: Ay'a veya Mars'a üs kurmayı düşündüğümüz bölgelere benzeyen Dünya sahalarını, açık uydu verisiyle bulmak ve karşılaştırmak. Çünkü astronotlar ve mühendisler Ay'a gitmeden önce rover'ları, radarları ve ekipmanları Dünya'daki benzer arazilerde test ediyor. Ama hiçbir Dünya sahası Ay'ı her yönüyle kopyalayamaz. Biz bu yüzden tek bir puan vermek yerine, sahaları eksen bazında, belirsizliğiyle ve analojinin kırıldığı sınırlarla birlikte analiz eden bir karar destek sistemi kurduk."

---

## 2. Yaklaşım ve Karar #30 Şeffaflığı (1 dakika)

**Söyle:**
> "Görev metnindeki en kritik cümleden yola çıktık: *'Hiçbir Dünya yeri Ay'ı kusursuz yeniden üretemez.'* Dünya'da Ay'ın altıda bir yerçekimi, vakumu ve radyasyonu yok. Bu yüzden 40 Dünya sahasını 5 Ay Güney Kutbu referans bölgesine karşı üç temel eksende inceledik:
> 1. **Mobilite (Aktif Sayısal Eksen)** — ortalama eğim, dik yamaç payı (`slope_p90`), yüzey pürüzlülüğü ve rölyef (Ay'da `5 m/px` LRO LOLA DEM, Dünya'da `30 m/px` Copernicus GLO-30 DEM).
> 2. **Yüzey Parlaklığı (Aktif Sayısal Eksen)** — geniş bant güneş albedosu (`1000 m` LOLA `×0.38` geniş bant eşdeğeri vs `500 m` MODIS `MCD43A3.061`).
> 3. **Termal Eksen (`Karar #30` ile v1'de Askıda / `NaN`)** — Resmî PDS3 `.lbl` etiketlerini denetlediğimizde, Ay LRO Diviner kutup yerel saat dilimi (`ltim`) ürünleri ile Dünya `MOD11A2.061` yıllık ortalama gündüz–gece sıcaklık farkının aynı fiziksel günlük döngü tanımına oturmadığını ve eş ölçekli küresel `thermal_inertia` ürünü bulunmadığını tespit ettik. Elma ile armutu çarpıştırıp yanıltıcı bir termal puan üretmek yerine, veri sözleşmesi kurallarımız gereği (`AGENTS.md §5`) Termal eksenini v1'de `NaN` olarak askıya aldık ve sayısal skorlamayı **2 aktif eksen (`Mobilite + Yüzey`)** üzerinden yürüttük.
>
> Her sayısal puana 200 çekilişli Monte Carlo belirsizlik aralığını (`q05–q95`, ekranda `expanded_interval` ile) ekledik."

**Uygulamada:** Sol ayarlar panelini ve üstteki `Karar #30` bilgi bandını göster.

---

## 3. Canlı Demo (3 dakika)

### Adım 1 — Ay Referansını Seç ve Haritayı Göster (`🗺️ Harita`)
**Uygulamada:** Sol panelden **"Shackleton Krateri Kenarı"** seç ve `🗺️ Harita` sekmesini göster.

**Söyle:**
> "Referanslarımız NASA'nın Artemis III iniş bölgesi adaylarından (`Shackleton Krateri Kenarı`, `Bağlantı Sırtı`, `de Gerlache`, `Shackleton Yakını Zirve`, `Faustini`). Haritada 40 Dünya sahasını görüyoruz: mavi halkalı noktalar literatürden bilinen doğrulama sahaları (`Etna`, `Atacama`, `Haughton`, `Meteor Crater` vb.), diğerleri ise 10'u Türkiye'den olmak üzere 30 aday saha. Hem doğrulama (`color_val`) hem aday (`color`) noktalarının rengi ve yarıçapı doğrudan seçili referans ve görev skorunu yansıtır."

### Adım 2 — Görsel Karşılaştırma ve 3B Arazi (`📊 Görsel Karşılaştırma & Eksenler` & `⛰️ 3D Arazi`)
**Uygulamada:** Önce `📊 Görsel Karşılaştırma & Eksenler`, ardından `⛰️ 3D Arazi` sekmesine tıkla.

**Söyle:**
> "İkinci sekmede 40 Dünya sahasını ve seçili Ay referansını (⭐ altın yıldız) doğrudan iki aktif eksenin fiziksel uzayında (`Ortalama Eğim` vs `Albedo`) görüyoruz; altında ise her sahanın `Mobilite`, `Yüzey` ve `Genel` indeks çubukları belirsizlik şeritleriyle (`expanded_interval`) yer alıyor.
> `⛰️ 3D Arazi` sekmesinde ise çevrimdışı commit'lenmiş gerçek yörünge DEM paftalarını — solda `5 m/px` LRO LOLA Ay arazisini, sağda `30 m/px` Copernicus GLO-30 Dünya arazisini — `r = 1 km` analiz çemberiyle yan yana 3 boyutlu inceleyebiliyoruz."

### Adım 3 — Skor Tablosu ve Kompakt Portföy Kartı (`📊 Skor Tablosu & Portföy`)
**Uygulamada:** `📊 Skor Tablosu & Portföy` sekmesini aç; tabloyu ve hemen altındaki **Kompakt Çok-Sahalı Test Portföyü Kartı**'nı göster.

**Söyle:**
> "Skor tablosunda askıdaki ölü `Termal` sütununu kaldırıp yalnızca `Genel (2 Aktif Eksen)`, `Mobilite` ve `Yüzey` sütunlarını gösteriyoruz. Shackleton Krateri Kenarı için dengeli ağırlıkta **Karapınar Meke Maarı (`0.53 [0.41–0.57]`, Yüzey `0.90`)**, **McMurdo Dry Valleys (`0.51`)** ve **Hasan Dağı Keçekalecik (`0.50`, Mobilite `0.335` ile 40 saha arasında 1. sırada)** öne çıkıyor.
> Tablonun hemen altındaki **Kompakt Portföy Kartı (`select_portfolio`)** ise tek bir saha yerine, `0.70` sezgisel indeks eşiğinde kapsanan eksenleri (`Yüzey: Meke Maarı 0.90`) ve eşiği aşamayan ya da askıda kalan eksenleri (`Mobilite` için hedefli dik-yamaç testi, `Termal` ve vakum/yerçekimi için laboratuvar/simülasyon) açıkça ayırıyor."

### Adım 4 — Betimsel Sıra Tanısı (`✅ Betimsel Sıra Tanısı`)
**Uygulamada:** `✅ Betimsel Sıra Tanısı` sekmesine geç.

**Söyle:**
> "Literatürden bilinen 10 doğrulama sahasını skorlayıcıya rol etiketi vermeden aynı 40 sahalık havuz içinde sıraladık. Önemli bilimsel dürüstlük notumuz: 40 sahanın tamamı Z-ölçeklemesine katıldığı için bu tablo **bağımsız bir holdout testi veya ilk-5 geçer/kalır sınavı değildir; betimsel bir sıra tanısıdır**. `docs/validation_expectations.md` dosyasındaki ön-kayıtlı beklentiler ve doğrulanmış DOI/URL kaynaklarıyla yan yana baktığımızda, dik krater/volkan yamacı olan **Etna (`Mobilite #3/40`)**, **Lunar Crater Nevada (`Mobilite #7/40`, `Yüzey #11/40`)** ve **Meteor Crater (`Mobilite #8/40`)** sahalarının Shackleton krater duvarı karşısında Mobilite ekseninde üst sıralara yerleştiğini, düz çöl tabanı olan **Atacama Yungay (`Mobilite #28/40`)** sahasının ise beklendiği gibi dik krater kenarından ayrıştığını görüyoruz."

### Adım 5 — Analojinin Sınırları ve 8 Boyutlu Karne (`⚠️ Analojinin Sınırları`)
**Uygulamada:** `⚠️ Analojinin Sınırları` sekmesini aç; 8 Boyutlu Karne'yi ve yerel `LRO LOLA 5 m/px` ↔ `Sentinel-2 L2A 10 m/px` kanıt kartını göster.

**Söyle:**
> "Son sekmede Dünya'da sahadan asla test edilemeyecek fiziksel sınırları (`1/6 g` yerçekimi, vakum, radyasyon, `29.5` günlük Ay günü), teknik ölçek sınırlarımızı (`5 m/px` LOLA vs `30 m/px` GLO-30 DEM çözünürlük farkı ve `Karar #30` Termal askı durumu), **8 Boyutlu Görev Karnemizi** ve yerel olarak doğrulanmış `LRO LOLA 5 m/px` ile bulutsuz `Sentinel-2 L2A 10 m/px` (`scene_id`, çekim tarihi ve `%bulut` bilgili) görsel kanıt kartlarını sunuyoruz."

---

## 4. Güvenilirlik Özeti (1 dakika)

**Söyle:**
> "Üç katmanlı bilimsel şeffaflık uyguladık:
> 1. **Sıfır sentetik veri (`0 MOCK`):** Tüm özellikler ve görseller NASA LRO (LOLA, Diviner) ve ESA/NASA (Copernicus GLO-30, NASADEM, MODIS, Sentinel-2) arşivlerinden üretildi ve `validate_all.py --fail-on-mock` ile doğrulandı.
> 2. **Bağımsız matematiksel çapraz kontrol:** 5 Ay referansı × 40 Dünya sahası × 3 eksen = 600 eksen skoru ve 200 görev ağırlıklı toplam skor, formülden bağımsız olarak çapraz hesaplandı (`sapma = 0`).
> 3. **Dürüst sınırlar:** PDS `.lbl` etiketlerinden yakaladığımız Ay–Dünya sıcaklık tanımı farkını gizlemek yerine `Karar #30` ile açıkça belgeleyip Termal ekseni `NaN` olarak askıya aldık."

---

## 5. Kapanış (30 saniye)

**Söyle:**
> "Özetle: Tek bir Dünya sahası Ay'ı temsil edemez — ancak eksen bazlı skorlama, belirsizlik yayılımı ve kompakt portföy seçimi bir görev planlayıcısına *'hangi yeteneği hangi sahada test etmeliyim, hangisini laboratuvara bırakmalıyım?'* sorusunun kanıta dayalı cevabını verir. 5 Ay Güney Kutbu bölgesi, 40 Dünya sahası, 2 aktif sayısal eksen + şeffaf biçimde belgelenmiş sınırlar. Teşekkürler."

---

## Olası Jüri Soruları ve Hazır Cevaplar

**S: Mars neden v1 arayüzünde yok?**
> "Görev metni *'Ay VEYA Mars'* diyor. v1'de NASA Artemis III Güney Kutbu bölgelerine odaklanarak `5 m/px` LOLA DEM ve tam DOI doğrulamalı derin bir analiz kurduk. Veri sözleşmemiz (`AGENTS.md §5`) ve skorlama motorumuz gök cismi bağımsızdır; Mars MOLA/THEMIS entegrasyonu v2 yol haritasında hazırdır."

**S: Termal eksen neden v1'de askıda (`NaN`)?**
> "Resmî PDS3 `.lbl` etiketlerini kontrol ettiğimizde, Ay Güney Kutbu LRO Diviner `ltim` yerel saat dilimi ürünleri ile Dünya `MOD11A2.061` yıllık ortalama gündüz–gece yüzey sıcaklık farkının aynı günlük döngü tanımını paylaşmadığını gördük. `AGENTS.md §5` (*her özellik her gök cisminde aynı tanımla hesaplanmalıdır*) kuralımız gereği, farklı tanımlı iki sayıyı birbirinden çıkarıp yapay bir skor basmak yerine `Karar #30` ile Ay termal sütunlarını v1'de `NaN` yaptık ve 24 saatlik `ltim01..ltim96` serisini `docs/data_sources_moon.md` içinde belgeledik."

**S: Portföy kartındaki `0.70` eşiği ne anlama geliyor?**
> "`0.70` bir olasılık veya kalibre edilmiş fiziksel yeterlilik sınırı değildir; eksen kapsamını özetlemek için kullanılan sezgisel bir benzerlik indeksi eşiğidir (`docs/data_notes.md §2b`)."
