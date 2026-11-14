# Ay Güney Kutbu (Shackleton Çevresi) Veri Kaynakları

Bu belge, projemizdeki **Ay Güney Kutbu (Shackleton Krateri Kenarı)** referans sahası için kullanacağımız 3 temel veri grubunu (**1. Yükseklik/Eğim**, **2. Yüzey Sıcaklığı**, **3. Albedo**) sade ve doğrulanabilir şekilde özetler.

---

## Hızlı Özet Tablosu (Önerilen Birincil Ürünler)

| # | Ne Ölçüyor? | Sözleşmedeki Kolonlar | Önerilen NASA Ürünü | Versiyon | Çözünürlük (`X_res_m`) | Dosya Formatı & Boyutu | Durum |
|---|---|---|---|---|---|---|---|
| **1** | **Yükseklik ve Eğim (DEM)** | `slope_mean`, `slope_p90`, `roughness`, `relief` | **LRO LOLA — Shackleton Rim Özel Haritası** (`Site04_final_adj_5mpp_surf.tif`) | `v2021` (Barker vd., 2021) | **5 metre** (`5.0 m`) | GeoTIFF (`.tif`), **39 MB** | **Doğrulandı** (Sunucuda aktif) |
| **2** | **Yüzey Sıcaklığı** | `temp_amplitude` | **LRO Diviner — Güney Kutbu Saatlik/Mevsimlik Sıcaklık** (`pcp_avg_tbol_pols_*_240`) | `v1.0` (Williams vd., 2022) | **240 metre** (`240.0 m`) | ASCII Tablo (`.tab` + `.xml`) | **Doğrulandı** (Sunucuda aktif) |
| **3** | **Yüzey Parlaklığı (Albedo)** | `albedo` | **LRO LOLA — Güney Kutbu Lazer Albedo Haritası** (`LDAM_50S_1000M_FLOAT`) | `V1.0` (Lemelin vd., 2016) | **1000 metre** (`1000.0 m`) | İkili Raster (`.IMG` + `.LBL`), **25.6 MB** | **Doğrulandı** (Sunucuda aktif) |

---

## 1. YÜKSEKLİK VE EĞİM VERİSİ (LRO LOLA — DEM)

Ay yüzeyinin yüksekliğini metre cinsinden veren haritadır. Buradan **ortalama eğim (`slope_mean`)**, **%90 eğim (`slope_p90`)**, **yüzey pürüzlülüğü (`roughness`)** ve **yükseklik farkı (`relief`)** hesaplanır.

### Seçenek 1A (ÖNERİLEN): NASA GSFC PGDA — Shackleton Rim 5 Metre Haritası
* **Neden bunu seçmeliyiz?**
  1. Doğrudan **Shackleton Krateri kenarı (`Site04`)** için hazırlanmış **~20×20 km'lik** hazır bir kutudur.
  2. Standart `.IMG` dosyalarının aksine doğrudan **GeoTIFF (`.tif`)** formatındadır; Python (`rasterio`) ile tek satırda hatasız açılır.
  3. Yanında NASA'nın kendi hesapladığı **eğim belirsizliği (`_slperr.tif`)** ve **yükseklik belirsizliği (`_toterr.tif`)** dosyaları vardır. Böylece sözleşmedeki `slope_mean_sd` (belirsizlik) kolonuna uydurma değil, gerçek NASA hata değerini yazabiliriz.
* **Tam Ürün Adı:** `PGDA High-Resolution LOLA Topography for Lunar South Pole Sites — Site04_final_adj_5mpp_surf.tif`
* **Versiyon:** `final_adj_5mpp` (Barker et al., 2021, *Planetary and Space Science*, 203, 105119)
* **Çözünürlük (`X_res_m`):** `5.0` metre/piksel (Güney Kutbu Stereografik Projeksiyon, metre birimli)
* **Dosya Formatı:** GeoTIFF (`.tif`, 39 MB)
* **Doğrudan İndirme Linkleri:**
  * Tanıtım Sayfası: https://pgda.gsfc.nasa.gov/products/78
  * Yükseklik Haritası (DEM): https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/Site04/Site04_final_adj_5mpp_surf.tif
  * Eğim Hata Haritası (`_sd` için): https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/Site04/Site04_final_adj_5mpp_slperr.tif
  * Yükseklik Hata Haritası: https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/Site04/Site04_final_adj_5mpp_toterr.tif
* **Doğrulama Notu:** `TODO(verify)` — `_src` kolonuna `LRO_LOLA_PGDA_Site04_5mpp_v2021` yazılması ekipçe onaylanmalı.

### Seçenek 1B (ALTERNATİF): MIT / PDS Standart LOLA Kutup Mozaiği (`LDEM_875S_20M`)
* **Nedir?** 87.5° Güney enleminden kutup noktasına (90°S) kadar tüm bölgeyi kapsayan standart PDS arşiv dosyasıdır.
* **Tam Ürün Adı:** `LRO-L-LOLA-4-GDR-V1.0` — `LDEM_875S_20M` (veya 5 metrelik `LDEM_875S_5M`)
* **Versiyon:** `V2.0` (`PRODUCT_VERSION_ID = "V2.0"`, 2017-06-15)
* **Çözünürlük (`X_res_m`):** `20.0` metre/piksel (Güney Kutbu Stereografik Projeksiyon)
* **Dosya Formatı:** PDS3 İkili Dosya (`.IMG`, 110 MB) + Metin Etiketi (`.LBL`)
* **Doğrudan İndirme Linkleri:**
  * Veri (`.IMG`): https://imbrium.mit.edu/DATA/LOLA_GDR/POLAR/IMG/LDEM_875S_20M.IMG
  * Etiket (`.LBL`): https://imbrium.mit.edu/DATA/LOLA_GDR/POLAR/IMG/LDEM_875S_20M.LBL

---

## 2. YÜZEY SICAKLIĞI VERİSİ (LRO Diviner)

Ay yüzeyinin gece ve gündüz arasındaki sıcaklık farkını (**`temp_amplitude` = Maksimum Sıcaklık − Minimum Sıcaklık**, Kelvin cinsinden) hesaplamak için kullanılır.

### Seçenek 2A (ÖNERİLEN): LRO Diviner — Güney Kutbu Günlük/Mevsimlik Sıcaklık Haritaları (PCP)
* **Nedir?** LRO Diviner termal kamerasının 10 yıllık (2009–2019) ölçümlerini birleştirerek Güney Kutbu'nu **240 metrelik** kutucuklara bölen ve bir Ay günü boyunca sıcaklığın nasıl değiştiğini Kelvin (K) cinsinden veren resmi NASA veri setidir.
* **Tam Ürün Adı:** `urn:nasa:pds:lro_diviner_derived1:data_derived_pcp` — `pcp_avg_tbol_pols_sum_ltim01_240` .. `ltim48_240`
* **Versiyon:** `1.0` (Williams et al., 2022; PDS4 Arşivi)
* **Çözünürlük (`X_res_m`):** `240.0` metre (80°S–90°S Güney Kutbu Stereografik ızgara)
* **Dosya Formatı:** ASCII Metin Tablosu (`.tab`) + PDS4 Etiketi (`.xml`)
* **Doğrudan İndirme Linkleri:**
  * Günlük (Saatlik Dilimler): https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_pcp/diurnal/ltim/pols/
  * Mevsimlik Dilimler: https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_pcp/seasonal/slon/pols/
* **Doğrulama Notu:** `TODO(verify)` — `temp_amplitude` hesabı için yaz (`sum`) günlük çevrimindeki `max - min` değerinin mi yoksa yıllık farkın mı kullanılacağı liderle netleştirilmeli.

### Seçenek 2B (ALTERNATİF RASTER): LRO Diviner Seviye 3 Gündüz/Gece Haritaları (`DGDR_TBOL_AVG_POLS`)
* **Tam Ürün Adı:** `LRO-L-DLRE-5-GDR-V1.0` — `DGDR_TBOL_AVG_POLS_<TARİH><D|N>_240_IMG` (`D`: Gündüz, `N`: Gece)
* **Versiyon:** `V5.0` (Kalibrasyon v4.1)
* **Çözünürlük (`X_res_m`):** `240.0` metre/piksel (75°S–90°S Güney Kutbu Stereografik)
* **Dosya Formatı:** PDS3 `.img` + `.lbl` (Örn. ~29 MB)
* **Doğrudan İndirme Linki:** https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_gdr_l3/2015/polar/img/

---

## 3. YÜZEY PARLAKLIĞI / ALBEDO VERİSİ (`albedo`: 0 ile 1 arası)

Yüzeyin ışığı ne kadar yansıttığını (`0`: tam karanlık, `1`: tam yansıtıcı) gösterir. **Güney Kutbu'ndaki en kritik sorun güneş ışığının yatay gelmesi ve krater içlerinin sürekli karanlık (gölgede) olmasıdır.**

### Seçenek 3A (ÖNERİLEN): LRO LOLA — Aktif Lazer Normal Albedo Haritası (`LDAM_50S_1000M_FLOAT`)
* **Neden bunu seçmeliyiz?**
  * Güneş ışığına ihtiyaç duymaz! Uydu kendi lazerini (1064 nm) yüzeye gönderip yansımasını ölçtüğü için **Shackleton'ın karanlık bölgelerinde bile %100 dolu ve gölgesiz albedo verisi (`0.156` – `0.577` arası)** verir.
* **Tam Ürün Adı:** `LRO-L-LOLA-4-GDR-V1.0` — `LDAM_50S_1000M_FLOAT`
* **Versiyon:** `V1.0` (Lemelin et al., 2016; `2015-12-15`)
* **Çözünürlük (`X_res_m`):** `1000.0` metre/piksel (50°S–90°S Güney Kutbu Stereografik Projeksiyon)
* **Dosya Formatı:** 32-bit Float `.IMG` (25.6 MB) + `.LBL`
* **Doğrudan İndirme Linkleri:**
  * Veri (`.IMG`): https://imbrium.mit.edu/DATA/LOLA_GDR/POLAR/FLOAT_IMG/LDAM_50S_1000M_FLOAT.IMG
  * Etiket (`.LBL`): https://imbrium.mit.edu/DATA/LOLA_GDR/POLAR/FLOAT_IMG/LDAM_50S_1000M_FLOAT.LBL
* **Doğrulama Notu:** `TODO(verify)` — 1064 nm lazer albedosunun sözleşmedeki `albedo` kolonu için kullanılacağı `docs/data_notes.md` içine not düşülmeli.

### Seçenek 3B (ALTERNATİF): LRO Diviner Görünür/Solar Kanal (`DGDR_VB1_AVG_POLS`)
* **Tam Ürün Adı:** `LRO-L-DLRE-5-GDR-V1.0` — `DGDR_VB1_AVG_POLS_20150122D_240_IMG` (0.35–2.80 µm genişbant güneş yansıması)
* **Versiyon:** `V5.0`
* **Çözünürlük (`X_res_m`):** `240.0` metre/piksel
* **Dosya Formatı:** PDS3 `.img` + `.lbl`
* **Doğrudan İndirme Linki:** https://pds-geosciences.wustl.edu/lro/lro-l-dlre-4-rdr-v1/lrodlr_1001/data/gdr_l2/2015/polar/img/dgdr_vb1_avg_pols_20150122d_240_img.img
* **Kısıt (`TODO(verify)`):** Güneş görmeyen krater içlerinde değer ölçemez ve güneş geliş açısı düzeltmesi gerektirir.

### Neden Clementine UV/VIS veya LROC WAC Kutup İçin Uygun Değil? (Kontrol Edildi)
1. **Clementine UVVIS 750 nm (`Lunar_Clementine_UVVIS_750nm_Global_Mosaic_118m_v2.1.tif`, 118 m):** Sunucuda doğrulandı (https://planetarymaps.usgs.gov/mosaic/Lunar_Clementine_UVVIS_750nm_Global_Mosaic_118m_v2.1.tif), ancak 89.9° Güney kutbunda derin gölgeler nedeniyle Shackleton çevresinde boşluklar (NoData) içerir (`TODO(verify)`).
2. **LROC WAC Hapke Albedo (`WAC_HAPKE_*`):** Yalnızca **70° Kuzey ile 70° Güney** enlemleri arasını kapsar; 89.9° Güney'deki Shackleton kraterini **hiç kapsamaz**.

---

## 4. Görev 2 İçin Onay Listesi (Sizin Kararınız Bekleniyor)

Görev 2'de **Shackleton çevresi ~20×20 km eğim (`slope_mean`, `slope_p90`) hesabını** başlatmam için şu 2 maddeyi onaylamanız yeterli:

- [ ] **1. DEM Seçimi:** **Seçenek 1A** (`Site04_final_adj_5mpp_surf.tif` — 5 metre çözünürlüklü, 39 MB hazır Shackleton GeoTIFF + gerçek hata haritası) kullanılsın mı?
- [ ] **2. Shackleton Rim Merkez Koordinatı (`moon_shackleton_rim`, yarıçap `radius_m = 1000` m):**
  - **Öneri (`Site04` Shackleton Aydınlık Kenar Sırtı):** Enlem `lat = -89.78`, Boylam `lon = 123.0` *(TODO(verify): İندirilen DEM üzerinde en aydınlık/düz sırt noktası harita üstünde de gösterilecek).*
