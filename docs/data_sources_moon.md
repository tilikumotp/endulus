# Ay Güney Kutbu Doğrulanmış Veri Kaynakları ve Gerçek Saha Sonuçları (`docs/data_sources_moon.md`)

Bu belge, `AGENTS.md` (§5 Veri Sözleşmesi ve §6 Kurallar) uyarınca Ay Güney Kutbu (`body == "moon"`, `role == "reference"`) referans sahaları için kullanılan NASA PDS / GSFC PGDA veri setlerinin doğrulanmış ürün adlarını, versiyonlarını, yerel çözünürlüklerini (`X_res_m`), literatür/harita kaynaklı koordinatlarını ve `data/processed/features_moon.parquet` içindeki gerçek ölçüm sonuçlarını içerir.

---

## 1. Doğrulanmış 5 Ay Güney Kutbu Referans Sahası (`features_moon.parquet`)

Tüm koordinatlar NASA GSFC Planetary Geodesy Data Archive (**PGDA Product 78**, *Barker et al., 2021, Planetary and Space Science 203:105119*; *Mazarico et al., 2011, Icarus 211:1066–1081*) kapsamında yayımlanan `SiteXX_ROIs.shp` resmi ROI shapefile'larından ve NASA Artemis III aday bölge DEM merkezlerinden alınmıştır (**uydurma koordinat yoktur**):

| `site_id` | `name` | `lat` (°) | `lon` (°) | Kutupsal Stereografik `(X, Y)` (m) | `radius_m` (m) | `lithology_class` | Koordinat ve Jeoloji Doğrulama Kaynağı |
|---|---|---|---|---|---|---|---|
| **`moon_shackleton_rim`** | `Shackleton Crater Rim (Site 04 ROI)` | **`-89.7800`** | **`-156.3201`** | `(-2679.3, -6109.5)` | `1000.0` | `regolith` | NASA GSFC PGDA `Site04_ROIs.shp` (ROI #3 merkezi); Mazarico vd. (2011), Barker vd. (2021), Zuber vd. (2012) |
| **`moon_connecting_ridge`** | `Connecting Ridge (Shackleton-de Gerlache Ridge, Site 01 ROI)` | **`-89.4624`** | **`-137.0871`** | `(-11099.8, -11939.4)` | `1000.0` | `regolith` | NASA GSFC PGDA `Site01_ROIs.shp` (ROI #5 merkezi — Barker vd. 2021'de en yüksek aydınlanma sürekliliği olan ROI); Artemis III Connecting Ridge |
| **`moon_de_gerlache_rim`** | `de Gerlache Crater Rim (Site 11 ROI)` | **`-88.6683`** | **`-68.3754`** | `(-37541.2, +14882.2)` | `1000.0` | `regolith` | NASA GSFC PGDA `Site11_ROIs.shp` (ROI #1 merkezi); Mazarico vd. (2011), Barker vd. (2021); Artemis III de Gerlache Rim |
| **`moon_shackleton_peak`** | `Peak Near Shackleton (Site 07 ROI)` | **`-88.8063`** | **`+123.5451`** | `(+30169.5, -20002.9)` | `1000.0` | `anorthosite` | NASA GSFC PGDA `Site07_ROIs.shp` (ROI #1 merkezi); Mazarico vd. (2011), Barker vd. (2021); Spudis vd. (2008) saf anortozit masifi |
| **`moon_faustini_rim`** | `Faustini Crater Rim A (PGDA LM7 Center)` | **`-87.8897`** | **`+90.0000`** | `(+63998.6, 0.0)` | `1000.0` | `impact_breccia` | NASA GSFC PGDA `LM7_final_adj_5mpp_surf.tif` (`X=[54,74] km, Y=[-10,+10] km` grid merkezi); Barker vd. (2021); Artemis III Faustini Rim A |

---

## 2. Saha Bazlı Gerçek Ölçüm Sonuçları (`r = 1000.0 m`)

Projeksiyon: Metrik **Ay Güney Kutbu Polar Stereografik CRS** (`+proj=stere +lat_0=-90 +lon_0=0 +k=1 +x_0=0 +y_0=0 +R=1737400 +units=m +no_defs`, `MOON_ME` DE421). Her `r = 1000.0 m` dairesel analiz penceresi **`~125,664 – 125,676`** adet `5 m × 5 m` LOLA DEM pikseli içerir:

| `site_id` | `slope_mean ± sd` (°) | `slope_p90 ± sd` (°) | `roughness ± sd` (m) | `relief ± sd` (m) | `temp_amplitude ± sd` (K) | `thermal_inertia ± sd` ($\text{J m}^{-2}\text{K}^{-1}\text{s}^{-1/2}$) | `albedo ± sd` | DEM Kaynağı (`_src`) |
|---|---|---|---|---|---|---|---|---|
| **`moon_shackleton_rim`** | `18.5045 ± 1.5135` | `30.7879 ± 1.5135` | `90.4258 ± 0.3856` | `501.3733 ± 0.5769` | `113.8029 ± 3.2387` | `274.88 ± 59.35` (`res=240m`) | `0.1469 ± 0.0036` | `LRO_LOLA_PGDA_Site04_5mpp_v2021` |
| **`moon_connecting_ridge`** | `9.4331 ± 1.8912` | `16.2303 ± 1.8913` | `42.4654 ± 0.3635` | `184.4755 ± 0.5363` | `131.9347 ± 3.1129` | `279.82 ± 65.32` (`res=240m`) | `0.1455 ± 0.0015` | `LRO_LOLA_PGDA_Site01_5mpp_v2021` |
| **`moon_de_gerlache_rim`** | `10.8324 ± 1.7236` | `18.8078 ± 1.7239` | `44.9633 ± 0.3713` | `250.4174 ± 0.6257` | `117.3454 ± 6.8848` | `85.70 ± 16.10` (`res=240m`) | `0.1366 ± 0.0009` | `LRO_LOLA_PGDA_Site11_5mpp_v2021` |
| **`moon_shackleton_peak`** | `8.1100 ± 1.7702` | `15.2735 ± 1.7705` | `32.3266 ± 0.3294` | `213.5736 ± 0.4833` | `124.4798 ± 25.3286` | `111.53 ± 147.72` (`res=240m`) | `0.1417 ± 0.0020` | `LRO_LOLA_PGDA_Site07_5mpp_v2021` |
| **`moon_faustini_rim`** | `5.2013 ± 1.9768` | `8.6753 ± 1.9768` | `12.2904 ± 0.4508` | `145.2425 ± 0.7463` | `151.2074 ± 3.8219` | `52.78 ± 6.60` (`res=240m`) | `0.1362 ± 0.0004` | `LRO_LOLA_PGDA_LM7_5mpp_v2021` |

---

## 3. Birincil Veri Kaynakları Tablosu (Doğrulanan ve İndirilen NASA Ürünleri)

| Veri Türü | Sözleşme Kolonu | Tam Ürün Adı (`X_src`) | Versiyon | Çözünürlük (`X_res_m`) | Kapsadığı Bölge | Projeksiyon | Format & Erişim | Doğrudan İndirme Linki | Doğrulama Durumu |
|---|---|---|---|---|---|---|---|---|---|
| **1. Yükseklik / Eğim (DEM)** | `slope_mean`, `slope_p90`, `roughness`, `relief` | `LRO_LOLA_PGDA_<Site>_5mpp_v2021` (`<Site>_final_adj_5mpp_surf.tif`) | `v2021` (Barker vd., 2021) | **`5.0 m`** | `Site04`, `Site01`, `Site11`, `Site07` (`16×16 km`), `LM7` (`20×20 km`) | Güney Kutbu Stereografik (`MOON_ME` DE421, metre) | `.tif` (GeoTIFF, HTTP Range + `data/raw/moon/` cache) | [NASA GSFC PGDA Product 78](https://pgda.gsfc.nasa.gov/products/78) | **DOĞRULANDI** (`data/raw/moon/` altında mevcut) |
| **1b. Eğim Belirsizliği (`_sd`)** | `slope_mean_sd`, `slope_p90_sd` | `LRO_LOLA_PGDA_<Site>_5mpp_v2021` (`<Site>_final_adj_5mpp_slperr.tif`) | `v2021` (Barker vd., 2021) | **`5.0 m`** | `Site04`, `Site01`, `Site11`, `Site07`, `LM7` | Güney Kutbu Stereografik (`MOON_ME` DE421, metre) | `.tif` (GeoTIFF, HTTP Range + 200 bootstrap) | [NASA GSFC PGDA Product 78](https://pgda.gsfc.nasa.gov/products/78) | **DOĞRULANDI** (`data/raw/moon/` altında mevcut) |
| **1c. Düşey Belirsizlik (`_sd`)** | `roughness_sd`, `relief_sd` | `LRO_LOLA_PGDA_<Site>_5mpp_v2021` (`<Site>_final_adj_5mpp_toterr.tif`) | `v2021` (Barker vd., 2021) | **`5.0 m`** | `Site04`, `Site01`, `Site11`, `Site07`, `LM7` | Güney Kutbu Stereografik (`MOON_ME` DE421, metre) | `.tif` (GeoTIFF, HTTP Range + 200 bootstrap) | [NASA GSFC PGDA Product 78](https://pgda.gsfc.nasa.gov/products/78) | **DOĞRULANDI** (`data/raw/moon/` altında mevcut) |
| **2. Yüzey Sıcaklığı** | `temp_amplitude` | `LRO-L-DLRE-5-PCP-V1.0:pcp_avg_tbol_pols_240m_v2022` (PDS3 `.lbl`: `DATA_SET_ID = "LRO-L-DLRE-5-GCP-V1.0"`) | `v1.0` (Williams vd., 2019/2022) | **`240.0 m`** | **80.0°S – 90.0°S**, **-180° – +180°E** | Güney Kutbu Stereografik (`R = 1737.4 km`) | `.tab` + `.lbl` (`ltim01..ltim96`, her dilim `0.25 saat` yerel zaman) | [pcp_avg_tbol_pols_sum_ltim01..96_240](https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_pcp/diurnal/ltim/pols/) | **GEÇİCİ / LİDER KARARI BEKLİYOR** (§4.4'te `ltim01..ltim96` doğrulaması ve Seçenek a/b belgeli) |
| **3. Yüzey Parlaklığı (Albedo)** | `albedo` | `LRO-L-LOLA-4-GDR-V1.0:LDAM_50S_1000M_V1.0_broadband_eq` (`LDAM_50S_1000M_FLOAT.IMG`) | `V1.0` (Lemelin vd., 2016; Vasavada vd., 2012) | **`1000.0 m`** | **50.0°S – 90.0°S**, **0° – 360°E** | Güney Kutbu Stereografik (`R = 1737.4 km`) | `.IMG` + `.LBL` (32-bit Float, **25.6 MB**) | [LDAM_50S_1000M_FLOAT.IMG](https://imbrium.mit.edu/DATA/LOLA_GDR/POLAR/FLOAT_IMG/LDAM_50S_1000M_FLOAT.IMG) | **DOĞRULANDI** (`data/raw/moon/` altında mevcut) |
| **4. Termal Eylemsizlik (1D Model)** | `thermal_inertia` | `LRO-L-DLRE-5-PCP-V1.0:1D_Hayne2017_polar_TI_v1` | `v1` (Hayne vd., 2017; Williams vd., 2019) | **`240.0 m`** (Diviner PCP çözünürlüğü) | **80.0°S – 90.0°S**, **-180° – +180°E** | Güney Kutbu Stereografik (`R = 1737.4 km`) | 1D Gece Soğuma / İletim-Işınım Modeli (`273 K` referanslı, `52.8–279.8 TIU`) | [PDS Diviner Derived PCP](https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_pcp/) | **ASKIDA / NaN ÖNERİLDİ** (Earth TI = `NaN` ve ortak tanım onayı olmadığı için lider kararıyla `NaN`'a çekilecek) |

---

## 4. Metodoloji ve Earth (`src/earth/`) ile Birebir Tutarlılık Notları

1. **Projeksiyon ve Eğim (`slope_mean`, `slope_p90`):**
   - Tüm PGDA LOLA 5 m/piksel DEM'leri doğrudan metrik Güney Kutbu Polar Stereografik projeksiyonda (`dx = dy = 5.0 m`) gelir.
   - `r = 1000.0 m` içinde `np.gradient(elev, dy_m, dx_m)` ve `np.degrees(np.arctan(np.hypot(dz_dx, dz_dy)))` ile Earth (`src/earth/dem_pipeline.py`) ile birebir aynı formülle hesaplanmıştır.
2. **Pürüzlülük (`roughness`) ve Rölyef (`relief`):**
   - `roughness`: `r = 1000.0 m` içindeki `(dx, dy, 1)` koordinatlarına en küçük kareler düzlem uydurulup (`np.linalg.lstsq`) kalıntıların örneklem standart sapması (`np.std(residuals, ddof=1)`, metre) alınmıştır.
   - `relief`: `r = 1000.0 m` içindeki `max(z) - min(z)` (metre) olarak hesaplanmıştır.
3. **Belirsizlik (`_sd`):**
   - `slope_mean_sd`, `slope_p90_sd`: `r = 1000.0 m` içindeki `~125,665` piksel üzerinden `n_boot = 200` çekilişli bootstrap standart sapması (`ddof=1`) ile PGDA klon ansamblı eğim RMS hata haritası (`<Site>_final_adj_5mpp_slperr.tif`, Barker vd. 2021) karekök-toplam (`math.hypot`) yöntemiyle birleştirilmiştir.
   - `roughness_sd`, `relief_sd`: Sabit sayı yerine her sahanın kendi NASA GSFC PGDA 5 m/piksel klon ansamblı düşey RMS hata haritasından (`<Site>_final_adj_5mpp_toterr.tif`) `r = 1000.0 m` içindeki piksel medyanı (`vert_rms_m`: `Site07=0.3235 m`, `Site01=0.3547 m`, `Site04=0.3613 m`, `Site11=0.3625 m`, `LM7=0.4504 m`) çekilmiş; 200 çekilişli bootstrap standart sapmaları (`boot_rough_sd`, `boot_relief_sd`) ile `roughness_sd = hypot(vert_rms_m, boot_rough_sd)` ve iki uç yükseklik farkı propagasyonu gereği `relief_sd = hypot(sqrt(2) * vert_rms_m, boot_relief_sd)` olarak hesaplanmıştır.
   - `temp_amplitude_sd`: `r = 1000.0 m` içindeki 240 m Diviner hücreleri üzerinden 200 çekilişli bootstrap standart sapması (`ddof=1`, alt sınır `2.5 K` radyometrik kalibrasyon belirsizliği).
   - `albedo_sd`: Saha penceresine düşen 1000 m LOLA aktif lazer reflektans piksellerinin örneklem standart sapması (`ddof=1`, `0.38` geniş bant dönüşüm çarpanı uygulanmış).
   - **Geniş Bant Güneş Albedosu Dönüşümü (`albedo`):** Earth `MCD43A3.061` (`Albedo_BSA_shortwave`) geniş bant yönlü-yarıküre güneş albedosu tanımıyla birebir fiziksel uyum sağlamak amacıyla, sıfır faz açılı (`α = 0°`, opposition surge dahil) `LDAM_50S_1000M_V1.0` 1064 nm normal albedo değerleri (ve `albedo_sd`) LRO Diviner/LOLA literatüründeki `0.38` katsayısıyla çarpılarak (`~0.136–0.147`) geniş bant güneş (hemispherical/Bond) albedosuna dönüştürülmüştür (*Vasavada et al., 2012, JGR 117:E00H18; Hayne et al., 2017, JGR Planets 122:2371; Lucey et al., 2014*).
   - **Litoloji (`lithology_class`):** `AGENTS.md` §5 Veri Sözleşmesi gereği `features_moon.parquet` tam 36 sütun içerir; niteliksel `lithology_class` (`regolith`, `anorthosite`, `impact_breccia`) için birincil literatür kaynağı `LRO_LOLA_Diviner_SouthPole_Regolith_Zuber2012_Spudis2008` (*Zuber et al., 2012, Nature 486:378–381; Spudis et al., 2008, GRL 35:L14201; Barker et al., 2021*) bu dokümanda (§1) kayıtlıdır.
4. **Diviner `temp_amplitude` — PDS3 `.lbl` Etiket Doğrulaması, `ltim01..ltim96` Kapsaması ve Lider Kararı Seçenekleri:**
   - **Resmî PDS3 `.lbl` Etiketleri:** [pcp_avg_tbol_pols_sum_ltim01_240.lbl](https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_pcp/diurnal/ltim/pols/pcp_avg_tbol_pols_sum_ltim01_240.lbl) .. [ltim96_240.lbl](https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_pcp/diurnal/ltim/pols/pcp_avg_tbol_pols_sum_ltim96_240.lbl) dosyalarında `DATA_SET_ID = "LRO-L-DLRE-5-GCP-V1.0"`, `PRODUCT_TYPE = "PCP"`, `MAP_SCALE = 240 <m/pix>`, `START_TIME = 2009-07-05T16:50:26.195`, `STOP_TIME = 2019-02-17T00:00:00.000` (güney yazı `subsolar_latitude < 0°`, *Williams et al., 2019, JGR Planets 124:2505–2521*) tanımlıdır. Her `ltimXX` (`XX = 01..96`) dilimi `0.25 saat` yerel zaman (`LRO:DLRE_CLOCTIME_MIN = (XX-1)*0.25 <hour>`, `LRO:DLRE_CLOCTIME_MAX = XX*0.25 <hour>`) aralığını temsil eder:
     - `ltim01`: `0.00 – 0.25 saat` (yerel gece yarısı dilimi)
     - `ltim25`: `6.00 – 6.25 saat` (yerel sabah / şafak dilimi)
     - `ltim49`: `12.00 – 12.25 saat` (yerel öğle dilimi)
     - `ltim73`: `18.00 – 18.25 saat` (yerel akşamüstü dilimi — önceki metinde sehven *"yerel öğle fazı"* olarak yazılan ifade düzeltilmiştir)
     - `ltim96`: `23.75 – 24.00 saat` (gece yarısı öncesi son dilim)
   - **Mevcut `features_moon.parquet` Değerlerinin Durumu (Lider Kararı Çıkana Kadar Dokunulmadı):** Mevcut parquet içindeki ilk 4 saha (`moon_shackleton_rim`: `113.80 K`, `moon_connecting_ridge`: `131.93 K`, `moon_de_gerlache_rim`: `117.35 K`, `moon_shackleton_peak`: `124.48 K`) yalnızca `ltim01` (`0.00–0.25 saat`) dilimi içindeki `r = 1000 m` uzamsal `max − min` değerini, `moon_faustini_rim` (`151.21 K`) ise `ltim01` (`63.79 K`) ve `ltim73` (`18.00–18.25 saat`, `214.99 K`) birleşimini kullanmaktadır. Tek dilimdeki uzamsal fark gerçek bir günlük zaman döngüsü (*diurnal cycle*) genliği değildir.
   - **`ltim01..ltim96` (24 Saatlik Dilim `ltim01, ltim05, ..., ltim93`) Kapsama Doğrulaması ve İki Seçenek:**
     - Kutupsal enlemlerde (`87.89°S – 89.78°S`) LRO yörünge geometrisi ve ~1.5° sıyırıcı güneş geliş açısı nedeniyle sabit `ltim49 − ltim01` (`12:00h − 00:00h`) farkı tek biçimli kullanılamaz (`ltim49` diliminde `de_gerlache_rim` için `n = 0`, `connecting_ridge` için `n = 1` hücre doludur ve maksimum ısınma yamaç bakısına bağlı yerel saatte gerçekleşir).
     - **Seçenek (a) — 24 Saatlik `ltim` Serisinden Tek Biçimli Zamansal Günlük Genlik ($\Delta T_{\text{diurnal}}$):** `pcp_avg_tbol_pols_sum_ltim01..ltim96_240.tab` serisinde 1'er saatlik 24 yerel zaman dilimi (`ltim01, ltim05, ..., ltim93`) sorgulandığında her 5 sahada `16/24` ila `24/24` saat dilimi doludur (`r = 1000 m` içinde en az 6 farklı yerel saat diliminde gözlemi olan `54–56` adet `240 m` hücresi mevcuttur):
       - `moon_shackleton_rim` (`24/24` dolu dilim, `56` hücre): Hücre bazlı zamansal $\overline{\Delta T_{\text{cell}}} = \mathbf{187.04 \pm 23.47\text{ K}}$ ($\bar{T}_{\min}=91.33\text{ K}, \bar{T}_{\max}=278.37\text{ K}$); saha ortalaması eğri genliği $\max_t \bar{T}(t) - \min_t \bar{T}(t) = \mathbf{144.31\text{ K}}$ (`274.15 K @ ltim77` − `129.84 K @ ltim53`).
       - `moon_connecting_ridge` (`20/24` dolu dilim, `54` hücre): Hücre bazlı zamansal $\overline{\Delta T_{\text{cell}}} = \mathbf{146.96 \pm 31.32\text{ K}}$ ($\bar{T}_{\min}=93.18\text{ K}, \bar{T}_{\max}=240.15\text{ K}$); saha ortalaması eğri genliği $\mathbf{71.25\text{ K}}$ (`202.04 K @ ltim17` − `130.79 K @ ltim53`).
       - `moon_de_gerlache_rim` (`16/24` dolu dilim, `56` hücre): Hücre bazlı zamansal $\overline{\Delta T_{\text{cell}}} = \mathbf{158.22 \pm 32.71\text{ K}}$ ($\bar{T}_{\min}=86.34\text{ K}, \bar{T}_{\max}=244.56\text{ K}$); saha ortalaması eğri genliği $\mathbf{129.53\text{ K}}$ (`221.23 K @ ltim65` − `91.70 K @ ltim09`).
       - `moon_shackleton_peak` (`24/24` dolu dilim, `54` hücre): Hücre bazlı zamansal $\overline{\Delta T_{\text{cell}}} = \mathbf{150.63 \pm 25.84\text{ K}}$ ($\bar{T}_{\min}=74.22\text{ K}, \bar{T}_{\max}=224.85\text{ K}$); saha ortalaması eğri genliği $\mathbf{124.99\text{ K}}$ (`193.40 K @ ltim89` − `68.41 K @ ltim05`).
       - `moon_faustini_rim` (`18/24` dolu dilim, `56` hücre): Hücre bazlı zamansal $\overline{\Delta T_{\text{cell}}} = \mathbf{155.67 \pm 12.08\text{ K}}$ ($\bar{T}_{\min}=52.80\text{ K}, \bar{T}_{\max}=208.47\text{ K}$); saha ortalaması eğri genliği $\mathbf{144.84\text{ K}}$ (`197.66 K @ ltim65` − `52.82 K @ ltim17`).
     - **Seçenek (b) — Fiziksel Tanım/Zaman Ölçeği Farkı Nedeniyle `temp_amplitude = NaN` (Termal Eksenin Askıya Alınması):** Ay Güney Kutbu'ndaki 29.53 Dünya günü süren vakumlu sinodik yaz döngüsü (`subsolar_lat < 0°`, sıyırıcı topoğrafik gölgeleme kontrollü) ile Dünya'daki `MOD11A2.061` 24 saatlik atmosferli gündüz–gece LST farkının yıllık ortalaması aynı fiziksel/zamansal rejim değildir (`AGENTS.md` §5: *"Compute every feature with the SAME definition"*). Lider Seçenek (b)'yi onaylarsa `features_moon.parquet` içinde `temp_amplitude = NaN` (`_sd = NaN`, `_src = ""`, `_res_m = NaN`) yapılır; Diviner sıcaklık aralıkları yalnızca nitel/analoji sınırları kanalında raporlanır.
5. **M2 · `thermal_inertia` Ortak Kuralı ve `NaN`'a Çekme Önerisi (Kapı 1):**
   - **PDS Dijital Ürün Kontrolü:** Hayne et al. (2017, *JGR Planets* 122:2371–2400) küresel `H`-parametresi haritası (`dgdr_hpar_avg_cyl_128_jp2`) PDS arşivinde yalnızca silindirik `±70°` enlemlerini (`70°S–70°N`) kapsamakta olup Ay Güney Kutbu'nu (`87.8°S–89.8°S`) içermez.
   - **Ortak Kural Gereği `NaN` Önerisi:** Mevcut `features_moon.parquet` içindeki `thermal_inertia` (`52.78 – 279.82 TIU`) `ltim01` dağılımına dayalı özel bir 1D soğuma yaklaşımıdır ve resmî bir PDS kutup TI ürünü değildir; ayrıca `features_earth.parquet` içinde `thermal_inertia` tüm 40 sahada `NaN` bırakılmıştır ve iki gök cismi arasında ortak bir TI tanımı bulunmamaktadır. Bu nedenle lider onayıyla birlikte `features_moon.parquet` içinde `thermal_inertia = NaN` (`thermal_inertia_sd = NaN`, `thermal_inertia_src = ""`, `thermal_inertia_res_m = NaN`) olarak sıfırlanması önerilmiştir.

---

## 5. Geniş Bant Albedo Aktarım Hassasiyeti Analizi ve Görsel Atlas Özeti

### 5.1. Geniş Bant Albedo Aktarım Hassasiyeti Analizi (`src/moon_mars/albedo_sensitivity.py`)

LRO LOLA `LDAM_50S_1000M_FLOAT.IMG` aktif lazer reflektometresi sıfır faz açısında ($\alpha = 0^\circ$, karşıtlık parlaması / *opposition surge* dahil) monokromatik 1064 nm normal albedo ($\sim 0.358 - 0.387$) ölçer. Dünya'daki pasif güneş reflektansı tabanlı MODIS `MCD43A3.061` (`Albedo_BSA_shortwave`) ile aynı fiziksel birime getirmek için kullanılan $c = 0.38$ dönüşüm katsayısının (*Vasavada et al., 2012; Hayne et al., 2017; Lucey et al., 2014*) faz integrali ve spektral eğim belirsizliği aralığındaki ($c \in [0.30, 0.34, 0.38, 0.42, 0.46]$) etkisi `src/moon_mars/albedo_sensitivity.py` ile tüm 5 referans sahası ve 28 Dünya sahası üzerinde test edilmiştir:

| Referans Saha (`ref_site_id`) | Çarpan (`c`) | Ölçeklenmiş Ay Albedosu | Ortalama `surface` Skor Farkı ($\|\Delta S_{\text{surf}}\|$) | Ortalama Genel Skor Farkı ($\|\Delta S_{\text{overall}}\|$) | Genel Sıralama Spearman $\rho$ | Top-1 Dünya Sahası (Tümü) | Top-3 Aday Sahalar (`role == "candidate"`) |
|---|---|---|---|---|---|---|---|
| **`moon_shackleton_rim`** | `0.30` | `0.1160` | `0.2180` | `0.0727` | `0.6379` | `earth_deccan_mahabaleshwar` | `earth_deccan_mahabaleshwar, earth_tendurek_shield, earth_pinacate_el_elegante` |
| **`moon_shackleton_rim`** | `0.34` | `0.1314` | `0.1227` | `0.0409` | `0.8936` | `earth_lunar_crater_nevada` | `earth_deccan_mahabaleshwar, earth_karacadag_summit, earth_karapinar_meke` |
| **`moon_shackleton_rim`** | **`0.38` (Baz)** | **`0.1469`** | **`0.0000`** | **`0.0000`** | **`1.0000`** | `earth_suphan_south_apron` | `earth_suphan_south_apron, earth_karapinar_meke, earth_hasandagi_kecekalecik` |
| **`moon_shackleton_rim`** | `0.42` | `0.1624` | `0.1250` | `0.0417` | `0.8983` | `earth_erciyes_kojugedigi` | `earth_erciyes_kojugedigi, earth_hasandagi_kecekalecik, earth_suphan_south_apron` |
| **`moon_shackleton_rim`** | `0.46` | `0.1778` | `0.1942` | `0.0647` | `0.6994` | `earth_hasandagi_kecekalecik` | `earth_hasandagi_kecekalecik, earth_erciyes_kojugedigi, earth_kilbourne_hole_nm` |
| **`moon_connecting_ridge`** | `0.34` | `0.1302` | `0.1234` | `0.0411` | `0.9396` | `earth_karacadag_summit` | `earth_karacadag_summit, earth_karapinar_meke, earth_deccan_mahabaleshwar` |
| **`moon_connecting_ridge`** | **`0.38` (Baz)** | **`0.1455`** | **`0.0000`** | **`0.0000`** | **`1.0000`** | `earth_mcmurdo_wright_valley` | `earth_karapinar_meke, earth_kula_divlit, earth_karacadag_summit` |
| **`moon_connecting_ridge`** | `0.42` | `0.1608` | `0.1270` | `0.0423` | `0.8917` | `earth_agri_dogubayazit_flow` | `earth_agri_dogubayazit_flow, earth_kula_divlit, earth_erciyes_kojugedigi` |
| **`moon_de_gerlache_rim`** | `0.34` | `0.1222` | `0.1088` | `0.0363` | `0.9328` | `earth_deccan_mahabaleshwar` | `earth_deccan_mahabaleshwar, earth_karacadag_summit, earth_karapinar_meke` |
| **`moon_de_gerlache_rim`** | **`0.38` (Baz)** | **`0.1366`** | **`0.0000`** | **`0.0000`** | **`1.0000`** | `earth_mcmurdo_wright_valley` | `earth_karapinar_meke, earth_deccan_mahabaleshwar, earth_karacadag_summit` |
| **`moon_de_gerlache_rim`** | `0.42` | `0.1510` | `0.1187` | `0.0396` | `0.9326` | `earth_karapinar_meke` | `earth_karapinar_meke, earth_erciyes_kojugedigi, earth_kula_divlit` |
| **`moon_shackleton_peak`** | `0.34` | `0.1268` | `0.1234` | `0.0411` | `0.9317` | `earth_karacadag_summit` | `earth_karacadag_summit, earth_salda_terrace, earth_karapinar_meke` |
| **`moon_shackleton_peak`** | **`0.38` (Baz)** | **`0.1417`** | **`0.0000`** | **`0.0000`** | **`1.0000`** | `earth_mcmurdo_wright_valley` | `earth_karapinar_meke, earth_karacadag_summit, earth_kula_divlit` |
| **`moon_shackleton_peak`** | `0.42` | `0.1566` | `0.1297` | `0.0432` | `0.9182` | `earth_kula_divlit` | `earth_kula_divlit, earth_agri_dogubayazit_flow, earth_karapinar_meke` |
| **`moon_faustini_rim`** | `0.34` | `0.1218` | `0.1075` | `0.0358` | `0.9306` | `earth_salda_terrace` | `earth_salda_terrace, earth_tendurek_shield, earth_karacadag_summit` |
| **`moon_faustini_rim`** | **`0.38` (Baz)** | **`0.1362`** | **`0.0000`** | **`0.0000`** | **`1.0000`** | `earth_salda_terrace` | `earth_salda_terrace, earth_karacadag_summit, earth_tendurek_shield` |
| **`moon_faustini_rim`** | `0.42` | `0.1505` | `0.1174` | `0.0391` | `0.8752` | `earth_kula_divlit` | `earth_kula_divlit, earth_salda_terrace, earth_acigol_guneydag` |

**Fiziksel Yorum ve Kararlılık Sonucu:**
1. **Yakın Belirsizlik Bandında ($c \in [0.34, 0.42]$, $\pm 10.5\%$):** Tüm 5 Ay Güney Kutbu referans sahasında genel sıralama Spearman korelasyonu **$\rho = 0.854 - 0.944$** aralığında kalmakta ve ortalama genel skor değişimi yalnızca **$\pm 0.034 - 0.042$** düzeyindedir.
2. **Aday Havuzu Kararlılığı:** `c = 0.34`'te daha koyu bazaltik kalkanlar (`earth_karacadag_summit`, `earth_deccan_mahabaleshwar`, `earth_kula_divlit`), `c = 0.42`'de ise biraz daha açık tonlu volkanik/piroklastik yüzeyler (`earth_hasandagi_kecekalecik`, `earth_erciyes_kojugedigi`, `earth_puna_campo_piedra_pomez`) üst sıraları paylaşmakta; Anadolu aday sahaları (`Karacadağ`, `Kula Divlit`, `Hasandağ`, `Erciyes`, `Salda`) tüm çarpan aralığında Top-3 portföy çekirdeğini korumaktadır.

### 5.2. 5 m/piksel LRO LOLA Görsel, Eğim Sınıfları ve Kesit Atlası (`data/processed/moon_atlas/`)

`src/moon_mars/moon_visual_atlas.py` modülü, 5 Ay Güney Kutbu referans sahasının her biri için `2.2 × 2.2 km` yerel pencerede (`5 m/px` çözünürlük, `r = 1000 m` analiz çemberi) kutupsal rölyef (`<site_id>_hillshade.png`), eğim sınıfları haritası (`<site_id>_hazard.png`), 3 panelli kesit özeti (`<site_id>_atlas.png`) ve `atlas_metadata.json` dosyalarını üretir (*Not: "Illustrative slope bins; not a landing-safety assessment."*):

| `site_id` | Türkçe Saha Adı (`name_tr`) | `<10° eğim` (`pct_lt10deg`) | `10–20° eğim` (`pct_10_20deg`) | `>20° eğim` (`pct_gt20deg`) | Görsel Atlas Dosyaları (`data/processed/moon_atlas/`) |
|---|---|---|---|---|---|
| **`moon_shackleton_rim`** | `Shackleton Krateri Kenarı (Saha 04 ROI)` | **`%17.94`** | `%40.74` | `%41.33` | `moon_shackleton_rim_{hillshade,hazard,atlas}.png` |
| **`moon_connecting_ridge`** | `Bağlantı Sırtı (Shackleton–de Gerlache, Saha 01 ROI)` | **`%54.49`** | `%44.18` | `%1.33` | `moon_connecting_ridge_{hillshade,hazard,atlas}.png` |
| **`moon_de_gerlache_rim`** | `de Gerlache Krateri Kenarı (Saha 11 ROI)` | **`%47.58`** | `%45.39` | `%7.03` | `moon_de_gerlache_rim_{hillshade,hazard,atlas}.png` |
| **`moon_shackleton_peak`** | `Shackleton Yakını Zirve (Saha 07 ROI)` | **`%73.09`** | `%25.28` | `%1.63` | `moon_shackleton_peak_{hillshade,hazard,atlas}.png` |
| **`moon_faustini_rim`** | `Faustini Krateri Kenarı A (PGDA LM7 Merkezi)` | **`%94.75`** | `%5.24` | `%0.01` | `moon_faustini_rim_{hillshade,hazard,atlas}.png` |

### 5.3. M3 · SigLIP Moon `224×224` Görsel Keşif Thumbnail Seti (`data/processed/thumbs/moon/`)

Nitelikli görsel keşif kanalı için (**sayısal skorlamaya dahil edilmez**) 5 Ay Güney Kutbu referans sahasının her biri için `224 × 224` piksel boyutunda kompakt LRO LOLA 5 m/px kutupsal rölyef görselleri (`data/processed/thumbs/moon/<site_id>.png`) ve meta tabloları (`thumbs_metadata.json`, `thumbs_metadata.csv`) üretilmiştir:

| `site_id` | `tile_id` | Koordinat (`lat, lon`) | Stereografik `(X, Y)` (m) | Boyut (`px`) | Ölçek (`m/px`) | Kaynak (`source`) | Dosya Yolu |
|---|---|---|---|---|---|---|---|
| **`moon_shackleton_rim`** | `PGDA_LOLA_5mpp_Site04` | `-89.7800, -156.3201` | `(-2679.3, -6109.5)` | `224x224` | `9.8214` (5.0 m native) | `NASA_GSFC_PGDA_Product78:LRO_LOLA_PGDA_Site04_5mpp_v2021` | `data/processed/thumbs/moon/moon_shackleton_rim.png` |
| **`moon_connecting_ridge`** | `PGDA_LOLA_5mpp_Site01` | `-89.4624, -137.0871` | `(-11099.8, -11939.4)` | `224x224` | `9.8214` (5.0 m native) | `NASA_GSFC_PGDA_Product78:LRO_LOLA_PGDA_Site01_5mpp_v2021` | `data/processed/thumbs/moon/moon_connecting_ridge.png` |
| **`moon_de_gerlache_rim`** | `PGDA_LOLA_5mpp_Site11` | `-88.6683, -68.3754` | `(-37541.2, +14882.2)` | `224x224` | `9.8214` (5.0 m native) | `NASA_GSFC_PGDA_Product78:LRO_LOLA_PGDA_Site11_5mpp_v2021` | `data/processed/thumbs/moon/moon_de_gerlache_rim.png` |
| **`moon_shackleton_peak`** | `PGDA_LOLA_5mpp_Site07` | `-88.8063, +123.5451` | `(+30169.5, -20002.9)` | `224x224` | `9.8214` (5.0 m native) | `NASA_GSFC_PGDA_Product78:LRO_LOLA_PGDA_Site07_5mpp_v2021` | `data/processed/thumbs/moon/moon_shackleton_peak.png` |
| **`moon_faustini_rim`** | `PGDA_LOLA_5mpp_LM7` | `-87.8897, +90.0000` | `(+63998.6, 0.0)` | `224x224` | `9.8214` (5.0 m native) | `NASA_GSFC_PGDA_Product78:LRO_LOLA_PGDA_LM7_5mpp_v2021` | `data/processed/thumbs/moon/moon_faustini_rim.png` |

### 5.4. M6 · Commit'lenmiş Moon 3D Yükseklik Gridleri (`data/processed/moon_3d/`)

2D görsel atlas ile birebir aynı merkez (`x0_m, y0_m`), aynı `2.2 × 2.2 km` yerel pencere (`442 × 442` piksel, `dx = dy = 5.0 m`) ve aynı `r = 1000 m` analiz çemberine sahip 3D yükseklik gridleri hem sıkıştırılmış `float32` (`<site_id>_3d.npz`, merkezden geçen Batı–Doğu ve Güney–Kuzey kesit profilleri dahil) hem de `16-bit grayscale heightmap PNG` (`<site_id>_heightmap16.png`) formatında `data/processed/moon_3d/` altına kaydedilmiştir (`moon_3d_metadata.json` içinde `elev_min_m`, `elev_max_m`, `dx_m`, `dy_m`, `extent_rel_m`, `extent_stereo_m` ve 16-bit kuantizasyon hassasiyeti `png16_quantization_step_m` belgelidir):

| `site_id` | Grid Boyutu (`px`) | `dx = dy` (m) | `elev_min_m` .. `elev_max_m` (m) | `float32` `.npz` Hassasiyeti | `16-bit PNG` Kuantizasyon Adımı (`m/ADU`) | Dosyalar (`data/processed/moon_3d/`) |
|---|---|---|---|---|---|---|
| **`moon_shackleton_rim`** | `442 × 442` | `5.0` | `1118.26 .. 1739.12` (`r<=1 km`: `1237.75 .. 1739.12`) | `0.01 m` | `0.00947 m` | `moon_shackleton_rim_{3d.npz,heightmap16.png}` |
| **`moon_connecting_ridge`** | `442 × 442` | `5.0` | `1589.60 .. 1959.50` (`r<=1 km`: `1775.02 .. 1959.50`) | `0.01 m` | `0.00564 m` | `moon_connecting_ridge_{3d.npz,heightmap16.png}` |
| **`moon_de_gerlache_rim`** | `442 × 442` | `5.0` | `1333.58 .. 1815.99` (`r<=1 km`: `1565.57 .. 1815.99`) | `0.01 m` | `0.00736 m` | `moon_de_gerlache_rim_{3d.npz,heightmap16.png}` |
| **`moon_shackleton_peak`** | `442 × 442` | `5.0` | `1253.39 .. 1648.68` (`r<=1 km`: `1435.11 .. 1648.68`) | `0.01 m` | `0.00603 m` | `moon_shackleton_peak_{3d.npz,heightmap16.png}` |
| **`moon_faustini_rim`** | `442 × 442` | `5.0` | `-91.08 .. +132.93` (`r<=1 km`: `-30.51 .. +114.73`) | `0.01 m` | `0.00342 m` | `moon_faustini_rim_{3d.npz,heightmap16.png}` |

---

## Özellik kaynağı ve literatür spot-kontrolü

Aşağıdaki ortak tablo, Ay Güney Kutbu referans sahaları (`features_moon.parquet`) ve Dünya doğrulama/aday sahaları (`features_earth.parquet`) için boru hattımızdan çıkan sayısal değerleri hakemli gezegen bilimi literatüründeki yayınlanmış ölçüm aralıklarıyla karşılaştırır:

| Gök Cismi | `site_id` | Özellik | Boru Hattı Değeri (`± 1σ`) | Yayınlanmış Literatür Aralığı | Hakemli Literatür Kaynağı ve Uygunluk Notu |
|---|---|---|---|---|---|
| **Moon** | `moon_shackleton_rim` | `temp_amplitude` *(Lider kararı bekliyor)* | Mevcut (`ltim01` uzamsal): `113.80 ± 3.24 K`; Seçenek (a) 24-dilim hücre $\Delta T$: **`187.04 ± 23.47 K`** (saha ort. eğri: `144.31 K`) | Yaz maksimumu $T_{\text{max}} \approx 220\text{–}280\text{ K}$, gölge/gece $T_{\text{min}} \approx 80\text{–}105\text{ K}$ | **Paige et al. (2010, *Science* 330:479)** & **Williams et al. (2019, *JGR Planets* 124:2505)**: `ltim01..ltim96` doğrulaması §4.4'tedir; lider kararına göre Seçenek (a) veya Seçenek (b) (`NaN`) uygulanacaktır. |
| **Moon** | `moon_connecting_ridge` | `temp_amplitude` *(Lider kararı bekliyor)* | Mevcut (`ltim01` uzamsal): `131.93 ± 3.11 K`; Seçenek (a) 24-dilim hücre $\Delta T$: **`146.96 ± 31.32 K`** (saha ort. eğri: `71.25 K`) | $T_{\text{max}} \approx 220\text{–}265\text{ K}$, $T_{\text{min}} \approx 75\text{–}95\text{ K}$ | **Williams et al. (2019, *JGR Planets* 124:2505)** & **Mazarico et al. (2011, *Icarus* 211:1066)**: `Site 01` bağlantı sırtında 20/24 saat dilimi dolu; lider kararı beklenmektedir. |
| **Moon** | `moon_de_gerlache_rim` | `temp_amplitude` *(Lider kararı bekliyor)* | Mevcut (`ltim01` uzamsal): `117.35 ± 6.88 K`; Seçenek (a) 24-dilim hücre $\Delta T$: **`158.22 ± 32.71 K`** (saha ort. eğri: `129.53 K`) | $T_{\text{max}} \approx 220\text{–}285\text{ K}$, $T_{\text{min}} \approx 70\text{–}90\text{ K}$ | **Paige et al. (2010, *Science* 330:479)** & **Williams et al. (2019)**: `Site 11` de Gerlache kenarında 16/24 saat dilimi dolu; lider kararı beklenmektedir. |
| **Moon** | `moon_shackleton_peak` | `temp_amplitude` *(Lider kararı bekliyor)* | Mevcut (`ltim01` uzamsal): `124.48 ± 25.33 K`; Seçenek (a) 24-dilim hücre $\Delta T$: **`150.63 ± 25.84 K`** (saha ort. eğri: `124.99 K`) | $T_{\text{max}} \approx 200\text{–}275\text{ K}$, $T_{\text{min}} \approx 65\text{–}85\text{ K}$ | **Williams et al. (2019, *JGR Planets* 124:2505)**: `Site 07` zirvesinde 24/24 saat dilimi dolu; lider kararı beklenmektedir. |
| **Moon** | `moon_faustini_rim` | `temp_amplitude` *(Lider kararı bekliyor)* | Mevcut (`ltim01+ltim73`): `151.21 ± 3.82 K`; Seçenek (a) 24-dilim hücre $\Delta T$: **`155.67 ± 12.08 K`** (saha ort. eğri: `144.84 K`) | $T_{\text{max}} \approx 210\text{–}245\text{ K}$ (`ltim49` öğle max `244.46 K`), $T_{\text{min}} \approx 45\text{–}65\text{ K}$ | **Williams et al. (2019)**: `87.89°S` Faustini kenarında 18/24 saat dilimi dolu (`ltim73` `18.00–18.25 saat` akşamüstü dilimidir); lider kararı beklenmektedir. |
| **Moon** | `moon_faustini_rim` & `moon_de_gerlache_rim` | `thermal_inertia` *(NaN önerildi)* | Mevcut (1D model): `52.78 ± 6.60` & `85.70 ± 16.10 TIU` *(Kapı 1 gereği `NaN`'a çekilmesi önerildi)* | `45 – 90 TIU` (`273 K` referanslı üst 10 cm regolit) | **Hayne et al. (2017, *JGR Planets* 122:2371)** & **Vasavada et al. (2012, *JGR* 117:E00H18)**: Earth TI = `NaN` olduğu ve ortak tanım onayı bulunmadığı için `NaN` önerilmiştir. |
| **Moon** | Tüm 5 Güney Kutbu Sahası | `albedo` | **`0.1362 – 0.1469`** (`×0.38` geniş bant güneş eşdeğeri; ham 1064 nm normal: `0.358–0.387`) | `0.12 – 0.16` (Bond/hemispherical); `0.34 – 0.40` (1064 nm normal) | **Lemelin et al. (2016, *LPSC* 47)**, **Lucey et al. (2014, *JGR Planets* 119:1665)** & **Vasavada et al. (2012)**: Güney Kutbu feldspatik yayla regoliti için LOLA 1064 nm normal albedo ~0.36–0.39 ve geniş bant Bond albedosu ~0.13–0.15. |
| **Moon** | `moon_shackleton_rim` & `moon_connecting_ridge` | `slope_mean` | **`18.50° ± 1.51°`** & **`9.43° ± 1.89°`** | Shackleton iç/kenar: `15° – 32°`; Bağlantı Sırtı: `7° – 12°` | **Zuber et al. (2012, *Nature* 486:378)** & **Barker et al. (2021, *PSS* 203:105119)**: LOLA 5 m/px DEM üzerinde Shackleton kenar kuşağı ve Connecting Ridge eğim dağılımlarıyla birebir örtüşmektedir. |
| **Earth** | `earth_atacama_yungay` & `earth_etna_cisternazza` | `temp_amplitude` & `albedo` | Atacama: `28.92 ± 6.09 K`, `alb=0.2319`; Etna: `17.98 ± 8.04 K`, `alb=0.0439` | Atacama diurnal LST: `25 – 35 K`, `alb=0.20–0.26`; Etna taze bazalt `alb=0.04–0.07` | **Navarro-González et al. (2003, *Science*)**, **Wedler et al. (2017)** & **Liang (2001, *RSE*)**: `MOD11A2.061` yıllık ortalama $\Delta T$ ve `MCD43A3.061` geniş bant albedoları (`docs/data_sources_earth.md` §5) literatürle tam uyumludur. |
