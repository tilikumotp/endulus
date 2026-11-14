# Sunum Rehberi — "Hocaya bunu ben sunacağım" (5-6 dakika)

> Bu metin konuşma diliyle yazılmıştır. Okuyarak da sunulabilir. Her adımda uygulamada neye tıklayacağın doğrudan sadeleştirilmiş siyah arayüze göre güncellenmiştir. Geniş sayısal tablolar `report/final_report_tr.md` içindedir.

---

## 1. Giriş (30 saniye)

**Söyle:**
> "NASA'nın bize verdiği görev şuydu: Ay'a veya Mars'a üs kurmayı düşündüğümüz yerlere benzeyen Dünya sahalarını, açık uydu verisiyle bulmak. Çünkü astronotlar Ay'a çıkmadan önce ekipmanlarını Dünya'da benzer yerlerde test ediyor. Ama hangi Dünya yeri gerçekten benzer? Biz bunu kanıtlı ve sınırlarıyla cevaplayan bir sistem yaptık."

---

## 2. Yaklaşım (1 dakika)

**Söyle:**
> "Önce görevin içindeki kritik cümleyi okuduk: 'Hiçbir Dünya yeri Ay'ı kusursuz yeniden üretemez.' Doğru — Dünya'da Ay'ın `1/6 g` yerçekimi, vakumu ve radyasyonu yok. O yüzden 'en benzer TEK yer' tuzağına düşmedik. Her sahayı ayrı eksenlerde ele aldık:
> 1. **Arazi (Mobilite)** — eğim, pürüzlülük, yükselti farkı (`5 m/px` Ay LOLA DEM vs `30 m/px` Dünya Copernicus GLO-30) — **aktif**
> 2. **Yüzey** — geniş bant albedo / parlaklık (`1000 m` LOLA vs `500 m` MODIS `MCD43A3`) — **aktif**
> 3. **Sıcaklık (Termal)** — Ay güney kutbunda `29.5` günlük vakum döngüsü ile Dünya'nın `24` saatlik yıllık farkı eşdeğer tanımlı olmadığı için sahte skor üretmek yerine **bilinçli olarak askıda (`NaN`)** tuttuk.
>
> Her puana ölçüm hatasını da kattık; yani tek bir sayı değil, `200` çekilişli Monte Carlo `P5–P95` belirsizlik aralığını gösteriyoruz."

**Uygulamada:** Sol panel ve **Eksen Grafikleri** sekmesi gösterilir — Mobilite ve Yüzey çubukları net, arayüz tek saf siyah tema ve sıfır dikkat dağıtıcı süsleme.

---

## 3. Canlı Demo (3 dakika)

### Adım 1 — Ay Referansını seç
**Uygulamada:** Sol panelden **"Shackleton Krateri Kenarı"** seç (`Site XX ROI` gibi karmaşık kodlar yerine doğrudan krater adları görünür).

**Söyle:**
> "Referansımız NASA Artemis III aday bölgeleri arasından alınan 5 gerçek Ay Güney Kutbu bölgesi. Koordinatların tamamı NASA GSFC PGDA shapefile'larından alındı."

### Adım 2 — Görev Değişince Sıra Değişiyor (`Skor Tablosu`)
**Uygulamada:** **Skor Tablosu** sekmesini aç. Dengeli modda en üst sırayı göster; ardından sol panelden **Rover Hareket Testi** seçip sıralamanın anında değiştiğini göster.

**Söyle:**
> "Dengeli ağırlıkta `40` Dünya sahası içinde ilk sırada **Karapınar Meke Krateri (`0.528`, P5–P95: `0.406–0.569`)** yer alır; ancak gücü esasen **Yüzey (`0.903`)** yakınlığından gelir, Mobilite (`0.153`) ortadadır. Sol menüden görevi **Rover Hareket Testi**'ne aldığımızda ise **`#1 Hasandağı Keçikaleçik (0.446)`** ilk sıraya yükselir — çünkü artık saha listesi test edeceğimiz ekipmanın ihtiyacına göre ağırlıklandırılıyor."

### Adım 3 — Harita ve Gerçek 3D Arazi
**Uygulamada:** Önce **Harita** sekmesine geç (mavi dış halka = 10 doğrulama sahası, kırmızı–yeşil dolgu = aktif skor), ardından **3D Arazi** sekmesini aç.

**Söyle:**
> "Haritada mavi dış halkalar literatürde zaten bilinen `10` doğrulama analogunu, diğer noktalar Türkiye'den `14` ve dünyadan `16` olmak üzere `30` aday test sahasını gösterir. **3D Arazi** sekmesinde ise yapay örnek yüzey değil, doğrudan taahhüt edilmiş gerçek **5 m/px LRO LOLA** Ay yükselti gridini ve **30 m/px Copernicus GLO-30** Dünya topografyasını (`~2.2 km` pencere) yan yana döndürüyoruz."

### Adım 4 — Analojinin Sınırları, Çevrimdışı Görseller ve Akademik Kaynakça
**Uygulamada:** **Analojinin Sınırları** sekmesini aç; saha seçiciden **Karacadağ** veya **Karapınar Meke** seçip 8 boyutlu kapsam tablosunu, 3 panelli görseli, `z_diff` fark tablosunu ve en alttaki **Veri Kaynakları ve Akademik Kaynakça (Ay & Dünya)** açılır kutusunu göster.

**Söyle:**
> "Bu sekme iki işi birden yapar. Üstte `8 Boyutlu Kapsam Tablosu` hangi fiziki boyutun sahada sınanabildiğini (`Mobilite`, `Yüzey`), hangilerinin mutlaka laboratuvar/simülasyona kaldığını (`1/6 g`, vakum, radyasyon, elektrostatik toz) ayırır. Ortada internet kesilse bile açılan yerel `5 m` LOLA kabartma/eğim haritası ve `10 m` Sentinel-2 L2A görüntüsü ile altındaki özellik fark tablosu (`5 m` vs `30 m` çözünürlük etiketiyle) yer alır. En alttaki kaynakça panelinde ise Emirhan'ın Ay makale DOI'leri (`Barker 2021`, `Lucey 2014`, `Lemelin 2016`) ile Eray'ın `40` Dünya sahası kaynakçası şeffafça listelenir."

### Adım 5 — Betimsel Sıra Tanısı (`Sıra Tanısı (Doğrulama)`)
**Uygulamada:** **Sıra Tanısı (Doğrulama)** sekmesi — `Mobilite Sırası`na göre küçükten büyüğe sıralı 10 bilinen doğrulama sahası, E8 nitel buz envanteri ve tıklanabilir DOI tablosu.

**Söyle:**
> "Burada Etna, Atacama, McMurdo, Haughton gibi bilinen `10` Dünya sahasını skorlayıcıya rol etiketi göstermeden puanladık ve önceden kayıtlı DOI beklentileriyle (`docs/validation_expectations.md`) karşılaştırdık. Shackleton gibi dik bir kraterde **Etna Mobilite'de `#3 / 40`** çıkar; ancak albedosu koyu (`0.047`) olduğu için parlak Shackleton (`0.147`) karşısında Yüzey'de geri düşer. Yatık **Faustini Kenarı** seçildiğinde ise Atacama ve Haughton gibi düz sahalar Mobilite'de üst sıralara çıkar. Önemli dürüstlük notu: tüm `40` saha Z-ölçeklemesine girdiği için bu tablo bağımsız holdout doğrulaması değil, **betimsel bir sıra tanısıdır**. Benzer biçimde Karacadağ gibi adayları da asla kesin analog ilan etmiyoruz, test adayı olarak sunuyoruz."

---

## 4. Güvenilirlik Özeti & Olası Sorular (1 dakika)

* **Veriler gerçek mi?** `40` Dünya + `5` Ay sahasında `scripts/validate_all.py --fail-on-mock` çıktısı `0 MOCK, 0 hata, 0 uyarı`dır. Tüm NASA/ESA ürün kodları `*_src` ve `*_res_m` kolonlarıyla kayıtlıdır.
* **Neden portföy kartını rapora aldık?** Çekirdek motor (`src/scoring/portfolio.py`) her Ay bölgesi için en küçük kapsayıcı saha grubunu hesaplar (sonuçlar `report/final_report_tr.md` §4.2'de tam tablolu); arayüz ise jüri demosu için yalınlaştırılıp `6` ana sekmeye odaklanmıştır.
* **Termal neden askıda?** `Karar #30` (`docs/data_notes.md`): 29.5 günlük LRO Diviner döngüsüyle yıllık MODIS `MOD11A2` farkı eşdeğer olmadığı için bilerek `NaN` bırakılmıştır; tam gün eğrileri v2 yol haritasındadır.
* **Mars neden v2'de?** Data sözleşmesi (`AGENTS.md` §5) ve `src/scoring/` cisim-bağımsızdır; v1'de derinlik ve yüksek çözünürlük kalitesi için Artemis III Ay Güney Kutbu seçilmiş, Mars MOLA/TES entegrasyonu v2'ye konmuştur.
