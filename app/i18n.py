"""Central UI strings for app/main.py — Turkish (default) + English.

Every user-visible string lives here so main.py stays free of hardcoded
copy. Data-contract codes (site_id, slope_mean, ...) may appear only
inside parentheses as technical hints; sentences must be understandable
without them.
"""
from __future__ import annotations

DEFAULT_LANG = "tr"

# The language switch itself is shown before a language is chosen.
LANGUAGE_LABEL = "Dil / Language"

LANG_OPTIONS: dict[str, str] = {"tr": "Türkçe", "en": "English"}

# Clean Moon South Pole reference site names (no internal ROI/LM7 codes on screen).
MOON_SITE_LABELS: dict[str, dict[str, str]] = {
    "moon_shackleton_rim": {
        "tr": "Shackleton Krateri Kenarı",
        "en": "Shackleton Crater Rim",
    },
    "moon_connecting_ridge": {
        "tr": "Shackleton–de Gerlache Bağlantı Sırtı",
        "en": "Shackleton–de Gerlache Connecting Ridge",
    },
    "moon_de_gerlache_rim": {
        "tr": "de Gerlache Krateri Kenarı",
        "en": "de Gerlache Crater Rim",
    },
    "moon_shackleton_peak": {
        "tr": "Shackleton Yakını Zirve",
        "en": "Peak Near Shackleton",
    },
    "moon_faustini_rim": {
        "tr": "Faustini Krateri Kenarı",
        "en": "Faustini Crater Rim",
    },
}

TEXTS: dict[str, dict[str, str]] = {
    # ── shell ────────────────────────────────────────────────────────────────
    "data_missing": {
        "tr": "{stem}.parquet dosyası data/processed/ klasöründe bulunamadı.",
        "en": "Cannot find {stem}.parquet in data/processed/.",
    },
    "app_title": {
        "tr": "🌕 Ay ↔ Dünya Benzer Koşullar Analizi",
        "en": "🌕 Moon ↔ Earth Similar-Conditions Analysis",
    },
    "app_badge": {
        "tr": "Ay Güney Kutbu (5 referans bölge) · 40 Dünya sahası · 2 aktif sayısal eksen (Mobilite + Yüzey) · Termal v1'de askıda (NaN)",
        "en": "Lunar South Pole (5 reference regions) · 40 Earth sites · 2 active numeric axes (Mobility + Surface) · Thermal suspended in v1 (NaN)",
    },
    "subtitle": {
        "tr": ("Bu uygulama Ay Güney Kutbu'nda seçilen bir referans bölgeyi Dünya "
               "üzerindeki {n} sahayla karşılaştırır. v1 sürümünde sayısal "
               "karşılaştırma **iki aktif eksen** üzerinden çalışır: **Mobilite** "
               "(eğim, pürüzlülük, rölyef) ve **Yüzey** (geniş bant albedo / parlaklık). "
               "**Termal** ekseni (`temp_amplitude` ve `thermal_inertia`) `Karar #30` "
               "uyarınca v1'de askıdadır (`NaN`). Her saha 0 ile 1 arasında bir "
               "benzerlik indeksi alır; bu indeks bir olasılık veya kalibre edilmiş "
               "fiziksel eşdeğerlik yüzdesi değildir."),
        "en": ("This application compares a selected Lunar South Pole reference "
               "region against {n} Earth sites. In v1, numeric scoring operates on "
               "**two active axes**: **Mobility** (slope, roughness, relief) and "
               "**Surface** (broadband albedo / brightness). The **Thermal** axis "
               "(`temp_amplitude` and `thermal_inertia`) is suspended (`NaN`) in v1 "
               "under Decision #30. Each Earth site receives a similarity index "
               "between 0 and 1; this index is neither a probability nor a "
               "calibrated physical equivalence percentage."),
    },
    "thermal_note": {
        "tr": ("ℹ️ **Termal Eksen Durumu (Karar #30 — Askıda / `NaN`):** Ay LRO Diviner "
               "kutup yerel saat dilimi (`ltim`) ölçümleri ile Dünya `MOD11A2.061` "
               "yıllık ortalama gündüz–gece yüzey sıcaklık farkı aynı fiziksel günlük "
               "döngü (`diurnal cycle`) tanımına oturtulamadığından ve eş ölçekli "
               "küresel `thermal_inertia` ürünü bulunmadığından Ay tarafında "
               "`temp_amplitude = NaN` ve her iki gök cisminde `thermal_inertia = NaN` "
               "bırakılmıştır. v1 genel ve eksen skorları **Mobilite + Yüzey** "
               "üzerinden hesaplanır; teknik sınırlar `Analojinin Sınırları` sekmesindedir."),
        "en": ("ℹ️ **Thermal Axis Status (Decision #30 — Suspended / `NaN`):** Because "
               "lunar LRO Diviner polar local-time (`ltim`) slices and Earth "
               "`MOD11A2.061` annual-mean day–night LST differences cannot be placed "
               "on an equivalent physical diurnal-cycle definition, and no uniform "
               "global `thermal_inertia` product exists at matching scale, Moon "
               "`temp_amplitude = NaN` and both bodies' `thermal_inertia = NaN`. "
               "v1 overall and per-axis scores run on **Mobility + Surface**; see "
               "`Limits of the Analogy` for full technical details."),
    },
    "table_thermal_note": {
        "tr": ("Termal sütunu (`Karar #30` kapsamında Ay `temp_amplitude = NaN` ve "
               "`thermal_inertia = NaN` olarak askıya alındığı için) bu tabloda "
               "gösterilmemektedir. Tablodaki Genel skor **2 aktif sayısal eksen "
               "(Mobilite + Yüzey)** üzerinden hesaplanır (ayrıntı: `Analojinin Sınırları`)."),
        "en": ("The Thermal column is omitted from this table because the Thermal "
               "axis is suspended in v1 under Decision #30 (Moon `temp_amplitude = NaN` "
               "and `thermal_inertia = NaN`). The Overall score is computed across the "
               "**2 active numeric axes (Mobility + Surface)** (see `Limits of the Analogy`)."),
    },
    "table_widened_note": {
        "tr": ("📐 **Gösterilen aralık notu (`expanded_interval`):** Nokta benzerlik "
               "indeksinin ham Monte Carlo `q05–q95` yüzdelik aralığının dışına düştüğü "
               "hücrelerde (`*` ile işaretli), ekranda hata gibi okunmaması için yalnızca "
               "**gösterilen** aralık nokta değerini kapsayacak biçimde genişletilmiştir; "
               "arka plandaki skor ve yüzdelik değerleri değiştirilmez (`docs/data_notes.md §1`)."),
        "en": ("📐 **Displayed interval note (`expanded_interval`):** Where the point "
               "similarity index falls outside the raw Monte Carlo `q05–q95` percentile "
               "bounds (marked with `*`), only the **displayed** interval is widened to "
               "contain the point estimate so it does not read as a display bug; "
               "underlying scored values and percentiles are never altered (`docs/data_notes.md §1`)."),
    },
    # ── sidebar ──────────────────────────────────────────────────────────────
    "settings_header": {"tr": "⚙️ Ayarlar", "en": "⚙️ Settings"},
    "body_moon": {"tr": "Ay", "en": "Moon"},
    "ref_site_label_moon": {
        "tr": "Ay Referansı",
        "en": "Moon Reference",
    },
    "ref_site_caption": {
        "tr": "Enlem {lat}°, Boylam {lon}° · Zemin: {lith}",
        "en": "Latitude {lat}°, Longitude {lon}° · Ground: {lith}",
    },
    "ref_site_tooltip": {
        "tr": "Sahanın veri sözleşmesi kodu: {site_id}",
        "en": "Data-contract site code: {site_id}",
    },
    "mission_label": {
        "tr": "Görev / kullanım amacı",
        "en": "Mission / use case",
    },
    "mission_default": {
        "tr": "Dengeli (aktif eksenler eşit ağırlıkta)",
        "en": "Balanced (active criteria equal)",
    },
    "mission_rover_mobility": {
        "tr": "Gezgin araç arazi testi (Mobilite ağırlıklı)",
        "en": "Rover mobility test (Mobility-weighted)",
    },
    "mission_isru_ice": {
        "tr": "Termal ağırlıklı senaryo (buz verisi içermez)",
        "en": "Thermal-weighted scenario (no ice data)",
    },
    "mission_radar_calibration": {
        "tr": "Yer altı radar kalibrasyonu (Mobilite + Yüzey ağırlıklı)",
        "en": "Subsurface radar calibration (Mobility + Surface weighted)",
    },
    "top_n_label": {
        "tr": "Gösterilecek Dünya sahası sayısı",
        "en": "Number of Earth sites to show",
    },
    # ── reference measurements ───────────────────────────────────────────────
    "ref_subheader": {
        "tr": "📍 Ay Referansı: {name} ({body})",
        "en": "📍 Moon Reference: {name} ({body})",
    },
    "ref_expander": {
        "tr": "Referans sahanın yörünge ölçümleri",
        "en": "Orbital measurements of the reference site",
    },
    "ref_col_feature": {"tr": "Ölçüt", "en": "Criterion"},
    "ref_col_value": {"tr": "Değer", "en": "Value"},
    "ref_col_unit": {"tr": "Birim", "en": "Unit"},
    "ref_col_sd": {"tr": "Belirsizlik (±1σ)", "en": "Uncertainty (±1σ)"},
    "ref_col_res": {"tr": "Çözünürlük (m)", "en": "Resolution (m)"},
    "ref_col_src": {"tr": "Kaynak", "en": "Source"},
    "ref_table_caption": {
        "tr": ("Değer: r = 1000 m analiz penceresinde ölçülen değer. Belirsizlik (±1σ): "
               "ölçüm / bootstrap standart sapması. Çözünürlük (m): verinin doğal piksel "
               "boyutu (`5 m` LOLA DEM, `1000 m` LOLA geniş bant eşdeğeri albedo). "
               "Kaynak: veriyi üreten uzay aracı ve veri ürünü."),
        "en": ("Value: measurement within the r = 1000 m analysis window. Uncertainty (±1σ): "
               "instrument / bootstrap standard deviation. Resolution (m): native pixel size "
               "(`5 m` LOLA DEM, `1000 m` LOLA broadband-equivalent albedo). "
               "Source: spacecraft and dataset version."),
    },
    "temp_note": {
        "tr": ("Not (`Karar #30`): Ay referanslarında `temp_amplitude` ve `thermal_inertia` "
               "değerleri, Dünya `MOD11A2.061` yıllık ortalama gündüz–gece ΔT tanımıyla "
               "birebir eşdeğer günlük döngü kurulamadığından v1'de `NaN` (askıda) "
               "bırakılmıştır (`_res_m = 240 m` veri sözleşmesi gereği korunur)."),
        "en": ("Note (`Decision #30`): On Moon references, `temp_amplitude` and "
               "`thermal_inertia` are left `NaN` (suspended) in v1 because an equivalent "
               "diurnal-cycle definition with Earth `MOD11A2.061` annual mean day–night ΔT "
               "is not established (`_res_m = 240 m` is retained per data contract)."),
    },
    # ── tabs ─────────────────────────────────────────────────────────────────
    "tab_map": {"tr": "🗺️ Harita", "en": "🗺️ Map"},
    "tab_radar": {
        "tr": "📊 Görsel Karşılaştırma & Eksenler",
        "en": "📊 Visual Comparison & Axes",
    },
    "tab_terrain": {"tr": "⛰️ 3D Arazi", "en": "⛰️ 3D Terrain"},
    "tab_table": {"tr": "📊 Skor Tablosu & Portföy", "en": "📊 Score Table & Portfolio"},
    "tab_validation": {
        "tr": "✅ Betimsel Sıra Tanısı",
        "en": "✅ Descriptive Rank Diagnostic",
    },
    "tab_breakdown": {
        "tr": "⚠️ Analojinin Sınırları",
        "en": "⚠️ Limits of the Analogy",
    },
    # ── map tab ──────────────────────────────────────────────────────────────
    "map_heading": {
        "tr": ("Haritadaki her nokta bir Dünya sahasıdır (ilk {n} saha). Nokta rengi "
               "(kırmızı → yeşil) ve yarıçapı, seçili Ay referansı ve görev ağırlığına "
               "göre hesaplanan **2 aktif eksenli (`Mobilite + Yüzey`) benzerlik indeksini** "
               "kodlar."),
        "en": ("Each dot on this map is an Earth site (top {n} sites). Dot colour "
               "(red → green) and radius encode the mission-weighted **2-active-axis "
               "(`Mobility + Surface`) similarity index** for the selected Moon reference."),
    },
    "map_caption": {
        "tr": ("Mavi halkalı noktalar literatürden bilinen doğrulama sahalarını "
               "(`role='validation'`: Etna, Atacama, Haughton, Meteor Crater vb.), "
               "diğer noktalar ise aday sahaları (`role='candidate'`) gösterir. "
               "Her iki katmanda da iç dolgu rengi (`color_val` / `color`) ve boyut "
               "doğrudan görev skorunu yansıtır."),
        "en": ("Blue-ringed dots mark literature-known validation sites "
               "(`role='validation'`: Etna, Atacama, Haughton, Meteor Crater, etc.); "
               "other dots are candidate sites (`role='candidate'`). In both layers, "
               "fill colour (`color_val` / `color`) and size reflect the mission score."),
    },
    "map_tooltip": {
        "tr": ("<b>{name}</b><br/>Rol: {role}<br/>Benzerlik: {score}"
               "<br/>Gösterilen aralık: {interval}<br/>Zemin: {lith}"),
        "en": ("<b>{name}</b><br/>Role: {role}<br/>Similarity: {score}"
               "<br/>Displayed interval: {interval}<br/>Ground: {lith}"),
    },
    "map_fallback": {
        "tr": "Harita kütüphanesi eksik; basit haritaya geçildi.",
        "en": "Map library missing; switched to the simple map.",
    },
    "role_validation": {"tr": "Bilinen analog", "en": "Known analogue"},
    "role_candidate": {"tr": "Aday saha", "en": "Candidate site"},
    # ── visual comparison & axis bars tab ────────────────────────────────────
    "scatter_heading": {
        "tr": "### 1) 2B Fiziksel Konum Haritası (Ortalama Eğim ↔ Yüzey Parlaklığı)",
        "en": "### 1) 2D Physical Feature Space (Mean Slope ↔ Surface Brightness)",
    },
    "scatter_caption": {
        "tr": ("40 Dünya sahası (daireler; renk = genel benzerlik indeksi, boyut = "
               "yüzey pürüzlülüğü) ve seçili Ay Güney Kutbu referansı (⭐ altın yıldız) "
               "aktif iki sayısal eksenin temel fiziksel değişkenleri üzerinde birlikte "
               "gösterilir. Yıldız konumuna fiziksel yakınlık arazi eğimi ve parlaklık "
               "uyumunu özetler. (`Karar #30` gereği Termal ekseni v1'de `NaN` olarak "
               "askıdadır; `5 m/px` LOLA ile `30 m/px` GLO-30 çözünürlük farkı "
               "`Analojinin Sınırları` sekmesinde açıklanmıştır.)"),
        "en": ("All 40 Earth sites (circles; colour = overall similarity index, size = "
               "surface roughness) and the selected Lunar South Pole reference (⭐ gold star) "
               "plotted in the physical space of the two active numeric axes. Proximity to "
               "the star reflects terrain-slope and brightness closeness. (Under Decision #30, "
               "the Thermal axis is suspended as `NaN` in v1; the `5 m/px` LOLA vs `30 m/px` "
               "GLO-30 resolution difference is documented on `Limits of the Analogy`.)"),
    },
    "scatter_x": {"tr": "Ortalama Eğim — slope_mean (°)", "en": "Mean Slope — slope_mean (°)"},
    "scatter_y": {"tr": "Yüzey Parlaklığı — albedo (0–1)", "en": "Surface Brightness — albedo (0–1)"},
    "scatter_colorbar": {"tr": "Benzerlik", "en": "Similarity"},
    "bars_heading": {
        "tr": "### 2) Eksen Bazlı Benzerlik ve Belirsizlik Şeritleri (İlk {n} Saha)",
        "en": "### 2) Per-Axis Similarity & Uncertainty Bars (Top {n} Sites)",
    },
    "radar_caption": {
        "tr": ("Her saha kartında **2 aktif sayısal eksen (`Mobilite` ve `Yüzey`)** ile "
               "**Genel** benzerlik indeksi yatay çubuk olarak, Monte Carlo belirsizlik "
               "aralığı (`scoring.display.expanded_interval(score, q05, q95)`) ise siyah "
               "hata şeridi olarak gösterilir. **Termal** ekseni `Karar #30` uyarınca "
               "v1'de askıdadır (`NaN`)."),
        "en": ("Each site card displays the **2 active numeric axes (`Mobility` and `Surface`)** "
               "and the **Overall** similarity index as horizontal bars with their displayed "
               "Monte Carlo uncertainty interval (`scoring.display.expanded_interval(score, q05, q95)`). "
               "The **Thermal** axis is suspended (`NaN`) in v1 under Decision #30."),
    },
    "radar_line": {
        "tr": ("**Genel:** {score} [{interval}] · **Aktif eksen:** {n}/2 "
               "(Termal: Askıda / `NaN`) · **Zemin:** {lith}"),
        "en": ("**Overall:** {score} [{interval}] · **Active axes:** {n}/2 "
               "(Thermal: Suspended / `NaN`) · **Ground:** {lith}"),
    },
    "card_strength_line": {
        "tr": "Güçlü aktif eksen: **{strong}** · Daha zayıf aktif eksen: **{weak}** · Termal: **v1'de askıda (`NaN`)**",
        "en": "Stronger active axis: **{strong}** · Weaker active axis: **{weak}** · Thermal: **suspended in v1 (`NaN`)**",
    },
    "uncertainty_unavailable": {
        "tr": "belirsizlik aralığı yok",
        "en": "uncertainty interval unavailable",
    },
    "q95_label": {"tr": "üst sınır (%95)", "en": "upper bound (95%)"},
    "q05_label": {"tr": "alt sınır (%5)", "en": "lower bound (5%)"},
    "axis_mobility": {"tr": "Mobilite", "en": "Mobility"},
    "axis_thermal": {"tr": "Termal", "en": "Thermal"},
    "axis_surface": {"tr": "Yüzey", "en": "Surface"},
    # ── 3D terrain tab ───────────────────────────────────────────────────────
    "body_earth": {"tr": "Dünya", "en": "Earth"},
    "terrain_intro": {
        "tr": ("Seçili Ay Güney Kutbu referansı (`5 m/px` LRO LOLA PGDA, `2.2×2.2 km`) ile "
               "seçili Dünya sahasının (`30 m/px` Copernicus GLO-30 / NASADEM, `2.22×2.22 km`) "
               "gerçek yörünge sayısal yükseklik modelleri yan yana 3B yüzey olarak "
               "gösterilir. Yüzey rengi kuzeybatı (`315°`, `45°`) ışık kaynağından "
               "türetilen arazi gölgelendirmesidir (`hillshade`). Üstteki koyu halka "
               "`r = 1 km` analiz çemberini gösterir."),
        "en": ("Real orbital digital elevation models of the selected Lunar South Pole "
               "reference (`5 m/px` LRO LOLA PGDA, `2.2×2.2 km`) and the selected Earth "
               "site (`30 m/px` Copernicus GLO-30 / NASADEM, `2.22×2.22 km`) rendered "
               "side by side as 3D surfaces. Surface colour is NW (`315°`, `45°`) "
               "hillshade; the dark ring marks the `r = 1 km` measurement radius."),
    },
    "terrain_pick": {
        "tr": "Sağ tarafta gösterilecek Dünya sahası",
        "en": "Earth site shown on the right",
    },
    "terrain_exag_label": {
        "tr": "Dikey abartı (×)",
        "en": "Vertical exaggeration (×)",
    },
    "terrain_exag_note": {
        "tr": "Dikey ölçek abartılı gösteriliyor (varsayılan 2×; yerel rölyef farklarını görünür kılmak için)",
        "en": "Vertical scale is exaggerated (default 2×; to make local relief visible)",
    },
    "terrain_orbit_label": {
        "tr": "Kamera yörünge açısı (derece)",
        "en": "Camera orbit angle (degrees)",
    },
    "terrain_hover": {
        "tr": ("X: %{x:.2f} km<br/>Y: %{y:.2f} km"
               "<br/>Gerçek yükselti: %{customdata:.0f} m<extra></extra>"),
        "en": ("X: %{x:.2f} km<br/>Y: %{y:.2f} km"
               "<br/>True elevation: %{customdata:.0f} m<extra></extra>"),
    },
    "terrain_card_source": {
        "tr": ("Doğrulanmış yörünge DEM · Kaynak: {src} · Çözünürlük: {res} m/piksel · "
               "Pencere: ~{km} km (r = 1 km çemberi işaretli)"),
        "en": ("Verified orbital DEM · Source: {src} · Resolution: {res} m/pixel · "
               "Window: ~{km} km (r = 1 km ring marked)"),
    },
    "terrain_card_stub": {
        "tr": ("Örnek arazi verisi · istatistik kaynağı: {src} · "
               "Çözünürlük: {res} m/piksel · Pencere: {km} km"),
        "en": ("Generated sample terrain · stats source: {src} · "
               "Resolution: {res} m/pixel · Window: {km} km"),
    },
    "terrain_stub_note": {
        "tr": ("Bu 3B kartlarda örnek arazi verisi kullanılıyor; gerçek yükselti "
               "paftaları bulunduğunda otomatik olarak gerçek DEM'e geçilir."),
        "en": ("These 3D cards use generated sample terrain and switch to real DEM "
               "tiles automatically when present."),
    },
    # ── score table & compact portfolio card ─────────────────────────────────
    "table_caption": {
        "tr": ("40 Dünya sahası için görev ağırlıklı **Genel** benzerlik indeksi ve "
               "**2 aktif sayısal eksen (`Mobilite`, `Yüzey`)** skorları. Köşeli "
               "parantez içindeki değerler `scoring.display.expanded_interval` ile "
               "gösterilen 5.–95. yüzdelik Monte Carlo belirsizlik aralığıdır."),
        "en": ("Mission-weighted **Overall** similarity index and **2 active numeric "
               "axis (`Mobility`, `Surface`)** scores across all 40 Earth sites. "
               "Bracketed bounds show the 5th–95th percentile Monte Carlo uncertainty "
               "interval via `scoring.display.expanded_interval`."),
    },
    "col_site": {"tr": "Saha", "en": "Site"},
    "col_role": {"tr": "Rol", "en": "Role"},
    "col_lith": {"tr": "Zemin (litoloji)", "en": "Ground (lithology)"},
    "col_overall": {"tr": "Genel (2 Aktif Eksen)", "en": "Overall (2 Active Axes)"},
    "filter_lith": {"tr": "Zemine göre filtrele", "en": "Filter by ground type"},
    "filter_region": {"tr": "Kıta", "en": "Continent"},
    "region_all": {"tr": "Tüm sahalar", "en": "All sites"},
    "region_europe": {"tr": "Avrupa", "en": "Europe"},
    "region_asia": {"tr": "Asya", "en": "Asia"},
    "region_africa": {"tr": "Afrika", "en": "Africa"},
    "region_north_america": {"tr": "Kuzey Amerika", "en": "North America"},
    "region_south_america": {"tr": "Güney Amerika", "en": "South America"},
    "region_oceania": {"tr": "Okyanusya", "en": "Oceania"},
    "region_antarctica": {"tr": "Antarktika", "en": "Antarctica"},
    "table_footer_caption": {
        "tr": ("Zemin (litoloji) sütunu nitel bağlam bilgisi sunar; sayısal benzerlik "
               "puanına katılmaz (`AGENTS.md §2`)."),
        "en": ("The Ground (lithology) column provides qualitative context only and "
               "does not enter the numeric similarity score (`AGENTS.md §2`)."),
    },
    "portfolio_heading": {
        "tr": "### 🧭 Kompakt Çok-Sahalı Test Portföyü Kartı (`select_portfolio`)",
        "en": "### 🧭 Compact Multi-Site Test Portfolio Card (`select_portfolio`)",
    },
    "portfolio_intro": {
        "tr": ("Tek bir Dünya sahası tüm görev gereksinimlerini karşılayamaz. Aşağıdaki "
               "kompakt portföy, `scoring.portfolio.select_portfolio` (açgözlü küme "
               "örtme / greedy set cover) algoritmasıyla **`0.70` benzerlik indeksi "
               "eşiğini** aşan eksenleri en az sayıda sahayla tamamlar ve hiçbir Dünya "
               "sahasının eşiği geçemediği veya v1'de askıda kalan eksenleri açıkça "
               "laboratuvar/simülasyon doğrulamasına ayırır."),
        "en": ("No single Earth site satisfies every mission requirement. The compact "
               "portfolio below uses `scoring.portfolio.select_portfolio` (greedy set "
               "cover) at the **`0.70` similarity-index threshold** to cover the most "
               "axes with the fewest sites, while explicitly routing axes that remain "
               "below `0.70` or suspended in v1 to laboratory/simulation testing."),
    },
    "portfolio_col_order": {"tr": "Seçim Sırası", "en": "Pick Order"},
    "portfolio_col_site": {"tr": "Seçilen Dünya Sahası", "en": "Selected Earth Site"},
    "portfolio_col_role": {"tr": "Rol", "en": "Role"},
    "portfolio_col_covered": {
        "tr": "Kapsadığı Eksenler (≥ 0.70)",
        "en": "Axes Covered (≥ 0.70)",
    },
    "portfolio_col_scores": {
        "tr": "Aktif Eksen Skorları (Mobilite / Yüzey)",
        "en": "Active Axis Scores (Mobility / Surface)",
    },
    "portfolio_covered_label": {
        "tr": "✅ **Portföyün ≥ 0.70 eşiğinde kapsadığı eksenler:** {axes}",
        "en": "✅ **Axes covered by portfolio at ≥ 0.70 threshold:** {axes}",
    },
    "portfolio_uncovered_label": {
        "tr": ("🔬 **Kapsam dışı / laboratuvar, simülasyon veya hedefli dik-yamaç "
               "testine kalan eksenler:** {axes}"),
        "en": ("🔬 **Uncovered axes routed to laboratory, simulation, or targeted "
               "steep-slope testing:** {axes}"),
    },
    "portfolio_best_mobility_note": {
        "tr": ("💡 *Mobilite notu:* Seçili Ay referansı için `0.70` eşiğini aşan tekil "
               "bir saha olmadığında en yüksek Mobilite indeksine sahip saha "
               "**{site}** (`{score}`) olup saha içi rover/eğim testlerinde "
               "portföye tamamlayıcı aday olarak eklenebilir."),
        "en": ("💡 *Mobility note:* When no single site exceeds the `0.70` threshold on "
               "Mobility for the selected Moon reference, the highest-scoring Mobility "
               "site is **{site}** (`{score}`), which can complement the portfolio for "
               "field rover/slope trials."),
    },
    "portfolio_none_selected": {
        "tr": "Seçili Ay referansı için hiçbir Dünya sahası `0.70` indeks eşiğini aşmadı.",
        "en": "No Earth site exceeded the `0.70` index threshold for the selected Moon reference.",
    },
    "portfolio_threshold_note": {
        "tr": ("⚠️ **Eşik uyarısı (`0.70`):** Bu eşik olasılık ya da kalibre edilmiş "
               "benzerlik değildir; seçilen minimal küme sayısı `0.70` sezgisel eşik "
               "ayarına bağlıdır (`<= 3` eksende açgözlü seçim en küçük saha kümesini "
               "verir, daha fazla eksende sezgiseldir; `docs/data_notes.md §2b`)."),
        "en": ("⚠️ **Threshold caveat (`0.70`):** This threshold is neither a probability "
               "nor a calibrated similarity bound; the selected minimal set size depends "
               "on the `0.70` heuristic threshold setting (greedy selection yields the "
               "exact minimum site count for `<= 3` axes and is a heuristic for larger "
               "axis sets; `docs/data_notes.md §2b`)."),
    },
    # ── validation tab (Descriptive Rank Diagnostic) ─────────────────────────
    "val_intro": {
        "tr": ("### ✅ Betimsel Sıra Tanısı (10 Bilinen Doğrulama Sahası × Kaynaklı Beklenti Matrisi)\n\n"
               "> **Yöntemsel Sınır (`docs/data_notes.md §2b`):** Bu ekran **bağımsız bir "
               "holdout doğrulaması veya ilk-5 geçer/kalır testi değildir**; 40 Dünya "
               "sahasının tamamı (`10 doğrulama + 30 aday`) Z-skor ölçeklemesinin "
               "ortalama ve standart sapma hesabına katılır. Aşağıdaki tablo, bilinen "
               "10 doğrulama sahasının rol etiketinden habersiz sıralamadaki **ham yerini "
               "(`1–40`)**, `docs/validation_expectations.md` içinde önceden kayıtlı "
               "**beklenen eksen (`Kesin` / `Aday`)**, **gerekçe**, **nitel buz/permafrost "
               "durumu (`E8`)** ve **doğrulanmış DOI/URL kaynaklarıyla** yan yana gösteren "
               "**betimsel bir sıra tanısıdır**.\n\n"
               "- **Aktif sayısal eksenler (`Karar #30`):** Ham sıralamalar v1'de aktif "
               "olan **Mobilite** (`/40`) ve **Yüzey** (`/40`) eksenleri için verilir; "
               "**Termal** ekseni Ay `temp_amplitude = NaN` ve `thermal_inertia = NaN` "
               "nedeniyle v1'de **Askıda (`NaN`)** durumundadır."),
        "en": ("### ✅ Descriptive Rank Diagnostic (10 Known Validation Sites × Sourced Expectation Matrix)\n\n"
               "> **Methodological Caveat (`docs/data_notes.md §2b`):** This screen is "
               "**neither an independent holdout validation nor a top-5 pass/fail test**; "
               "all 40 Earth sites (`10 validation + 30 candidate`) participate in the "
               "Z-score standardization mean and standard deviation. The table below is a "
               "**descriptive rank diagnostic** showing the raw blind rank (`1–40`) of "
               "the 10 known validation sites alongside their pre-registered **expected "
               "axes (`Confirmed` / `Candidate`)**, **rationale**, **qualitative "
               "ice/permafrost status (`E8`)**, and **verified DOI/URL citations** from "
               "`docs/validation_expectations.md`.\n\n"
               "- **Active numeric axes (`Decision #30`):** Raw ranks are reported for "
               "the active **Mobility** (`/40`) and **Surface** (`/40`) axes; the "
               "**Thermal** axis is **Suspended (`NaN`)** in v1 because Moon "
               "`temp_amplitude = NaN` and `thermal_inertia = NaN`."),
    },
    "val_col_site": {"tr": "Doğrulama Sahası", "en": "Validation Site"},
    "val_col_expected": {
        "tr": "Beklenen Eksen(ler) (Kesin / Aday)",
        "en": "Expected Axis/Axes (Confirmed / Candidate)",
    },
    "val_col_raw_rank": {
        "tr": "Ham Sıralama (40 Saha İçinde)",
        "en": "Raw Rank (out of 40 Sites)",
    },
    "val_col_ice": {
        "tr": "Buz / Permafrost (E8 Nitel)",
        "en": "Ice / Permafrost (E8 Qualitative)",
    },
    "val_col_rationale": {"tr": "Gerekçe", "en": "Rationale"},
    "val_col_source": {
        "tr": "Doğrulanmış Kaynak (DOI / URL)",
        "en": "Verified Source (DOI / URL)",
    },
    "val_rank_cell": {
        "tr": "Mobilite #{mob}/40 · Yüzey #{surf}/40 · Termal: Askıda (NaN)",
        "en": "Mobility #{mob}/40 · Surface #{surf}/40 · Thermal: Suspended (NaN)",
    },
    "val_footer_note": {
        "tr": ("Not: `docs/validation_expectations.md` ön-kayıt kuralı gereği "
               "beklenti sınıfları (`Kesin` / `Aday`) sıralama çıktılarına göre "
               "geri dönük olarak değiştirilmez. Düşük sıralamalar `5 m/px` (Ay LOLA) "
               "vs `30 m/px` (Dünya GLO-30) DEM ölçek farkı, krater duvarı vs düz "
               "ova/kalkan morfolojisi farkı veya `1 km / 500 m` MODIS karma piksel "
               "etkisi bağlamında yorumlanır."),
        "en": ("Note: Per the pre-registration rule in `docs/validation_expectations.md`, "
               "expectation tiers (`Confirmed` / `Candidate`) are never tuned "
               "retroactively to rankings. Lower ranks reflect `5 m/px` (Moon LOLA) vs "
               "`30 m/px` (Earth GLO-30) DEM scale differences, steep crater-rim vs "
               "flat plain/shield morphology differences, or `1 km / 500 m` MODIS "
               "mixed-pixel effects."),
    },
    # ── analogy limits tab ───────────────────────────────────────────────────
    "breakdown_notes": {
        "tr": (
            "### 1) Fiziksel ve Teknik Analoji Sınırları\n\n"
            "Hiçbir Dünya sahası Ay Güney Kutbu koşullarını her boyutta aynı anda "
            "temsil edemez. Skorları yorumlarken iki grup sınır birlikte dikkate alınmalıdır:\n\n"
            "#### A. Dünya'da Doğal Olarak Bulunmayan Fiziksel Koşullar (Sahadan Bağımsız — Laboratuvar / Simülasyon)\n"
            "- **Yerçekimi (`~1.62 m/s²`, `~1/6 g`):** Regolit mekaniği, tekerlek batması ve "
            "toz çökme hızı Dünya yerçekiminde (`9.81 m/s²`) birebir üretilemez.\n"
            "- **Vakum / Atmosfersiz Ortam:** Ay yüzeyindeki ultra-yüksek vakum, ısı "
            "taşınımını (konveksiyon yokluğu) ve elektrostatik toz yapışmasını belirler.\n"
            "- **Radyasyon:** Ay'da küresel manyetosfer ve atmosferik koruma yoktur; "
            "galaktik kozmik ışınlar ve güneş parçacık olayları laboratuvarda test edilir.\n"
            "- **Sinodik Gün Uzunluğu (`~29.5` Dünya günü) ve Sıyırıcı Kutup Güneşi (`~1.5°`):** "
            "Kutup krater sırtlarındaki uzun gölgeleme ve aydınlanma ritmi Dünya'da bulunmaz.\n"
            "- **Regolit Mineralojisi ve Camlaşmış Kürecikler (Agglutinates):** Mikrometeorit "
            "çarpmalarıyla oluşan keskin kenarlı Ay regoliti Dünya toprağından farklıdır.\n\n"
            "#### B. Skorların Yorumlanmasını Etkileyen Teknik ve Ölçek Sınırları (`docs/data_notes.md`)\n"
            "- **Topoğrafya Çözünürlük Ölçeği Farkı (`5 m/px` Ay LOLA vs `30 m/px` Dünya GLO-30):** "
            "Her iki gök cisminde aynı `r = 1000 m` penceresi ve metrik projeksiyonda "
            "`np.gradient → atan` eğim tanımı kullanılsa da `5 m` (LRO LOLA PGDA) ile "
            "`30 m` (Copernicus DEM GLO-30) doğal piksel boyutu `slope_mean`, `slope_p90` "
            "ve `roughness` değerlerini ölçeğe duyarlı kılar; sayısal karşılaştırma "
            "yaklaşım/vekil niteliktedir.\n"
            "- **Termal Eksenin v1'de Askıya Alınması (`Karar #30` — `temp_amplitude = NaN`, `thermal_inertia = NaN`):** "
            "Resmî PDS3 `.lbl` etiket doğrulamasında Ay Diviner `ltim` yerel saat dilimlerinin "
            "Dünya `MOD11A2.061` yıllık ortalama gündüz–gece ΔT (`1 km`) ürünüyle aynı günlük "
            "döngü tanımını paylaşmadığı ve her iki gök cisminde ortak kalibre edilmiş küresel "
            "`thermal_inertia` ürünü bulunmadığı belgelendiğinden, v1'de Termal ekseni `NaN` "
            "olarak askıya alınmış ve sayısal skorlama **2 aktif eksen (`Mobilite + Yüzey`)** "
            "üzerinden çalıştırılmıştır.\n"
            "- **Kaba Çözünürlüklü Yüzey Ürünleri (`500 m`–`1000 m`):** Dünya `MCD43A3.061` "
            "albedo (`500 m`) ve `MOD11A2.061` (`1000 m`) ürünleri alt-kilometrik yerel yama "
            "farklarını doğrudan çözmez (`Ay LOLA 1064 nm` normal albedosu `× 0.38` faz "
            "integrali düzeltmesiyle geniş bant güneş albedosuna hizalanmıştır)."
        ),
        "en": (
            "### 1) Physical & Technical Limits of the Analogy\n\n"
            "No Earth site reproduces Lunar South Pole conditions across every dimension "
            "at once. Two groups of limits govern how the scores must be interpreted:\n\n"
            "#### A. Physical Conditions Absent on Earth (Field-Independent — Laboratory / Simulation)\n"
            "- **Surface Gravity (`~1.62 m/s²`, `~1/6 g`):** Regolith mechanics, wheel sinkage, "
            "and dust settling cannot be reproduced under Earth gravity (`9.81 m/s²`).\n"
            "- **Hard Vacuum:** The airless lunar environment governs radiative-only heat "
            "transfer and electrostatic dust adhesion.\n"
            "- **Radiation Environment:** Lack of a global magnetosphere and atmosphere "
            "exposes the surface to galactic cosmic rays and solar particle events.\n"
            "- **Synodic Day (`~29.5` Earth days) & Grazing Polar Illumination (`~1.5°`):** "
            "Topographic shadowing and illumination cycles at polar rims have no terrestrial counterpart.\n"
            "- **Regolith Mineralogy & Agglutinates:** Impact-gardened, glass-welded lunar "
            "regolith differs fundamentally from weathered terrestrial soils.\n\n"
            "#### B. Technical & Scale Limits Affecting Score Interpretation (`docs/data_notes.md`)\n"
            "- **DEM Resolution Scale Difference (`5 m/px` Moon LOLA vs `30 m/px` Earth GLO-30):** "
            "Although both bodies use the same `r = 1000 m` window and metric-CRS "
            "`np.gradient → atan` definition, the `5 m` (LRO LOLA PGDA) vs `30 m` "
            "(Copernicus DEM GLO-30) native pixel size makes `slope_mean`, `slope_p90`, "
            "and `roughness` scale-sensitive (proxy comparison).\n"
            "- **Suspended Thermal Axis in v1 (`Decision #30` — `temp_amplitude = NaN`, `thermal_inertia = NaN`):** "
            "Official PDS3 `.lbl` verification showed that lunar Diviner `ltim` local-time "
            "slices do not share an equivalent diurnal definition with Earth `MOD11A2.061` "
            "annual mean day–night ΔT (`1 km`), and no uniform global `thermal_inertia` "
            "product exists at matching scale. Accordingly, the Thermal axis is suspended "
            "(`NaN`) in v1 and numeric scoring runs on the **2 active axes (`Mobility + Surface`)**.\n"
            "- **Coarse Surface Products (`500 m`–`1000 m`):** Earth `MCD43A3.061` albedo "
            "(`500 m`) and `MOD11A2.061` (`1000 m`) do not resolve sub-kilometer patches "
            "(`Moon LOLA 1064 nm` normal albedo is scaled by `× 0.38` phase-integral "
            "conversion to broadband solar hemispherical albedo)."
        ),
    },
    "scorecard_heading": {
        "tr": "### 2) 8 Boyutlu Görev Karnesi (Sayısal / Askıda / Nitel / Laboratuvar-Simülasyon)",
        "en": "### 2) 8-Dimension Challenge Scorecard (Numeric / Suspended / Qualitative / Lab-Simulation)",
    },
    "scorecard_col_dim": {"tr": "Analiz Boyutu", "en": "Analysis Dimension"},
    "scorecard_col_status": {"tr": "v1 Durumu", "en": "v1 Status"},
    "scorecard_col_data": {
        "tr": "Veri Kaynağı & Çözünürlük",
        "en": "Data Source & Resolution",
    },
    "scorecard_col_note": {
        "tr": "Kapsam & Sınır Notu",
        "en": "Scope & Limitation Note",
    },
    "inspect_label": {
        "tr": "Ayrıntılı incelenecek Dünya sahası",
        "en": "Earth site to inspect in detail",
    },
    "inspect_help": {
        "tr": ("Yalnızca ilk sıradakini değil, listedeki herhangi bir sahayı "
               "inceleyebilirsiniz."),
        "en": ("Inspect any site in the list, not only the top-ranked one."),
    },
    # ── visual evidence panel ────────────────────────────────────────────────
    "vis_heading": {
        "tr": "### 3) 🛰️ Doğrulanmış Yörünge Görsel ve Topografik Kanıt Kartı: {ref} ↔ {sel}",
        "en": "### 3) 🛰️ Verified Orbital Visual & Topographic Evidence Card: {ref} ↔ {sel}",
    },
    "vis_col_moon_opt": {
        "tr": "Ay Referansı — LOLA 5 m/px Kabartma & Kesit",
        "en": "Moon Reference — LOLA 5 m/px Hillshade & Profile",
    },
    "vis_col_moon_relief": {
        "tr": "Ay Referansı — LOLA 5 m/px Eğim Sınıfları",
        "en": "Moon Reference — LOLA 5 m/px Slope Classes",
    },
    "vis_col_earth": {
        "tr": "Dünya Adayı — Sentinel-2 L2A 10 m/px Uydu Görüntüsü",
        "en": "Earth Candidate — Sentinel-2 L2A 10 m/px Satellite Image",
    },
    "vis_moon_hillshade_caption": {
        "tr": ("{ref} — LRO LOLA PGDA `5 m/px` gölgeli kabartma (`2.2×2.2 km` pencere, "
               "`r = 1000 m` çemberi; rölyef `{relief} m`, ort. eğim `{slope}°`)"),
        "en": ("{ref} — LRO LOLA PGDA `5 m/px` hillshade (`2.2×2.2 km` window, "
               "`r = 1000 m` circle; relief `{relief} m`, mean slope `{slope}°`)"),
    },
    "vis_moon_hazard_caption": {
        "tr": ("{ref} — LRO LOLA `5 m/px` eğim sınıfları: `<10°` %{lt10} · `10–20°` %{mid} · "
               "`>20°` %{gt20} (*Illustrative slope bins; not a landing-safety assessment*)"),
        "en": ("{ref} — LRO LOLA `5 m/px` slope classes: `<10°` {lt10}% · `10–20°` {mid}% · "
               "`>20°` {gt20}% (*Illustrative slope bins; not a landing-safety assessment*)"),
    },
    "vis_moon_local_source": {
        "tr": "Kaynak: `data/processed/moon_atlas/` (`LRO_LOLA_PGDA_5mpp_v2021`, `5 m/piksel`).",
        "en": "Source: `data/processed/moon_atlas/` (`LRO_LOLA_PGDA_5mpp_v2021`, `5 m/pixel`).",
    },
    "vis_moon_missing": {
        "tr": "Bu Ay referansı için yerel `moon_atlas` kartı bulunamadı.",
        "en": "Local `moon_atlas` card not found for this Moon reference.",
    },
    "vis_earth_s2_caption": {
        "tr": ("{sel} (`{lat}°`, `{lon}°`) — `5.12×5.12 km` pencere (`10 m/piksel` doğal "
               "çözünürlük; merkezdeki `2.22×2.22 km` alan 3B DEM ile tam hizalı)"),
        "en": ("{sel} (`{lat}°`, `{lon}°`) — `5.12×5.12 km` footprint (`10 m/pixel` "
               "native resolution; central `2.22×2.22 km` patch aligned with 3D DEM)"),
    },
    "vis_earth_s2_meta": {
        "tr": ("**Koleksiyon:** `{collection}` · **Sahne (`scene_id`):** `{scene_id}` · "
               "**Çekim tarihi:** `{date}` · **Yerel bulut:** `%{cloud}`"),
        "en": ("**Collection:** `{collection}` · **Scene (`scene_id`):** `{scene_id}` · "
               "**Acquisition date:** `{date}` · **Local cloud:** `{cloud}%`"),
    },
    "vis_earth_missing": {
        "tr": "Bu Dünya sahası için yerel `earth_atlas` görüntüsü bulunamadı.",
        "en": "Local `earth_atlas` image not found for this Earth site.",
    },
    "vis_link_worldview": {
        "tr": "🔗 [NASA Worldview'de bölgeyi aç]({url})",
        "en": "🔗 [Open the region in NASA Worldview]({url})",
    },
    "vis_link_gmaps": {
        "tr": "[Google Maps Uydu]({url})",
        "en": "[Google Maps Satellite]({url})",
    },
    "vis_quant_head": {
        "tr": "Yukarıdaki görüntüler için sayısal bağlam — ",
        "en": "Quantitative context for the images above — ",
    },
    "vis_quant_line": {
        "tr": "**{axis}:** {score} (belirsizlik: {lo}–{hi})",
        "en": "**{axis}:** {score} (uncertainty: {lo}–{hi})",
    },
    "vis_quant_suspended": {
        "tr": "**{axis}:** Askıda (`NaN` — `Karar #30`)",
        "en": "**{axis}:** Suspended (`NaN` — `Decision #30`)",
    },
    "vis_quant_msg": {
        "tr": ("Görsel benzerlik tek başına puanlama kanalı değildir (`AGENTS.md §6`): "
               "yukarıdaki yörünge görüntülerini aşağıdaki sayısal ölçüt farkları, "
               "belirsizlik aralıkları ve çözünürlüklerle birlikte değerlendirin."),
        "en": ("Visual similarity is never a scoring channel (`AGENTS.md §6`): "
               "evaluate the orbital imagery above together with the quantitative "
               "feature gaps, uncertainty bounds, and native resolutions below."),
    },
    # ── feature gaps table ───────────────────────────────────────────────────
    "gaps_heading": {
        "tr": "### 4) Ölçüt Farkları ve Çözünürlük Şeffaflığı: {sel} ↔ {ref}",
        "en": "### 4) Criterion Gaps & Resolution Transparency: {sel} ↔ {ref}",
    },
    "gaps_empty": {
        "tr": "Bu saha için karşılaştırılabilir sayısal ölçüt yok.",
        "en": "No comparable numeric criteria for this site.",
    },
    "gaps_caption": {
        "tr": ("Fark (σ) büyük → en büyük fiziksel uyuşmazlık (tablo mutlak standart "
               "farka göre büyükten küçüğe sıralanır). Çözünürlük (m): verinin doğal "
               "piksel boyutu (`5 m` Ay LOLA DEM vs `30 m` Dünya GLO-30 DEM; `1000 m` "
               "LOLA albedo vs `500 m` MODIS albedo). `Karar #30` uyarınca Ay tarafında "
               "`NaN` olan termal özellikler bu sayısal fark tablosuna girmez."),
        "en": ("Large Diff (σ) → largest physical mismatch (sorted descending by "
               "absolute standardized difference). Resolution (m): native pixel size "
               "(`5 m` Moon LOLA DEM vs `30 m` Earth GLO-30 DEM; `1000 m` LOLA albedo "
               "vs `500 m` MODIS albedo). Thermal features suspended as `NaN` on the "
               "Moon under Decision #30 are excluded from numeric gaps."),
    },
}

# 8-Dimension Challenge Scorecard (Analogy Limits tab).
DIMENSION_SCORECARD: dict[str, list[dict[str, str]]] = {
    "tr": [
        {
            "Boyut": "1. Topografya & Arazi (slope_mean, slope_p90, roughness, relief)",
            "v1 Durumu": "✅ Sayısal eksende (Aktif — Mobilite)",
            "Veri Kaynağı & Çözünürlük": "Ay: LRO LOLA PGDA (5 m/px) · Dünya: Copernicus GLO-30 / NASADEM (30 m/px)",
            "Kapsam & Sınır Notu": "Her ikisinde r = 1000 m ve metrik CRS eğim hesabı; 5 m vs 30 m doğal çözünürlük farkı nedeniyle vekil karşılaştırma.",
        },
        {
            "Boyut": "2. Yüzey Parlaklığı (albedo)",
            "v1 Durumu": "✅ Sayısal eksende (Aktif — Yüzey)",
            "Veri Kaynağı & Çözünürlük": "Ay: LRO LOLA 1064 nm ×0.38 geniş bant eşdeğeri (1000 m) · Dünya: MODIS MCD43A3.061 (500 m)",
            "Kapsam & Sınır Notu": "Geniş bant güneş albedosuna hizalı (c = 0.38 duyarlılığı belgeli); 500 m–1 km piksel alt-kilometrik yamaları çözmez.",
        },
        {
            "Boyut": "3. Sıcaklık Genliği & Termal Atalet (temp_amplitude, thermal_inertia)",
            "v1 Durumu": "⏸️ v1'de Askıda (NaN — Karar #30)",
            "Veri Kaynağı & Çözünürlük": "Ay: LRO Diviner PCP (240 m, NaN) · Dünya: MODIS MOD11A2.061 yıllık ort. ΔT (1000 m)",
            "Kapsam & Sınır Notu": "Ay Diviner ltim yerel saat dilimleri ile Dünya MODIS yıllık ort. gündüz–gece farkı eşdeğer günlük döngü tanımında olmadığından ve ortak TI ürünü bulunmadığından v1'de askıda.",
        },
        {
            "Boyut": "4. Yüzey Litolojisi (lithology_class)",
            "v1 Durumu": "🏷️ Nitel olarak (Skor dışı)",
            "Veri Kaynağı & Çözünürlük": "Küratörlü jeoloji haritaları ve saha literatürü (src/earth/sites.py)",
            "Kapsam & Sınır Notu": "Farklı aygıt spektrumları sayısal skora karıştırılmaz (AGENTS.md §2); tablo ve haritada nitel gösterilir.",
        },
        {
            "Boyut": "5. Su Buzu / Kalıcı Gölge (PSR) & Permafrost",
            "v1 Durumu": "🏷️ Nitel olarak (Skor dışı — E8)",
            "Veri Kaynağı & Çözünürlük": "Doğrulama sahaları için DOI'li literatür envanteri (docs/validation_expectations.md §4)",
            "Kapsam & Sınır Notu": "Haughton, McMurdo ve Svalbard'da sürekli permafrost/yeraltı buzu var; Ay vakumlu kriyojenik PSR buzu laboratuvarda test edilir.",
        },
        {
            "Boyut": "6. Lav Tüpleri & Yeraltı Boşlukları",
            "v1 Durumu": "🏷️ Nitel olarak (Skor dışı — v2 SAR yolu)",
            "Veri Kaynağı & Çözünürlük": "Jeolojik literatür (Lanzarote PANGAEA, Craters of the Moon vb.)",
            "Kapsam & Sınır Notu": "v1'de nitel; v2'de CSA RADARSAT-1 SAR ve LRO Mini-RF verileriyle sayısal radar ekseni olarak genişletilecek.",
        },
        {
            "Boyut": "7. Toz, Rüzgâr & Elektrostatik Toz Davranışı",
            "v1 Durumu": "🔬 Nitel / Laboratuvar & Simülasyon",
            "Veri Kaynağı & Çözünürlük": "Saha gözlemleri + vakum/plazma toz odası literatürü",
            "Kapsam & Sınır Notu": "Dünya'da rüzgâr/nem süreci baskındır; Ay'da UV/plazma kaynaklı elektrostatik toz levitasyonu yalnız vakum odasında üretilir.",
        },
        {
            "Boyut": "8. Yerçekimi (1/6 g), Vakum, Radyasyon & 29.5 Günlük Ay Günü",
            "v1 Durumu": "🔬 Sahadan bağımsız — Laboratuvar & Simülasyon",
            "Veri Kaynağı & Çözünürlük": "Fiziksel temel sabitler ve görev ortam modelleri",
            "Kapsam & Sınır Notu": "Hiçbir Dünya sahası bu koşulları doğal olarak sunamaz; saha testleri mutlaka simülatör ve termal-vakum odalarıyla tamamlanır.",
        },
    ],
    "en": [
        {
            "Dimension": "1. Topography & Terrain (slope_mean, slope_p90, roughness, relief)",
            "v1 Status": "✅ Numeric Axis (Active — Mobility)",
            "Data Source & Resolution": "Moon: LRO LOLA PGDA (5 m/px) · Earth: Copernicus GLO-30 / NASADEM (30 m/px)",
            "Scope & Limitation Note": "Both use r = 1000 m and metric-CRS slope; proxy comparison due to 5 m vs 30 m native pixel scale difference.",
        },
        {
            "Dimension": "2. Surface Brightness (albedo)",
            "v1 Status": "✅ Numeric Axis (Active — Surface)",
            "Data Source & Resolution": "Moon: LRO LOLA 1064 nm ×0.38 broadband eq. (1000 m) · Earth: MODIS MCD43A3.061 (500 m)",
            "Scope & Limitation Note": "Aligned to broadband solar albedo (c = 0.38 sensitivity documented); 500 m–1 km pixels do not resolve sub-km patches.",
        },
        {
            "Dimension": "3. Temperature Swing & Thermal Inertia (temp_amplitude, thermal_inertia)",
            "v1 Status": "⏸️ Suspended in v1 (NaN — Decision #30)",
            "Data Source & Resolution": "Moon: LRO Diviner PCP (240 m, NaN) · Earth: MODIS MOD11A2.061 annual mean ΔT (1000 m)",
            "Scope & Limitation Note": "Suspended in v1 because lunar Diviner ltim slices and Earth MODIS annual mean day–night ΔT lack an equivalent diurnal definition and no uniform global TI product exists.",
        },
        {
            "Dimension": "4. Surface Lithology (lithology_class)",
            "v1 Status": "🏷️ Qualitative (Unscored)",
            "Data Source & Resolution": "Curated geologic maps and field literature (src/earth/sites.py)",
            "Scope & Limitation Note": "Cross-instrument mineral spectra are never mixed into a numeric score (AGENTS.md §2); shown qualitatively in table and map.",
        },
        {
            "Dimension": "5. Water Ice / PSR & Permafrost",
            "v1 Status": "🏷️ Qualitative (Unscored — E8)",
            "Data Source & Resolution": "DOI-backed literature inventory for validation sites (docs/validation_expectations.md §4)",
            "Scope & Limitation Note": "Continuous permafrost/ground ice documented at Haughton, McMurdo, and Svalbard; cryogenic vacuum PSR ice requires lab chambers.",
        },
        {
            "Dimension": "6. Lava Tubes & Subsurface Cavities",
            "v1 Status": "🏷️ Qualitative (Unscored — v2 SAR path)",
            "Data Source & Resolution": "Geologic literature (Lanzarote PANGAEA, Craters of the Moon, etc.)",
            "Scope & Limitation Note": "Qualitative in v1; planned v2 extension via CSA RADARSAT-1 SAR and LRO Mini-RF backscatter comparison.",
        },
        {
            "Dimension": "7. Dust, Wind & Electrostatic Dust Behavior",
            "v1 Status": "🔬 Qualitative / Laboratory & Simulation",
            "Data Source & Resolution": "Field observations + vacuum/plasma dust chamber literature",
            "Scope & Limitation Note": "Terrestrial dust is wind/moisture driven; UV/plasma electrostatic dust levitation on the Moon requires vacuum chambers.",
        },
        {
            "Dimension": "8. Gravity (1/6 g), Vacuum, Radiation & 29.5-Day Lunar Day",
            "v1 Status": "🔬 Field-Independent — Laboratory & Simulation",
            "Data Source & Resolution": "Fundamental physical constants and mission environment models",
            "Scope & Limitation Note": "No Earth site reproduces these conditions naturally; field campaigns must be paired with simulators and thermal-vacuum chambers.",
        },
    ],
}

# Pre-registered validation expectations from docs/validation_expectations.md (10 validation sites).
VALIDATION_EXPECTATIONS: dict[str, dict[str, dict[str, str]]] = {
    "earth_etna_cisternazza": {
        "tr": {
            "expected": "Kesin: Mobilite · Aday: Yüzey (koyu tefra/bazalt)",
            "ice": "kısmi (dağ ölçeği mağara buzu + kış karı)",
            "rationale": "ARCHES ve ROBEX kampanyaları Cisternazza yamacını doğrudan Ay rover otonom mobilite sahası olarak doğrulamıştır.",
            "source": "Schuster et al. (2020) https://doi.org/10.1109/LRA.2020.3007468 · Vayugundla et al. (2018) https://elib.dlr.de/124514/",
        },
        "en": {
            "expected": "Confirmed: Mobility · Candidate: Surface (dark tephra/basalt)",
            "ice": "partial (mountain-scale cave ice + winter snow)",
            "rationale": "ARCHES and ROBEX campaigns directly validated the Cisternazza flank as a lunar rover autonomous mobility testbed.",
            "source": "Schuster et al. (2020) https://doi.org/10.1109/LRA.2020.3007468 · Vayugundla et al. (2018) https://elib.dlr.de/124514/",
        },
    },
    "earth_atacama_yungay": {
        "tr": {
            "expected": "Kesin: Mobilite (düz zemin), Termal (hiperkurak ΔT — v1'de askıda) · Aday: Yüzey (evaporit)",
            "ice": "yok",
            "rationale": "Zoë otonom sürüş testleri düz çöl mobilitesini, 4 yıllık meteoroloji ise hiperkurak günlük sıcaklık rejimini doğrular; dik krater duvarlarını temsil etmez.",
            "source": "Wettergreen et al. (2005) https://doi.org/10.1109/ROBOT.2005.1570227 · McKay et al. (2003) https://doi.org/10.1089/153110703769016460 · Navarro-González et al. (2003) https://doi.org/10.1126/science.1089143",
        },
        "en": {
            "expected": "Confirmed: Mobility (flat terrain), Thermal (hyperarid ΔT — suspended in v1) · Candidate: Surface (evaporite)",
            "ice": "none",
            "rationale": "Zoë rover trials validate flat-desert mobility and 4-year meteorology documents a hyperarid diurnal thermal regime; does not represent steep crater walls.",
            "source": "Wettergreen et al. (2005) https://doi.org/10.1109/ROBOT.2005.1570227 · McKay et al. (2003) https://doi.org/10.1089/153110703769016460 · Navarro-González et al. (2003) https://doi.org/10.1126/science.1089143",
        },
    },
    "earth_haughton_crater": {
        "tr": {
            "expected": "Kesin: Mobilite, Termal (permafrost — v1'de askıda) · Aday: Yüzey (karbonat breşi)",
            "ice": "var (sürekli permafrost + yeraltı buzu)",
            "rationale": "Haughton-Mars Projesi çarpma krateri içinde rover/EVA mobilitesini ve yüksek Arktik yeraltı buzu/permafrost rejimini doğrulamıştır.",
            "source": "Lee & Osinski (2005) https://doi.org/10.1111/j.1945-5100.2005.tb00144.x · Osinski et al. (2005) https://doi.org/10.1111/j.1945-5100.2005.tb00147.x · Thomson et al. (2012) https://doi.org/10.1029/2012JE004053",
        },
        "en": {
            "expected": "Confirmed: Mobility, Thermal (permafrost — suspended in v1) · Candidate: Surface (carbonate breccia)",
            "ice": "present (continuous permafrost + ground ice)",
            "rationale": "The Haughton-Mars Project validated rover/EVA mobility and High Arctic ground-ice/permafrost regimes inside the impact structure.",
            "source": "Lee & Osinski (2005) https://doi.org/10.1111/j.1945-5100.2005.tb00144.x · Osinski et al. (2005) https://doi.org/10.1111/j.1945-5100.2005.tb00147.x · Thomson et al. (2012) https://doi.org/10.1029/2012JE004053",
        },
    },
    "earth_mauna_loa_hiseas": {
        "tr": {
            "expected": "Kesin: Mobilite · Aday: Termal (askıda), Yüzey (koyu bazalt)",
            "ice": "veri yok (HI-SEAS ~2500 m noktasında)",
            "rationale": "HI-SEAS analog görevleri Mauna Loa bazalt akıntıları üzerinde EVA ve rover saha jeolojisi mobilitesini doğrulamıştır.",
            "source": "Shiro et al. (2022) https://doi.org/10.1016/j.pss.2021.105409",
        },
        "en": {
            "expected": "Confirmed: Mobility · Candidate: Thermal (suspended), Surface (dark basalt)",
            "ice": "no data (at ~2500 m HI-SEAS site)",
            "rationale": "HI-SEAS analog missions validated EVA and rover field-geology mobility on Mauna Loa basalt flows.",
            "source": "Shiro et al. (2022) https://doi.org/10.1016/j.pss.2021.105409",
        },
    },
    "earth_mcmurdo_wright_valley": {
        "tr": {
            "expected": "Kesin: Termal (soğuk çöl permafrost — v1'de askıda) · Aday: Mobilite, Yüzey (karma dolerit/kar)",
            "ice": "var (kuru/buz-çimentolu permafrost)",
            "rationale": "Dry Valleys çalışmaları soğuk çöl mikrokliması, termal kasılma poligonları ve yeraltı gözenek buzu kararlılığını doğrudan doğrular.",
            "source": "Marchant & Head (2007) https://doi.org/10.1016/j.icarus.2007.06.018 · Levy et al. (2010) https://doi.org/10.1016/j.icarus.2009.09.005",
        },
        "en": {
            "expected": "Confirmed: Thermal (cold-desert permafrost — suspended in v1) · Candidate: Mobility, Surface (mixed dolerite/snow)",
            "ice": "present (dry/ice-cemented permafrost)",
            "rationale": "Dry Valleys studies directly validate cold-desert microclimate zonation, thermal contraction polygons, and subsurface pore-ice stability.",
            "source": "Marchant & Head (2007) https://doi.org/10.1016/j.icarus.2007.06.018 · Levy et al. (2010) https://doi.org/10.1016/j.icarus.2009.09.005",
        },
    },
    "earth_lanzarote_timanfaya": {
        "tr": {
            "expected": "Kesin: Mobilite · Aday: Yüzey (koyu bazalt/skorya)",
            "ice": "veri yok",
            "rationale": "ESA PANGAEA astronot eğitimi ve karşılaştırmalı volkanik morfoloji çalışmaları Lanzarote bazalt akıntılarını saha mobilite analogu kılar.",
            "source": "Sauro et al. (2023) https://doi.org/10.1016/j.actaastro.2022.12.034 · Sauro et al. (2020) https://doi.org/10.1016/j.earscirev.2020.103288",
        },
        "en": {
            "expected": "Confirmed: Mobility · Candidate: Surface (dark basalt/scoria)",
            "ice": "no data",
            "rationale": "ESA PANGAEA astronaut training and comparative volcanic morphology studies establish Lanzarote basalt flows as a field mobility analogue.",
            "source": "Sauro et al. (2023) https://doi.org/10.1016/j.actaastro.2022.12.034 · Sauro et al. (2020) https://doi.org/10.1016/j.earscirev.2020.103288",
        },
    },
    "earth_meteor_crater_arizona": {
        "tr": {
            "expected": "Kesin: Mobilite · Aday: Termal (askıda), Yüzey (ejekta + seyrek çalı)",
            "ice": "veri yok",
            "rationale": "Kring rehberi ve krater jeomorfometrisi Meteor Crater'i dik basit çarpma krateri duvar/kenar eğimi ve Apollo eğitimi standardı olarak kurar.",
            "source": "Kring (2017) https://www.lpi.usra.edu/publications/books/barringer_crater_guidebook/chapter_6.pdf · Poelchau et al. (2009) https://doi.org/10.1029/2008JE003235 · Shoemaker (1959) https://doi.org/10.3133/ofr59108",
        },
        "en": {
            "expected": "Confirmed: Mobility · Candidate: Thermal (suspended), Surface (ejecta + sparse shrub)",
            "ice": "no data",
            "rationale": "Kring's guidebook and crater geomorphometry establish Meteor Crater as the standard for steep simple impact crater rim/wall slopes and Apollo training.",
            "source": "Kring (2017) https://www.lpi.usra.edu/publications/books/barringer_crater_guidebook/chapter_6.pdf · Poelchau et al. (2009) https://doi.org/10.1029/2008JE003235 · Shoemaker (1959) https://doi.org/10.3133/ofr59108",
        },
    },
    "earth_craters_of_the_moon": {
        "tr": {
            "expected": "Kesin: Mobilite · Aday: Yüzey (koyu bazalt)",
            "ice": "veri yok",
            "rationale": "NASA BASALT ve FINESSE programları Craters of the Moon bazalt akıntılarını pürüzlülük ve EVA/rover saha operasyonları analogu olarak seçmiştir.",
            "source": "Hughes et al. (2019) https://doi.org/10.1089/ast.2018.1847 · Lim et al. (2019) https://doi.org/10.1089/ast.2018.1869",
        },
        "en": {
            "expected": "Confirmed: Mobility · Candidate: Surface (dark basalt)",
            "ice": "no data",
            "rationale": "NASA BASALT and FINESSE programs selected Craters of the Moon basalt flows as a roughness and EVA/rover field operations analogue.",
            "source": "Hughes et al. (2019) https://doi.org/10.1089/ast.2018.1847 · Lim et al. (2019) https://doi.org/10.1089/ast.2018.1869",
        },
    },
    "earth_svalbard_bockfjorden": {
        "tr": {
            "expected": "Aday: Mobilite (alkali bazalt konisi), Termal (Arktik permafrost — askıda) · (fiyort/tundra karışımı)",
            "ice": "var (yüksek Arktik sürekli permafrost)",
            "rationale": "Sverrefjellet bazalt konisi ve Arktik permafrost AMASE sahasıdır; kıyı fiyort suyu (%15.5) ve tundra (%43.1) 1 km penceresini karıştırır.",
            "source": "Treiman (2012) https://doi.org/10.3402/polar.v31i0.17320 · Humlum et al. (2003) https://doi.org/10.3402/polar.v22i2.6455",
        },
        "en": {
            "expected": "Candidate: Mobility (alkali basalt cone), Thermal (Arctic permafrost — suspended) · (fjord/tundra mix)",
            "ice": "present (High Arctic continuous permafrost)",
            "rationale": "Sverrefjellet basalt cone and Arctic permafrost form an AMASE field site; coastal fjord water (15.5%) and tundra (43.1%) mix the 1 km window.",
            "source": "Treiman (2012) https://doi.org/10.3402/polar.v31i0.17320 · Humlum et al. (2003) https://doi.org/10.3402/polar.v22i2.6455",
        },
    },
    "earth_lunar_crater_nevada": {
        "tr": {
            "expected": "Kesin: Mobilite (SAR yüzey pürüzlülüğü) · Aday: Termal (GRSFE TIMS — askıda), Yüzey (playa/koni)",
            "ice": "veri yok",
            "rationale": "Evans et al. (1992) AIRSAR deneylerinde yüzey pürüzlülüğü yer-gerçeği kalibrasyonu için LCVF'yi birincil saha olarak ölçmüştür.",
            "source": "Evans et al. (1992) https://doi.org/10.1109/36.134087 · Valentine et al. (2017) https://doi.org/10.1130/GES01428.1 · Scott & Trask (1971) https://doi.org/10.3133/pp599i",
        },
        "en": {
            "expected": "Confirmed: Mobility (SAR surface roughness) · Candidate: Thermal (GRSFE TIMS — suspended), Surface (playa/cone)",
            "ice": "no data",
            "rationale": "Evans et al. (1992) measured LCVF as a primary ground-truth calibration site for surface roughness in AIRSAR experiments.",
            "source": "Evans et al. (1992) https://doi.org/10.1109/36.134087 · Valentine et al. (2017) https://doi.org/10.1130/GES01428.1 · Scott & Trask (1971) https://doi.org/10.3133/pp599i",
        },
    },
}

# Data-contract feature codes → readable names (code kept as a hint).
FEATURE_LABELS: dict[str, dict[str, str]] = {
    "slope_mean": {
        "tr": "Ortalama eğim (slope_mean)",
        "en": "Mean slope (slope_mean)",
    },
    "slope_p90": {
        "tr": "Dik yamaç payı — %90 yüzdelik (slope_p90)",
        "en": "90th-percentile slope (slope_p90)",
    },
    "roughness": {
        "tr": "Yüzey pürüzlülüğü (roughness)",
        "en": "Surface roughness (roughness)",
    },
    "relief": {
        "tr": "Yükselti farkı / rölyef (relief)",
        "en": "Elevation range / relief (relief)",
    },
    "temp_amplitude": {
        "tr": "Gün-gece sıcaklık farkı (temp_amplitude)",
        "en": "Day–night temperature swing (temp_amplitude)",
    },
    "thermal_inertia": {
        "tr": "Termal atalet (thermal_inertia)",
        "en": "Thermal inertia (thermal_inertia)",
    },
    "albedo": {
        "tr": "Yüzey parlaklığı (albedo)",
        "en": "Surface brightness (albedo)",
    },
}

# Lithology class codes → readable names; unknown codes pass through as-is.
LITHOLOGY_LABELS: dict[str, dict[str, str]] = {
    "regolith": {
        "tr": "regolit (kırıntılı yüzey örtüsü)",
        "en": "regolith (broken-surface layer)",
    },
    "anorthosite": {
        "tr": "anortozit (Ay kabuğu kayası)",
        "en": "anorthosite (lunar crust rock)",
    },
    "impact_breccia": {
        "tr": "krater döküntü kayası (breş)",
        "en": "impact breccia (crater debris rock)",
    },
    "regolith_permafrost": {
        "tr": "donmuş regolit (permafrost)",
        "en": "frozen regolith (permafrost)",
    },
    "basalt": {"tr": "bazalt", "en": "basalt"},
    "pyroclastic_tuff": {
        "tr": "volkanik tüflü (piroklastik tüf)",
        "en": "pyroclastic tuff",
    },
    "evaporite": {
        "tr": "tuz çökeltisi (evaporit)",
        "en": "salt deposit (evaporite)",
    },
}

# Feature-gaps table column headers, in fixed column order.
GAP_COLUMNS: dict[str, list[str]] = {
    "tr": [
        "Ölçüt", "Referans değeri", "Aday değeri", "Fark", "Fark (σ)",
        "Referans kaynağı", "Referans çözünürlüğü (m)",
        "Aday kaynağı", "Aday çözünürlüğü (m)",
    ],
    "en": [
        "Criterion", "Reference value", "Candidate value", "Difference",
        "Diff (σ)", "Reference source", "Reference resolution (m)",
        "Candidate source", "Candidate resolution (m)",
    ],
}


def t(key: str, lang: str = DEFAULT_LANG, **kwargs: object) -> str:
    """Return the translated string for `key`, formatted with `kwargs`."""
    entry = TEXTS.get(key)
    if entry is None:
        raise KeyError(f"i18n: unknown key {key!r}")
    text = entry.get(lang) or entry["tr"]
    return text.format(**kwargs) if kwargs else text


def moon_site_label(site_id: str, lang: str = DEFAULT_LANG) -> str:
    """Clean display name for a Moon reference site_id."""
    return MOON_SITE_LABELS.get(site_id, {}).get(lang) or site_id


def feature_label(code: str, lang: str = DEFAULT_LANG) -> str:
    """Readable name for a feature code; unknown codes pass through."""
    return FEATURE_LABELS.get(code, {}).get(lang) or code


def lith_label(code: str, lang: str = DEFAULT_LANG) -> str:
    """Readable name for a lithology class; unknown codes pass through."""
    return LITHOLOGY_LABELS.get(code, {}).get(lang) or code
