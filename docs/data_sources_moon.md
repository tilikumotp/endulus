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

| `site_id` | `slope_mean ± sd` (°) | `slope_p90 ± sd` (°) | `roughness ± sd` (m) | `relief ± sd` (m) | `temp_amplitude ± sd` (K) | `thermal_inertia` | `albedo ± sd` | DEM Kaynağı (`_src`) |
|---|---|---|---|---|---|---|---|---|
| **`moon_shackleton_rim`** | `18.5045 ± 1.5135` | `30.7879 ± 1.5135` | `90.4258 ± 0.3856` | `501.3733 ± 0.5769` | `113.8029 ± 3.2387` | `NaN` (`res=240m`) | `0.1469 ± 0.0036` | `LRO_LOLA_PGDA_Site04_5mpp_v2021` |
| **`moon_connecting_ridge`** | `9.4331 ± 1.8912` | `16.2303 ± 1.8913` | `42.4654 ± 0.3635` | `184.4755 ± 0.5363` | `131.9347 ± 3.1129` | `NaN` (`res=240m`) | `0.1455 ± 0.0015` | `LRO_LOLA_PGDA_Site01_5mpp_v2021` |
| **`moon_de_gerlache_rim`** | `10.8324 ± 1.7236` | `18.8078 ± 1.7239` | `44.9633 ± 0.3713` | `250.4174 ± 0.6257` | `117.3454 ± 6.8848` | `NaN` (`res=240m`) | `0.1366 ± 0.0009` | `LRO_LOLA_PGDA_Site11_5mpp_v2021` |
| **`moon_shackleton_peak`** | `8.1100 ± 1.7702` | `15.2735 ± 1.7705` | `32.3266 ± 0.3294` | `213.5736 ± 0.4833` | `124.4798 ± 25.3286` | `NaN` (`res=240m`) | `0.1417 ± 0.0020` | `LRO_LOLA_PGDA_Site07_5mpp_v2021` |
| **`moon_faustini_rim`** | `5.2013 ± 1.9768` | `8.6753 ± 1.9768` | `12.2904 ± 0.4508` | `145.2425 ± 0.7463` | `151.2074 ± 3.8219` | `NaN` (`res=240m`) | `0.1362 ± 0.0004` | `LRO_LOLA_PGDA_LM7_5mpp_v2021` |

---

## 3. Birincil Veri Kaynakları Tablosu (Doğrulanan ve İndirilen NASA Ürünleri)

| Veri Türü | Sözleşme Kolonu | Tam Ürün Adı (`X_src`) | Versiyon | Çözünürlük (`X_res_m`) | Kapsadığı Bölge | Projeksiyon | Format & Erişim | Doğrudan İndirme Linki | Doğrulama Durumu |
|---|---|---|---|---|---|---|---|---|---|
| **1. Yükseklik / Eğim (DEM)** | `slope_mean`, `slope_p90`, `roughness`, `relief` | `LRO_LOLA_PGDA_<Site>_5mpp_v2021` (`<Site>_final_adj_5mpp_surf.tif`) | `v2021` (Barker vd., 2021) | **`5.0 m`** | `Site04`, `Site01`, `Site11`, `Site07` (`16×16 km`), `LM7` (`20×20 km`) | Güney Kutbu Stereografik (`MOON_ME` DE421, metre) | `.tif` (GeoTIFF, HTTP Range + `data/raw/moon/` cache) | [NASA GSFC PGDA Product 78](https://pgda.gsfc.nasa.gov/products/78) | **DOĞRULANDI** (`data/raw/moon/` altında mevcut) |
| **1b. Eğim Belirsizliği (`_sd`)** | `slope_mean_sd`, `slope_p90_sd` | `LRO_LOLA_PGDA_<Site>_5mpp_v2021` (`<Site>_final_adj_5mpp_slperr.tif`) | `v2021` (Barker vd., 2021) | **`5.0 m`** | `Site04`, `Site01`, `Site11`, `Site07`, `LM7` | Güney Kutbu Stereografik (`MOON_ME` DE421, metre) | `.tif` (GeoTIFF, HTTP Range + 200 bootstrap) | [NASA GSFC PGDA Product 78](https://pgda.gsfc.nasa.gov/products/78) | **DOĞRULANDI** (`data/raw/moon/` altında mevcut) |
| **1c. Düşey Belirsizlik (`_sd`)** | `roughness_sd`, `relief_sd` | `LRO_LOLA_PGDA_<Site>_5mpp_v2021` (`<Site>_final_adj_5mpp_toterr.tif`) | `v2021` (Barker vd., 2021) | **`5.0 m`** | `Site04`, `Site01`, `Site11`, `Site07`, `LM7` | Güney Kutbu Stereografik (`MOON_ME` DE421, metre) | `.tif` (GeoTIFF, HTTP Range + 200 bootstrap) | [NASA GSFC PGDA Product 78](https://pgda.gsfc.nasa.gov/products/78) | **DOĞRULANDI** (`data/raw/moon/` altında mevcut) |
| **2. Yüzey Sıcaklığı** | `temp_amplitude` | `LRO-L-DLRE-5-PCP-V1.0:pcp_avg_tbol_pols_240m_v2022` | `v1.0` (Williams vd., 2019/2022) | **`240.0 m`** | **80.0°S – 90.0°S**, **-180° – +180°E** | Güney Kutbu Stereografik (`R = 1737.4 km`) | `.tab` + `.lbl` (`ltim01` yerel + `ltim73` HTTP Range) | [pcp_avg_tbol_pols_sum_ltim01_240.tab](https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_pcp/diurnal/ltim/pols/pcp_avg_tbol_pols_sum_ltim01_240.tab) | **DOĞRULANDI** (`data/raw/moon/` altında mevcut) |
| **3. Yüzey Parlaklığı (Albedo)** | `albedo` | `LRO-L-LOLA-4-GDR-V1.0:LDAM_50S_1000M_V1.0_broadband_eq` (`LDAM_50S_1000M_FLOAT.IMG`) | `V1.0` (Lemelin vd., 2016; Vasavada vd., 2012) | **`1000.0 m`** | **50.0°S – 90.0°S**, **0° – 360°E** | Güney Kutbu Stereografik (`R = 1737.4 km`) | `.IMG` + `.LBL` (32-bit Float, **25.6 MB**) | [LDAM_50S_1000M_FLOAT.IMG](https://imbrium.mit.edu/DATA/LOLA_GDR/POLAR/FLOAT_IMG/LDAM_50S_1000M_FLOAT.IMG) | **DOĞRULANDI** (`data/raw/moon/` altında mevcut) |
| **4. Termal Eylemsizlik** | `thermal_inertia` | Doğrudan kalibre kutup TI ürünü yok (`""`) | — | **`240.0 m`** (Diviner nominal çözünürlüğü) | — | — | `NaN` (`thermal_inertia_src = ""`) | — | **Sözleşme Kuralı:** `NaN` + boş `_src` + pozitif `_res_m = 240.0` |

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
4. **Diviner `temp_amplitude` (Diurnal Genlik, Kelvin):**
   - LRO Diviner Polar Cumulative Products (`LRO-L-DLRE-5-PCP-V1.0`, Williams vd., 2019/2022) 240 m çözünürlüklü bolometrik yüzey sıcaklığı (`TBOL`) tablolarından saha çevresindeki aydınlık ve gölge/gece fazlarının maksimum-minimum farkı (`T_max - T_min`, Kelvin) çıkarılmıştır. `90°E` boylamındaki `moon_faustini_rim` için `ltim01` (gece/alacakaranlık fazı, `T_min = 63.79 K`) ve `ltim73` (yerel öğle fazı, `T_max = 214.99 K`) birleştirilerek tam diurnal genlik (`151.21 K`) elde edilmiştir.
5. **`thermal_inertia` için `NaN` Gerekçesi:**
   - Ay Güney Kutbu (`87.8°S – 89.8°S`) aşırı düşük güneş geliş açıları ve kalıcı gölge/aydınlık sırt geçişleri nedeniyle standart ekvatoral gece soğuma eğrisi (Vasavada vd., 2012; Hayne vd., 2017 `H`-parametresi yalnızca `±70°` enlemleri arasında tanımlıdır) kutupta doğrudan `J m^-2 K^-1 s^-1/2` birimine dönüştürülememektedir. Sözleşme gereği uydurma değer yazılmamış; `thermal_inertia = NaN`, `thermal_inertia_sd = NaN`, `thermal_inertia_src = ""` ve `thermal_inertia_res_m = 240.0` bırakılmıştır.

---

## 5. Geniş Bant Albedo Aktarım Hassasiyeti Analizi (Broadband Albedo Sensitivity Analysis)

LRO LOLA `LDAM_50S_1000M_FLOAT.IMG` aktif lazer reflektometresi sıfır faz açısında ($\alpha = 0^\circ$, karşıtlık parlaması / *opposition surge* dahil) monokromatik 1064 nm normal albedo ($\sim 0.358 - 0.387$) ölçer. Dünya'daki pasif güneş reflektansı tabanlı MODIS `MCD43A3.061` (`Albedo_BSA_shortwave`) ile aynı fiziksel birime getirmek için kullanılan $c = 0.38$ dönüşüm katsayısının (*Vasavada et al., 2012; Hayne et al., 2017; Lucey et al., 2014*) faz integrali ve spektral eğim belirsizliği aralığındaki ($c \in [0.30, 0.34, 0.38, 0.42, 0.46]$) etkisi `src/moon_mars/albedo_sensitivity.py` ile tüm 5 referans sahası ve 28 Dünya sahası üzerinde test edilmiştir:

| Referans Saha (`ref_site_id`) | Çarpan (`c`) | Ölçeklenmiş Ay Albedosu | Ortalama `surface` Skor Farkı ($\|\Delta S_{\text{surf}}\|$) | Ortalama Genel Skor Farkı ($\|\Delta S_{\text{overall}}\|$) | Genel Sıralama Spearman $\rho$ | Top-1 Dünya Sahası (Tümü) | Top-3 Aday Sahalar (`role == "candidate"`) |
|---|---|---|---|---|---|---|---|
| **`moon_shackleton_rim`** | `0.30` | `0.1160` | `0.2060` | `0.0687` | `0.6842` | `earth_deccan_mahabaleshwar` | `earth_deccan_mahabaleshwar, earth_tendurek_shield, earth_pinacate_el_elegante` |
| **`moon_shackleton_rim`** | `0.34` | `0.1314` | `0.1231` | `0.0410` | `0.8818` | `earth_lunar_crater_nevada` | `earth_deccan_mahabaleshwar, earth_karacadag_summit, earth_salda_terrace` |
| **`moon_shackleton_rim`** | **`0.38` (Baz)** | **`0.1469`** | **`0.0000`** | **`0.0000`** | **`1.0000`** | `earth_hasandagi_kecekalecik` | `earth_hasandagi_kecekalecik, earth_erciyes_kojugedigi, earth_kula_divlit` |
| **`moon_shackleton_rim`** | `0.42` | `0.1624` | `0.1214` | `0.0405` | `0.8544` | `earth_hasandagi_kecekalecik` | `earth_hasandagi_kecekalecik, earth_erciyes_kojugedigi, earth_harrat_ash_shaam` |
| **`moon_shackleton_rim`** | `0.46` | `0.1778` | `0.2084` | `0.0695` | `0.6656` | `earth_hasandagi_kecekalecik` | `earth_hasandagi_kecekalecik, earth_erciyes_kojugedigi, earth_kilbourne_hole_nm` |
| **`moon_connecting_ridge`** | `0.34` | `0.1302` | `0.1234` | `0.0411` | `0.9190` | `earth_karacadag_summit` | `earth_karacadag_summit, earth_salda_terrace, earth_deccan_mahabaleshwar` |
| **`moon_connecting_ridge`** | **`0.38` (Baz)** | **`0.1455`** | **`0.0000`** | **`0.0000`** | **`1.0000`** | `earth_mcmurdo_wright_valley` | `earth_kula_divlit, earth_karacadag_summit, earth_puna_campo_piedra_pomez` |
| **`moon_connecting_ridge`** | `0.42` | `0.1608` | `0.1235` | `0.0412` | `0.8560` | `earth_puna_campo_piedra_pomez` | `earth_puna_campo_piedra_pomez, earth_kula_divlit, earth_erciyes_kojugedigi` |
| **`moon_de_gerlache_rim`** | `0.34` | `0.1222` | `0.1039` | `0.0346` | `0.9382` | `earth_lunar_crater_nevada` | `earth_deccan_mahabaleshwar, earth_karacadag_summit, earth_tendurek_shield` |
| **`moon_de_gerlache_rim`** | **`0.38` (Baz)** | **`0.1366`** | **`0.0000`** | **`0.0000`** | **`1.0000`** | `earth_mcmurdo_wright_valley` | `earth_deccan_mahabaleshwar, earth_karacadag_summit, earth_erciyes_kojugedigi` |
| **`moon_de_gerlache_rim`** | `0.42` | `0.1510` | `0.1181` | `0.0394` | `0.8987` | `earth_mcmurdo_wright_valley` | `earth_erciyes_kojugedigi, earth_kula_divlit, earth_deccan_mahabaleshwar` |
| **`moon_shackleton_peak`** | `0.34` | `0.1268` | `0.1218` | `0.0406` | `0.9398` | `earth_karacadag_summit` | `earth_karacadag_summit, earth_salda_terrace, earth_tendurek_shield` |
| **`moon_shackleton_peak`** | **`0.38` (Baz)** | **`0.1417`** | **`0.0000`** | **`0.0000`** | **`1.0000`** | `earth_mcmurdo_wright_valley` | `earth_karacadag_summit, earth_kula_divlit, earth_puna_campo_piedra_pomez` |
| **`moon_shackleton_peak`** | `0.42` | `0.1566` | `0.1251` | `0.0417` | `0.8883` | `earth_kula_divlit` | `earth_kula_divlit, earth_puna_campo_piedra_pomez, earth_karacadag_summit` |
| **`moon_faustini_rim`** | `0.34` | `0.1218` | `0.1023` | `0.0341` | `0.9436` | `earth_salda_terrace` | `earth_salda_terrace, earth_tendurek_shield, earth_karacadag_summit` |
| **`moon_faustini_rim`** | **`0.38` (Baz)** | **`0.1362`** | **`0.0000`** | **`0.0000`** | **`1.0000`** | `earth_salda_terrace` | `earth_salda_terrace, earth_karacadag_summit, earth_tendurek_shield` |
| **`moon_faustini_rim`** | `0.42` | `0.1505` | `0.1172` | `0.0391` | `0.8916` | `earth_kula_divlit` | `earth_kula_divlit, earth_salda_terrace, earth_acigol_guneydag` |

### Fiziksel Yorum ve Kararlılık Sonucu
1. **Yakın Belirsizlik Bandında ($c \in [0.34, 0.42]$, $\pm 10.5\%$):** Tüm 5 Ay Güney Kutbu referans sahasında genel sıralama Spearman korelasyonu **$\rho = 0.854 - 0.944$** aralığında kalmakta ve ortalama genel skor değişimi yalnızca **$\pm 0.034 - 0.042$** düzeyindedir.
2. **Aday Havuzu Kararlılığı:** `c = 0.34`'te daha koyu bazaltik kalkanlar (`earth_karacadag_summit`, `earth_deccan_mahabaleshwar`, `earth_kula_divlit`), `c = 0.42`'de ise biraz daha açık tonlu volkanik/piroklastik yüzeyler (`earth_hasandagi_kecekalecik`, `earth_erciyes_kojugedigi`, `earth_puna_campo_piedra_pomez`) üst sıraları paylaşmakta; Anadolu aday sahaları (`Karacadağ`, `Kula Divlit`, `Hasandağ`, `Erciyes`, `Salda`) tüm çarpan aralığında Top-3 portföy çekirdeğini korumaktadır.
