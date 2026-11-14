# Ay Güney Kutbu Veri Kaynakları ve Referans Koordinat Tablosu (`docs/data_sources_moon.md`)

## 1. Referans Saha Koordinat Tablosu (`AGENTS.md` §5 Kimlik Kolonları)

| `site_id` | `name` | `body` | `role` | Enlem (`lat`) | Boylam (`lon`) | Kutupsal X (m) | Kutupsal Y (m) | Yarıçap (`radius_m`) | Durum / Kaynak |
|---|---|---|---|---|---|---|---|---|---|
| `moon_shackleton_rim` | Shackleton Crater Rim (Site 04 ROI) | `moon` | `reference` | **-89.7800°** | **-156.3201°** | **-2679 m** | **-6110 m** | `1000.0` | `TODO(verify)` — NASA PGDA `Site04_ROIs.shp` (Mazarico vd. 2011 / Barker vd. 2021) resmi Shackleton aydınlık krater sırtı merkezi |
| `moon_connecting_ridge` *(Aday 2)* | Shackleton–de Gerlache Connecting Ridge (Site 01) | `moon` | `reference` | **-89.5400°** | **-137.0000°** | **-9512 m** | **-10200 m** | `1000.0` | `TODO(verify)` — Barker vd. (2021) `Site01` Artemis aday sırtı |

---

## 2. Birincil Veri Kaynakları Tablosu (Kullanılacak Ana Ürünler)

| Veri Türü | Sözleşme Kolonu | Tam Ürün Adı (`X_src`) | Versiyon | Çözünürlük (`X_res_m`) | Kapsadığı Enlem / Boylam | Projeksiyon | Format & Boyut | Doğrudan İndirme Linki | Doğrulama Durumu |
|---|---|---|---|---|---|---|---|---|---|
| **1. Yükseklik / Eğim (DEM)** | `slope_mean`, `slope_p90`, `roughness`, `relief` | `LRO_LOLA_PGDA_Site04_5mpp_v2021` (`Site04_final_adj_5mpp_surf.tif`) | `v2021` (Barker vd., 2021) | **5.0 m** | **89.4°S – 90.0°S**, **0° – 360°E** (~20×20 km Shackleton kutusu) | Güney Kutbu Stereografik (`MOON_ME` DE421, metre) | `.tif` (GeoTIFF, **39 MB**) | [Site04_final_adj_5mpp_surf.tif](https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/Site04/Site04_final_adj_5mpp_surf.tif) | **HTTP 200 Doğrulandı** |
| **1b. Eğim Belirsizliği (`_sd`)** | `slope_mean_sd`, `slope_p90_sd` | `LRO_LOLA_PGDA_Site04_5mpp_v2021` (`Site04_final_adj_5mpp_slperr.tif`) | `v2021` (Barker vd., 2021) | **5.0 m** | **89.4°S – 90.0°S**, **0° – 360°E** (~20×20 km Shackleton kutusu) | Güney Kutbu Stereografik (`MOON_ME` DE421, metre) | `.tif` (GeoTIFF, **39 MB**) | [Site04_final_adj_5mpp_slperr.tif](https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/Site04/Site04_final_adj_5mpp_slperr.tif) | **HTTP 200 Doğrulandı** |
| **2. Yüzey Sıcaklığı** | `temp_amplitude` | `LRO-L-DLRE-5-PCP-V1.0` (`pcp_avg_tbol_pols_sum_ltim01..48_240`) | `v1.0` (Williams vd., 2022) | **240.0 m** | **80.0°S – 90.0°S**, **-180° – +180°E** | Güney Kutbu Stereografik (`R = 1737.4 km`) | `.tab` + `.xml` (ASCII Tablo) | [Diviner PCP Diurnal PolS](https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_pcp/diurnal/ltim/pols/) | **PDS4 `.xml` Doğrulandı** (`TODO(verify)`: yaz `sum` vs yıllık) |
| **3. Yüzey Parlaklığı (Albedo)** | `albedo` | `LRO-L-LOLA-4-GDR-V1.0:LDAM_50S_1000M_V1.0` (`LDAM_50S_1000M_FLOAT.IMG`) | `V1.0` (Lemelin vd., 2016) | **1000.0 m** | **50.0°S – 90.0°S**, **0° – 360°E** | Güney Kutbu Stereografik (`R = 1737.4 km`) | `.IMG` + `.LBL` (32-bit Float, **25.6 MB**) | [LDAM_50S_1000M_FLOAT.IMG](https://imbrium.mit.edu/DATA/LOLA_GDR/POLAR/FLOAT_IMG/LDAM_50S_1000M_FLOAT.IMG) | **PDS3 `.LBL` Doğrulandı** (`TODO(verify)`: 1064 nm lazer albedosu) |

---

## 3. Alternatif / Yedek Ürünler Tablosu (Karşılaştırma İçin İncelenenler)

| Veri Türü | Tam Ürün Adı | Versiyon | Çözünürlük (`X_res_m`) | Kapsadığı Enlem / Boylam | Format & Boyut | İndirme Linki | Neden Yedek / Durumu (`TODO(verify)`) |
|---|---|---|---|---|---|---|---|
| **Yükseklik (DEM)** | `LRO-L-LOLA-4-GDR-V1.0:LDEM_875S_20M` | `V2.0` (2017) | **20.0 m** | **87.5°S – 90.0°S**, **0° – 360°E** | `.IMG` + `.LBL` (110 MB) | [LDEM_875S_20M.IMG](https://imbrium.mit.edu/DATA/LOLA_GDR/POLAR/IMG/LDEM_875S_20M.IMG) | **Doğrulandı.** Geniş kutup mozaiği; `Site04` 5 m GeoTIFF daha yüksek çözünürlüklü ve hazır hata haritalı olduğu için yedek. |
| **Yükseklik (DEM)** | `PGDA_LDEM_80S_20MPP_ADJ.TIF` | `v2023` (Barker vd., 2023) | **20.0 m** | **80.0°S – 90.0°S**, **0° – 360°E** | `.TIF` (COG, 2.6 GB) | [LDEM_80S_20MPP_ADJ.TIF](https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_20MPP_ADJ.TIF) | **Doğrulandı.** 80°S–90°S arası ek sahalar eklendiğinde HTTP Range ile pencere kesmek için ideal. |
| **Sıcaklık** | `LRO-L-DLRE-5-GDR-V1.0:DGDR_TBOL_AVG_POLS_*_240` | `V5.0` (2016) | **240.0 m** | **75.0°S – 90.0°S**, **0° – 360°E** | `.img` + `.lbl` (29 MB) | [Diviner GDR L3 PolS](https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_gdr_l3/2015/polar/img/) | **Doğrulandı.** Tekil 28 günlük harita döngüleridir; PCP 10 yıllık birikimli olduğu için PCP birincil seçildi. |
| **Sıcaklık** | `LRO-L-DLRE-5-PRP-V2.0:DLRE_PRP_SOUTH.TAB` | `V2.0` (2018) | **~500.0 m** | **80.0°S – 90.0°S**, **0° – 360°E** | `.tab` + `.xml` | [dlre_prp_south.tab](https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_prp/dlre_prp_south.tab) | **Doğrulandı.** Sadece `temp_avg` ve `temp_max` içerir (`temp_min` yok); `temp_amplitude` için tek başına yetmez. |
| **Albedo** | `LRO-L-DLRE-5-GDR-V1.0:DGDR_VB1_AVG_POLS_*_240` | `V5.0` (2016) | **240.0 m** | **75.0°S – 90.0°S**, **0° – 360°E** | `.img` + `.lbl` (29 MB) | [Diviner GDR L2 PolS](https://pds-geosciences.wustl.edu/lro/lro-l-dlre-4-rdr-v1/lrodlr_1001/data/gdr_l2/2015/polar/img/) | **Doğrulandı.** 0.35–2.8 µm solar kanal; ancak karanlık krater içlerinde (PSR) ölçüm yapamaz (`TODO(verify)`). |
| **Albedo** | `Lunar_Clementine_UVVIS_750nm_Global_Mosaic_118m_v2.1` | `v2.1` (2022) | **118.0 m** | **90.0°S – 90.0°N**, **-180° – +180°E** | `.tif` (4.25 GB) | [Clementine 750nm v2.1](https://planetarymaps.usgs.gov/mosaic/Lunar_Clementine_UVVIS_750nm_Global_Mosaic_118m_v2.1.tif) | **Doğrulandı.** `TODO(verify)`: 89.9°S Shackleton'da güneş açısı nedeniyle derin gölge boşlukları (NoData) içerir. |
| **Albedo** | `LRO-L-LROC-5-RDR-V1.0:WAC_HAPKE_7BAND` | `V1.0` (2014) | **100.0 m** | **70.0°S – 70.0°N**, **-180° – +180°E** | `.IMG` / `.tif` | [LROC RDR Arşivi](https://pds.lroc.asu.edu/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/) | **Uygun Değil:** 70° Güney enleminde biter; 89.78°S Shackleton kraterini kapsamaz. |
