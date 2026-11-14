# data_notes.md — Tanım kararları ve NaN gerekçeleri (lider sahipliği)

AGENTS.md §5 gereği: bir özelliğin tanımı bedenler arasında farklıysa, ya da
NaN bırakılıyorsa gerekçesi buraya yazılır. Sözleşmeyi değiştiren hiçbir şey
buraya lider onayı olmadan girmez.

## 1. Tanım kararları (bedenler arası tutarlılık)

| Konu | Karar | Durum |
|---|---|---|
| Eğim hesabı (Earth & Moon) | Earth: yerel metrik CRS (UTM zon; lat>=84 → EPSG:3413, lat<=-80 → EPSG:3031), 30 m native grid (`Copernicus_DEM_GLO30_v2023_1`). Moon: Güney Kutbu Polar Stereografik CRS (`R=1737.4 km`, metre), 5 m native grid (`LRO_LOLA_PGDA_<Site>_5mpp_v2021`). Her ikisinde `np.gradient` → `atan`. Derece tabanlı eğim yasak. | Aktif (p2 & p3 tamamlandı) |
| slope_mean/p90 belirsizliği | Earth: radius içi piksellerin 200 çekiliş uzamsal bootstrap std'si (`1-sigma`). Moon: PGDA ortak-kayıtlı `slperr` (RMS eğim hatası) + 200 çekiliş uzamsal bootstrap birleşimi (`hypot`). | Aktif (p2 & p3 tamamlandı) |
| roughness & relief belirsizliği (`sigma_z_rel`) | Radius içi elevasyona planar fit (`lstsq`) uygulanıp artıkların std'si (`ddof=1`). Earth `roughness_sd` / `relief_sd` için kullanılan `sigma_z_rel = 1.0 m` değeri doğrudan saha içi yersel ölçüm değil, **Airbus/ESA Copernicus DEM Product Handbook (2022, GEO.2018-1988-2, §4.2)** belgesindeki `< 2.0 m` bağıl düşey doğruluk (`LE90` → `1σ ≈ 1.0 m`) ürün spesifikasyonu varsayımıdır. Moon için LOLA 5 m/px bağıl düşey hassasiyeti `sigma_z_rel = 0.50 m` (*Barker et al., 2021*) kullanılmıştır. | Aktif |
| temp_amplitude (Earth & Moon) | Earth: Gündüz-gece LST farkı (`MOD11A2.061_annual_mean`, DN × 0.02 K, 1000 m, `2024-01-01/2024-12-31` tam yıl `max_composites=24`; `temp_amplitude_sd` 3×3 piksel + granül birleşik std). Moon: Diviner L3 bolometrik yüzey sıcaklığı (`LRO-L-DLRE-5-PCP-V1.0:pcp_avg_tbol_pols_240m_v2022`, 240 m) yerel öğle (`ltim01`) eksi gece yarısı (`ltim73`) farkı. | Aktif (p2 & p3 tamamlandı) |
| albedo (Broadband uyumu) | Earth: `MCD43A3.061` shortwave (`Albedo_BSA_shortwave`, DN × 0.001, 500 m Sinusoidal grid). Moon: `LRO-L-LOLA-4-GDR-V1.0:LDAM_50S_1000M_V1.0` 1064 nm sıfır-faz (`α=0°`) normal albedosu, standart Ay faz integrali / opposition surge katsayısı **`× 0.38`** (*Vasavada et al., 2012, JGR; Hayne et al., 2017, JGR*) ile çarpılarak Dünya ile aynı fiziksel tanıma (**broadband solar hemispherical albedo**, `_src = ..._broadband_eq`, 1000 m) dönüştürüldü. | Aktif (p2 & p3 tamamlandı) |
| Benzerlik mesafesi | Her özellikte aday–referans farkı, Earth aday havuzu + referansın nüfus standart sapmasına bölünür. Eksen uzaklığı `D = sqrt(mean(z_diff²))`, benzerlik indeksi `exp(-D)`; bileşen z değerleri kırpılmaz. `axis_gaps.z_diff` ile skor aynı farkı kullanır. | Aktif |
| Skor yorumlama | İndeks `[0, 1]` aralığındadır; olasılık ya da kalibre edilmiş yüzde değildir. Standartlaştırma havuzu ve `exp(-D)` dönüşümü yöntem varsayımlarıdır. Aday havuzunun bileşimi değişirse ölçek ve sıralama da değişebilir. | Arayüz ve raporda açıklanır |
| Belirsizlik yayılımı | Her aday ve referansın kendi `_sd` değeriyle, aday, referans, özellik ve eksen hatalarının bağımsız Normal dağıldığı varsayımı altında 200 Monte Carlo çekilişi. Standartlaştırma havuzunun ortalama/std'si çekilişler boyunca sabit tutulur. Eksen ve ağırlıklı toplam için aynı çekilişlerden q05/q95 hesaplanır; nokta tahminini aralığa zorla dahil etme yoktur. Bu bir bootstrap veya güven aralığı değildir; özellikler arası kovaryans modellenmez. | Aktif |
| Bilinmeyen `_sd` | Skorlanabilir bir özellikte aday veya referans `_sd` değeri `NaN` ise nokta skoru hesaplanır, o eksenin belirsizlik yüzdelikleri verilmez. Pozitif ağırlıklı herhangi bir eksenin çekilişleri eksikse toplam skor aralığı da verilmez; bilinmeyen SD sıfır varsayılmaz. Negatif veya sonsuz SD veri hatası olarak açıkça reddedilir. | Aktif |
| thermal_inertia (Moon & Earth) | Her iki gök cisminde de aynı ölçekte doğrudan kalibre edilmiş küresel ürün bulunmadığından `AGENTS.md` §5 gereği değer uydurulmamış, `NaN` (`_src = ""`) bırakılmıştır. | Onaysız sayı yasak → `NaN` |

## 1b. Site koordinat görsel teyidi (AGENTS.md §5 kural 2)

- Earth sahaları (28 sahalık çekirdek set ve 40 sahalık genişletilmiş aday havuzu) ile 5 Ay Güney Kutbu referans sahasının (`moon_shackleton_rim`, `moon_connecting_ridge`, `moon_de_gerlache_rim`, `moon_shackleton_peak`, `moon_faustini_rim`) koordinatları uydu/harita önizlemeleri (NASA Worldview, Esri World Imagery ve USGS Astrogeology LRO WAC / LOLA WMS) üzerinde kontrol edildi.

## 2. NaN gerekçeleri ve Tamamlanan Özellikler (hiçbir 0 yer tutucu kullanılmıyor)

- **Tamamlanan Gerçek Özellikler (`0 NaN`):** Hem `data/processed/features_moon.parquet` (Ay Güney Kutbu referans sahaları) hem `data/processed/features_earth.parquet` içinde `slope_mean`, `slope_p90`, `roughness`, `relief`, `temp_amplitude` ve `albedo` sütunları (`_sd`, `_src`, `_res_m` dahil) eksiksiz olarak gerçek yörünge verilerinden doldurulmuştur.
- **Moon & Earth `thermal_inertia` (`NaN`):** Doğrudan kalibre edilmiş ortak ölçekli küresel ürün bulunmadığı için `thermal_inertia` ve `thermal_inertia_sd` bilinçli olarak `NaN`, `thermal_inertia_src = ""` bırakılmıştır (`thermal_inertia_res_m` Moon için `240.0 m`, Earth için `1000.0 m`).

## 2b. Skor ve doğrulama sınırları

- Mevcut Ay referansları ile Dünya sahalarının karşılaştırması, yöntemce
  tanımlı bir benzerlik sıralamasıdır; skorlar olasılık veya fiziksel
  eşdeğerlik iddiası değildir. Mission preset ağırlıkları da ölçülmüş
  ekipman toleransları değil, açıkça belirtilmiş kullanım varsayımlarıdır.
- Mevcut veri setinde `thermal_inertia` tüm Moon ve Earth satırlarında
  eksiktir. Thermal ekseni bu nedenle yalnızca `temp_amplitude` özelliğiyle
  skorlanır; eşleştirilmiş inertia ürünü gelmeden tam termal analoji iddiası
  yapılamaz.
- Blind ranking ekranı her `validation` sahasını her eksenle karşılaştıran
  betimsel tanılamadır. Bu tüm 30 saha×eksen çiftini eşit derecede beklenen
  analog kabul etmez. Başarı oranı iddiası için sonuçlar görülmeden önce
  kaynaklandırılmış beklenen saha–eksen çiftleri tanımlanmalıdır; validation
  sıralamasına bakarak formül ayarlanmaz.

## 3. Bilinen bozulma alanları (breakdown kartı için)

Dünya hiçbir sahada şunları analog etmez (kartta sayılacak): yerçekimi
(1.62 / 3.71 m/s²), vakum (Ay) / 6-7 mbar CO₂ (Mars), radyasyon (atmosfer
yok/atmosfer ince), Ay kutbu termal çevrim hızı. Bunlar sayısal skorun
DIŞINDA, ayrı kart olarak sunulur (AGENTS.md §8 madde 2).
