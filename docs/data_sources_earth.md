# Earth Veri Kaynakları Tablosu (Person 3 — `p3-earth`)

Bu belge, `AGENTS.md` (§5 Veri Sözleşmesi ve §6 Kurallar) uyarınca Dünya (`body == "earth"`) doğrulama ve aday sahaları için kullanılan veri setlerinin **NASA CMR API**, **AWS Open Data** ve **Microsoft Planetary Computer STAC API** üzerinden doğrulanmış tam ürün adlarını, versiyonlarını, yerel çözünürlüklerini (`X_res_m`) ve erişim yollarını içerir.

---

## 1. Özet Veri Kaynakları Tablosu

| Özellik (`X`) | Rol / Öncelik | Tam Ürün Adı (Doğrulanmış) | Kısa Kod & Versiyon (`X_src`) | Yerel Çözünürlük (`X_res_m`) | Birim & Ölçek Çarpanı | Kapsam | Erişim Yolu (Doğrulanmış) | Durum / Notlar |
|---|---|---|---|---|---|---|---|---|
| `slope_mean`, `slope_p90`, `roughness`, `relief` | **Birincil DEM** | **Copernicus DEM - Global and European Digital Elevation Model (COP-DEM GLO-30 DGED)** | `Copernicus_DEM_GLO-30_2023.1` (`TODO(verify)` alt sürüm etiketi; AWS COG koleksiyonu `cop-dem-glo-30`) | `30.0` (1 arc-second; ekvatorda ~30 m) | Metre (m) → Eğim için yerel UTM/UPS projeksiyonda derece (°) | Küresel (90°N – 90°S; **Haughton 75.37°N dahil**) | 1) **AWS S3 (Public COG, Auth gerekmez):** `https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_{N/S}{lat}_00_{E/W}{lon}_00_DEM/Copernicus_DSM_COG_10_{N/S}{lat}_00_{E/W}{lon}_00_DEM.tif`<br>2) **Planetary Computer STAC:** `cop-dem-glo-30` | **Doğrulandı (HTTP 200).** Küresel kapsamı nedeniyle ana DEM kaynağıdır. |
| `slope_mean`, `slope_p90`, `roughness`, `relief` | **Alternatif DEM** | **NASADEM Merged DEM Global 1 arc second V001** (NASA CMR ID: `C2763264762-LPCLOUD`) | `NASADEM_HGT_v001` | `30.0` (1 arc-second) | Metre (m) | 60°N – 56°S (**Haughton Krateri'ni kapsamaz**) | 1) **Planetary Computer STAC:** `nasadem`<br>2) **NASA LP DAAC / Earthdata:** `https://doi.org/10.5067/MEaSUREs/NASADEM/NASADEM_HGT.001` | **Doğrulandı.** 60°N üstü kutup sahalarını kapsamadığı için yedek/doğrulama amaçlıdır. |
| `temp_amplitude` | **Birincil LST (8-Günlük Kompozit)** | **MODIS/Terra Land Surface Temperature/Emissivity 8-Day L3 Global 1km SIN Grid V061** (NASA CMR ID: `C2269056084-LPCLOUD`) | `MOD11A2.061` (Yıllık ortalama ise `MOD11A2.061_annual_mean` olarak belirtilir) | `1000.0` (Nominal 1 km; gerçek Sinusoidal piksel: `926.625 m`) | Kelvin ($\text{DN} \times 0.02\text{ K}$); $\Delta T = \text{LST\_Day\_1km} - \text{LST\_Night\_1km}$ | Küresel | 1) **Planetary Computer STAC (COG):** `modis-11A2-061`<br>2) **NASA LP DAAC / Earthdata Cloud:** `s3://lp-prod-protected/MOD11A2.061` | **Doğrulandı.** Bulut boşluklarını azaltmak için 8-günlük kompozit veya yıllık çevrim ortalaması kullanılır. |
| `temp_amplitude` | **Alternatif LST (Günlük)** | **MODIS/Terra (veya Aqua) Land Surface Temperature/Emissivity Daily L3 Global 1km SIN Grid V061** (`C1748058432-LPCLOUD` / `C1748046084-LPCLOUD`) | `MOD11A1.061` / `MYD11A1.061` | `1000.0` (Gerçek Sinusoidal: `926.625 m`) | Kelvin ($\text{DN} \times 0.02\text{ K}$) | Küresel | 1) **Planetary Computer STAC (COG):** `modis-11A1-061`<br>2) **NASA LP DAAC / AppEEARS** | **Doğrulandı.** Bulutsuz tekil gün analizleri için uygundur. |
| `albedo` | **Birincil Albedo** | **MODIS/Terra+Aqua BRDF/Albedo Albedo Daily L3 Global - 500m V061** (NASA CMR ID: `C2278860820-LPCLOUD`) | `MCD43A3.061` | `500.0` (Nominal 500 m; gerçek Sinusoidal piksel: `463.313 m`) | Boyutsuz `0`–`1` ($\text{DN} \times 0.001$); Band: `Albedo_BSA_shortwave` / `Albedo_WSA_shortwave` | Küresel | 1) **NASA LP DAAC / Earthdata (`EARTHDATA_TOKEN` gerekir):** `s3://lp-prod-protected/MCD43A3.061`<br>2) **AppEEARS / LAADS DAAC API** (`TODO(verify)`: Auth gerektirmeyen STAC COG yansısı kontrol edilecek; PC'de yalnızca `modis-43A4-061` NBAR mevcut) | **Ürün adı & versiyon NASA CMR'da doğrulandı.** İndirme için Earthdata token veya GEE/AppEEARS erişimi `TODO(verify)`. |
| `thermal_inertia` | **Termal Eylemsizlik** | Doğrudan standart küresel uydu ürünü yok (`TODO(verify)`) | Boş (`""`) — hesaplanana kadar `NaN` | `NaN` (Eğer MODIS ATI türetilirse `1000.0`) | $\text{J m}^{-2}\text{ K}^{-1}\text{ s}^{-1/2}$ | — | `TODO(verify)`: MODIS LST + Albedo üzerinden Apparent Thermal Inertia (ATI) veya literatür kalibrasyonu (`docs/data_notes.md`'de lider onayı gerekir) | **Sözleşme Kuralı:** Doğrulanmış fiziksel birim dönüşümü olmadan sayı uydurulmaz; v1'de `NaN` bırakılır. |

---

## 2. Kritik Sözleşme Kuralları (§5)

1. **Çözünürlük Dürüstlüğü (`X_res_m`):**
   - `~1 km` çözünürlüklü MODIS LST ürünleri (`MOD11A1.061`, `MOD11A2.061`) **500 m'lik bir sahayı çözemez**.
   - `radius_m = 1000.0` (1 km yarıçap = 2 km çap) kullanıldığında dahi bir sahaya yalnızca birkaç MODIS LST pikseli düşer.
   - Bu nedenle `temp_amplitude_res_m` kolonuna her zaman **`1000.0`** (veya tam `926.6`), `albedo_res_m` kolonuna **`500.0`**, Copernicus DEM türevlerine (`slope_mean_res_m`, `slope_p90_res_m`, `roughness_res_m`, `relief_res_m`) **`30.0`** yazılır. Kaba çözünürlüklü veri asla ince çözünürlüklü gibi yeniden örneklenip küçük `_res_m` ile sunulamaz.
2. **Projeksiyon Zorunluluğu:**
   - DEM verisi coğrafi koordinatlarda (`EPSG:4326`, derece) gelir. Eğim (`slope_mean`, `slope_p90`), pürüzlülük (`roughness`) ve rölyef (`relief`) hesaplanmadan **önce** saha merkezine uygun yerel **UTM zonu** (veya kutup bölgeleri için **UPS / Polar Stereographic**) metre tabanlı CRS'e (`bilinear` / `cubic`重örnekleme ile) projekte edilir. Derece birimi üzerinden eğim hesaplamak kesinlikle yasaktır.
3. **Belirsizlik (`X_sd`) ve Eksik Değerler:**
   - Henüz hesaplanmayan özellikler `NaN`, belirsizlikleri `X_sd = NaN`, kaynakları `X_src = ""` (boş string) olarak bırakılır (`0` placeholder olarak kullanılamaz, `MOCK` yazılamaz).
   - Eğim belirsizliği (`slope_mean_sd`, `slope_p90_sd`) için yerel pencere içi bootstrap / piksel yayılımı veya DEM düşey hata yayılımı (`TODO(verify)`: liderin `src/scoring/` metodolojisi ile uyumlu 1-sigma tanımı `docs/data_notes.md`'ye işlenecek; şimdilik doğrulanmamışsa `NaN` bırakılır).

