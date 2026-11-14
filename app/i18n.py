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
    "subtitle": {
        "tr": ("Bu uygulama Ay üzerinde seçilen bir bölgeyi Dünya üzerindeki "
               "{n} sahayla karşılaştırır. v1 sayısal skorlaması iki aktif "
               "eksende yürür: arazi/eğim (Mobilite) ve yüzey parlaklığı "
               "(Yüzey). Termal ekseni Ay günlük sıcaklık döngüsü tanımı "
               "nedeniyle v1'de askıdadır. Puanlar 0–1 arası benzerlik "
               "indeksidir, olasılık değildir."),
        "en": ("This app compares a selected Moon region with {n} Earth "
               "sites. v1 numeric scoring runs on two active axes: "
               "terrain/slope (Mobility) and surface brightness (Surface). "
               "The Thermal axis is suspended in v1 due to diurnal cycle "
               "definition mismatch. Scores are 0–1 similarity indices, "
               "not probabilities."),
    },
    "thermal_note": {
        "tr": ("Karar #30 (Termal Eksen Askıda): Ay tarafında temp_amplitude "
               "ve her iki gök cisminde thermal_inertia v1'de bilinçli olarak "
               "NaN bırakılmıştır; genel skorlar yalnızca Mobilite ve Yüzey "
               "eksenlerinden hesaplanır."),
        "en": ("Decision #30 (Thermal Axis Suspended): Lunar temp_amplitude "
               "and both bodies' thermal_inertia are intentionally kept NaN "
               "in v1; overall scores combine Mobility and Surface only."),
    },
    # ── sidebar ──────────────────────────────────────────────────────────────
    "settings_header": {"tr": "⚙️ Ayarlar", "en": "⚙️ Settings"},
    "theme_label": {"tr": "Görünüm teması", "en": "Visual theme"},
    "theme_moon_grey": {
        "tr": "🌑 Ay · Siyah–Gri",
        "en": "🌑 Moon · Black–Grey",
    },
    "theme_earth_blue": {
        "tr": "🌍 Dünya · Mavi",
        "en": "🌍 Earth · Blue",
    },
    "body_moon": {"tr": "Ay", "en": "Moon"},
    "ref_site_label_moon": {
        "tr": "Referans saha (Ay'dan)",
        "en": "Reference site (from the Moon)",
    },
    "ref_site_caption": {
        "tr": "Enlem {lat}°, Boylam {lon}° · Zemin: {lith}",
        "en": "Latitude {lat}°, Longitude {lon}° · Ground: {lith}",
    },
    "ref_site_tooltip": {
        "tr": "Sahanın kod adı: {site_id}",
        "en": "Site code: {site_id}",
    },
    "mission_label": {
        "tr": "Görev / kullanım amacı",
        "en": "Mission / use case",
    },
    "mission_default": {
        "tr": "Dengeli (tüm ölçütler eşit ağırlıkta)",
        "en": "Balanced (all criteria equal)",
    },
    "mission_rover_mobility": {
        "tr": "Gezgin araç arazi testi",
        "en": "Rover mobility test",
    },
    "mission_isru_ice": {
        "tr": "Kaynak / buz taraması (v1: buz nitel; termal askıda — yüzey ağırlıklı)",
        "en": "Resource / ice prospecting (v1: ice qualitative; thermal suspended — surface-weighted)",
    },
    "mission_isru_note": {
        "tr": ("ℹ️ Buz/permafrost verisi (E8) v1 sayısal skoruna girmez ve Ay "
               "termali askıdadır (NaN). Aktif sayısal oran Mobilite : Yüzey = "
               "1 : 2 (yüzey ağırlıklı) olarak çalışır."),
        "en": ("ℹ️ Ice/permafrost records (E8) do not enter numeric scores in "
               "v1 and lunar thermal data are suspended (NaN). Active numeric "
               "weights run at Mobility : Surface = 1 : 2 (surface-weighted)."),
    },
    "mission_radar_calibration": {
        "tr": "Yer altı radar kalibrasyonu",
        "en": "Subsurface radar calibration",
    },
    "top_n_label": {
        "tr": "Gösterilecek Dünya sahası sayısı",
        "en": "Number of Earth sites to show",
    },
    # ── reference measurements ───────────────────────────────────────────────
    "ref_subheader": {
        "tr": "📍 Referans saha: {name} ({body})",
        "en": "📍 Reference site: {name} ({body})",
    },
    "ref_expander": {
        "tr": "Referans sahanın ölçümleri",
        "en": "Measurements of the reference site",
    },
    "ref_col_feature": {"tr": "Ölçüt", "en": "Criterion"},
    "ref_col_value": {"tr": "Değer", "en": "Value"},
    "ref_col_unit": {"tr": "Birim", "en": "Unit"},
    "ref_col_sd": {"tr": "Belirsizlik (±)", "en": "Uncertainty (±)"},
    "ref_col_res": {"tr": "Çözünürlük (m)", "en": "Resolution (m)"},
    "ref_col_src": {"tr": "Kaynak", "en": "Source"},
    "ref_table_caption": {
        "tr": ("Değer: saha çevresinde ölçülen ortalama. Belirsizlik (±): "
               "ölçüm hatası. Çözünürlük (m): verinin piksel boyutu — küçük "
               "sayı, daha ayrıntılı veri demektir. Kaynak: ölçümü yapan uzay "
               "aracı ve veri seti."),
        "en": ("Value: mean measured around the site. Uncertainty (±): "
               "measurement error. Resolution (m): pixel size of the data — "
               "smaller means more detail. Source: spacecraft and dataset "
               "that produced the measurement."),
    },
    "temp_note": {
        "tr": ("Dünya sıcaklık genliği 2024 MODIS gün-gece ortalamasıdır; "
               "Ay tarafı günlük döngü uyumsuzluğu nedeniyle v1'de askıdadır (NaN)."),
        "en": ("Earth temperature swing is the 2024 MODIS day–night annual mean; "
               "the lunar side is suspended in v1 (NaN) due to diurnal-cycle mismatch."),
    },
    "ref_value_suspended": {
        "tr": "— (v1 askıda)",
        "en": "— (suspended v1)",
    },
    # ── tabs ─────────────────────────────────────────────────────────────────
    "tab_map": {"tr": "🗺️ Harita", "en": "🗺️ Map"},
    "tab_radar": {"tr": "📡 Eksen Grafikleri", "en": "📡 Axis Charts"},
    "tab_terrain": {"tr": "⛰️ 3D Arazi", "en": "⛰️ 3D Terrain"},
    "tab_table": {"tr": "📊 Skor & Portföy", "en": "📊 Scores & Portfolio"},
    "tab_validation": {"tr": "🧭 Sıra Tanısı (Doğrulama)", "en": "🧭 Rank Diagnostic"},
    "tab_portfolio": {"tr": "🧭 Ziyaret Portföyü", "en": "🧭 Visit Portfolio"},
    "tab_breakdown": {
        "tr": "⚠️ Analojinin Sınırları",
        "en": "⚠️ Limits of the Analogy",
    },
    # ── map tab ──────────────────────────────────────────────────────────────
    "map_heading": {
        "tr": ("Haritadaki her nokta bir Dünya sahasıdır. Nokta ne kadar "
               "büyük ve yeşilse o saha seçili Ay bölgesine o kadar çok "
               "benzer. Küçük ve kırmızı nokta daha az benzer demektir."),
        "en": ("Each dot on this map is an Earth site. The bigger and "
               "greener the dot, the more that site resembles the selected "
               "Moon region. A small red dot means less similarity."),
    },
    "map_caption": {
        "tr": ("Mavi halkalı noktalar literatürden bilinen referans analog "
               "sahalarıdır (bazıları Ekvatoral koyu Ay bazaltı ya da düz "
               "Mars/permafrost sahasıdır — her Ay kraterinde üstte "
               "çıkmamaları eksen bazlı fiziksel ayrımı gösterir). İç dolgu "
               "rengi (yeşilden kırmızıya) seçili Ay bölgesi için aktif "
               "benzerlik indeksini gösterir."),
        "en": ("Blue-ringed dots mark known literature analogue benchmarks "
               "(several are dark Mare basalt or flat Mars/permafrost testbeds "
               "— ranking lower on steep bright crater rims reflects genuine "
               "axis mismatch rather than missing data). Fill color (green to "
               "red) encodes the active similarity index for the selected Moon site."),
    },
    "map_show_all_val": {
        "tr": "Bilinen tüm 10 referans analog sahasını (mavi halkalar) haritada her zaman göster",
        "en": "Always show all 10 reference analogue benchmarks (blue rings) on the map",
    },
    "map_tooltip": {
        "tr": ("<b>{name}</b><br/>Rol: {role}<br/>Genel Skor: {score}"
               "<br/>Mobilite: {mob} · Yüzey: {surf}"
               "<br/>Aralık: {interval}<br/>Zemin: {lith}"),
        "en": ("<b>{name}</b><br/>Role: {role}<br/>Overall: {score}"
               "<br/>Mobility: {mob} · Surface: {surf}"
               "<br/>Interval: {interval}<br/>Ground: {lith}"),
    },
    "map_fallback": {
        "tr": "Harita kütüphanesi eksik; basit haritaya geçildi.",
        "en": "Map library missing; switched to the simple map.",
    },
    "role_validation": {"tr": "Bilinen analog", "en": "Known analogue"},
    "role_candidate": {"tr": "Aday saha", "en": "Candidate site"},
    # ── radar tab ────────────────────────────────────────────────────────────
    "radar_caption": {
        "tr": ("Aktif iki ölçüt için benzerlik skoru (0–1) ve %5–%95 Monte Carlo "
               "belirsizlik aralığı. Termal ekseni v1'de askıdadır (NaN)."),
        "en": ("Similarity score (0–1) and 5th–95th Monte Carlo uncertainty "
               "interval on the two active criteria. Thermal is suspended in v1 (NaN)."),
    },
    "radar_line": {
        "tr": ("Genel: {score} · Belirsizlik: {interval} · "
               "Aktif ölçüt: {n}/{total} · Mobilite: {mob} · Yüzey: {surf} · Zemin: {lith}"),
        "en": ("Overall: {score} · Uncertainty: {interval} · "
               "Active axes: {n}/{total} · Mobility: {mob} · Surface: {surf} · Ground: {lith}"),
    },
    "uncertainty_unavailable": {
        "tr": "belirsizlik aralığı hesaplanamıyor",
        "en": "uncertainty interval unavailable",
    },
    "q95_label": {"tr": "üst sınır (%95)", "en": "upper bound (95%)"},
    "q05_label": {"tr": "alt sınır (%5)", "en": "lower bound (5%)"},
    "axis_mobility": {"tr": "Mobilite", "en": "Mobility"},
    "axis_thermal": {"tr": "Termal", "en": "Thermal"},
    "axis_surface": {"tr": "Yüzey", "en": "Surface"},
    "scatter_heading": {
        "tr": "### Fiziksel Özellik Uzayı: Ortalama Eğim vs Geniş Bant Albedo (40 Dünya Sahası + Ay Referansı)",
        "en": "### Physical Feature Space: Mean Slope vs Broadband Albedo (40 Earth Sites + Moon Reference)",
    },
    "scatter_x": {"tr": "Ortalama eğim (slope_mean, °)", "en": "Mean slope (slope_mean, °)"},
    "scatter_y": {"tr": "Geniş bant albedo (0–1)", "en": "Broadband albedo (0–1)"},
    "scatter_colorbar": {"tr": "Genel skor", "en": "Overall score"},
    "scatter_caption": {
        "tr": ("Nokta konumu ham uydu ölçümlerini (`slope_mean` ve `albedo`), nokta boyutu yüzey pürüzlülüğünü (`roughness`), "
               "renk genel benzerlik indeksini, dış halka ise bilinen 10 doğrulama analogunu gösterir."),
        "en": ("Position reflects raw orbital features (`slope_mean` vs `albedo`), marker size encodes `roughness`, "
               "color shows overall similarity index, and highlighted rings mark the 10 known validation sites."),
    },
    "expanded_note": {
        "tr": ("* Yıldızlı aralıklar, nokta tahmini ham P5–P95 belirsizlik sınırlarının dışına düştüğünde "
               "yalnızca gösterimde `expanded_interval` ile genişletilmiştir; sayısal skorlar değiştirilmez."),
        "en": ("* Starred intervals indicate display-only widening (`expanded_interval`) where the point score sits "
               "outside raw P5–P95 draws; underlying numeric scores are never altered."),
    },
    # ── 3D terrain tab ───────────────────────────────────────────────────────
    "body_earth": {"tr": "Dünya", "en": "Earth"},
    "terrain_intro": {
        "tr": ("Seçili Ay bölgesi ile seçili Dünya sahasının arazisi yan "
               "yana 3D yüzey olarak gösterilir. Renk, arazi "
               "gölgelendirmesinden gelir. Uydu görüntüleri için Analojinin "
               "Sınırları sekmesindeki 2D kartlara bakın."),
        "en": ("The terrain of the selected Moon region and the selected "
               "Earth site are shown side by side as 3D surfaces. Colour "
               "comes from terrain shading. For satellite imagery see the "
               "2D cards on the Limits of the Analogy tab."),
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
        "tr": "Dikey ölçek abartılı gösteriliyor",
        "en": "Vertical scale is exaggerated",
    },
    "terrain_orbit_label": {
        "tr": "Kamera yörünge açısı (derece)",
        "en": "Camera orbit angle (degrees)",
    },
    "terrain_hover": {
        "tr": ("Sağa: %{x:.2f} km<br/>İleri: %{y:.2f} km"
               "<br/>Yükselti: %{z:.0f} m<extra></extra>"),
        "en": ("Right: %{x:.2f} km<br/>Forward: %{y:.2f} km"
               "<br/>Elevation: %{z:.0f} m<extra></extra>"),
    },
    "terrain_card_source": {
        "tr": ("Kaynak: {src} · Çözünürlük: {res} m/piksel · "
               "Pencere: {km} km · Yükselti verisi"),
        "en": ("Source: {src} · Resolution: {res} m/pixel · "
               "Window: {km} km · elevation data"),
    },
    "terrain_card_stub": {
        "tr": ("Örnek arazi verisi · istatistik kaynağı: {src} · "
               "Çözünürlük: {res} m/piksel · Pencere: {km} km"),
        "en": ("Generated sample terrain · stats source: {src} · "
               "Resolution: {res} m/pixel · Window: {km} km"),
    },
    "terrain_stub_note": {
        "tr": ("Bu 3D kartlarda örnek arazi verisi kullanılıyor. Örnek "
               "arazi, sahaların gerçek ölçüm istatistiklerinden (eğim, "
               "pürüz, yükselti farkı) üretilir; gerçek yükselti paftaları "
               "geldiğinde kartlar otomatik olarak gerçeğe döner."),
        "en": ("These 3D cards use generated sample terrain. The sample is "
               "built from the sites' real measured statistics (slope, "
               "roughness, relief); the cards switch to real elevation "
               "tiles automatically once they arrive."),
    },
    # ── score table ──────────────────────────────────────────────────────────
    "table_caption": {
        "tr": ("Her Dünya sahası için görev ağırlıklı genel benzerlik ve "
               "ölçüt bazında skorlar — her sayının yanında belirsizlik "
               "aralığı da yazar."),
        "en": ("Mission-weighted overall similarity and per-criterion scores "
               "for every Earth site — each number carries its uncertainty "
               "range."),
    },
    "col_site": {"tr": "Saha", "en": "Site"},
    "col_role": {"tr": "Rol", "en": "Role"},
    "col_lith": {"tr": "Zemin (litoloji)", "en": "Ground (lithology)"},
    "col_overall": {"tr": "Genel", "en": "Overall"},
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
        "tr": ("Termal ekseni (temp_amplitude ve thermal_inertia) Karar #30 "
               "uyarınca v1'de askıda (NaN) olduğundan tabloda yalnızca aktif "
               "Mobilite ve Yüzey skorları gösterilir. Zemin sütunundaki ✓ "
               "işareti referans ile aynı kaya sınıfını gösterir; skora girmez."),
        "en": ("Per Decision #30, Thermal (temp_amplitude and thermal_inertia) "
               "is suspended in v1 (NaN), so only active Mobility and Surface "
               "scores appear. A ✓ in ground means the same lithology class "
               "as the reference; informational only."),
    },
    # ── portfolio card (under score table) ───────────────────────────────────
    "portfolio_heading": {
        "tr": "🧭 Kompakt Ziyaret Portföyü (Test Kümesi)",
        "en": "🧭 Compact Visit Portfolio (Test Set)",
    },
    "portfolio_desc": {
        "tr": ("Tek bir Dünya sahası tüm eksenleri kapsamadığında, seçili eşikte "
               "en fazla aktif ekseni kapsayan en küçük saha kümesi seçilir. "
               "Eşik kalibre edilmiş bir olasılık değil, yalnızca sezgisel bir "
               "indeks ayarıdır."),
        "en": ("When no single Earth site covers all axes, this selects the "
               "smallest site set covering the most active axes at the chosen "
               "threshold. The threshold is a heuristic index setting, not a "
               "calibrated probability."),
    },
    "portfolio_threshold_label": {
        "tr": "Portföy kapsam eşiği (benzerlik indeksi)",
        "en": "Portfolio coverage threshold (similarity index)",
    },
    "portfolio_none": {
        "tr": "Seçili eşikte (≥ {thr:.2f}) hiçbir Dünya sahası aktif bir ekseni tek başına kapsamıyor; tüm açık eksenler yüksek uyuşmazlık / laboratuvar doğrulaması gerektirir.",
        "en": "At ≥ {thr:.2f}, no Earth site reaches coverage on any active axis; remaining gaps stay in simulation/lab verification.",
    },
    "portfolio_col_order": {"tr": "Sıra", "en": "Order"},
    "portfolio_col_site": {"tr": "Seçilen Saha", "en": "Selected Site"},
    "portfolio_col_role": {"tr": "Rol", "en": "Role"},
    "portfolio_col_covered": {"tr": "Kapsanan Eksen(ler) (≥ eşik)", "en": "Covered Axes (≥ threshold)"},
    "portfolio_col_scores": {"tr": "Eksen Skorları", "en": "Axis Scores"},
    "portfolio_best_mobility_note": {
        "tr": "ℹ️ Mobilite ekseni mevcut eşiği tek başına aşamasa da bu havuzdaki en yüksek Mobilite skoru: **{site}** ({score}).",
        "en": "ℹ️ Although Mobility falls below threshold here, the highest Mobility candidate in the pool is **{site}** ({score}).",
    },
    "portfolio_uncovered_label": {
        "tr": "Kapsam dışı / laboratuvara kalan eksenler:",
        "en": "Uncovered axes / deferred to lab or simulation:",
    },
    "portfolio_uncovered_thermal_note": {
        "tr": "Termal (v1'de askıda — günlük döngü farkı + ekstrem kutup salınımı)",
        "en": "Thermal (suspended in v1 — diurnal mismatch + extreme polar swings)",
    },
    "portfolio_all_active_covered": {
        "tr": "Aktif iki sayısal eksen (Mobilite + Yüzey) ≥ {thr:.2f} eşiğinde seçilen küme ile kapsanıyor; yalnızca v1'de askıda olan Termal ekseni açıkta kalıyor.",
        "en": "Both active numeric axes (Mobility + Surface) are covered at ≥ {thr:.2f}; only the v1-suspended Thermal axis remains uncovered.",
    },
    # ── validation tab (10-row descriptive rank diagnostic) ──────────────────
    "val_intro": {
        "tr": ("⚠️ **Bağımsız bir holdout doğrulaması değil, betimsel sıra tanısıdır:** "
               "40 sahanın tamamı Z-ölçeklemesine katılır; skorlayıcı rol etiketlerini "
               "görmeden tüm sahaları sıralar. Aşağıdaki beklenen eksenler ve kaynaklar "
               "(`docs/validation_expectations.md`), sıralama çıktılarına bakılmadan "
               "**ön-kayıtlı** literatürden alınmıştır."),
        "en": ("⚠️ **Descriptive rank diagnostic, not independent holdout validation:** "
               "all 40 sites enter Z-standardization while the scorer ranks blindly "
               "without role labels. Expected axes and citations below are "
               "**pre-registered** from `docs/validation_expectations.md`."),
    },
    "val_summary_note": {
        "tr": ("**v1 aktif eksen özeti (Mobilite & Yüzey):** Birincil literatürde "
               "Mobilite için **8/10** sahada kesin beklenti vardır; McMurdo yalnız "
               "Termal (v1 askıda) literatüründedir, Svalbard ise aktif eksenlerde "
               "doğrulanmış kaynak taşımaz. Yüzey (broadband albedo) için 10 sahada "
               "da kesin birincil yayın doğrulanmamıştır."),
        "en": ("**v1 active-axis summary (Mobility & Surface):** Primary literature "
               "documents Mobility expectations for **8/10** validation sites; "
               "McMurdo is documented on Thermal only (suspended in v1) and Svalbard "
               "has no verified active-axis analogue study."),
    },
    "val_sort_label": {
        "tr": "Tabloyu şuna göre sırala:",
        "en": "Sort table by:",
    },
    "val_sort_mobility": {"tr": "Mobilite Sırası", "en": "Mobility Rank"},
    "val_sort_overall": {"tr": "Genel Sıra", "en": "Overall Rank"},
    "val_sort_surface": {"tr": "Yüzey Sırası", "en": "Surface Rank"},
    "val_why_low_note": {
        "tr": ("💡 **Bazı bilinen sahalar (ör. Atacama, Haughton, Mauna Loa) neden düşük genel sırada görünüyor?** "
               "İki fiziksel nedeni var: **(1) Referans krater geometrisi:** Seçili *Shackleton Kenarı* **18.5° dik eğime** "
               "ve 501 m yükselti farkına sahiptir; **Atacama (2.65°)** ve **Haughton (3.51°)** düz Mars/permafrost çöl "
               "sahalarıdır (daha yatık **Faustini Kenarı** seçildiğinde Mobilite'de `#6–#8` sıraya çıkarlar), **Etna (22.7°)** "
               "ise Shackleton'da bile **Mobilite'de #3 / 40**'tır. **(2) Albedo ayrımı:** Etna (`0.047`), Mauna Loa (`0.030`) "
               "ve Lanzarote (`0.063`) koyu Ay Maria bazaltı albedosuna yakındır; Güney Kutbu (`0.147`) Yüzey ekseninde onları "
               "aşağı çeker. Bilinen sahaları yapay ağırlıkla yukarı zorlamak (`tuning`) bilimsel dürüstlük gereği yapılmaz."),
        "en": ("💡 **Why do some famous analogues (e.g., Atacama, Haughton, Mauna Loa) rank low overall here?** "
               "Two physical reasons: **(1) Crater geometry:** *Shackleton Rim* has an **18.5° steep wall** and 501 m relief, "
               "whereas **Atacama (2.65°)** and **Haughton (3.51°)** are flat Mars/Arctic analogues (they climb to `#6–#8` on "
               "gentler **Faustini Rim**), while **Mt. Etna (22.7°)** still ranks **#3 / 40 on Mobility** here. **(2) Albedo mismatch:** "
               "Etna (`0.047`), Mauna Loa (`0.030`), and Lanzarote (`0.063`) are ultra-dark basalt matching lunar Maria rather "
               "than brighter highlands regolith (`0.147`). We intentionally avoid tuning weights to inflate known benchmarks."),
    },
    "val_col_site": {"tr": "Doğrulama Sahası", "en": "Validation Site"},
    "val_col_overall_rank": {"tr": "Genel Sıra", "en": "Overall Rank"},
    "val_col_mob_rank": {"tr": "Mobilite Sırası", "en": "Mobility Rank"},
    "val_col_surf_rank": {"tr": "Yüzey Sırası", "en": "Surface Rank"},
    "val_col_expected": {"tr": "Beklenen Eksen (v1)", "en": "Expected Axis (v1)"},
    "val_col_ice": {"tr": "Buz / Permafrost (nitel E8)", "en": "Ice / Permafrost (E8)"},
    "val_col_rationale": {"tr": "Gerekçe", "en": "Rationale"},
    "val_col_source": {"tr": "Kaynak (DOI/URL)", "en": "Source (DOI/URL)"},
    "val_exp_mobility": {"tr": "Mobilite (Kesin)", "en": "Mobility (Confirmed)"},
    "val_exp_thermal_only": {"tr": "Yalnız Termal (v1 askıda)", "en": "Thermal only (v1 suspended)"},
    "val_exp_none": {"tr": "Kaynak doğrulanamadı", "en": "No verified primary source"},
    # ── analogy limits tab ───────────────────────────────────────────────────
    "breakdown_notes": {
        "tr": (
            "Hiçbir Dünya sahası Ay'in tüm koşullarını aynı anda sunmaz. "
            "Aşağıdaki koşullar Dünya üzerinde doğal olarak bulunmadığı "
            "için sahada test edilemez:\n\n"
            "- **Yerçekimi:** Ay yüzeyinde yerçekimi, Dünya'nınkinin "
            "yaklaşık altıda biridir. Zemin malzemesinin davranışı ve "
            "tozun çökme hızı bu yüzden Dünya'da tam olarak test edilemez.\n"
            "- **Atmosfer:** Ay'da hemen hemen hiç atmosfer yoktur. "
            "Dünya yüzeyinde böyle bir boşluk ortamı doğal olarak "
            "bulunmaz.\n"
            "- **Radyasyon:** Ay'da manyetik alan koruması yoktur. "
            "Dünya'daki radyasyon düzeyi bu koşul için ölçek değildir.\n"
            "- **Gün uzunluğu:** Ay'da bir gündüz gece döngüsü yaklaşık "
            "29 Dünya günü sürer. Dünya'da bu ritim yoktur.\n"
            "- **Zemin malzemesi:** Ay toprağının mineral bileşimi hiçbir "
            "Dünya kaya türüne birebir benzemez.\n\n"
            "Ayrıca şu bilgiler sahadan ayrı olarak okunur ve sayısal "
            "puana girmez: buz ve daima gölgede kalan alanlar, lav "
            "tüpleri ve tozun elektriklenmesi. Bunlar jeoloji "
            "haritalarından değerlendirilir.\n\n"
            "Bu nedenle saha testini yalnızca uyuşan ölçütler için "
            "kullanın. Geri kalan koşulları laboratuvar ve simülasyonlarla "
            "doğrulayın."
        ),
        "en": (
            "No Earth site reproduces all Moon conditions at once. The "
            "following conditions do not occur naturally on Earth, so they "
            "cannot be tested in the field:\n\n"
            "- **Gravity:** surface gravity on the Moon is about one sixth "
            "of Earth's. Soil behaviour and dust settling cannot be fully "
            "tested on Earth.\n"
            "- **Atmosphere:** the Moon has almost no atmosphere. No "
            "natural vacuum environment exists at Earth's surface.\n"
            "- **Radiation:** the Moon has no magnetic-field shielding. "
            "Earth radiation levels are no scale for this condition.\n"
            "- **Day length:** one day-night cycle on the Moon lasts about "
            "29 Earth days. This rhythm does not exist on Earth.\n"
            "- **Ground material:** the mineral composition of lunar soil "
            "matches no Earth rock type exactly.\n\n"
            "Also read separately from the site and excluded from the "
            "numeric score: ice and permanently shadowed areas, lava "
            "tubes, and dust electrification. These are assessed from "
            "geology maps.\n\n"
            "For these reasons, use field testing only for the criteria "
            "that match. Verify the remaining conditions in laboratories "
            "and simulations."
        ),
    },
    "inspect_label": {
        "tr": "İncelenecek Dünya sahası",
        "en": "Earth site to inspect",
    },
    "inspect_help": {
        "tr": ("Yalnızca ilk sıradakini değil, listedeki herhangi bir sahayı "
               "inceleyebilirsiniz."),
        "en": ("Inspect any site in the list, not only the top-ranked one."),
    },
    # ── visual evidence panel ────────────────────────────────────────────────
    "vis_heading": {
        "tr": "🛰️ Görsel ve Yükselti Bağlamı: {ref} vs {sel}",
        "en": "🛰️ Visual & Elevation Context: {ref} vs {sel}",
    },
    "vis_col_moon_hillshade": {
        "tr": "Ay Yükselti Kabartması (5 m LOLA)",
        "en": "Moon Shaded Relief (5 m LOLA)",
    },
    "vis_col_moon_hazard": {
        "tr": "Ay Eğim Sınıfları (5 m LOLA)",
        "en": "Moon Slope Classes (5 m LOLA)",
    },
    "vis_col_earth_s2": {
        "tr": "Dünya Uydu Görüntüsü (10 m Sentinel-2 L2A)",
        "en": "Earth Satellite Image (10 m Sentinel-2 L2A)",
    },
    "vis_moon_hillshade_caption": {
        "tr": "{ref} — LRO LOLA 5 m/piksel kabartma & r=1 km analiz çemberi ({lat}°, {lon}°)",
        "en": "{ref} — LRO LOLA 5 m/px hillshade & r=1 km analysis circle ({lat}°, {lon}°)",
    },
    "vis_moon_hazard_caption": {
        "tr": "{ref} — Açıklayıcı eğim sınıfları (<10° / 10–20° / >20°); iniş güvenliği değerlendirmesi değildir.",
        "en": "{ref} — Illustrative slope bins (<10° / 10–20° / >20°); not a landing-safety assessment.",
    },
    "vis_moon_atlas_source": {
        "tr": "Yerel 5 m LRO LOLA PGDA atlası (`data/processed/moon_atlas/`). Yalnızca görsel bağlam içindir.",
        "en": "Local 5 m LRO LOLA PGDA atlas (`data/processed/moon_atlas/`). Visual context only.",
    },
    "vis_earth_s2_caption": {
        "tr": "{sel} — Sentinel-2 L2A 10 m (5.12×5.12 km) · Tarih: {date} · Yerel bulut: %{cloud} · Sahne: {scene}",
        "en": "{sel} — Sentinel-2 L2A 10 m (5.12×5.12 km) · Date: {date} · Local cloud: {cloud}% · Scene: {scene}",
    },
    "vis_earth_s2_source": {
        "tr": "Yerel ESA Sentinel-2 L2A atlası (`data/processed/earth_atlas/`); sayısal skorlar aşağıdaki tablo veri setlerindendir.",
        "en": "Local ESA Sentinel-2 L2A atlas (`data/processed/earth_atlas/`); numeric scores come from the datasets listed below.",
    },
    "vis_atlas_expander": {
        "tr": "📐 3 Panelli Ay LOLA Yükselti + Kesit Atlasını Aç",
        "en": "📐 Open 3-Panel Lunar LOLA Relief & Profile Atlas",
    },
    "vis_quant_suspended": {
        "tr": "**Termal:** v1'de askıda (`NaN` — Karar #30)",
        "en": "**Thermal:** suspended in v1 (`NaN` — Decision #30)",
    },
    "vis_wac_caption": {
        "tr": ("{ref} — LRO WAC ortomozaik (~30×30 km pencere, ~71 m/piksel; "
               "merkez {lat}°, {lon}°)"),
        "en": ("{ref} — LRO WAC orthomosaic (~30×30 km window, ~71 m/px; "
               "centered on {lat}°, {lon}°)"),
    },
    "vis_wac_error": {
        "tr": "Ay WAC önizlemesi alınamadı ({err}).",
        "en": "Lunar WAC preview unavailable ({err}).",
    },
    "vis_wac_source": {
        "tr": "Görüntü kaynağı: NASA LRO Geniş Açılı Kamera (WAC), USGS "
              "Astrogeology WMS servisi.",
        "en": "Imagery source: NASA LRO Wide Angle Camera (WAC) via USGS "
              "Astrogeology WMS.",
    },
    "vis_lola_caption": {
        "tr": "{ref} — LOLA kabartma haritası (~30×30 km pencere; ölçüm "
              "yarıçapı = {rad} m)",
        "en": "{ref} — LOLA shaded relief (~30×30 km window; measurement "
              "radius = {rad} m)",
    },
    "vis_lola_error": {
        "tr": "Ay LOLA önizlemesi alınamadı ({err}).",
        "en": "Lunar LOLA preview unavailable ({err}).",
    },
    "vis_lola_source": {
        "tr": ("Kabartma önizleme: NASA LRO LOLA, USGS Astrogeology WMS. "
               "Sayısal ölçümler aşağıdaki tablodaki kaynaklardandır."),
        "en": ("Relief preview: NASA LRO LOLA via USGS Astrogeology WMS. "
               "Numeric measurements come from the sources listed below."),
    },
    "vis_moon_only_note": {
        "tr": ("Canlı Ay Güney Kutbu görüntü servisi yalnızca Ay referans "
               "sahalarında çalışır."),
        "en": ("The live lunar South Pole image service applies to Moon "
               "reference sites only."),
    },
    "vis_earth_caption": {
        "tr": ("{sel} ({lat}°, {lon}°) — ~{km}×{km} km pencere (ölçüm "
               "yarıçapı = {rad} m)"),
        "en": ("{sel} ({lat}°, {lon}°) — ~{km}×{km} km window (measurement "
               "radius = {rad} m)"),
    },
    "vis_earth_error": {
        "tr": "Esri uydu görüntüsü alınamadı ({err}).",
        "en": "Esri imagery preview unavailable ({err}).",
    },
    "vis_earth_source": {
        "tr": ("**Optik önizleme kaynağı:** Esri World Imagery (Esri, Maxar, "
               "Earthstar Geographics). Not: sayısal skorlar bu önizlemeden "
               "değil, aşağıdaki tabloda listelenen uydu veri setlerinden "
               "hesaplanır."),
        "en": ("**Optical preview source:** Esri World Imagery (Esri, Maxar, "
               "Earthstar Geographics). Note: numeric scores are computed "
               "from the satellite datasets listed below, not from this "
               "preview."),
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
    "vis_quant_msg": {
        "tr": ("Görsel benzerlik tek başına yeterli değildir: yukarıdaki "
               "uydu görüntülerini aşağıdaki sayısal skorlar, belirsizlik "
               "aralıkları ve ölçüm çözünürlükleriyle birlikte "
               "değerlendirin."),
        "en": ("Visual similarity alone is not enough: judge the orbital "
               "images above together with the numeric scores, uncertainty "
               "ranges and measurement resolutions below."),
    },
    # ── feature gaps table ───────────────────────────────────────────────────
    "gaps_heading": {
        "tr": "Ölçüt farkları: {sel} vs {ref}",
        "en": "Criterion gaps: {sel} vs {ref}",
    },
    "gaps_empty": {
        "tr": "Bu saha için karşılaştırılabilir ölçüt yok.",
        "en": "No comparable criteria for this site.",
    },
    "gaps_caption": {
        "tr": ("Fark (σ) büyük → en büyük fiziksel uyuşmazlık (listeyi "
               "büyükten küçüğe sıralar). Çözünürlük (m): verinin piksel "
               "boyutu — kaba bir ürün (örn. ~1 km'lik sıcaklık verisi) 500 "
               "m'lik bir sahayı çözemez; yükseklik verisi 30 m'dir."),
        "en": ("Large diff (σ) → biggest physical mismatch (the list is "
               "sorted largest first). Resolution (m): pixel size of the "
               "data — a coarse product (e.g. ~1 km temperature data) cannot "
               "resolve a 500 m site; the elevation data is 30 m."),
    },
    "scorecard_heading": {
        "tr": "### 📊 8 Boyutlu Yarışma Kapsam & Sınır Karnesi",
        "en": "### 📊 8-Dimension Challenge Scope & Limits Scorecard",
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
            "Kapsam & Sınır Notu": "Geniş bant güneş albedosuna hizalı (×0.38 duyarlılığı belgeli); 500 m–1 km piksel alt-kilometrik yamaları çözmez.",
        },
        {
            "Boyut": "3. Sıcaklık Genliği & Termal Atalet (temp_amplitude, thermal_inertia)",
            "v1 Durumu": "⏸️ v1'de Askıda (NaN — Karar #30)",
            "Veri Kaynağı & Çözünürlük": "Ay: LRO Diviner PCP (240 m, NaN) · Dünya: MODIS MOD11A2.061 yıllık ort. ΔT (1000 m)",
            "Kapsam & Sınır Notu": "Ay Diviner ltim dilimleri ile Dünya MODIS yıllık ort. gündüz–gece farkı eşdeğer günlük döngü tanımında olmadığından ve ortak TI ürünü bulunmadığından v1'de askıda.",
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
            "v1 Durumu": "🔬 Saha Dışı — Laboratuvar & Simülasyon",
            "Veri Kaynağı & Çözünürlük": "Temel fiziksel sabitler ve görev ortam modelleri",
            "Kapsam & Sınır Notu": "Hiçbir Dünya sahası bu koşulları doğal olarak üretemez; saha kampanyaları simülatör ve termal-vakum odalarıyla eşlenmelidir.",
        },
    ],
    "en": [
        {
            "Dimension": "1. Topography & Terrain (slope_mean, slope_p90, roughness, relief)",
            "v1 Status": "✅ Numeric Axis (Active — Mobility)",
            "Data Source & Resolution": "Moon: LRO LOLA PGDA (5 m/px) · Earth: Copernicus GLO-30 / NASADEM (30 m/px)",
            "Scope & Limitation Note": "Uniform r = 1000 m and metric CRS slope calculation; 5 m vs 30 m pixel-scale ratio makes it a proxy comparison.",
        },
        {
            "Dimension": "2. Surface Brightness (albedo)",
            "v1 Status": "✅ Numeric Axis (Active — Surface)",
            "Data Source & Resolution": "Moon: LRO LOLA 1064 nm ×0.38 broadband eq. (1000 m) · Earth: MODIS MCD43A3.061 (500 m)",
            "Scope & Limitation Note": "Aligned to broadband solar albedo (sensitivity documented); 500 m–1 km pixels do not resolve sub-km patches.",
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

# Data-contract feature codes → readable names (code kept as a hint).
FEATURE_LABELS: dict[str, dict[str, str]] = {
    "slope_mean": {
        "tr": "Ortalama eğim (slope_mean)",
        "en": "Mean slope (slope_mean)",
    },
    "slope_p90": {
        "tr": "Dik yama payı (slope_p90)",
        "en": "Steep-slope share (slope_p90)",
    },
    "roughness": {
        "tr": "Yüzey pürüzü (roughness)",
        "en": "Surface roughness (roughness)",
    },
    "relief": {
        "tr": "Yükselti farkı (relief)",
        "en": "Elevation range (relief)",
    },
    "temp_amplitude": {
        "tr": "Gün-gece sıcaklık farkı (temp_amplitude)",
        "en": "Day–night temperature swing (temp_amplitude)",
    },
    "thermal_inertia": {
        "tr": "Tozun ısı tutumu (thermal_inertia)",
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


def feature_label(code: str, lang: str = DEFAULT_LANG) -> str:
    """Readable name for a feature code; unknown codes pass through."""
    return FEATURE_LABELS.get(code, {}).get(lang) or code


def lith_label(code: str, lang: str = DEFAULT_LANG) -> str:
    """Readable name for a lithology class; unknown codes pass through."""
    return LITHOLOGY_LABELS.get(code, {}).get(lang) or code
