# data_notes.md — Tanım kararları ve NaN gerekçeleri (lider sahipliği)

AGENTS.md §5 gereği: bir özelliğin tanımı bedenler arasında farklıysa, ya da
NaN bırakılıyorsa gerekçesi buraya yazılır. Sözleşmeyi değiştiren hiçbir şey
buraya lider onayı olmadan girmez.

## 1. Tanım kararları (bedenler arası tutarlılık)

| Konu | Karar | Durum |
|---|---|---|
| Eğim hesabı (Earth & Moon) | Earth: yerel metrik CRS (UTM zon; lat>=84 → EPSG:3413, lat<=-80 → EPSG:3031), 30 m native grid (`Copernicus_DEM_GLO30_v2023_1`). Moon: Güney Kutbu Polar Stereografik CRS (`R=1737.4 km`, metre), 5 m native grid (`LRO_LOLA_PGDA_<Site>_5mpp_v2021`). Her ikisinde `np.gradient` → `atan`. Derece tabanlı eğim yasak. **Ölçek sınırı:** Her iki gök cisminde aynı `r = 1000 m` penceresi kullanılsa da `5 m` (Ay) ve `30 m` (Dünya) doğal grid aralığı `slope_mean`, `slope_p90` ve `roughness` değerlerini çözünürlüğe duyarlı kılar; sayısal karşılaştırma yaklaşım/vekil niteliktedir. | Aktif (ölçek farkı belgeli) |
| slope_mean/p90 belirsizliği | Earth: radius içi piksellerin 200 çekiliş uzamsal bootstrap std'si (`1-sigma`). Moon: PGDA ortak-kayıtlı `slperr` (RMS eğim hatası) + 200 çekiliş uzamsal bootstrap birleşimi (`hypot`). | Aktif (p2 & p3 tamamlandı) |
| roughness & relief belirsizliği (`sigma_z_rel`) | Radius içi elevasyona planar fit (`lstsq`) uygulanıp artıkların std'si (`ddof=1`). Earth `roughness_sd` / `relief_sd` için kullanılan `sigma_z_rel = 1.0 m` değeri doğrudan saha içi yersel ölçüm değil, **Airbus/ESA Copernicus DEM Product Handbook (2022, GEO.2018-1988-2, §4.2)** belgesindeki `< 2.0 m` bağıl düşey doğruluk (`LE90` → `1σ ≈ 1.0 m`) ürün spesifikasyonu varsayımıdır. Moon için LOLA 5 m/px bağıl düşey hassasiyeti `sigma_z_rel = 0.50 m` (*Barker et al., 2021*) kullanılmıştır. | Aktif |
| temp_amplitude (Earth & Moon) | Earth: 2024 tam yıl gündüz–gece LST farklarının yıllık ortalaması (`MOD11A2.061_annual_mean`, `DN × 0.02 K`, `1000 m` nominal / `926.6 m` Sinusoidal piksel, `2024-01-01/2024-12-31`, `max_composites=24`; `temp_amplitude_sd` 3×3 piksel + granül birleşik std). Moon (`İNCELENİYOR — LİDER KARARI BEKLİYOR`): mevcut `features_moon.parquet`, LRO Diviner yaz yarım-yılı ürününden (`LRO-L-DLRE-5-PCP-V1.0` / PDS3 etiketinde `DATA_SET_ID = LRO-L-DLRE-5-GCP-V1.0`, `240 m`) alınmış; ancak resmi `.lbl` etiketlerine göre `ltim01` `LRO:DLRE_CLOCTIME = 0.00–0.25 saat` (gece yarısı dilimi), `ltim49` `12.00–12.25 saat` (öğle) ve `ltim73` `18.00–18.25 saat` (akşamüstü) olup mevcut kod ilk 4 Ay sahasında yalnızca `ltim01` içinde `r = 1000 m` uzamsal `max − min` (`113.80–131.93 K`), `moon_faustini_rim` (`+90°E`) içinse `ltim01` (`63.79 K`) ve `ltim73` (`214.99 K`) birleşimi (`151.21 K`) üretmiştir. **Bilimsel engel:** Tek bir `ltim` dilimindeki uzamsal fark bir günlük zaman döngüsü genliği değildir (`AGENTS.md` §5 tanımıyla uyuşmaz) ve Dünya'nın yıllık ortalama gündüz–gece farkıyla aynı fiziksel tanımlı değildir. P2 tam `ltim` doğrulamasını tamamlayıp yeniden hesaplama veya `NaN` yapma kararı verilene kadar mevcut `thermal` ve genel skorlar kesin/doğrulanmış karşılaştırma sayılamaz. | Geçici engel (P2 doğrulama & lider kararı bekleniyor) |
| albedo (Broadband uyumu) | Earth: `MCD43A3.061` shortwave (`Albedo_BSA_shortwave`, DN × 0.001, 500 m Sinusoidal grid). Moon: `LRO-L-LOLA-4-GDR-V1.0:LDAM_50S_1000M_V1.0` 1064 nm sıfır-faz (`α=0°`) normal albedosu, standart Ay faz integrali / opposition surge katsayısı **`× 0.38`** (*Vasavada et al., 2012, JGR; Hayne et al., 2017, JGR*) ile çarpılarak Dünya ile aynı fiziksel tanıma (**broadband solar hemispherical albedo**, `_src = ..._broadband_eq`, 1000 m) dönüştürüldü. | Aktif (p2 & p3 tamamlandı) |
| Benzerlik mesafesi | Her özellikte aday–referans farkı, Earth aday havuzu + referansın nüfus standart sapmasına bölünür. Eksen uzaklığı `D = sqrt(mean(z_diff²))`, benzerlik indeksi `exp(-D)`; bileşen z değerleri kırpılmaz. `axis_gaps.z_diff` ile skor aynı farkı kullanır. | Aktif |
| Skor yorumlama | İndeks `[0, 1]` aralığındadır; olasılık ya da kalibre edilmiş yüzde değildir. Standartlaştırma havuzu ve `exp(-D)` dönüşümü yöntem varsayımlarıdır. Aday havuzunun bileşimi değişirse ölçek ve sıralama da değişebilir. | Arayüz ve raporda açıklanır |
| Belirsizlik yayılımı | Her aday ve referansın kendi `_sd` değeriyle, aday, referans, özellik ve eksen hatalarının bağımsız Normal dağıldığı varsayımı altında 200 Monte Carlo çekilişi. Standartlaştırma havuzunun ortalama/std'si çekilişler boyunca sabit tutulur. Eksen ve ağırlıklı toplam için aynı çekilişlerden q05/q95 hesaplanır; nokta tahminini aralığa zorla dahil etme yoktur. Bu bir bootstrap veya güven aralığı değildir; özellikler arası kovaryans modellenmez. | Aktif |
| Bilinmeyen `_sd` | Skorlanabilir bir özellikte aday veya referans `_sd` değeri `NaN` ise nokta skoru hesaplanır, o eksenin belirsizlik yüzdelikleri verilmez. Pozitif ağırlıklı herhangi bir eksenin çekilişleri eksikse toplam skor aralığı da verilmez; bilinmeyen SD sıfır varsayılmaz. Negatif veya sonsuz SD veri hatası olarak açıkça reddedilir. | Aktif |
| Aralık gösterimi (yalnız arayüz) | q05/q95 ham yüzdecilikler olarak saklanır; nokta tahmini aralığın dışına çıkabilir (meşru yayılım sonucu). Arayüzde bu görüntü hata gibi okunabildiğinden **gösterilen** aralık `scoring.display.expanded_interval` ile nokta indeksini kapsayacak şekilde genişletilir; skorlanan değerler değişmez. Çapraz doğrulama: parquet + belgelenen formülle elle yeniden hesap (5 referans × 40 aday × 3 eksen = 600 kontrol ve 200 ağırlıklı toplam) → sapma 0. | Aktif |
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
- Blind ranking ekranı **bağımsız holdout doğrulaması değildir**; rol
  etiketlerinden habersiz bir **betimsel tanılamadır**. Skorlayıcı `role`
  sütununu görmese de 40 Earth satırının (10 doğrulama + 30 aday) tamamı
  Z-skor ölçeklemesinin ortalama/std hesabına katılır. Ayrıca bu ekran tüm
  30 saha×eksen çiftini eşit derecede beklenen analog kabul etmez; başarı
  iddiası için sonuçlar görülmeden önce kaynaklandırılmış beklenen saha–eksen
  çiftleri ve gerekçeleri tanımlanmalıdır; validation sıralamasına bakarak
  formül ayarlanmaz.
- **Ay `temp_amplitude` tanım engeli (açık engel):** Mevcut
  `features_moon.parquet` içindeki `temp_amplitude` değerleri ilk 4 sahada
  yalnızca `ltim01` içindeki `r = 1000 m` uzamsal `max − min` farkını,
  Faustini'de ise iki dilim (`ltim01` + `ltim73`) farkını yansıtmaktadır; bu,
  `AGENTS.md` §5'teki günlük zaman döngüsü genliği (`diurnal cycle`) tanımıyla
  ve Dünya `MOD11A2.061` yıllık ortalama gün–gece ΔT tanımıyla uyuşmamaktadır.
  P2 tam `ltim` doğrulaması yapılıp lider tarafından yeniden hesaplama veya
  `NaN` kararı verilene kadar `thermal` ve ağırlıklı genel skorlar bilimsel
  olarak "Ay'a en yakın saha" şeklinde yorumlanmamalıdır.
- **Çözünürlük ve ölçek sınırı:** Topoğrafya ekseninde Ay DEM'i (`5 m/px`, LOLA
  PGDA) ile Dünya DEM'i (`30 m/px`, Copernicus GLO-30) aynı `r = 1000 m`
  yarıçapı içinde izlense de farklı doğal piksel boyutları taşır; `MODIS`
  `1000 m` ve `500 m` ürünleri alt-kilometrik yerel yama farklılıklarını
  doğrudan çözmez.
- **Portföy kapsam eşiği (`0.70`):** `select_portfolio`, mevcut v1'deki
  `<= 3` eksen için seçilen eşikte kapsanan eksen sayısını maksimize ederek
  en küçük saha kümesini verir (daha fazla eksende açgözlü sezgiseldir).
  Ancak varsayılan `0.70` eşiği kalibre edilmiş olasılık veya fiziksel
  yeterlilik sınırı değil yalnızca bir benzerlik indeksi ayarıdır; "minimal"
  küme tanımı yalnızca bu eşik ve skorlama varsayımları altında geçerlidir.

## 3. Bilinen bozulma alanları (breakdown kartı için)

Dünya hiçbir sahada şunları analog etmez (kartta sayılacak): yerçekimi
(1.62 / 3.71 m/s²), vakum (Ay) / 6-7 mbar CO₂ (Mars), radyasyon (atmosfer
yok/atmosfer ince), Ay kutbu termal çevrim hızı. Bunlar sayısal skorun
DIŞINDA, ayrı kart olarak sunulur (AGENTS.md §8 madde 2).
