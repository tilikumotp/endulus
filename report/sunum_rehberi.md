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
> 1. **Arazi** — eğim, pürüzlülük, yükseklik farkı (rover gidip gidemeyeceği)
> 2. **Sıcaklık** — gece-gündüz sıcaklık dalgalanması
> 3. **Yüzey** — parlaklık (zemin malzemesinin ipucu)
>
> Ve her puana ölçüm hatasını da ekledik — yani sadece '0.37' demiyoruz, '0.37, belirsizlik aralığı şu' diyoruz."

**Uygulamada:** Ayarlar paneli gösterilir — üç ölçütün listesi görünsün.

---

## 3. Canlı Demo (3 dakika)

### Adım 1 — Referansı seç
**Uygulamada:** Sol panelden **"Shackleton Krateri Kenarı"** seç. (Ay güney kutbu, NASA'nın Artemis görevinin iniş bölgesi.)

**Söyle:**
> "Referansımız Ay güney kutbundan gerçek NASA bölge adayları — Artemis III'ün iniş için incelediği ROI'ler. Yani Ay tarafı uydurmadır değil; NASA'nın kendisinin baktığı koordinatlardır."

### Adım 2 — Skorlara bak
**Uygulamada:** Skorlar tablosu aç. En üst satırı işaret et.

**Söyle:**
> "En benzer çıkan: **Süphan Dağı** — Bitlis'teki az bilinen bir volkanik saha, puanı 0.37. Dikkat ederseniz Etna, Atacama gibi uzmanların yıllardır çalıştığı yerler de listede var ama en üstte az bilinen bir Türk sahası var. NASA'nın görev metninde 'bizi şaşırtın' yazıyordu — işte bulgumuz bu."

### Adım 3 — Harita
**Uygulamada:** Harita sekmesine geç.

**Söyle:**
> "40 Dünya sahası haritada. Nokta ne kadar büyük ve koyuysa, o saha Ay referansına o kadar benziyor. En güçlüler Türkiye'de ve Antarktika'da toplanmış."

### Adım 4 — Neden benzer / neden değil
**Uygulamada:** Çubuk kartlarını göster (Görsel Karşılaştırma varsa orada; yoksa radar).

**Söyle:**
> "Bir sahaya açıldığında neden benzer gördüğünüzü ayrı ayrı gösteriyoruz. Örneğin bu saha arazide güçlü ama sıcaklıkta zayıf. Neden? Ay'ın gece-gündüz farkı 131 Kelvin; Dünya'da bunun en uç örneği bile 29 Kelvin. Bu uçurumu saklamıyoruz — ekranda yazıyor. Çünkü görevin bir diğer cümlesi şuydu: 'analojinin nerede bozulduğunu açıklayın.' Biz bunu bir sekmeye dönüştürdük."

### Adım 5 — Analojinin Sınırları
**Uygulamada:** "⚠️ Analojinin Sınırları" sekmesi.

**Söyle:**
> "Bu sekme, Dünya'da sahadan ASLA test edilemeyecek şeyleri listeliyor: yerçekimi, vakum, radyasyon, 29 gün süren Ay gündüzü. Bunlar sahadan değil, laboratuvardan doğrulanır. Yani sistemimiz abartmıyor — 'burada test edin' dediği şeyi, 'burada test edemezsiniz' diye de sınırlıyor."

### Adım 6 — Yöntemin sınavı (Doğrulama)
**Uygulamada:** Doğrulama sekmesi.

**Söyle:**
> "Peki bu sisteme güvenebilir miyiz? Yöntemi test ettik: Dünya'da Ay'a benzediği bilinen 10 saha — Etna, Atacama, Haughton Krateri gibi — skorlayıcıya 'sen bunların analog olduğunu biliyorsun' demeden puanlandı. Sonuç: birçoğu ilk 5'e girdi. Yani sistem gerçekten çalışan bir şey yakalıyor, kendini kandırmıyor."

---

## 4. Güvenilirlik bölümü (1 dakika) — "gerçekten güvenilir mi?" sorusunun cevabı

**Söyle:**
> "Üç katmanlı güvenilirlik:
> 1. **Her sayının kaynağı yazılı.** Eğim puanı hangi uydu verisinden (LOLA, metre cinsinden çözünürlüğü), sıcaklık hangi sensörden — hepsi veri dosyasında etiketli.
> 2. **Bağımsız doğrulama yaptık.** Sistemin ürettiği her sayıyı, formülü elle yeniden yazıp 600'den fazla karşılaştırmayla tekrar hesapladık. Sapma: sıfır.
> 3. **Belirsizliği saklamıyoruz.** Ölçüm hatası olan her sayı aralık olarak gösteriliyor. Verisi olmayan özellik hiç varsa '0' yazmıyoruz, boş bırakıp belgeliyoruz.
>
> Kısacası: bu bir gösteriş projesi değil, savunulabilir bir bilimsel yöntem."

---

## 5. Kapanış (30 saniye)

**Söyle:**
> "Özet: Tek bir Dünya yeri Ay'ı temsil edemiyor — ama her saha farklı bir konuda güçlü bir analog. Sistemimiz, bir görev planlayıcısına 'bu yeteneği hangi sahada test etmeliyim?' sorusunu veriyle cevaplıyor. 40 Dünya sahası, 5 Ay bölgesi, üç eksen, her sayı kaynaklı ve doğrulanmış. Teşekkürler."

---

## Olası sorular + hazır cevaplar

**S: Mars neden yok?**
> "Görev metni 'Ay VEYA Mars' diyor. v1'de Ay güney kutbunu seçtik çünkü NASA'nın Artemis verisi ve hazir ROI koordinatları açıkta; yöntemimiz cisim-bağımsız, Mars'a genişletme yolu raporda belgeli."

**S: Bu skorlar ne demek? Olasılık mı?**
> "Hayır, olasılık değil. 0-1 arası bir benzerlik ölçüsü: 1'e yakın 'bu konuda benzer', 0'a yakın 'farklı'. Görsel benzerlik ya da kader değil; üç ölçütten standartlaştırılmış hesap."

**S: Peki benzerlik eşiği kaç olmalı ki 'analog' diyelim?**
> "Kesin bir eşik koymadık — bunun yerine sahaları sıralıyoruz ve her ekseni ayrı gösteriyoruz. 'Analog' etiketini kalifikasyonlu kaynaklara bırakıyoruz; katkımız 'nereden başlamalı' sorusunu veriyle yanıtlamak."

**S: Veriler gerçek mi? Kendi verinizi mi kullandınız?**
> "Hepsi NASA ve ESA'nın açık arşivleri: LOLA (Ay yükseklik haritası, 5 metre/px), Diviner (Ay sıcaklık), Sentinel-2 (Dünya uydu görüntüsü), Copernicus GLO-30 (Dünya yükseklik), MODIS (Dünya sıcaklık). Çözünürlükler ve tarihler veri notlarımızda."

**S: Sıcaklık puanları neden hep düşük?**
> "Çünkü Ay gerçekten çok daha aşırı: gece-gündüz farkı 114-151 K, Dünya'da en uç çölde bile 29 K. Bu bir hata değil, fiziksel gerçeğin dürüst raporlanması. Yani Dünya hiçbir saha Ay'ın sıcaklık testi için kullanılamaz — sistem bunu ekranda söylüyor."

**Uygulama açılmazsa (yedek plan):** `report/figures/` klasöründeki ekran görüntüleriyle aynı hikâyeyi anlat — sıra değişmez.
