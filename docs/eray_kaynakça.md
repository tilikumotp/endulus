# ENDÜLÜS — Eray Eksiksiz Proje Veri Kaynakları, Doğrulama Yerleri ve Literatür Kaynakçası (`eray_kaynakça`)

**Proje:** NASA Space Apps 2026 — *Permanent Moon Base Locations and Mars* (ENDÜLÜS: Ay Güney Kutbu ↔ Dünya Çok Eksenli Analog Puanlayıcı)  
**Hazırlanan Kapsam:** Resmi **v1** veri ve doğrulama envanteri (**40 Dünya sahası** [10 `validation` + 30 `candidate`: 14 Türkiye, 16 küresel] + **5 Ay Güney Kutbu referans sahası** [`reference`]).  
**Dal / Sürüm Notu:** Yerel çalışma dalı `p3-earth` (`197c6e8`) + `origin/main` (`40ada8a` — Lider Kararı #30 ve P2 `b321ff5` merge'ü dahil). *Not: Lider Kararı (#33, `2026-11-14T20:27:04Z`) ile 14.000 hücrelik küresel tarama (`E9/S8/B9`) v1 kapsamından tamamen çıkarılmıştır; bu belgede yalnızca kalıcı v1 kaynakları ve doğrulamaları yer alır.*

---

## İçindekiler
1. [Veri Çekilen Platformlar, API Uç Noktaları ve Projeksiyon Standartları](#1-veri-çekilen-platformlar-api-uç-noktaları-ve-projeksiyon-standartları)
2. [Dünya (`Earth`, P3 / `p3-earth`) Uydu, DEM ve Optik Veri Kaynakları](#2-dünya-earth-p3--p3-earth-uydu-dem-ve-optik-veri-kaynakları)
3. [40 Dünya Sahasının Tam Veri Kanıt ve Sahne Matrisi](#3-40-dünya-sahasının-tam-veri-kanıt-ve-sahne-matrisi)
4. [Ay Güney Kutbu (`Moon`, P2 / `p2-moonmars`) Uydu ve Referans Veri Kaynakları](#4-ay-güney-kutbu-moon-p2--p2-moonmars-uydu-ve-referans-veri-kaynakları)
5. [Uygulama İçi Canlı Görsel Servisler ve Harita Altlıkları (`app/`)](#5-uygulama-içi-canlı-görsel-servisler-ve-harita-altlıkları-app)
6. [Tüm Doğrulama Yerleri, Çapraz Denetimler ve Kalite Kapıları](#6-tüm-doğrulama-yerleri-çapraz-denetimler-ve-kalite-kapıları)
7. [Eksiksiz Literatür, Teknik Standart ve Jeoloji Haritası Kaynakçası](#7-eksiksiz-literatür-teknik-standart-ve-jeoloji-haritası-kaynakçası)
8. [Yazılım Yığını ve Sabitlenmiş Bağımlılıklar (`requirements.txt`)](#8-yazılım-yığını-ve-sabitlenmiş-bağımlılıklar-requirementstxt)

---

## 1. Veri Çekilen Platformlar, API Uç Noktaları ve Projeksiyon Standartları

Projedeki tüm sayısal ve görsel veriler doğrudan aşağıdaki resmî arşivlerden ve API'lerden çekilmiştir (sentetik / `MOCK` veri yoktur):

### 1.1 Programatik Veri Çekme Uç Noktaları (Kod İçi Doğrulanmış URL'ler)

| Sağlayıcı / Arşiv | Amaç | Doğrudan Uç Nokta / Kök URL (`endpoint`) | Auth / Erişim Yöntemi | Kullanan Modül |
|---|---|---|---|---|
| **AWS Open Data (`copernicus-dem-30m`)** | Copernicus DEM GLO-30 COG (1°×1° karo indirme / HTTP Range okuma) | `https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_{N/S}{lat}_00_{E/W}{lon}_00_DEM/Copernicus_DSM_COG_10_{N/S}{lat}_00_{E/W}{lon}_00_DEM.tif` | Public S3 (Auth gerekmez; HTTP Range + BigTIFF için `/vsicurl/` fallback) | `src/earth/dem_pipeline.py` |
| **Microsoft Planetary Computer STAC API** | STAC katalog sorgusu (`nasadem`, `modis-11A2-061`, `modis-43A4-061`, `sentinel-2-l2a`) | `https://planetarycomputer.microsoft.com/api/stac/v1/search` | Anonim STAC POST | `dem_pipeline.py`, `modis_pipeline.py`, `build_atlas.py`, `build_3d_grids.py` |
| **Microsoft Planetary Computer Collection Probe** | `modis-43A3-061` varlık kontrolü (`HTTP 404` doğrulandı — yalnızca `MCD43A4` var) | `https://planetarycomputer.microsoft.com/api/stac/v1/collections/modis-43A3-061` | Anonim GET | `src/earth/modis_pipeline.py` |
| **Planetary Computer SAS Token (NASADEM)** | `nasadem` COG varlıkları için imzalı SAS token (`N39 E044` Ağrı fallback) | `https://planetarycomputer.microsoft.com/api/sas/v1/token/nasadem` | Anonim GET -> `?{token}` | `src/earth/dem_pipeline.py` |
| **Planetary Computer SAS Token (MODIS COG)** | `modis-11A2-061` ve `modis-43A4-061` COG imzalı token | `https://planetarycomputer.microsoft.com/api/sas/v1/token/modiseuwest/modis-061-cogs` | Anonim GET -> `?{token}` | `src/earth/modis_pipeline.py` |
| **Planetary Computer SAS Token (Sentinel-2 L2A)** | `sentinel-2-l2a` `visual` (10m RGB) ve `SCL` (20m) COG imzalı token | `https://planetarycomputer.microsoft.com/api/sas/v1/token/sentinel-2-l2a` | Anonim GET -> `?{token}` (`sentinel2l2a01.blob.core.windows.net`) | `src/earth/build_atlas.py` |
| **NASA Earthdata CMR API** | `MCD43A3.061` granül araması (`short_name="MCD43A3"`, `version="061"`) | `https://cmr.earthdata.nasa.gov/search/granules.json` | Anonim GET | `src/earth/modis_pipeline.py` |
| **NASA LP DAAC Earthdata Cloud** | `MCD43A3.061` HDF-EOS2 granüllerinden HTTP 206 byte-range okuma (`Albedo_BSA_shortwave`) | `https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MCD43A3.061/...` (ve `s3://lp-prod-protected/MOD11A2.061`) | `.env` içi `EARTHDATA_TOKEN` (`Authorization: Bearer <token>`) | `src/earth/modis_pipeline.py` |
| **NASA GSFC PGDA (Product 78)** | 5 m/px LRO LOLA Güney Kutbu DEM (`_surf.tif`, `_slperr.tif`, `_toterr.tif`) ve `SiteXX_ROIs.shp` | `https://pgda.gsfc.nasa.gov/products/78` ve `https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/{pgda_site}/{pgda_site}_final_adj_5mpp_{suffix}.tif` | Public HTTP Range | `src/moon_mars/shackleton_slope.py` |
| **PDS Geosciences Node (WUSTL)** | LRO Diviner Polar Cumulative Products (`240 m` bolometrik sıcaklık `.tab` ve `.lbl` etiketleri, `ltim01..ltim96`) | `https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_pcp/diurnal/ltim/pols/pcp_avg_tbol_pols_sum_ltim01_240.tab`, `https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_pcp/diurnal/ltim/pols/pcp_avg_tbol_pols_sum_ltim01_240.lbl`, `https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_pcp/diurnal/ltim/pols/pcp_avg_tbol_pols_sum_ltim96_240.lbl` (ve ara `ltim02..ltim95` `.lbl/.tab`) | Public HTTP / HTTP Range | `src/moon_mars/shackleton_slope.py` |
| **MIT Imbrium LOLA Archive** | 1064 nm LOLA Gridded Polar Albedo Data Record (`LDAM_50S_1000M_FLOAT.IMG` & `.LBL`) | `https://imbrium.mit.edu/DATA/LOLA_GDR/POLAR/FLOAT_IMG/LDAM_50S_1000M_FLOAT.IMG` (ve `.LBL`) | Public HTTPS | `src/moon_mars/shackleton_slope.py` |

**HTTP Dayanıklılık Politikası (`src/earth/modis_pipeline.py` `_make_retrying_session`):** `total=5`, `connect=5`, `read=5`, `backoff_factor=0.8`, `status_forcelist=[429, 500, 502, 503, 504]`, `pool_connections=16`, `pool_maxsize=16`.

### 1.2 Koordinat ve Projeksiyon Standartları (CRS)

- **Depolama / Ekran Koordinatları (`lat`, `lon`):** Earth için `EPSG:4326` (WGS84), Moon için gezegen merkezli küresel (`+proj=longlat +R=1737400 +no_defs`, `MOON_ME` DE421).
- **Dünya Metrik Projeksiyon Kuralı (`get_metric_crs`, `src/earth/dem_pipeline.py`):**
  - `lat >= 84.0°` $\rightarrow$ `EPSG:3413` (WGS 84 / NSIDC Sea Ice Polar Stereographic North)
  - `lat <= -80.0°` $\rightarrow$ `EPSG:3031` (WGS 84 / Antarctic Polar Stereographic)
  - Arası tüm enlemler $\rightarrow$ Yerel UTM zonu: Kuzey `EPSG:32601..32660`, Güney `EPSG:32701..32760` (`zone = floor((lon + 180) / 6) % 60 + 1`).
- **MODIS Sinusoidal Grid Projeksiyonu (`MODIS_SINU_PROJ4`):** `+proj=sinu +R=6371007.181 +nadgrids=@null +wktext` (Karo kenarı `MODIS_SINU_TILE_M = 1,111,950.5196666666 m`; `MOD11A2` `1200×1200` piksel = `926.625 m`; `MCD43A3/A4` `2400×2400` piksel = `463.313 m`).
- **Ay Güney Kutbu Metrik Projeksiyonu (`MOON_STEREO_PROJ4`):** `+proj=stere +lat_0=-90 +lon_0=0 +k=1 +x_0=0 +y_0=0 +R=1737400 +units=m +no_defs` (USGS WMS önizlemesinde `EPSG:32761`).

---

## 2. Dünya (`Earth`, P3 / `p3-earth`) Uydu, DEM ve Optik Veri Kaynakları

Çıktı dosyası: `data/processed/features_earth.parquet` (`40` satır × tam `36` sözleşme sütunu; `29,376` byte; `0 MOCK`).

### 2.1 Topoğrafya (`slope_mean`, `slope_p90`, `roughness`, `relief`) ve E7 3B Gridler

| Kısa Kod (`*_src`) | Tam Ürün Adı & Versiyonu | Yerel Çözünürlük (`*_res_m`) | Düşey Datum & Hata Referansı | Kapsam / Kullanım |
|---|---|---|---|---|
| **`Copernicus_DEM_GLO-30`** | **Copernicus DEM — Global and European Digital Elevation Model (COP-DEM GLO-30 DGED; TanDEM-X 2021-04-22)** | `30.0 m` (`1 arc-second`) | **EGM2008** (`EPSG:3855` ortometrik). Bağıl düşey belirsizlik `sigma_z_rel = 1.0 m`: **Airbus / ESA Copernicus DEM Product Handbook (2022, GEO.2018-1988-2, §4.2: LE90 < 2.0 m)**. | **39 / 40 Dünya sahası** (Haughton `75.37°N` dahil; `N39 E044` eksik). |
| **`NASADEM_HGT_v001`** | **NASADEM Merged DEM Global 1 arc second V001** (NASA CMR ID: `C2763264762-LPCLOUD`, DOI: `https://doi.org/10.5067/MEaSUREs/NASADEM/NASADEM_HGT.001`) | `30.0 m` (`1 arc-second`) | **EGM96** geoid ortometrik (`sigma_z_rel_m = null` E7 metasında). `60°N – 56°S`. | **1 / 40 saha (Otomatik Fallback):** Yalnızca `earth_agri_dogubayazit_flow` (`N39 E044` Copernicus karesi AWS/PC'de `HTTP 404` olduğu için). |

- **Hesaplama Tanımı (`radius_m = 1000.0 m`, `src/earth/dem_pipeline.py`):** Dairesel pencere içindeki metre projeksiyonlu `30 m` piksellerde `np.gradient(dem_m, dy, dx)` $\rightarrow$ `degrees(arctan(hypot(dz_dx, dz_dy)))`; `slope_mean` (ortalama), `slope_p90` (90. yüzdelik), `relief = max(z) - min(z)`, `roughness` ise `(dx, dy, 1)` OLS düzlem kalıntılarının örneklem std'si (`ddof=1`).
- **Belirsizlik (`*_sd`):** `n_boot = 200` (`seed = 42`) piksel bootstrap (1-sigma); `roughness_sd` ve `relief_sd` hesabında her bootstrap çekilişine `N(0, sigma_z_rel=1.0 m)` dikey gürültü eklenir (alt sınır `1e-4`).
- **Ağrı (`earth_agri_dogubayazit_flow`) Düşey Datum Notu (`docs/data_sources_earth.md §8`):** EGM96 vs EGM2008 arasında metre ölçeğinde sabit bölgesel ofset bulunabileceğinden mutlak kot (`elev_min_m`–`elev_max_m`) doğrudan kıyaslanmamalıdır; pencere içi türev/fark metrikleri (`slope_*`, `roughness`, `relief`) ofsetten pratikte etkilenmez.
- **E7 3B Arazi Gridleri (`src/earth/build_3d_grids.py`):**
  - Çıktılar: `data/processed/earth_3d_grids.npz` (`687,085` byte; `40 × (74, 74)` `float32`, `30.0 m` aralık, `2220 × 2220 m` pencere) ve `data/processed/earth_3d_meta.json` (`63,999` byte).
  - E5 Sentinel-2 görsel yamasıyla geometrik merkez hizalaması sağlanmıştır (`e5_uv_box = [0.283203125, ..., 0.716796875]`, `e5_px_crop_xyxy = [145, 145, 367, 367]`, `center_offset_from_site_m <= 7.5 m`). Sayısal sözleşme skorlarına girmez.

### 2.2 Yüzey Sıcaklığı Genliği (`temp_amplitude`)

| Kısa Kod (`*_src`) | Tam Ürün Adı & Versiyonu | Yerel Çözünürlük (`*_res_m`) | Zaman Penceresi & Parametreler |
|---|---|---|---|
| **`MOD11A2.061_annual_mean`** *(Birincil, 40/40 saha)* | **MODIS/Terra Land Surface Temperature/Emissivity 8-Day L3 Global 1km SIN Grid V061** (NASA CMR ID: `C2269056084-LPCLOUD`, PC: `modis-11A2-061`) | `1000.0 m` (Gerçek Sinusoidal piksel: `926.625 m`) | `2024-01-01/2024-12-31`, `max_composites = 24` eşit aralıklı kompozit, kesin `hXXvYY` karo filtresi, `3×3` piksel (`~3×3 km`), `7500 <= DN <= 65535`, ölçek `0.02 K`, `(QC_Day & 0b11) <= 1` ve `(QC_Night & 0b11) <= 1`, yalnızca `diff = T_day - T_night > 0`. |
| **`MOD11A1.061` / `MYD11A1.061`** *(Dokümante Alternatif)* | **MODIS/Terra (Aqua) Daily L3 Global 1km SIN Grid V061** (`C1748058432-LPCLOUD` / `C1748046084-LPCLOUD`, PC: `modis-11A1-061`) | `1000.0 m` (`926.625 m`) | Bulutsuz tekil gün analizleri için `docs/data_sources_earth.md §1`'de belgelenmiş alternatif. |

- **Belirsizlik (`temp_amplitude_sd`):** 2024 tam yılı boyunca seçilen tüm geçerli `3×3` piksel + granül çiftlerinin birleşik örneklem standart sapması (`ddof=1`). Mevsimsel kış–yaz değişimi nedeniyle `27/40` sahada `CV_temp > 0.30` gözlenir (`docs/data_sources_earth.md §5`).

### 2.3 Geniş Bant Albedo (`albedo`)

| Kısa Kod (`*_src`) | Tam Ürün Adı & Versiyonu | Yerel Çözünürlük (`*_res_m`) | Pencere, Kalite Filtresi ve Dönüşüm |
|---|---|---|---|
| **`MCD43A3.061`** *(Birincil, 40/40 saha)* | **MODIS/Terra+Aqua BRDF/Albedo Albedo Daily L3 Global - 500m V061** (NASA CMR ID: `C2278860820-LPCLOUD`, LP DAAC HDF-EOS2 Range) | `500.0 m` (Gerçek Sinusoidal piksel: `463.313 m`) | Bant: `Albedo_BSA_shortwave` (SDS ref `458`), `0 <= DN < 32767`, ölçek `0.001`. `5×5` piksel (`~2.3×2.3 km`), `max_granules = 4`. Kuzey & tropikler için `2024-07-01..08-31` (muson bulutluluğu nedeniyle `earth_deccan_mahabaleshwar`'da otomatik kuru kış penceresi `2024-01-01..02-28`); `lat < -45°` (`earth_mcmurdo_wright_valley`) için Güney yazı `2024-01-01..02-28`. |
| **`MCD43A4.061_Liang2001`** *(İkincil / Çapraz Doğrulama)* | **MODIS/Terra+Aqua BRDF/Albedo Nadir BRDF-Adjusted Reflectance Daily L3 Global - 500m V061** (PC: `modis-43A4-061`) | `500.0 m` (`463.313 m`) | Bant `1..7` (`DN * 0.0001`), `BRDF_Albedo_Band_Mandatory_Quality_Band1..7 <= 1`, kar maskesi `NDSI = (ρ4 - ρ6)/(ρ4 + ρ6) < 0.40` (*Hall et al., 2002*) ve **Liang (2001, Eq. 9)** kısa dalga dönüşümü: $\alpha_{\text{sw}} = 0.160\rho_1 + 0.291\rho_2 + 0.243\rho_3 + 0.116\rho_4 + 0.112\rho_5 + 0.081\rho_7 - 0.0015$. |

### 2.4 Termal Eylemsizlik (`thermal_inertia`) ve Niteliksel Sütunlar

- **`thermal_inertia`:** Ortak ölçekli küresel uydu ürünü bulunmadığından v1 sözleşmesi gereği `40/40` sahada **`NaN`**, `thermal_inertia_sd = NaN`, `thermal_inertia_src = ""`, `thermal_inertia_res_m = 1000.0`.
- **`lithology_class`:** Niteliksel (`basalt` ×27, `pyroclastic_tuff` ×6, `evaporite` ×4, `impact_breccia` ×2, `regolith_permafrost` ×1); sayısal skora girmez (`AGENTS.md §2`).

### 2.5 E5 Görsel Atlas ve Karışık Piksel Temsiliyet Denetimi (`mixed_pixel.py` & `build_atlas.py`)

- **Sentinel-2 L2A Görsel Atlas (E5):** Planetary Computer `sentinel-2-l2a`, **40/40 saha**, `512 × 512 px` @ `10.0 m/px` = `5120 × 5120 m` WebP (`quality=92`, toplam `metadata.json` = `25,362` byte; `SCL` `20 m` lokal bulut kontrolü `<= %2.0`, geçerli piksel `>= %98.0`). Dosyalar: `data/processed/earth_atlas/<site_id>.webp` ve `data/processed/earth_atlas/metadata.json`.
- **ESA WorldCover 10m 2021 v200 (`src/earth/mixed_pixel.py` & `docs/data_sources_earth.md §7`):** Şüpheli 6 saha ve Etna aday taraması için kullanılan karolar:
  - `ESA_WorldCover_10m_2021_v200_N36E027` (`earth_salda_terrace`)
  - `ESA_WorldCover_10m_2021_v200_N36E033` (`earth_tuz_golu_south`)
  - `ESA_WorldCover_10m_2021_v200_N78E012` (`earth_svalbard_bockfjorden`)
  - `ESA_WorldCover_10m_2021_v200_N36E042` (`earth_suphan_south_apron`)
  - `ESA_WorldCover_10m_2021_v200_N33W114` (`earth_meteor_crater_arizona`)
  - `ESA_WorldCover_10m_2021_v200_N36E012+N36E015` (Etna `15°E` boylam sınırı mozaik)

---

## 3. 40 Dünya Sahasının Tam Veri Kanıt ve Sahne Matrisi

Aşağıdaki tablo `data/processed/features_earth.parquet`, `data/raw/earth/*.json`, `data/processed/earth_3d_meta.json` ve `data/processed/earth_atlas/metadata.json` dosyalarından birebir derlenmiştir:

| # | `site_id` | Rol | Koordinat (`lat, lon`) | Litoloji | DEM (`_src`, E7 datum, CRS) | `MOD11A2.061` (hXXvYY, kompozit/px) | `MCD43A3.061` (pencere, px) | `MCD43A4.061` Çapraz Teyit | Sentinel-2 L2A `scene_id` (E5, tarih, lokal bulut) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `earth_etna_cisternazza` | `validation` | `37.7257, 15.0084` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32633`) | `h19v05`, n=22/24 (165 px) | `h19v05`, `2024-07-01`.. (`4` grn, 87 px) | `0.0490` (NDSI `-0.204`, kar `0/75`) | `S2B_MSIL2A_20240715T094549_R079_T33SVB_20240715T135442` (2024-07-15, `0.0%`) |
| 2 | `earth_atacama_yungay` | `validation` | `-24.1052, -70.0321` | `evaporite` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32719`) | `h11v11`, n=24/24 (216 px) | `h11v11`, `2024-07-01`.. (`4` grn, 100 px) | `0.2436` (NDSI `-0.338`, kar `0/100`) | `S2A_MSIL2A_20231214T143741_R096_T19KCP_20231219T212001` (2023-12-14, `0.0%`) |
| 3 | `earth_haughton_crater` | `validation` | `75.3700, -89.6800` | `impact_breccia` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32616`) | `h15v01`, n=23/24 (167 px) | `h15v01`, `2024-07-01`.. (`3` grn, 49 px) | `0.2632` (NDSI `+0.031`, kar `0/24`) | `S2A_MSIL2A_20240708T190921_R056_T16XDJ_20240709T021834` (2024-07-08, `0.0%`) |
| 4 | `earth_mauna_loa_hiseas` | `validation` | `19.6028, -155.4878` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32605`) | `h03v07`, n=24/24 (216 px) | `h03v07`, `2024-07-01`.. (`4` grn, 100 px) | — | `S2A_MSIL2A_20240814T205941_R014_T05QKB_20240815T011751` (2024-08-14, `0.0%`) |
| 5 | `earth_mcmurdo_wright_valley` | `validation` | `-77.5180, 161.8500` | `regolith_permafrost` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32758`) | `h21v16`, n=22/24 (110 px) | `h21v16`, `2024-01-01`.. (`4` grn, 77 px) | `0.2078` (NDSI `+0.434`, kar `19/41`) | `S2B_MSIL2A_20231211T204609_R128_T58CDV_20240903T020626` (2023-12-11, `0.52%`) |
| 6 | `earth_lanzarote_timanfaya` | `validation` | `29.0150, -13.7150` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32628`) | `h16v06`, n=24/24 (204 px) | `h16v06`, `2024-07-01`.. (`4` grn, 99 px) | — | `S2B_MSIL2A_20240715T113319_R080_T28RFT_20240715T170157` (2024-07-15, `0.0%`) |
| 7 | `earth_meteor_crater_arizona` | `validation` | `35.0272, -111.0225` | `impact_breccia` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32612`) | `h08v05`, n=24/24 (214 px) | `h08v05`, `2024-07-01`.. (`4` grn, 100 px) | — | `S2A_MSIL2A_20240707T175911_R041_T12SVD_20240708T004658` (2024-07-07, `0.0%`) |
| 8 | `earth_craters_of_the_moon` | `validation` | `43.4617, -113.5625` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32611`) | `h09v04`, n=24/24 (200 px) | `h09v04`, `2024-07-01`.. (`4` grn, 100 px) | — | `S2B_MSIL2A_20240830T182919_R027_T11TQJ_20240830T235532` (2024-08-30, `0.0%`) |
| 9 | `earth_svalbard_bockfjorden` | `validation` | `79.4280, 13.3850` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32633`) | `h18v01`, n=22/24 (123 px) | `h18v01`, `2024-07-01`.. (`4` grn, 99 px) | `0.1007` (NDSI `-0.113`, kar `11/94`) | `S2A_MSIL2A_20240717T125711_R038_T33XVJ_20240717T172120` (2024-07-17, `1.05%`) |
| 10 | `earth_lunar_crater_nevada` | `validation` | `38.3840, -116.0680` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32611`) | `h08v05`, n=24/24 (216 px) | `h08v05`, `2024-07-01`.. (`4` grn, 100 px) | — | `S2B_MSIL2A_20240731T182919_R027_T11SNC_20240731T220220` (2024-07-31, `0.0%`) |
| 11 | `earth_karacadag_summit` | `candidate` | `37.6700, 39.8300` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32637`) | `h21v05`, n=23/24 (196 px) | `h21v05`, `2024-07-01`.. (`4` grn, 100 px) | `0.1552` (NDSI `-0.406`, kar `0/99`) | `S2B_MSIL2A_20240824T080609_R078_T37SEB_20240824T111913` (2024-08-24, `0.0%`) |
| 12 | `earth_karacadag_ovabag` | `candidate` | `37.7850, 40.0250` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32637`) | `h21v05`, n=22/24 (198 px) | `h21v05`, `2024-07-01`.. (`4` grn, 100 px) | — | `S2B_MSIL2A_20240824T080609_R078_T37SEB_20240824T111913` (2024-08-24, `0.0%`) |
| 13 | `earth_kula_divlit` | `candidate` | `38.5660, 28.6360` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32635`) | `h20v05`, n=24/24 (216 px) | `h20v05`, `2024-07-01`.. (`4` grn, 100 px) | — | `S2B_MSIL2A_20240809T085559_R007_T35SPC_20240809T120033` (2024-08-09, `0.0%`) |
| 14 | `earth_tendurek_shield` | `candidate` | `39.3200, 43.9200` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32638`) | `h21v05`, n=24/24 (215 px) | `h21v05`, `2024-07-01`.. (`4` grn, 100 px) | — | `S2B_MSIL2A_20240821T075609_R035_T38SMJ_20240821T113401` (2024-08-21, `0.0%`) |
| 15 | `earth_erciyes_kojugedigi` | `candidate` | `38.5050, 35.5350` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32636`) | `h20v05`, n=24/24 (209 px) | `h20v05`, `2024-07-01`.. (`4` grn, 100 px) | — | `S2A_MSIL2A_20240815T082601_R021_T36SYH_20240815T130452` (2024-08-15, `0.0%`) |
| 16 | `earth_hasandagi_kecekalecik` | `candidate` | `38.1750, 34.1200` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32636`) | `h20v05`, n=23/24 (199 px) | `h20v05`, `2024-07-01`.. (`4` grn, 100 px) | — | `S2B_MSIL2A_20240721T082609_R021_T36SWH_20240721T122421` (2024-07-21, `0.0%`) |
| 17 | `earth_acigol_guneydag` | `candidate` | `38.5250, 34.5550` | `pyroclastic_tuff` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32636`) | `h20v05`, n=24/24 (193 px) | `h20v05`, `2024-07-01`.. (`4` grn, 100 px) | — | `S2A_MSIL2A_20240815T082601_R021_T36SXH_20240815T130452` (2024-08-15, `0.0%`) |
| 18 | `earth_cappadocia_kavakkoy` | `candidate` | `38.6500, 34.8600` | `pyroclastic_tuff` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32636`) | `h20v05`, n=22/24 (197 px) | `h20v05`, `2024-07-01`.. (`4` grn, 100 px) | — | `S2A_MSIL2A_20240815T082601_R021_T36SXH_20240815T130452` (2024-08-15, `0.0%`) |
| 19 | `earth_tuz_golu_south` | `candidate` | `38.5500, 33.6200` | `evaporite` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32636`) | `h20v05`, n=23/24 (186 px) | `h20v05`, `2024-07-01`.. (`1` grn, 6 px) | *(Dry run: 30/31 px NDSI>=0.40 yanlışı)* | `S2B_MSIL2A_20240823T083559_R064_T36SWH_20240823T130614` (2024-08-23, `0.29%`) |
| 20 | `earth_salda_terrace` | `candidate` | `37.5150, 29.6350` | `evaporite` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32636`) | `h20v05`, n=24/24 (214 px) | `h20v05`, `2024-07-01`.. (`4` grn, 100 px) | *(Dry run: `0.1578`, 0/100 kar)* | `S2B_MSIL2A_20240816T084559_R107_T36STG_20240816T111352` (2024-08-16, `0.27%`) |
| 21 | `earth_askja_holuhraun` | `candidate` | `64.8800, -16.8200` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32628`) | `h17v02`, n=19/24 (149 px) | `h17v02`, `2024-07-01`.. (`4` grn, 98 px) | `0.0223` (NDSI `-0.107`, kar `0/86`) | `S2A_MSIL2A_20240905T130301_R038_T28WDT_20240905T155849` (2024-09-05, `0.0%`) |
| 22 | `earth_harrat_rahat_madinah` | `candidate` | `24.3300, 39.7700` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32637`) | `h21v06`, n=23/24 (207 px) | `h21v06`, `2024-07-01`.. (`4` grn, 100 px) | — | `S2A_MSIL2A_20240704T074611_R135_T37QEG_20240705T225617` (2024-07-04, `0.0%`) |
| 23 | `earth_pinacate_el_elegante` | `candidate` | `31.8403, -113.3951` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32612`) | `h08v05`, n=24/24 (216 px) | `h08v05`, `2024-07-01`.. (`4` grn, 100 px) | `0.1418` (NDSI `-0.292`, kar `0/100`) | `S2B_MSIL2A_20240814T180919_R084_T12STA_20240814T220020` (2024-08-14, `0.0%`) |
| 24 | `earth_puna_campo_piedra_pomez` | `candidate` | `-26.5700, -67.4400` | `pyroclastic_tuff` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32719`) | `h11v11`, n=24/24 (216 px) | `h11v11`, `2024-07-01`.. (`4` grn, 100 px) | — | `S2A_MSIL2A_20231211T142711_R053_T19JFL_20231213T004036` (2023-12-11, `0.0%`) |
| 25 | `earth_deccan_mahabaleshwar` | `candidate` | `17.9240, 73.8050` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32643`) | `h25v07`, n=18/24 (154 px) | `h25v07`, `2024-01-01`.. (`4` grn, 80 px) | — | `S2B_MSIL2A_20241005T052649_R105_T43QCV_20241005T081613` (2024-10-05, `0.4%`) |
| 26 | `earth_harrat_ash_shaam` | `candidate` | `32.2200, 37.1500` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32637`) | `h21v05`, n=24/24 (216 px) | `h21v05`, `2024-07-01`.. (`4` grn, 100 px) | — | `S2A_MSIL2A_20240710T080611_R078_T37SCR_20240710T133142` (2024-07-10, `0.0%`) |
| 27 | `earth_kilbourne_hole_nm` | `candidate` | `31.9680, -106.9720` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32613`) | `h08v05`, n=24/24 (216 px) | `h08v05`, `2024-07-01`.. (`4` grn, 100 px) | — | `S2A_MSIL2A_20240909T173901_R098_T13SCR_20240910T005106` (2024-09-09, `0.0%`) |
| 28 | `earth_qaidam_dalangtan` | `candidate` | `38.4800, 91.4500` | `evaporite` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32646`) | `h25v05`, n=24/24 (216 px) | `h25v05`, `2024-07-01`.. (`4` grn, 100 px) | *(Dry run: `0/100` kar)* | `S2B_MSIL2A_20240814T044659_R076_T46SCH_20240814T080440` (2024-08-14, `0.0%`) |
| 29 | `earth_karapinar_meke` | `candidate` | `37.6750, 33.6650` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32636`) | `h20v05`, n=24/24 (211 px) | `h20v05`, `2024-07-01`.. (`4` grn, 100 px) | — | `S2B_MSIL2A_20240820T082559_R021_T36SWG_20240820T130351` (2024-08-20, `0.0%`) |
| 30 | `earth_suphan_south_apron` | `candidate` | `38.8650, 42.8300` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32638`) | `h21v05`, n=24/24 (213 px) | `h21v05`, `2024-07-01`.. (`4` grn, 100 px) | `0.2274` (NDSI `-0.377`, kar `0/100`) | `S2A_MSIL2A_20240905T075611_R035_T38SLJ_20240905T123250` (2024-09-05, `0.0%`) |
| 31 | `earth_nemrut_caldera_flank` | `candidate` | `38.6100, 42.3100` | `pyroclastic_tuff` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32638`) | `h21v05`, n=23/24 (198 px) | `h21v05`, `2024-07-01`.. (`4` grn, 100 px) | — | `S2A_MSIL2A_20240905T075611_R035_T38SKH_20240905T123250` (2024-09-05, `0.0%`) |
| 32 | `earth_agri_dogubayazit_flow` | `candidate` | `39.6800, 44.1400` | `basalt` | **`NASADEM_HGT_v001`** (**EGM96**, `EPSG:32638`) | `h21v05`, n=24/24 (203 px) | `h21v05`, `2024-07-01`.. (`4` grn, 100 px) | `0.1779` (NDSI `-0.365`, kar `0/100`) | `S2B_MSIL2A_20240821T075609_R035_T38SMJ_20240821T113401` (2024-08-21, `0.0%`) |
| 33 | `earth_payunia_pampa_negra` | `candidate` | `-36.1800, -69.1800` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32719`) | `h12v12`, n=24/24 (206 px) | `h12v12`, `2024-07-01`.. (`4` grn, 100 px) | — | `S2B_MSIL2A_20240214T142719_R053_T19HDV_20240214T201044` (2024-02-14, `0.0%`) |
| 34 | `earth_chajnantor_plateau` | `candidate` | `-23.0230, -67.7540` | `pyroclastic_tuff` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32719`) | `h11v11`, n=24/24 (216 px) | `h11v11`, `2024-07-01`.. (`4` grn, 100 px) | — | `S2B_MSIL2A_20240108T143739_R096_T19KFQ_20240108T211337` (2024-01-08, `0.0%`) |
| 35 | `earth_waw_an_namus_apron` | `candidate` | `24.9500, 17.7600` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32633`) | `h19v06`, n=24/24 (208 px) | `h19v06`, `2024-07-01`.. (`4` grn, 71 px) | — | `S2A_MSIL2A_20240711T092031_R093_T33RYH_20240711T152307` (2024-07-11, `0.0%`) |
| 36 | `earth_tibesti_tarso_voon` | `candidate` | `20.9200, 17.2800` | `pyroclastic_tuff` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32633`) | `h19v06`, n=24/24 (216 px) | `h19v06`, `2024-07-01`.. (`4` grn, 100 px) | — | `S2A_MSIL2A_20240711T092031_R093_T33QYD_20240711T152310` (2024-07-11, `0.0%`) |
| 37 | `earth_paricutin_lava_field` | `candidate` | `19.4930, -102.2510` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32613`) | `h08v07`, n=19/24 (159 px) | `h08v07`, `2024-07-01`.. (`3` grn, 57 px) | — | `S2A_MSIL2A_20241020T171341_R112_T13QGB_20241020T232550` (2024-10-20, `0.0%`) |
| 38 | `earth_tolbachik_apron` | `candidate` | `55.7550, 160.2950` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32657`) | `h27v03`, n=23/24 (160 px) | `h27v03`, `2024-07-01`.. (`4` grn, 67 px) | — | `S2B_MSIL2A_20240905T002609_R102_T57UWB_20240905T020902` (2024-09-05, `0.14%`) |
| 39 | `earth_kilauea_kau_desert` | `candidate` | `19.3650, -155.3350` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32604`) | `h03v07`, n=23/24 (189 px) | `h03v07`, `2024-07-01`.. (`4` grn, 100 px) | — | `S2B_MSIL2A_20240908T205939_R014_T04QHG_20240909T000602` (2024-09-08, `0.22%`) |
| 40 | `earth_tongariro_rangipo` | `candidate` | `-39.2850, 175.7200` | `basalt` | `Copernicus_DEM_GLO-30` (EGM2008, `EPSG:32760`) | `h31v12`, n=11/24 (95 px) | `h31v12`, `2024-07-01`.. (`4` grn, 100 px) | — | `S2B_MSIL2A_20240229T221559_R129_T60HUB_20240301T022210` (2024-02-29, `0.0%`) |

---

## 4. Ay Güney Kutbu (`Moon`, P2 / `p2-moonmars`) Uydu ve Referans Veri Kaynakları

Çıktı dosyası: `data/processed/features_moon.parquet` (`5` satır × `36` sözleşme sütunu; `0 MOCK`).  
*(Not: Yerel `p3-earth` `@ 197c6e8` sürümü geçici `temp_amplitude` değerlerini içerirken, `origin/main` `@ 40ada8a` sürümü Lider Kararı #30 Kapı 0 Seçenek (b) + Kapı 1 ile `temp_amplitude = NaN` ve `thermal_inertia = NaN` olarak güncellenmiştir.)*

### 4.1 5 Resmî Referans Saha Koordinatı ve ROI Kaynakları (`docs/data_sources_moon.md`)

| `site_id` | Saha Adı (`name`) | Koordinat (`lat`, `lon`) | Stereografik `(X, Y)` (m) | `lithology_class` | Resmî Koordinat / ROI / Jeoloji Kaynağı |
|---|---|---|---|---|---|
| `moon_shackleton_rim` | Shackleton Crater Rim (Site 04 ROI) | `-89.7800, -156.3201` | `(-2679.3, -6109.5)` | `regolith` | NASA GSFC PGDA `Site04_ROIs.shp` (ROI #3 merkezi); Mazarico vd. (2011), Barker vd. (2021), Zuber vd. (2012) |
| `moon_connecting_ridge` | Connecting Ridge (Shackleton-de Gerlache Ridge, Site 01 ROI) | `-89.4624, -137.0871` | `(-11099.8, -11939.4)` | `regolith` | NASA GSFC PGDA `Site01_ROIs.shp` (ROI #5 merkezi); Mazarico vd. (2011), Barker vd. (2021); Artemis III Connecting Ridge |
| `moon_de_gerlache_rim` | de Gerlache Crater Rim (Site 11 ROI) | `-88.6683, -68.3754` | `(-37541.2, +14882.2)` | `regolith` | NASA GSFC PGDA `Site11_ROIs.shp` (ROI #1 merkezi); Mazarico vd. (2011), Barker vd. (2021); Artemis III de Gerlache Rim |
| `moon_shackleton_peak` | Peak Near Shackleton (Site 07 ROI) | `-88.8063, +123.5451` | `(+30169.5, -20002.9)` | `anorthosite` | NASA GSFC PGDA `Site07_ROIs.shp` (ROI #1 merkezi); Mazarico vd. (2011), Barker vd. (2021); Spudis vd. (2008) saf anortozit masifi |
| `moon_faustini_rim` | Faustini Crater Rim A (PGDA LM7 Center) | `-87.8897, +90.0000` | `(+63998.6, 0.0)` | `impact_breccia` | NASA GSFC PGDA `LM7_final_adj_5mpp_surf.tif` (`X=[54,74] km, Y=[-10,+10] km` grid merkezi); Barker vd. (2021); Artemis III Faustini Rim A |

### 4.2 Ay Enstrüman ve Türev Ürünleri

| Özellik / Ürün | Kısa Kod (`*_src`) | Dosya / Arşiv / Versiyon | Çözünürlük | Metodoloji ve Doğrulama Notu |
|---|---|---|---|---|
| **`slope_mean`, `slope_p90`, `roughness`, `relief`** | `LRO_LOLA_PGDA_Site04_5mpp_v2021`, `LRO_LOLA_PGDA_Site01_5mpp_v2021`, `LRO_LOLA_PGDA_Site11_5mpp_v2021`, `LRO_LOLA_PGDA_Site07_5mpp_v2021`, `LRO_LOLA_PGDA_LM7_5mpp_v2021` | `{Site}_final_adj_5mpp_surf.tif` (NASA GSFC PGDA Product 78, Barker vd., 2021) | `5.0 m` | `r = 1000.0 m` (`~125,664–125,676` piksel), `np.gradient` $\rightarrow$ `atan` ve OLS düzlem kalıntısı (`Earth` ile özdeş). |
| **DEM Belirsizliği (`_sd`)** | `..._slperr.tif` ve `..._toterr.tif` | `<Site>_final_adj_5mpp_slperr.tif` (eğim RMS); `<Site>_final_adj_5mpp_toterr.tif` (düşey RMS medyanı: `0.3235–0.4504 m`, `origin/main`) + 200 bootstrap | `5.0 m` | Klon ansamblı RMS hata haritalarıyla `hypot` (karekök-toplam) birleştirme. (`197c6e8`'de `sigma_z = 0.35 m` sabit medyan; `40ada8a`'da piksel `toterr` haritasından çekildi). |
| **`albedo`** | `LRO-L-LOLA-4-GDR-V1.0:LDAM_50S_1000M_V1.0_broadband_eq` | `LDAM_50S_1000M_FLOAT.IMG` & `.LBL` (MIT Imbrium, 25.6 MB, `50°S–90°S`) | `1000.0 m` | 1064 nm sıfır-faz ($\alpha = 0^\circ$) normal albedosu $\times 0.38$ faz integrali katsayısıyla geniş bant güneş yarıküre albedosuna dönüştürüldü (Vasavada vd. 2012; Hayne vd. 2017; Lucey vd. 2014). Hassasiyet aralığı $c \in [0.30, 0.46]$ test edildi. |
| **`temp_amplitude`** | *Referans:* `LRO-L-DLRE-5-PCP-V1.0:pcp_avg_tbol_pols_240m_v2022` *(v1 `origin/main`'de `""` / `NaN`)* | `pcp_avg_tbol_pols_sum_ltim01..96_240.tab/.lbl` (PDS3 `DATA_SET_ID = LRO-L-DLRE-5-GCP-V1.0`, `80°S–90°S`) | `240.0 m` | `.lbl` doğrulamasında `ltim01` (`0.00–0.25 h` gece yarısı), `ltim49` (`12.00–12.25 h` öğle), `ltim73` (`18.00–18.25 h` akşamüstü) saptandı; 29.53 günlük vakumlu sinodik döngü ile MODIS 24 saatlik yıllık ortalama eşleşmediğinden `40ada8a` (Karar #30) ile v1'de **`NaN`** (`_src=""`, `_res_m=240.0`) yapılıp `ltim01..96` v2 referansına bırakıldı. |
| **`thermal_inertia`** | `""` (`NaN`) | Hayne et al. (2017) `dgdr_hpar_avg_cyl_128_jp2` (`±70°` sınırı) | `240.0 m` | Standart ürün `87.8°S–89.8°S` kutup bölgesini kapsamadığı ve Earth'te `NaN` olduğu için Karar #30 Kapı 1 ile **`NaN`**. |
| **`lithology_class`** *(niteliksel)* | `LRO_LOLA_Diviner_SouthPole_Regolith_Zuber2012_Spudis2008` | `docs/data_sources_moon.md §1–§3` (Zuber vd. 2012; Spudis vd. 2008; Barker vd. 2021) | `5.0–1000.0 m` | Sayısal skora girmez (`regolith`, `anorthosite`, `impact_breccia`). Yerel `p3-earth` kopyasında 37. sütun (`lithology_class_src`) olarak, `origin/main` `40ada8a`'da ise 36 sütunlu sözleşme uyarınca `docs/data_sources_moon.md`'de kayıtlıdır. |
| **Ay Görsel & 3D Türevler (`origin/main`)** | `data/processed/moon_atlas/`, `data/processed/thumbs/moon/`, `data/processed/moon_3d/` | `5` hillshade/hazard/atlas PNG (`2.2×2.2 km @ 5 m`), `5` `224×224` PNG + CSV/JSON, `5` `442×442` `.npz` + `16-bit PNG` + `moon_3d_metadata.json` | `5.0 m` (`9.82 m` thumb) | Yalnızca görsel/keşif ve 3B arazi görselleştirme içindir (`Illustrative slope bins; not a landing-safety assessment`). |

---

## 5. Uygulama İçi Canlı Görsel Servisler ve Harita Altlıkları (`app/`)

`app/main.py` ve `app/i18n.py` yalnızca görsel/bağlamsal inceleme sağlar (sayısal skora **hiçbir zaman** girmez):

| Servis / Sağlayıcı | Tam URL Şablonu | Katmanlar / Parametreler | Atıf / Lisans Notu (`app/i18n.py`) |
|---|---|---|---|
| **USGS Astrogeology WMS (Ay Optik)** | `https://planetarymaps.usgs.gov/cgi-bin/mapserv?map=/maps/earth/moon_spole.map&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=LRO_WAC_south&SRS=EPSG:32761&...` | `LRO_WAC_south` (~71 m/px ortomozaik, `30×30 km`, `420×420 px`) | NASA LRO Wide Angle Camera (WAC) via USGS Astrogeology WMS |
| **USGS Astrogeology WMS (Ay Kabartma)** | `https://planetarymaps.usgs.gov/cgi-bin/mapserv?map=/maps/earth/moon_spole.map&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=LOLA_south&SRS=EPSG:32761&...` | `LOLA_south` (kabartma haritası, `30×30 km`, `420×420 px`) | NASA LRO LOLA via USGS Astrogeology WMS |
| **Esri World Imagery REST Export** | `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?bbox=...&bboxSR=4326&imageSR=4326&size=420,420&format=png&f=image` | Yüksek çözünürlüklü optik uydu mozaiği (`3×3 km` veya `9×9 km` yedek pencere) | Esri World Imagery (Esri, Maxar, Earthstar Geographics) |
| **NASA Worldview** | `https://worldview.earthdata.nasa.gov/?v=...&l=Reference_Labels_15m,MODIS_Terra_Land_Surface_Temp_Day,Coastlines_15m` | `Reference_Labels_15m`, `MODIS_Terra_Land_Surface_Temp_Day`, `Coastlines_15m` | Saha koordinat ve termal bağlam görsel teyidi |
| **Google Maps (Uydu)** | `https://www.google.com/maps/@{lat},{lon},14z/data=!3m1!1e3` | `14z` uydu katmanı | Saha koordinat görsel teyidi (`AGENTS.md §6 Kural 2`) |
| **PyDeck Harita Görselleştirme** | `pydeck` `ScatterplotLayer` (`app/main.py:337-365`, fallback `st.map`) | Dünya aday/doğrulama sahaları katmanı | Konumsal harita görünümü |

---

## 6. Tüm Doğrulama Yerleri, Çapraz Denetimler ve Kalite Kapıları

Projenin bilimsel, yazılımsal ve verisel doğrulamaları **5 ayrı katmanda** gerçekleştirilmiştir:

### 6.1 Otomatik Veri Sözleşmesi Doğrulama Scriptleri (`scripts/`)
- **`scripts/validate_contract.py --fail-on-mock`:** Her `features_*.parquet` için kimlik şeması (`site_id` `^[a-z0-9]+(_[a-z0-9]+)*$`, `body` ∈ `{moon,mars,earth}`, `role` ∈ `{reference,validation,candidate,grid}`, `lat ∈ [-90,90]`, `lon ∈ [-180,180]`, `radius_m > 0`), fiziksel aralıklar (`albedo ∈ [0,1]`, `slope_* ∈ [0,90]`, `slope_p90 >= slope_mean`, `temp_amplitude > 0` veya `NaN`, `roughness/relief/thermal_inertia >= 0`), meta kuralları (dolu değerde `X_sd >= 0` zorunlu, `X_src != ""` zorunlu, `X_res_m > 0` her satırda zorunlu) ve `%95+ sıfır yer tutucu` uyarısı ile **`0 MOCK`** kontrolü yapar.
- **`scripts/validate_all.py --fail-on-mock`:** `data/processed/features_*.parquet` altındaki tüm dosyaları toplu doğrular (`features_earth.parquet` = `0/40 MOCK`, `0 hata`, `0 uyarı`; `origin/main` üzerinde `features_moon.parquet` = `0/5 MOCK`, `0 hata`, `0 uyarı`).

### 6.2 Pytest Test Paketleri (`src/earth/`, `src/moon_mars/`, `tests/`)
- **`src/earth/test_earth_audit.py`:** Tam 36 sütun şeması, 40 saha dağılımı (`10` doğrulama + `14` TR aday + `16` küresel aday) ve koordinat bölge sınırları (`SITE_REGION_BOUNDS`), `|temp_amplitude - (lst_day_mean_k - lst_night_mean_k)| < 0.1 K` (`docs/data_sources_earth.md`'de $\le 9.95 \times 10^{-14}\text{ K}$), koyu bazalt albedosu `[0.02, 0.10]` vs evaporit `[0.18, 0.45]`, enjekte `MOCK` reddi, `docs/data_sources_earth.md §4/§5/§6` çapraz tablo tutarlılığı, Ağrı `NASADEM` fallback kısıtı, HTTP retry/backoff politikası, `mixed_pixel.py` kuralları ve E7 `earth_3d_grids.npz` (< 1 MB, E5 sahne ID ve merkez ofseti ≤ 7.5 m) testleri.
- **`tests/` (Lider Skorlama Testleri):**
  - `test_similarity.py`, `test_combine_axes.py`, `test_axis_pivot.py`, `test_axis_gaps.py`, `test_display.py`, `test_portfolio_validation.py`.
  - Ayrıca `docs/data_notes.md §1`'de belgelenen manuel çapraz doğrulama: `5 referans × 40 aday × 3 eksen = 600` eksen skoru + `200` ağırlıklı toplamın parquet + formül üzerinden elle yeniden hesaplanması (**sapma: 0**).
- **`src/moon_mars/test_moon_pipeline.py` (`origin/main`):** 6 adet LOLA/Diviner/broadband albedo birim ve çıktı doğrulama testi (`6/6`).

### 6.3 Çoklu Sensör ve Fiziksel Çapraz Doğrulamalar
1. **MODIS `MCD43A3.061` ↔ `MCD43A4.061` (Liang 2001 + NDSI Kar Maskesi):** Planetary Computer'dan bağımsız hesaplanan `MCD43A4.061` NBAR + Liang (2001) albedosu; Askja (`0.0278` vs `0.0223`), Etna (`0.0472` vs `0.0490`), Svalbard (`0.1187` vs `0.1007`), Karacadağ (`0.1291` vs `0.1552`), Atacama (`0.2319` vs `0.2436`), Haughton (`0.2636` vs `0.2632`), McMurdo (`0.1398` vs `0.2078`, `19/41` NDSI≥0.40 kar maskesi), Pinacate (`0.1041` vs `0.1418`), Süphan (`0.1984` vs `0.2274`), Ağrı (`0.1563` vs `0.1779`) sahalarında teyit edildi; Tuz Gölü'nde ise parlak halit kabuğunun `NDSI >= 0.40` (`30/31` piksel) yanlış kar pozitifi ürettiği saptanıp belgelendi.
2. **ESA WorldCover 10m + Sentinel-2 L2A `SCL` + Mevsimsel `NDVI` (`docs/data_sources_earth.md §7` & `src/earth/mixed_pixel.py`):**
   - **5 `MIXED_*` Saha Tespit Edildi:** `earth_salda_terrace` (`MIXED_CROP+VEG`), `earth_tuz_golu_south` (`MIXED_WATER`, ayrıca `SCL=11` halit yanlış pozitifi), `earth_svalbard_bockfjorden` (`MIXED_WATER+VEG`), `earth_suphan_south_apron` (`MIXED_CROP+VEG`, `T38SLJ` Haziran/Ağustos/Eylül NDVI fenolojisi + `<=5 km` 17 noktalı `Bare_sparse_60 > 50%` taramasıyla mevcut konum korundu), `earth_meteor_crater_arizona` (`MIXED_VEG`).
   - **Mount Etna Konum Optimizasyonu:** `15°E` WorldCover mozaik (`N36E012+N36E015`) + yaz/ilkbahar/kış `S2 SCL` (`T33SVB`) ile 3 aday nokta karşılaştırılarak en saf tefra/en az kar (`%99.4` çıplak, kış karı `%22.0`) noktası olan OSM **Cisternazza (`37.7257, 15.0084`)** seçildi.
   - **Evaporit Kar Maskesi Yanlış Pozitif Kontrolü:** `earth_qaidam_dalangtan` (`4` benzersiz tarih: `2024-01-27`, `2024-05-18`, `2024-07-20`, `2024-08-14`) ve `earth_salda_terrace` (`5` benzersiz tarih: `2024-02-03`, `2024-05-18`, `2024-07-02`, `2024-08-16`, `2024-09-05`; `r=1 km` ile Şubat ve Ağustos aylarındaki ek `r=2 km` kıyı taramaları dâhil toplam `7` tarama koşumu) S2 sahnelerinde yanlış kar pozitifi çıkmadığı doğrulandı.
3. **Görsel Koordinat Teyidi (`docs/data_notes.md §1b` & `sites.py`):** 40 Dünya + 5 Ay sahasının tamamı NASA Worldview, Esri World Imagery, USGS Astrogeology WMS (`LRO WAC` / `LOLA`) ve OSM üzerinde görsel olarak doğrulandı (`5 m/px` Ay DEM ↔ `30 m/px` Earth DEM ve `1 km / 500 m` MODIS çözünürlük farkları açıkça belgelenerek).
4. **Ay PDS3 `.lbl` Doğrulaması ve Albedo Çarpan Hassasiyeti (`origin/main` `docs/data_sources_moon.md §4–§5`):** `ltim01..ltim96` etiketlerindeki `LRO:DLRE_CLOCTIME` doğrulandı; `albedo_sensitivity.py` ile $c \in [0.30, 0.46]$ bandında Spearman $\rho$ kararlılığı ($c \in [0.34, 0.42]$ için $\rho = 0.866\text{–}0.944$) test edildi.

### 6.4 Ön-Kayıtlı Kör Doğrulama Matrisi ve E8 Buz/Permafrost Envanteri (`docs/validation_expectations.md`)
- Skorlayıcı çalıştırılmadan **önce** sabitlenmiş 10 doğrulama sahası × 3 eksen = 30 çiftlik literatür beklenti tablosu.
- **10 / 30 Kesin Beklenti Hücresi:** `mobility` = **7 saha** (`etna`, `atacama`, `haughton`, `mauna_loa`, `lanzarote`, `meteor_crater`, `craters_of_the_moon` — not: `earth_lunar_crater_nevada` (`38.3840, -116.0680`, `r=1 km`) `mobility` satırı, önceki taslaktaki `Evans et al. (1992)` Cima volkanik alanı SAR çalışması olduğu ve `Arvidson et al. (2002)` FIDO denemesi ~12.5 km KD'daki Black Rock Summit'te yürütüldüğü için **Aday beklenti**ye [`kaynak doğrulanamadı`] indirilmiştir); `thermal` = **3 saha** (`atacama`, `haughton`, `mcmurdo` — `earth_lunar_crater_nevada` `thermal` & `surface` satırları da Aday'dır); `surface` = **0 kesin saha** (tümü `kaynak doğrulanamadı` / `Aday beklenti`).
- **E8 Nitel Buz / Permafrost Envanteri (10 Doğrulama Sahası):** `var` = 3 (`haughton`, `mcmurdo`, `svalbard`); `yok` = 1 (`atacama`); `veri yok` = 5 (`mauna_loa`, `lanzarote`, `meteor_crater`, `craters_of_the_moon`, `lunar_crater_nevada`); `kaynak doğrulanamadı` = 1 (`etna` — dağ ölçeği *Grotta del Gelo* için atıf verilen *Oliva et al. 2018* açık erişim tam metni çekilemediğinden mağara buzu metin içi doğrulanamadı; `kısmi` = 0).
- **Metodolojik Tanım (`docs/data_notes.md §2b` & `validation_expectations.md §3`):** Bu ekran bağımsız holdout testi değil; 40 satırın tamamının Z-ölçeklemesine katıldığı, rol etiketlerinden habersiz **betimsel sıra tanısıdır**.

### 6.5 Bibliyografik API ve Birincil Yayın Doğrulama Servisleri
1. **Crossref REST API (`api.crossref.org/works/<doi>`):** `Bölüm 7.1`'deki tüm makale DOI'leri (`28` adet: `§7.1.A`'da `26` DOI + `§7.1.B`'de Süphan `Özdemir, Blundy & Güleç 2011` `10.1007/s00410-011-0613-8` ve `Özdemir & Güleç 2014` `10.1093/petrology/egt060`) `HTTP 200` ile başlık/yazar/cilt/sayfa düzeyinde doğrulanmıştır (`NASADEM` DataCite DOI'si beklendiği üzere Crossref'te `HTTP 404` döner).
2. **DataCite REST API (`api.datacite.org/dois/<doi>`) & doi.org Handle API (`doi.org/api/handles/<doi>`):** NASA MEaSUREs veri seti DOI'si `10.5067/MEaSUREs/NASADEM/NASADEM_HGT.001` her iki serviste `HTTP 200` (*NASADEM Merged DEM Global 1 arc second V001*) olarak doğrulanmıştır.
3. **NASA NTRS API (`ntrs.nasa.gov/api/citations/<id>`):** `Plaut & Rivard (1992)` (`19940012289`) ve `Brackett & Arvidson (1993)` (`19940007625`) GRSFE konferans/LPSC künyeleri `HTTP 200` ile doğrulanmıştır.
4. **LPI Guidebook & DLR eLib Arşiv Bağlantıları:** `Kring (2007/2017)` (`www.lpi.usra.edu`, 2 kalıcı URL) ve `Vayugundla et al. (2018)` (`elib.dlr.de/124514/`) canlı HTTP denetiminde `HTTP 200` ile doğrulanmıştır.
5. **Oliva et al. (2018) Açık Erişim Tam-Metin Denetimi:** `10.1016/j.earscirev.2018.06.018` için Unpaywall (`422`), Manchester OA PDF (`403`), Pisa IRIS (`403`), Oviedo (`ConnectTimeout`), HAL (yalnızca üstveri) ve USF DigitalCommons (yalnızca özet) üzerinden tam metin çekilemediği için Etna E8 (`earth_etna_cisternazza` — *Grotta del Gelo*) dürüstlük gereği **`kaynak doğrulanamadı`** yapılmıştır.

---

## 7. Eksiksiz Literatür, Teknik Standart ve Jeoloji Haritası Kaynakçası

> **Bibliyografik Dürüstlük Kuralı (`AGENTS.md §6 Kural 2`):** Aşağıdaki **Bölüm 7.1**, doğrudan API/arşiv sorgusuyla DOI veya kalıcı URL ile teyit edilmiş birincil yayınları içerir: **toplam 29 benzersiz DOI** (**26** adet `Bölüm 7.1.A` içinde `validation_expectations.md` ile birebir Crossref HTTP 200 doğrulanmış DOI + **3** adet `Bölüm 7.1.B` içinde `1` NASADEM DataCite/Handle + `2` Süphan Crossref DOI) ile **4 DOI'siz birincil yayın / 5 kalıcı arşiv URL'si** (+ 1 teknik ürün kılavuzu). **Bölüm 7.2 ve 7.3**, proje kodu (`src/earth/sites.py`) ve veri dokümanlarında (`docs/data_sources_earth.md`, `docs/data_sources_moon.md`) yer alan teknik belgeleri, MTA jeoloji haritalarını ve kısa yazar–yıl atıflarını uydurma DOI eklenmeksizin birebir belgeler.

### 7.1 DOI veya Kalıcı Arşiv URL'si ile Doğrulanmış Birincil Kaynaklar

#### A. Gezegensel Analog Literatürü ve E8 Buz/Permafrost Kaynakları (`docs/validation_expectations.md` — 26 benzersiz DOI + 4 Yayın / 5 Kalıcı URL)
1. **Svalbard Permafrost & Volkanoloji (`Amundsen` AMASE yerine E8 birincil kaynakları):**
   - **Humlum, O., Instanes, A. & Sollid, J. L. (2003).** Permafrost in Svalbard: a review of research history, climatic background and engineering challenges. *Polar Research*, 22(2):191–215. `https://doi.org/10.3402/polar.v22i2.6455` *(E8 `earth_svalbard_bockfjorden`)*
   - **Treiman, A. H. (2012).** Eruption age of the Sverrefjellet volcano, Spitsbergen Island, Norway. *Polar Research*, 31(1):17320. `https://doi.org/10.3402/polar.v31i0.17320` *(Sverrefjellet hidrotermal alterasyon/jeoloji bağlamı)*
2. **Arvidson, R. E., Squyres, S. W., Baumgartner, E. T., Schenker, P. S., Niebur, C. S., Larsen, K. W., Seelos, F. P. IV, Snider, N. O. & Jolliff, B. L. (2002).** FIDO prototype Mars rover field trials, Black Rock Summit, Nevada, as test of the ability of robotic mobility systems to conduct field science. *J. Geophys. Res.: Planets*, 107(E11). `https://doi.org/10.1029/2000JE001464` *(`earth_lunar_crater_nevada` ~12.5 km KD'daki Black Rock Summit; doğrudan `38.3840, -116.0680 r=1 km` iddiası taşımadığı için yalnızca Aday arka planı, Cima çalışması `Evans et al. 1992` çıkarılmıştır)*
3. **Brackett, R. A. & Arvidson, R. E. (1993).** Compositional and textural information from the dual inversion of visible, near and thermal infrared remotely sensed data. *LPSC XXIV*, Part 1: A–F *(LCVF GRSFE TIMS/ASAS tersçözüm özeti)*. Kalıcı NTRS URL: `https://ntrs.nasa.gov/citations/19940007625` *(`earth_lunar_crater_nevada` Aday arka planı)*
4. **Guinness, E. A., Arvidson, R. E., Irons, J. R. & Harding, D. J. (1991).** Surface scattering properties estimated from modeling ASAS multiple emission angle reflectance data over the Lunar Crater Volcanic Field, Nevada. *Geophysical Research Letters*, 18(11):2051–2054. `https://doi.org/10.1029/91GL02664` *(`earth_lunar_crater_nevada` ~7 km doğudaki Lunar Lake playa ASAS Hapke arka planı)*
5. **Hughes, S. S., Haberle, C. W., Kobs Nawotniak, S. E., Sehlke, A., Garry, W. B., Elphic, R. C., Payler, S. J. & Stevens, A. H. (2019).** Basaltic Terrains in Idaho and Hawai‘i as Planetary Analogs for Mars Geology and Astrobiology. *Astrobiology*, 19(3):260–283. `https://doi.org/10.1089/ast.2018.1847` *(`earth_craters_of_the_moon` `mobility` — Not: `sites.py`'da sehven `JVGR` yazılıdır; gerçek dergi `Astrobiology`'dir)*
6. **Kring, D. A. (2007, 1. basım; 2017, 2. basım).** *Guidebook to the Geology of Barringer Meteorite Crater, Arizona (a.k.a. Meteor Crater)*. Lunar and Planetary Institute, LPI Contrib. No. 1355 (Bölüm 6: *Crater Rim Uplift and Crater Wall Collapse*). Kalıcı LPI URL'leri: `https://www.lpi.usra.edu/publications/books/barringer_crater_guidebook/` ve `https://www.lpi.usra.edu/publications/books/barringer_crater_guidebook/chapter_6.pdf` *(`earth_meteor_crater_arizona`)*
7. **Kumar, P. S., Head, J. W. & Kring, D. A. (2010).** Erosional modification and gully formation at Meteor Crater, Arizona: Insights into crater degradation processes on Mars. *Icarus*, 208(2):608–620. `https://doi.org/10.1016/j.icarus.2010.03.032` *(`earth_meteor_crater_arizona`)*
8. **Lee, P. & Osinski, G. R. (2005).** The Haughton-Mars Project: Overview of science investigations at the Haughton impact structure and surrounding terrains, and relevance to planetary studies. *Meteoritics & Planetary Science*, 40(12):1755–1758. `https://doi.org/10.1111/j.1945-5100.2005.tb00144.x` *(`earth_haughton_crater` `mobility`, `thermal`, E8)*
9. **Levy, J. S., Head, J. W. & Marchant, D. R. (2008).** The role of thermal contraction crack polygons in cold-desert fluvial systems. *Antarctic Science*, 20(6):565–579. `https://doi.org/10.1017/S0954102008001375` *(`earth_mcmurdo_wright_valley` destekleyici çalışma)*
10. **Levy, J. S., Marchant, D. R. & Head, J. W. (2010).** Thermal contraction crack polygons on Mars: A synthesis from HiRISE, Phoenix, and terrestrial analog studies. *Icarus*, 206(1):229–252. `https://doi.org/10.1016/j.icarus.2009.09.005` *(`earth_mcmurdo_wright_valley` `thermal`, E8)*
11. **Lim, D. S. S., Abercromby, A. F. J., Kobs Nawotniak, S. E., Lees, D. S. et al. (2019).** The BASALT Research Program: Designing and Developing Mission Elements in Support of Human Scientific Exploration of Mars. *Astrobiology*, 19(3):245–259. `https://doi.org/10.1089/ast.2018.1869` *(`earth_craters_of_the_moon` `mobility`)*
12. **Marchant, D. R. & Head, J. W. III (2007).** Antarctic dry valleys: Microclimate zonation, variable geomorphic processes, and implications for assessing climate change on Mars. *Icarus*, 192(1):187–222. `https://doi.org/10.1016/j.icarus.2007.06.018` *(`earth_mcmurdo_wright_valley` `thermal`, E8)*
13. **McKay, C. P., Friedmann, E. I., Gómez-Silva, B., Cáceres-Villanueva, L., Andersen, D. T. & Landheim, R. (2003).** Temperature and Moisture Conditions for Life in the Extreme Arid Region of the Atacama Desert: Four Years of Observations Including the El Niño of 1997–1998. *Astrobiology*, 3(2):393–406. `https://doi.org/10.1089/153110703769016460` *(`earth_atacama_yungay` `thermal`, E8 `yok`)*
14. **Navarro-González, R. et al. (2003).** Mars-Like Soils in the Atacama Desert, Chile, and the Dry Limit of Microbial Life. *Science*, 302(5647):1018–1021. `https://doi.org/10.1126/science.1089143` *(`earth_atacama_yungay`)*
15. **Oliva, M., Žebre, M., Guglielmin, M., Hughes, P. D., Çiner, A., Vieira, G., Bodin, X., Andrés, N. et al. (2018).** Permafrost conditions in the Mediterranean region since the Last Glaciation. *Earth-Science Reviews*, 185:397–436. `https://doi.org/10.1016/j.earscirev.2018.06.018` *(E8 `earth_etna_cisternazza` `kaynak doğrulanamadı` notu: açık erişim tam metin çekilemediği için dağ ölçeği Grotta del Gelo mağara buzu metin içi doğrulanamadı)*
16. **Osinski, G. R., Spray, J. G. & Lee, P. (2005).** Impactites of the Haughton impact structure, Devon Island, Canadian High Arctic. *Meteoritics & Planetary Science*, 40(12):1789–1812. `https://doi.org/10.1111/j.1945-5100.2005.tb00147.x` *(`earth_haughton_crater` — Not: `sites.py` `40:1759-1776` genel sayfa aralığıyla birleşik Haughton makalesine atıf verir)*
17. **Pflitsch, A., Schörghofer, N., Smith, S. M. & Holmgren, D. (2016).** Massive Ice Loss from the Mauna Loa Icecave, Hawaii. *Arctic, Antarctic, and Alpine Research*, 48(1):33–43. `https://doi.org/10.1657/AAAR0014-095` *(E8 saha-dışı Mauna Loa Icecave `~3400–3600 m` karşılaştırma notu)*
18. **Plaut, J. J. & Rivard, B. (1992).** Lithological and textural controls on radar and diurnal thermal signatures of weathered volcanic deposits, Lunar Crater region, Nevada. *Summaries of the Third Annual JPL Airborne Geoscience Workshop, Vol. 3: AIRSAR Workshop* *(GRSFE TIMS LCVF)*. Kalıcı NTRS URL: `https://ntrs.nasa.gov/citations/19940012289` *(`earth_lunar_crater_nevada` `thermal` Aday arka planı)*
19. **Poelchau, M. H., Kenkmann, T. & Kring, D. A. (2009).** Rim uplift and crater shape in Meteor Crater: Effects of target heterogeneities and trajectory obliquity. *J. Geophys. Res.: Planets*, 114(E1):2008JE003235. `https://doi.org/10.1029/2008JE003235` *(`earth_meteor_crater_arizona`)*
20. **Sauro, F., Pozzobon, R., Massironi, M., De Berardinis, P., Santagata, T. & De Waele, J. (2020).** Lava tubes on Earth, Moon and Mars: A review on their size and morphology revealed by comparative planetology. *Earth-Science Reviews*, 209:103288. `https://doi.org/10.1016/j.earscirev.2020.103288` *(`earth_lanzarote_timanfaya` — Not: `sites.py`'da cilt `208` yazılıdır; gerçek cilt `209`'dur)*
21. **Sauro, F., Payler, S. J., Massironi, M., Pozzobon, R., Hiesinger, H., Mangold, N., Cockell, C. S. & Martínez Frías, J. (2023).** Training astronauts for scientific exploration on planetary surfaces: The ESA PANGAEA programme. *Acta Astronautica*, 204:222–238. `https://doi.org/10.1016/j.actaastro.2022.12.034` *(`earth_lanzarote_timanfaya`)*
22. **Schuster, M. J., Müller, M. G., Brunner, S. G., Lehner, H., Lehner, P. et al. (2020).** The ARCHES Space-Analogue Demonstration Mission: Towards Heterogeneous Teams of Autonomous Robots for Collaborative Scientific Sampling in Planetary Exploration. *IEEE Robotics and Automation Letters*, 5(4):5315–5322. `https://doi.org/10.1109/LRA.2020.3007468` *(`earth_etna_cisternazza`)*
23. **Scott, D. H. & Trask, N. J. (1971).** Geology of the Lunar Crater volcanic field, Nye County, Nevada. *USGS Professional Paper* 599-I. `https://doi.org/10.3133/pp599i` *(`earth_lunar_crater_nevada`)*
24. **Shiro, B. R., Rowland, S. K., Hurtado, J. M., Caldwell, B. J., Bleacher, J. E., Fagents, S. A., Roma, P. G. & Bedwell-Torres, W. L. (2022).** Geological tasks during HI-SEAS planetary analog mission simulations, Mauna Loa, Hawai'i. *Planetary and Space Science*, 212:105409. `https://doi.org/10.1016/j.pss.2021.105409` *(`earth_mauna_loa_hiseas`)*
25. **Shoemaker, E. M. (1959).** Impact mechanics at Meteor Crater, Arizona. *USGS Open-File Report* 59-108. `https://doi.org/10.3133/ofr59108` *(`earth_meteor_crater_arizona`)*
26. **Thomson, L. I., Osinski, G. R. & Pollard, W. H. (2012).** The dielectric permittivity of terrestrial ground ice formations: Considerations for planetary exploration using ground-penetrating radar. *J. Geophys. Res.: Planets*, 117(E9):E09003 (`2012JE004053`). `https://doi.org/10.1029/2012JE004053` *(`earth_haughton_crater` `thermal` & E8)*
27. **Valentine, G. A., Cortés, J. A., Widom, E. & Smith, E. I. (2017).** Lunar Crater volcanic field (Reveille and Pancake Ranges, Basin and Range Province, Nevada, USA). *Geosphere*, 13(2):391–438. `https://doi.org/10.1130/GES01428.1` *(`earth_lunar_crater_nevada`)*
28. **Vayugundla, M., Steidle, F., Smisek, M., Schuster, M. J., Bussmann, K. & Wedler, A. (2018).** Datasets of Long Range Navigation Experiments in a Moon Analogue Environment on Mount Etna. *50th International Symposium on Robotics (ISR 2018)*, s. 1–7. Kalıcı DLR URL: `https://elib.dlr.de/124514/` *(`earth_etna_cisternazza`)*
29. **Wettergreen, D., Cabrol, N., Teza, J., Tompkins, P., Urmson, C., Verma, V., Wagner, M. & Whittaker, W. (2005).** First Experiments in the Robotic Investigation of Life in the Atacama Desert of Chile. *Proc. 2005 IEEE ICRA*, s. 873–878. `https://doi.org/10.1109/ROBOT.2005.1570227` *(`earth_atacama_yungay` `mobility`)*

#### B. Uydu Veri Seti DOI, Doğrulanmış Aday Saha DOI'leri ve Teknik Standart Belgeleri (`docs/data_sources_earth.md` & `data_notes.md` — 3 benzersiz DOI + 1 teknik kılavuz)
30. **NASA MEaSUREs NASADEM:** *NASADEM Merged DEM Global 1 arc second V001*. NASA EOSDIS Land Processes DAAC (`C2763264762-LPCLOUD`). `https://doi.org/10.5067/MEaSUREs/NASADEM/NASADEM_HGT.001` *(DataCite / doi.org Handle doğrulamalı; `earth_agri_dogubayazit_flow` DEM yedeği)*
31. **Özdemir, Y., Blundy, J. & Güleç, N. (2011).** The importance of fractional crystallization and magma mixing in controlling chemical differentiation at Süphan stratovolcano, eastern Anatolia, Turkey. *Contributions to Mineralogy and Petrology*, 162(3):573–597. `https://doi.org/10.1007/s00410-011-0613-8` *(`earth_suphan_south_apron` — Crossref doğrulamalı; eski yanlış `Lithos 127:68-85` künyesinin yerine)*
32. **Özdemir, Y. & Güleç, N. (2014).** Geological and Geochemical Evolution of the Quaternary Süphan Stratovolcano, Eastern Anatolia, Turkey: Evidence for the Lithosphere–Asthenosphere Interaction in Post-Collisional Volcanism. *Journal of Petrology*, 55(1):37–62. `https://doi.org/10.1093/petrology/egt060` *(`earth_suphan_south_apron` — Crossref doğrulamalı)*
33. **Airbus / ESA (2022):** *Copernicus DEM — Product Handbook*, Doküman Kodu `GEO.2018-1988-2`, Bölüm 4.2 (`< 2.0 m` bağıl düşey doğruluk `LE90` $\rightarrow$ `sigma_z_rel = 1.0 m`).

---

### 7.2 Kod/Doküman İçi Kısa Künyeler: Türkiye ve Küresel Aday Sahalar (`src/earth/sites.py`, `docs/data_sources_earth.md §3, §4, §6`)

*(Aşağıdaki yayınlar ve jeoloji haritaları proje kodu ve dokümanlarında doğrulanmış saha kaynağı olarak yer almaktadır; doğrudan DOI URL'leri henüz `validation_expectations.md` formatında tam teyit sürecinden geçmediği için proje metinlerindeki özgün biçimiyle kaydedilmiştir.)*

#### A. Türkiye Aday Sahaları (`14` Saha — `AGENTS.md §7` Literatür / Novelty Ayrımı Dahil)
- **Zaten Literatürde Bilinen Gezegen Analogu Sahalar (Yeni keşif iddiası yapılmaz):**
  - `earth_salda_terrace`: **Horgan et al. (2020)**, *Icarus* 339:113526 & **Russell et al. (1999)**, *J. Geol. Soc.* 156:869–888 — NASA Mars 2020 *Perseverance* Jezero Krateri karbonat/hidromanyezit analogu.
  - `earth_tuz_golu_south`: **Çiner et al. (2021)** & **Kashima (2002)**, *Catena* 48:3–20 — kapalı havza halit/jips evaporit düzlüğü.
  - `earth_acigol_guneydag`: **Druitt et al. (1995)**, *J. Geol. Soc. London* 152:655–667 & **Schmitt et al. (2011)** — Acıgöl-Nevşehir kaldera maarları ve tefra halkası.
  - `earth_karapinar_meke`: **Keller (1974)**, *Bull. Volcanol.* 38:378–396 & **Reid et al. (2017)**, *JVGR* 338:1–13 — Karapınar maar/cüruf konisi alanı.
- **Volkanoloji / Petroloji Literatüründen Alınan Nicel Test Adayları (`candidate`, doğrulanmış analog iddiası yok):**
  - `earth_karacadag_summit`: **Lustrino et al. (2010)**, *Lithos* 117:135–151; **Keskin et al. (2012)**; **Ekici et al. (2014)**.
  - `earth_karacadag_ovabag`: **Ekici et al. (2014)**, *Geodinamica Acta* 26:3–4 & **Lustrino et al. (2012)**.
  - `earth_kula_divlit`: **Ersoy et al. (2010)**, *JVGR* 190:291–306 & **Aldanmaz et al. (2015)**.
  - `earth_tendurek_shield`: **Lebedev et al. (2016)**, *Petrology* 24:127–163 & **Yılmaz et al. (1998)**, *JVGR* 85:173–210.
  - `earth_erciyes_kojugedigi`: **Şen et al. (2003)**, *JVGR* 125:225–246 & **Friedrichs et al. (2020)**.
  - `earth_hasandagi_kecekalecik`: **Deniel et al. (1998)**, *JVGR* 87:275–302 & **Aydar & Gourgaud (1998)**.
  - `earth_cappadocia_kavakkoy`: **Le Pennec et al. (1994)**, *JVGR* 63:59–87 & **Aydar et al. (2012)**, *Bull. Volcanol.* 74:739–762.
  - `earth_suphan_south_apron`: **Özdemir, Blundy & Güleç (2011)**, *Contrib. Mineral. Petrol.* 162(3):573–597 (`doi:10.1007/s00410-011-0613-8`); **Özdemir & Güleç (2014)**, *J. Petrol.* 55(1):37–62 (`doi:10.1093/petrology/egt060`) & **Yılmaz et al. (1998)**, *JVGR* 85:173–210.
  - `earth_nemrut_caldera_flank`: **Çubukçu et al. (2012)**, *JVGR* 209–210:33–60 & **Ulusoy et al. (2008)**.
  - `earth_agri_dogubayazit_flow`: **Yılmaz et al. (1998)**, *JVGR* 85:173–210 & **Pearce et al. (1990)**, *JVGR* 44:189–229.
- **MTA 1:500.000 Türkiye Jeoloji Haritaları (`docs/data_sources_earth.md §6`):** Litoloji alt-sınıf denetiminde kullanılan resmî paftalar: **Kayseri**, **Konya**, **Van** ve **Kars** paftaları.

#### B. Küresel Aday Sahalar (`16` Saha)
- `earth_askja_holuhraun`: **Pedersen et al. (2017)**, *JVGR* 340:155–170 & **Greeley et al. (2000)**.
- `earth_harrat_rahat_madinah`: **Camp & Roobol (1989)**, *GSA Bulletin* 101:71–95 & **Downs et al. (2018)**.
- `earth_pinacate_el_elegante`: **Gutmann (2002)**, *GSA Special Paper* 365 & **Greeley et al. (1985)** (OSM teyitli).
- `earth_puna_campo_piedra_pomez`: **de Silva et al. (2010)**, *Geology* 38:219–222 & **Bridges et al. (2015)**, *JGR Planets*.
- `earth_deccan_mahabaleshwar`: **Self et al. (2006)**, *EPSL* 248:518–532 & **Jay & Widdowson (2008)**.
- `earth_harrat_ash_shaam`: **Ibrahim et al. (2006)** & **Shaw et al. (2003)**, *J. Petrology* 44:1657–1679.
- `earth_kilbourne_hole_nm`: **Seeger et al. (2019)** & **Padovani & Carter (1977)**.
- `earth_qaidam_dalangtan`: **Xiao et al. (2017)**, *ESR* 164:84–101 & **Anglés & Li (2017)**, *JGR Planets*.
- `earth_payunia_pampa_negra`: **Søager et al. (2013)**, *Chem. Geol.* 349–350:36–53 & **Hernando et al. (2014)**, *JVGR* 272:1–19.
- `earth_chajnantor_plateau`: **Salisbury et al. (2011)**, *GSA Bull.* 123:821–840 & **de Silva (1989)**, *Geology* 17:1102–1106.
- `earth_waw_an_namus_apron`: **Bardintzeff et al. (2012)**, *Chemie der Erde* 72:135–145 & **Busrewil & Wadsworth (1983)**.
- `earth_tibesti_tarso_voon`: **Permenter & Oppenheimer (2007)**, *Bull. Volcanol.* 69:609–626 & **Gourgaud & Vincent (2004)**, *JVGR* 129:261–294.
- `earth_paricutin_lava_field`: **Luhr & Simkin (1993)** & **Erlund et al. (2010)**, *Bull. Volcanol.* 72:347–363.
- `earth_tolbachik_apron`: **Belousov et al. (2015)**, *JVGR* 307:22–37 & **Fedotov et al. (1991)**.
- `earth_kilauea_kau_desert`: **Craddock et al. (2012)**, *JGR Planets* 117:E08009 & **Schiffman et al. (2006)**, *Geology* 34:921–924.
- `earth_tongariro_rangipo`: **Donoghue et al. (1995)**, *Bull. Volcanol.* 57:563–576 & **Hobden et al. (1999)**, *J. Petrology* 40:1965–1990.

#### C. `sites.py`'da Doğrulama Sahalarına Ek Geçen ve Revizyon Gerektiren Kısa Atıflar
- `Wedler et al. (2017)` ROBEX *(Etna)*; `Warren-Rhodes et al. (2006)` *(Atacama)*; `Lee` Haughton-Mars Project *(Haughton)*; `Binsted et al. (2016)` & `Bleacher et al. (2017, JVGR 342:1-10)` *(Mauna Loa HI-SEAS)*; `Levy et al. (2009)` *(McMurdo)*; `Bessone et al. (2018)` *(Lanzarote PANGAEA)*; `Shoemaker (1963)` *(Meteor Crater — 7.1'de birincil OFR 59-108 eklendi)*; `Steele et al. (2011, Astrobiology 11)` & `Amundsen et al. (2012)` *(Svalbard AMASE)*; `Greeley et al. (1972, NASA SP-315)` *(Not: Idaho Bear Crater hakkındadır; `sites.py` ve `docs/data_sources_earth.md`'de `Scott & Trask 1971` ve `Valentine et al. 2017` ile değiştirilmiştir; `Evans et al. 1992` `IEEE TGRS 30(2):382–389` ise Cima volkanik alanı SAR çalışması olduğu için çıkarılmıştır)*.

---

### 7.3 Ay Güney Kutbu (`Moon`) ve Uzaktan Algılama Metodolojisi Kaynakları

#### A. Ay Güney Kutbu Literatürü (`docs/data_sources_moon.md` & `shackleton_slope.py`)
- **Barker et al. (2021).** *Planetary and Space Science*, 203:105119 — NASA GSFC PGDA Product 78 (`LRO_LOLA_PGDA_<Site>_5mpp_v2021`, 5 m/px DEM, `slperr`, `toterr` klon ansamblı ve medyan düşey RMS hatası).
- **Hayne et al. (2017).** *J. Geophys. Res.: Planets*, 122:2371–2400 — LRO Diviner termal eylemsizlik `H`-parametresi (`±70°` enlem sınırı) & Ay faz/albedo ilişkisi.
- **Lemelin et al. (2016).** *LPSC* 47 — LOLA 1064 nm normal albedo ürün kalibrasyonu (`0.34–0.40` normal albedo aralığı).
- **Lucey et al. (2014).** *J. Geophys. Res.: Planets*, 119:1665 — Ay yüzeyi 1064 nm LOLA reflektans özellikleri.
- **Mazarico et al. (2011).** *Icarus*, 211:1066–1081 — Ay Güney Kutbu aydınlanma ve ROI topoğrafyası.
- **Paige et al. (2010).** *Science*, 330:479 — Diviner Ay Güney Kutbu aşırı düşük ve yüksek sıcaklıkları (`T_max`, `T_min`).
- **Spudis et al. (2008).** *Geophysical Research Letters*, 35:L14201 — Shackleton yakını masiflerde saf anortozit (`anorthosite`) jeolojisi.
- **Vasavada et al. (2012).** *J. Geophys. Res.*, 117:E00H18 — Diviner termal davranış ve `× 0.38` sıfır-faz 1064 nm normal $\rightarrow$ geniş bant güneş yarıküre albedo katsayısı.
- **Williams et al. (2019).** *J. Geophys. Res.: Planets*, 124:2505–2521 — LRO Diviner Polar Cumulative Products (`ltim01..ltim96`, bolometrik sıcaklık zaman serileri).
- **Zuber et al. (2012).** *Nature*, 486:378–381 — Shackleton krateri iç/kenar LOLA eğim ve yansıma analizi (`15°–32°`).

#### B. Uzaktan Algılama Dönüşüm Formülleri (`src/earth/modis_pipeline.py`)
- **Liang, S. (2001).** Narrowband to broadband conversions of land surface albedo I: Algorithms. *Remote Sensing of Environment*, 76:213–238, Eq. 9 (MODIS 7-bant kısa dalga genişbant albedo dönüşümü).
- **Hall, D. K. et al. (2002).** NDSI kar maskesi tanımı: $\text{NDSI} = (\rho_4 - \rho_6)/(\rho_4 + \rho_6) < 0.40$ (`docs/data_sources_earth.md §2.5`).

---

## 8. Yazılım Yığını ve Sabitlenmiş Bağımlılıklar (`requirements.txt`)

`Python 3.11+` ortamı için sabitlenmiş paket sürümleri:
- `numpy==2.4.6`, `pandas==3.1.1`, `pyarrow==26.0.1`, `scipy==1.17.1`, `scikit-learn==1.9.1`
- `geopandas==1.2.0`, `rasterio==1.4.4`, `xarray==2026.9.0`, `pyproj==3.7.2`
- `streamlit==1.67.0`, `pydeck==0.9.3`, `plotly==7.1.0`
- `shap==0.51.0`, `requests==2.34.2`, `pytest==9.2.0`
*(Not: `src/earth/build_atlas.py` WebP dönüşümünde ortamda bulunan `Pillow` (`PIL.Image`) kütüphanesini de kullanmaktadır; ayrıca `scripts/` ve `src/scoring/` tamamen standart Python + `numpy`/`pandas` üzerine kuruludur.)*
