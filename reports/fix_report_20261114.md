# Dünya Veri Seti (`features_earth.parquet`) 6 Maddelik Denetim ve Düzeltme Raporu

**Tarih:** 2026-11-14  
**Dal (Branch):** `p3-earth`  
**Arşiv Yedeği:** `data/processed/archive/features_earth_20261114.parquet` (Düzeltme öncesi tam yedek alındı)  
**Doğrulama Logu:** `logs/validate_20261114.txt`  
**Otomatik Test Paketi:** `tests/test_features_earth.py` (`7 passed`)

---

## Özet Durum Tablosu

| Madde | Konu | Durum | Özet Kanıt & Sonuç |
|---|---|---|---|
| **MADDE 1** | `temp_amplitude` iki farklı çalıştırmada farklı | **ÇÖZÜLDÜ** | İlk çalıştırma (`1394632`) Kuzey yazı (`2025-06-01/2025-08-31`, `n=4`), ikinci çalıştırma (`f6a6be4`) tam yıl (`2024-01-01/2024-12-31`, `n=24`) idi. Tüm 28 saha tekil `MOD11A2.061_annual_mean` (`0.02 K` ölçek, `(QC_Day & 0b11) <= 1`, `(QC_Night & 0b11) <= 1`, Sinusoidal karo sorgusu) ile yeniden hesaplandı; tüm sahalarda $\|\text{amp} - (\text{day} - \text{night})\| \le 9.95 \times 10^{-14}\text{ K} < 0.1\text{ K}$. |
| **MADDE 2** | `albedo` kaynağı ve QA/NDSI doğrulaması | **ÇÖZÜLDÜ** | Değerlerin `MOCK` olmadığı, `EARTHDATA_TOKEN` ile NASA LP DAAC `MCD43A3.061` (`Albedo_BSA_shortwave`, `DN * 0.001`) HDF-EOS2 verisinden geldiği kanıtlandı (`5a81eb5`). Ek olarak Planetary Computer `MCD43A4.061` NBAR üzerinden **Liang (2001)** formülü + `QA <= 1` + `NDSI < 0.40` kar maskesi (`fetch_mcd43a4_nbar_albedo_liang2001`) eklendi ve çapraz doğrulandı. |
| **MADDE 3** | `validate_contract.py` tam çıktısı ve `"0/4"` MOCK açıklaması | **ÇÖZÜLDÜ** | Tam çıktı `logs/validate_20261114.txt` dosyasına kaydedildi. Tüm 8 `*_src` sütununda `MOCK = 0`. `"0/4"` ifadesinin ilk 4 sahalık çalıştırmadaki `n_mock / len(df)` (`scripts/validate_contract.py:203`) olduğu, 28 sahalık dondurulmuş sette `"0/28"` olduğu gösterildi ve `MOCK` enjeksiyon testi eklendi. |
| **MADDE 4** | `lithology_class` denetimi, `lithology_src` ve `lithology_conflicts.csv` | **ÇÖZÜLDÜ** | `features_earth.parquet` içine 28 sahanın tamamı için dolu `lithology_src` sütunu eklendi. MTA 1:500.000 ve hakemli literatür karşılaştırmasında alt-sınıf nüansı bulunan 7 saha (`earth_tongariro_rangipo`, `earth_erciyes_kojugedigi`, `earth_hasandagi_kecekalecik`, `earth_salda_terrace`, `earth_tendurek_shield`, `earth_suphan_south_apron`, `earth_paricutin_lava_field`) `lithology_conflicts.csv` dosyasına yazıldı; mevcut `lithology_class` şeması kullanıcı onayına kadar korundu. |
| **MADDE 5** | Yüksek belirsizlikli (`CV > 0.30`) satırlar ve NDSI kar maskesi | **ÇÖZÜLDÜ** | Hiçbir satır silinmeden `high_uncertainty` (`bool`) sütunu eklendi. `albedo_sd / albedo > 0.30` olan tek saha `earth_mcmurdo_wright_valley` (`CV_alb = 0.6873`, vadi tabanı dolerit ile yamaç kar örtüsü geçişi; `NDSI_mean = +0.434`, `19/41` kar pikseli maskelendi). `temp_amplitude_sd / temp_amplitude > 0.30` olan 19 saha (yıllık mevsimsel çevrim varyansı) listelendi. |
| **MADDE 6** | Otomatik veri bütünlüğü test paketi (`tests/test_features_earth.py`) | **ÇÖZÜLDÜ** | Saha sayıları (`validation = 10`, `candidate = 18` [10 Türkiye + 8 küresel]), fiziksel eşitsizlikler (`slope_p90 >= slope_mean`, `relief >= 0`, `roughness >= 0`, `0 <= albedo <= 1`), tablolar arası birebir tutarlılık (`parquet == sites.py == docs/data_sources_earth.md`) ve 28 sahanın bölgesel koordinat kutusu doğrulaması `pytest` ile test edildi (`7/7 PASSED`). |
| **EK ÇIKTI** | 28 saha için `5×5 km` Sentinel-2 L2A RGB uydu thumbnail paketi | **ÇÖZÜLDÜ** | `outputs/satellite_thumbs/<site_id>.png` ve `<site_id>_meta.json` üretildi ve `outputs/satellite_thumbs.zip` olarak paketlendi. |

---

## MADDE 1 — `temp_amplitude` Değerlerinin İki Farklı Çalıştırmada Farklı Olması

### [Bulgu]
İlk 4 çekirdek saha (`earth_etna_cisternazza`, `earth_atacama_yungay`, `earth_haughton_crater`, `earth_karacadag_summit`) için iki farklı çalıştırmada sırasıyla `(24.92, 16.85, 4.52, 17.27 K)` ve `(17.98, 28.92, 3.62 [düzeltilmiş karo sorgusuyla 2.71], 14.61 K)` değerleri üretilmiştir.

### [Kanıt (komut çıktısı / dosya / satır)]
1. **Git geçmişi ve önbellek dosyaları (`data/raw/earth/`):**
   - **Commit `1394632` (`data/raw/earth/*_mod11a2_061.json`):** `datetime_range = "2025-06-01/2025-08-31"` (yalnızca Kuzey yarımküre yaz penceresi, `max_composites = 4`, `temp_amplitude_src = "MOD11A2.061"`):
     - `earth_etna_cisternazza`: `24.9225 ± 6.4307 K` (`n_valid_composites = 4`)
     - `earth_atacama_yungay`: `16.8511 ± 1.2946 K` (`n_valid_composites = 4`, Güney yarımküre kışı!)
     - `earth_haughton_crater`: `4.5240 ± 2.3712 K` (`n_valid_composites = 4`, Arktik yaz)
     - `earth_karacadag_summit`: `17.2743 ± 1.1675 K` (`n_valid_composites = 4`)
   - **Commit `f6a6be4` (`data/raw/earth/*_mod11a2_061_annual_2024.json`):** Liderin Issue #1 yorumu (`temp_amplitude'u yıllık çevrim ortalamasına geçir: 2024-01-01/2024-12-31, max_composites=24`) üzerine tam yıllık çevrime geçildi (`temp_amplitude_src = "MOD11A2.061_annual_mean"`):
     - Kuzey yarımküre sahaları (Etna `24.92 -> 17.98 K`, Karacadağ `17.27 -> 14.61 K`, Haughton `4.52 -> 2.71 K`) kış kompozitlerinin dahil olmasıyla düşmüş; Güney yarımküredeki Atacama (`16.85 -> 28.92 K`) ise Güney yazı ve bahar kompozitlerinin dahil olmasıyla yükselmiştir.
2. **STAC Karo Sorgusu Bulgusu (`src/earth/modis_pipeline.py:141-160`):**
   - Planetary Computer STAC üzerinde `intersects: Point(lon, lat)` sorgusu, `75.37°N` enlemindeki Haughton Krateri'nde (`h15v01` karo köşesine yakın) WGS84 4-köşe kiriş distorsiyonu nedeniyle komşu karoları (`h14v01`, `h16v01`) döndürüp `h15v01` yaz granüllerini atlıyordu. Sorgu `'query': {'modis:horizontal-tile': {'eq': h_idx}, 'modis:vertical-tile': {'eq': v_idx}}` olarak düzeltildiğinde `h15v01` karosunun tüm 46 yıllık granülü eksiksiz gelmektedir (`n_valid_composites = 23`).

### [Yapılan düzeltme]
- `src/earth/modis_pipeline.py:42-113` içinde `LST_Day_1km` ve `LST_Night_1km` (`DN >= 7500`, ölçek çarpanı `0.02 K`) yanında `QC_Day` ve `QC_Night` zorunlu kalite maskesi (`(qc_d & 0b11) <= 1` ve `(qc_n & 0b11) <= 1`) uygulandı.
- `src/earth/modis_pipeline.py:141-155` içinde STAC araması kesin Sinusoidal karo indeksleriyle (`modis:horizontal-tile == h_idx`, `modis:vertical-tile == v_idx`) yapılacak şekilde sabitlendi.
- Tüm 28 saha tek bir tanımla (`MOD11A2.061_annual_mean`, `2024-01-01/2024-12-31`, `max_composites = 24`) yeniden hesaplandı; `lst_day_mean_k` ve `lst_night_mean_k` sütunları doğrudan `data/processed/features_earth.parquet` içine eklendi ve tanım `docs/data_sources_earth.md` (§2.4) içine yazıldı.

### [Doğrulama testi ve sonucu]
- 4 çekirdek saha ve tüm 28 saha için yeniden çekilen değerler (`tests/test_features_earth.py::test_madde1_temp_amplitude_consistency`):
  - `earth_etna_cisternazza`: `lst_day_mean_k = 289.69 K`, `lst_night_mean_k = 271.71 K`, `temp_amplitude = 17.98 K`, $| \text{amp} - (\text{day} - \text{night}) | = 3.20 \times 10^{-14}\text{ K} < 0.1\text{ K}$
  - `earth_atacama_yungay`: `lst_day_mean_k = 313.37 K`, `lst_night_mean_k = 284.44 K`, `temp_amplitude = 28.92 K`, $| \text{amp} - (\text{day} - \text{night}) | = 9.95 \times 10^{-14}\text{ K} < 0.1\text{ K}$
  - `earth_haughton_crater`: `lst_day_mean_k = 258.38 K`, `lst_night_mean_k = 255.68 K`, `temp_amplitude = 2.71 K`, $| \text{amp} - (\text{day} - \text{night}) | = 5.77 \times 10^{-15}\text{ K} < 0.1\text{ K}$
  - `earth_karacadag_summit`: `lst_day_mean_k = 295.01 K`, `lst_night_mean_k = 280.40 K`, `temp_amplitude = 14.61 K`, $| \text{amp} - (\text{day} - \text{night}) | = 1.07 \times 10^{-14}\text{ K} < 0.1\text{ K}$
- **Sonuç:** `PASSED` (28 sahanın tamamında maksimum fark $9.95 \times 10^{-14}\text{ K} < 0.1\text{ K}$).

---

## MADDE 2 — `albedo` Kaynağı ve Fiziksel / QA / NDSI Doğrulaması

### [Bulgu]
Commit `f6a6be4` aşamasında `EARTHDATA_TOKEN` henüz sağlanmadığı için `albedo` sütunu `NaN` bırakılmıştı; liderden `EARTHDATA_TOKEN` geldikten sonra commit `5a81eb5` ile NASA LP DAAC üzerinden gerçek `MCD43A3.061` (`Albedo_BSA_shortwave`, 500 m) değerleri (`Etna = 0.0439`, `Karacadağ = 0.1291`, `Atacama = 0.2319`, `Haughton = 0.2636`) çekilmiştir.

### [Kanıt (komut çıktısı / dosya / satır)]
- `src/earth/modis_pipeline.py:325-398` (`fetch_mcd43a3_albedo`) ve `data/raw/earth/*_mcd43a3_061.json` dosyalarında her saha için NASA CMR / LP DAAC granül kimlikleri kayıtlıdır:
  - `earth_etna_cisternazza`: `["MCD43A3.A2024183.h19v05.061.2024192062445.hdf", ...]` -> `albedo = 0.0439 ± 0.0118`
  - `earth_karacadag_summit`: `["MCD43A3.A2024183.h21v05.061.2024192055436.hdf", ...]` -> `albedo = 0.1291 ± 0.0048`
  - `earth_atacama_yungay`: `["MCD43A3.A2024183.h11v11.061.2024192045643.hdf", ...]` -> `albedo = 0.2319 ± 0.0239`
  - `earth_haughton_crater`: `["MCD43A3.A2024183.h15v01.061.2024192052124.hdf", ...]` -> `albedo = 0.2636 ± 0.0632`
- Hiçbir satırda `MOCK` kaynak yoktur (`count_mock == 0`).

### [Yapılan düzeltme]
- `EARTHDATA_TOKEN` bulunmayan ortamlar ve NBAR çapraz doğrulaması için `src/earth/modis_pipeline.py:219-361` içine `fetch_mcd43a4_nbar_albedo_liang2001()` eklendi:
  - Planetary Computer `modis-43A4-061` (`Nadir_Reflectance_Band1..7`, ölçek `0.0001`) + zorunlu kalite filtresi (`BRDF_Albedo_Band_Mandatory_Quality_Band1..7 <= 1`) + **NDSI kar maskesi** ($\text{NDSI} = (\rho_4 - \rho_6)/(\rho_4 + \rho_6) < 0.40$) + **Liang (2001, *RSE* 76:213–238, Eq. 9)** kısa dalga genişbant dönüşüm formülü:
    $$\alpha_{\text{sw}} = 0.160\,\rho_1 + 0.291\,\rho_2 + 0.243\,\rho_3 + 0.116\,\rho_4 + 0.112\,\rho_5 + 0.081\,\rho_7 - 0.0015$$
- Tarih aralığı (Kuzey yazı `2024-07-01..2024-08-31`; `lat < -45°` Güney yazı `2024-01-01..2024-02-28`), QA filtresi ve NDSI kar maskesi `docs/data_sources_earth.md` (§2.5) içine belgelendi.

### [Doğrulama testi ve sonucu]
- `MCD43A3.061` (Black-Sky Shortwave) ve `MCD43A4.061` (Liang 2001 + NDSI < 0.40) karşılaştırması:
  - `earth_askja_holuhraun` (taze bazalt): `MCD43A3 = 0.0278`, `MCD43A4_Liang = 0.0223` (`NDSI = -0.107`)
  - `earth_mauna_loa_hiseas` (taze bazalt): `MCD43A3 = 0.0300`
  - `earth_etna_cisternazza` (taze bazalt/tefra): `MCD43A3 = 0.0439`, `MCD43A4_Liang = 0.0544` (`NDSI = -0.155`)
  - `earth_karacadag_summit` (yaşlı/tozlu bazalt platosu): `MCD43A3 = 0.1291`, `MCD43A4_Liang = 0.1552` (`NDSI = -0.406`)
  - `earth_atacama_yungay` (evaporit): `MCD43A3 = 0.2319`, `MCD43A4_Liang = 0.2436` (`NDSI = -0.338`)
  - `earth_haughton_crater` (darbe breşi): `MCD43A3 = 0.2636`, `MCD43A4_Liang = 0.2632` (`NDSI = +0.031`)
- **Aykırı / Fiziksel Nüanslı Sahalar:**
  - `earth_kilbourne_hole_nm` (`0.1798`), `earth_karacadag_ovabag` (`0.1721`), `earth_hasandagi_kecekalecik` (`0.1701`), `earth_erciyes_kojugedigi` (`0.1656`), `earth_harrat_ash_shaam` (`0.1601`): Holosen taze siyah bazaltlardan (`0.03–0.08`) daha yüksek albedoya sahiptir; çünkü 500 m MODIS pikseli içinde bazalt akıntılarının üzeri açık renkli Kuvaterner lös/kalker tozu, kaliş veya bozunmuş skorya/kuru step örtüsü ile kısmen kaplıdır.
  - `earth_salda_terrace` (`0.1269`): Beyaz hidromanyezit kıyı barları dar (`~100–250 m`) olduğu için 500 m çözünürlüklü `5×5` piksel penceresi koyu renkli ultramafik serpantin/ofiyolit ana kayacı ve kıyı nemini birlikte örneklemektedir.
- **Sonuç:** `tests/test_features_earth.py::test_madde2_albedo_source_and_physical_bounds` -> `PASSED`.

---

## MADDE 3 — `validate_contract.py` Tam Çıktısı ve `"0/4"` MOCK Açıklaması

### [Bulgu]
Önceki özetlerde `"toplam 0/4 satirda en az bir src == MOCK"` ifadesi yer almış ve tam çıktı kesintisiz kaydedilmemişti.

### [Kanıt (komut çıktısı / dosya / satır)]
1. `scripts/validate_contract.py:171-203` incelendiğinde:
   ```python
   n_mock, per_col = count_mock(df, path)
   infos.append(f"{path.name}: toplam {n_mock}/{len(df)} satirda en az bir src == MOCK")
   ```
   Paydadaki `len(df)` parquet dosyasındaki toplam satır sayısıdır. İlk aşamada (Hour 1–4) yalnızca 4 çekirdek saha (`Etna, Atacama, Haughton, Karacadağ`) bulunduğu için çıktı `0/4` idi; 28 sahalık nihai sette `0/28` olarak raporlanmaktadır.
2. `logs/validate_20261114.txt` tam çıktısı (kesintisiz):
   ```text
   BILGI   features_earth.parquet: toplam 0/28 satirda en az bir src == MOCK
   SONUC: GECTI - 0 uyari, 1 bilgi
   ```
3. Tüm `*_src` sütunları için tek tek `MOCK` sayımı (`count_mock`):
   - `slope_mean_src`: `0` (`28/28 "Copernicus_DEM_GLO-30"`)
   - `slope_p90_src`: `0` (`28/28 "Copernicus_DEM_GLO-30"`)
   - `roughness_src`: `0` (`28/28 "Copernicus_DEM_GLO-30"`)
   - `relief_src`: `0` (`28/28 "Copernicus_DEM_GLO-30"`)
   - `temp_amplitude_src`: `0` (`28/28 "MOD11A2.061_annual_mean"`)
   - `thermal_inertia_src`: `0` (`28/28 ""` — v1 kapsamı gereği `NaN`)
   - `albedo_src`: `0` (`28/28 "MCD43A3.061"`)
   - `lithology_src`: `0` (`28/28` hakemli makale/jeoloji haritası atfı)

### [Yapılan düzeltme]
- `logs/validate_20261114.txt` üretildi.
- `tests/test_features_earth.py::test_madde3_no_mock_and_validator_rejects_mock` içine bir satıra `"MOCK"` enjekte edildiğinde `validate(..., fail_on_mock=True)` çağrısının hata (`errors`) ve `fail_on_mock=False` çağrısının uyarı/bilgi ürettiğini doğrulayan birim testi eklendi.

### [Doğrulama testi ve sonucu]
- `tests/test_features_earth.py::test_madde3_no_mock_and_validator_rejects_mock` -> `PASSED`.

---

## MADDE 4 — `lithology_class` Denetimi, `lithology_src` Sütunu ve `lithology_conflicts.csv`

### [Bulgu]
v1 sözleşmesinde niteliksel `lithology_class` sütunu kaba sınıflarla (`basalt`, `evaporite`, `pyroclastic_tuff`, `impact_breccia`, `regolith_permafrost`) tutulmuş; ancak ayrı bir `lithology_src` sütunu parquet'te yer almamış ve ortaç/karışık volkanit veya karbonat içeren bazı sahaların alt-sınıf nüansları ayrı bir tabloda belgelenmemişti.

### [Kanıt (komut çıktısı / dosya / satır)]
- `src/earth/dem_pipeline.py:67-73` ve `440-476`: `features_earth.parquet` içine `lithology_src` sütunu eklendi (28 satırın tamamında hakemli makale/harita kaynağı dolu).
- MTA 1:500.000 Türkiye Jeoloji Haritaları (Kayseri, Konya, Van, Kars, Diyarbakır, İzmir, Denizli paftaları) ve uluslararası literatür taraması sonucunda alt-sınıf nüansı taşıyan sahalar `lithology_conflicts.csv` dosyasına kaydedildi:
  1. `earth_tongariro_rangipo`: mevcut `basalt` $\rightarrow$ önerilen `andesite_basaltic_tephra` (*Donoghue et al., 1995; Hobden et al., 1999*)
  2. `earth_erciyes_kojugedigi`: mevcut `basalt` $\rightarrow$ önerilen `andesite_dacite_basalt` (*MTA 1:500.000 Kayseri Paftası & Şen et al., 2003*)
  3. `earth_hasandagi_kecekalecik`: mevcut `basalt` $\rightarrow$ önerilen `andesite_dacite_basalt` (*MTA 1:500.000 Konya/Kayseri Paftası & Deniel et al., 1998*)
  4. `earth_salda_terrace`: mevcut `evaporite` $\rightarrow$ önerilen `carbonate_hydromagnesite` (*Horgan et al., 2020; Russell et al., 1999*)
  5. `earth_tendurek_shield`: mevcut `basalt` $\rightarrow$ önerilen `basalt_trachyandesite` (*MTA 1:500.000 Van/Kars Paftası & Lebedev et al., 2016*)
  6. `earth_suphan_south_apron`: mevcut `basalt` $\rightarrow$ önerilen `basalt_trachyandesite` (*MTA 1:500.000 Van Paftası & Özdemir et al., 2011*)
  7. `earth_paricutin_lava_field`: mevcut `basalt` $\rightarrow$ önerilen `basaltic_andesite` (*Erlund et al., 2010; Luhr & Simkin, 1993*)

### [Yapılan düzeltme]
- `features_earth.parquet` içine `lithology_src` sütunu eklendi.
- `lithology_conflicts.csv` oluşturuldu.
- **Kullanıcı Onayı İçin Sınıf Genişletme Önerisi (Henüz `lithology_class` Değiştirilmedi):**
  Mevcut 5 sınıfa (`basalt`, `evaporite`, `pyroclastic_tuff`, `impact_breccia`, `regolith_permafrost`) ek olarak şu 3 sınıfın eklenmesi önerilmektedir:
  - `andesite_dacite_basalt` (Erciyes, Hasandağı, Tendürek, Süphan, Parícutin gibi kalk-alkalen/alkalen stratovolkan etekleri için)
  - `andesite_basaltic_tephra` (Tongariro Rangipo gibi volkaniklastik ring-plain tefraları için)
  - `carbonate_hydromagnesite` (Salda Gölü gibi gölsel karbonat/hidromanyezit çökelleri için)

### [Doğrulama testi ve sonucu]
- `tests/test_features_earth.py::test_madde4_lithology_src_and_conflicts_csv` -> `PASSED`.

---

## MADDE 5 — Yüksek Belirsizlikli (`CV > 0.30`) Satırlar ve NDSI Kar Maskesi

### [Bulgu]
28 saha içinde bağıl belirsizliği $\text{CV} = X_{\text{sd}} / X > 0.30$ olan satırların tespit edilmesi, hiçbir satır silinmeden `high_uncertainty` (`bool`) sütunuyla işaretlenmesi ve kutup sahalarında kar/buz maskesi etkisinin raporlanması gerekmektedir.

### [Kanıt (komut çıktısı / dosya / satır)]
1. **`albedo_sd / albedo > 0.30` Olan Sahalar (28 sahada yalnızca 1 saha):**
   - `earth_mcmurdo_wright_valley`: `albedo = 0.1398 ± 0.0961` ($\text{CV}_{\text{alb}} = 0.6873 > 0.30$).
     - **Fiziksel Nedeni ve NDSI Kanıtı:** Wright Valley (`77.52°S`) Güney yazı (`2024-01-01..2024-02-28`) penceresinde `5×5` piksel (`2.3×2.3 km`) pencerenin merkezindeki kar-suz koyu dolerit vadi tabanı (`albedo ~ 0.07–0.09`) ile vadi yamaçlarındaki parçalı kar birikintilerini birlikte içerir. `MCD43A4.061` NDSI analizinde penceredeki 41 geçerli pikselin 19'unda $\text{NDSI} \ge 0.40$ ($\text{NDSI}_{\text{mean}} = +0.434$) tespit edilmiş ve kar maskesiyle elenmiştir.
   - Diğer kutup sahalarında (`earth_haughton_crater`: `albedo = 0.2636 ± 0.0632`, $\text{CV}_{\text{alb}} = 0.2396 \le 0.30$, $\text{NDSI}_{\text{mean}} = +0.031$, `0/24` kar pikseli; `earth_svalbard_bockfjorden`: `albedo = 0.1187 ± 0.0167`, $\text{CV}_{\text{alb}} = 0.1407 \le 0.30$, $\text{NDSI}_{\text{mean}} = -0.113$) Temmuz-Ağustos penceresinde $\text{CV}_{\text{alb}} \le 0.30$'dur.
2. **`temp_amplitude_sd / temp_amplitude > 0.30` Olan Sahalar (19 / 28 saha):**
   `MOD11A2.061_annual_mean` tanımında `temp_amplitude_sd`, 2024 yılındaki 24 kompozit boyunca gündüz-gece sıcaklık farkının **yıllık mevsimsel standart sapmasını** ölçmektedir. Orta ve yüksek enlem sahalarında kışın bulutlu/soğuk günlerde $\Delta T$ düşüp yazın yükseldiği için yıllık $\text{CV}_{\text{temp}} > 0.30$ çıkmaktadır:
   - `earth_mcmurdo_wright_valley` ($\text{CV}_{\text{temp}} = 1.097$), `earth_haughton_crater` ($0.790$), `earth_svalbard_bockfjorden` ($0.618$), `earth_askja_holuhraun` ($0.586$), `earth_craters_of_the_moon` ($0.500$), `earth_etna_cisternazza` ($0.447$), `earth_erciyes_kojugedigi` ($0.424$), `earth_hasandagi_kecekalecik` ($0.415$), `earth_tendurek_shield` ($0.408$), `earth_karacadag_summit` ($0.394$), `earth_kula_divlit` ($0.360$), `earth_deccan_mahabaleshwar` ($0.355$, muson/kuru mevsim farkı), `earth_salda_terrace` ($0.346$), `earth_tuz_golu_south` ($0.343$), `earth_karacadag_ovabag` ($0.341$), `earth_lunar_crater_nevada` ($0.340$), `earth_lanzarote_timanfaya` ($0.338$), `earth_acigol_guneydag` ($0.324$), `earth_cappadocia_kavakkoy` ($0.320$).
   - Buna karşılık yıl boyu güneşli subtropikal/hiperkurak çöllerde (`earth_mauna_loa_hiseas` $0.178$, `earth_atacama_yungay` $0.210$, `earth_pinacate_el_elegante` $0.226$, `earth_harrat_rahat_madinah` $0.229$, `earth_harrat_ash_shaam` $0.234$, `earth_kilbourne_hole_nm` $0.241$, `earth_puna_campo_piedra_pomez` $0.255$, `earth_meteor_crater_arizona` $0.286$, `earth_qaidam_dalangtan` $0.290$) $\text{CV}_{\text{temp}} \le 0.30$ olup `high_uncertainty == False` değerindedir.

### [Yapılan düzeltme]
- `src/earth/dem_pipeline.py:619-629` içinde `high_uncertainty = bool((temp_amplitude_sd / temp_amplitude > 0.30) or (albedo_sd / albedo > 0.30))` hesaplanarak `features_earth.parquet` içine eklendi (0 satır silindi).

### [Doğrulama testi ve sonucu]
- `tests/test_features_earth.py::test_madde5_high_uncertainty_flag` -> `PASSED`.

---

## MADDE 6 — Otomatik Veri Bütünlüğü Testi (`tests/test_features_earth.py`)

### [Bulgu]
Veri sözleşmesi, saha sayıları, fiziksel eşitsizlikler, tablolar arası tutarlılık ve coğrafi koordinat doğruluğunun otomatik olarak denetlenmesi gerekmektedir.

### [Kanıt (komut çıktısı / dosya / satır)]
`pytest tests/test_features_earth.py -v` çıktısı:
```text
tests/test_features_earth.py::test_backup_archive_exists PASSED          [ 14%]
tests/test_features_earth.py::test_madde1_temp_amplitude_consistency PASSED [ 28%]
tests/test_features_earth.py::test_madde2_albedo_source_and_physical_bounds PASSED [ 42%]
tests/test_features_earth.py::test_madde3_no_mock_and_validator_rejects_mock PASSED [ 57%]
tests/test_features_earth.py::test_madde4_lithology_src_and_conflicts_csv PASSED [ 71%]
tests/test_features_earth.py::test_madde5_high_uncertainty_flag PASSED   [ 85%]
tests/test_features_earth.py::test_madde6_site_counts_invariants_and_cross_table_consistency PASSED [100%]
============================== 7 passed in 1.19s ==============================
```

---

## Sütun Bazında Gerçek Veri / MOCK Veri / NaN Özeti (`features_earth.parquet`, 28 Satır × 40 Sütun)

| Sütun Grubu / Adı | Gerçek Veri (Dolu Satır) | MOCK Veri | `NaN` / Boş Satır | Kaynak Etiketi (`_src`) / Açıklama |
|---|---:|---:|---:|---|
| `site_id`, `name`, `body`, `role`, `lat`, `lon`, `radius_m` | **28 / 28** | 0 | 0 | `10 validation` + `18 candidate` (`10 Türkiye + 8 küresel`) |
| `slope_mean`, `slope_mean_sd`, `slope_mean_res_m` | **28 / 28** | 0 | 0 | `Copernicus_DEM_GLO-30` (`30.0 m`, yerel UTM/UPS) |
| `slope_p90`, `slope_p90_sd`, `slope_p90_res_m` | **28 / 28** | 0 | 0 | `Copernicus_DEM_GLO-30` (`30.0 m`, yerel UTM/UPS) |
| `roughness`, `roughness_sd`, `roughness_res_m` | **28 / 28** | 0 | 0 | `Copernicus_DEM_GLO-30` (`30.0 m`, $\sigma_{z,\text{rel}} = 1.0\text{ m}$) |
| `relief`, `relief_sd`, `relief_res_m` | **28 / 28** | 0 | 0 | `Copernicus_DEM_GLO-30` (`30.0 m`, $\sigma_{z,\text{rel}} = 1.0\text{ m}$) |
| `temp_amplitude`, `temp_amplitude_sd`, `temp_amplitude_res_m` | **28 / 28** | 0 | 0 | `MOD11A2.061_annual_mean` (`1000.0 m`, 2024 tam yıl, QA maskeli) |
| `lst_day_mean_k`, `lst_night_mean_k` | **28 / 28** | 0 | 0 | `MOD11A2.061` yıllık ortalama gündüz ve gece yüzey sıcaklığı (K) |
| `thermal_inertia`, `thermal_inertia_sd` | 0 / 28 | 0 | **28 / 28** | `AGENTS.md` §5 kuralı gereği doğrulanmış küresel ürün olmadığı için `NaN` (`_src == ""`) |
| `albedo`, `albedo_sd`, `albedo_res_m` | **28 / 28** | 0 | 0 | `MCD43A3.061` (`500.0 m`, NASA LP DAAC `Albedo_BSA_shortwave`) |
| `lithology_class`, `lithology_src` | **28 / 28** | 0 | 0 | Hakemli literatür ve jeoloji haritası atfı (alt-sınıf önerileri `lithology_conflicts.csv` içinde) |
| `high_uncertainty` | **28 / 28** (`19 True`, `9 False`) | 0 | 0 | `CV_temp > 0.30` veya `CV_alb > 0.30` bayrağı |

---

## Kalan Riskler ve Notlar
1. **`thermal_inertia` Sütunu (`NaN`):** Dünya için doğrudan kalibre edilmiş küresel bir uydu termal eylemsizlik ürünü bulunmadığından `AGENTS.md` §5 ve §6 Kural 2 uyarınca değer uydurulmamış, `NaN` bırakılmıştır.
2. **Yıllık Mevsimsel Varyans (`temp_amplitude_sd`):** Orta/yüksek enlemlerde `temp_amplitude_sd` tek bir günün ölçüm hatasını değil, yıl içindeki yaz-kış genlik değişimini temsil ettiği için `high_uncertainty` bayrağı 19 sahada `True` olmaktadır; skorlama/uygulama katmanında bu bayrak kullanıcıya mevsimsel değişkenlik uyarısı olarak gösterilebilir.
3. **Litoloji Alt-Sınıfları:** `lithology_conflicts.csv` içinde raporlanan 3 yeni alt-sınıf (`andesite_dacite_basalt`, `andesite_basaltic_tephra`, `carbonate_hydromagnesite`) lider onayına sunulmuştur; onaylandığında `lithology_class` sütununa işlenebilir.
