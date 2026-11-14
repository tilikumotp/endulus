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
               "{n} sahayla karşılaştırır. Karşılaştırma üç konuda yapılır: "
               "arazi ve eğim, sıcaklık dalgalanması, yüzey parlaklığı. "
               "Her saha 0 ile 1 arasında bir benzerlik puanı alır. "
               "1'e yakın puan çok benzer demektir, 0'a yakın puan çok "
               "farklı demektir. Puan bir olasılık değildir."),
        "en": ("This app compares a selected Moon region with {n} Earth "
               "sites. The comparison covers three topics: terrain and "
               "slope, temperature swings, surface brightness. Each Earth "
               "site gets a similarity score between 0 and 1. A score near "
               "1 means very similar, a score near 0 means very different. "
               "The score is not a probability."),
    },
    "thermal_note": {
        "tr": ("Termal karşılaştırması için şimdilik yalnızca sıcaklık "
               "dalgalanması ölçümü kullanılıyor. Tozun ısı tutma ölçümü "
               "(thermal inertia) henüz hiçbir sahada yok."),
        "en": ("The thermal comparison currently uses the temperature swing "
               "measurement only. The thermal inertia measurement is not "
               "yet available for any site."),
    },
    # ── sidebar ──────────────────────────────────────────────────────────────
    "settings_header": {"tr": "⚙️ Ayarlar", "en": "⚙️ Settings"},
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
        "tr": "Buz ve kaynak arama",
        "en": "Ice / resource prospecting",
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
        "tr": ("Sıcaklık dalgalanması ölçümü, bir yıllık gözlemlerin "
               "gün-gece ortalamasıdır."),
        "en": "The temperature-swing value is an annual mean of day–night cycles.",
    },
    # ── tabs ─────────────────────────────────────────────────────────────────
    "tab_map": {"tr": "🗺️ Harita", "en": "🗺️ Map"},
    "tab_radar": {"tr": "📡 Radar Grafikleri", "en": "📡 Radar Charts"},
    "tab_table": {"tr": "📊 Skor Tablosu", "en": "📊 Score Table"},
    "tab_validation": {"tr": "✅ Doğrulama", "en": "✅ Validation"},
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
        "tr": ("Mavi halkalı noktalar Ay'e benzediği önceden bilinen "
               "sahaları gösterir (Etna, Atacama, Haughton gibi). Diğer "
               "noktalar benzerliği denenmekte olan aday sahalar."),
        "en": ("Blue-ringed dots mark sites already known to resemble the "
               "Moon (Etna, Atacama, Haughton and similar). The other dots "
               "are candidate sites being tested."),
    },
    "map_tooltip": {
        "tr": ("<b>{name}</b><br/>Rol: {role}<br/>Benzerlik: {score}"
               "<br/>Aralık: {interval}<br/>Zemin: {lith}"),
        "en": ("<b>{name}</b><br/>Role: {role}<br/>Similarity: {score}"
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
        "tr": ("Her ölçüt için benzerlik skoru (0–1, dolgulu alan). Yeşil "
               "kesikli çizgi: belirsizlik üst sınırı; kırmızı noktalı çizgi: "
               "alt sınır. Dış çember: tam benzerlik."),
        "en": ("Similarity score per criterion (0–1, filled area). Green "
               "dashed line: upper uncertainty bound; red dotted line: lower "
               "bound. Outer ring: perfect match."),
    },
    "radar_line": {
        "tr": ("Genel benzerlik: {score} · Belirsizlik: {interval} · "
               "Kullanılan ölçüt: {n}/{total} · Zemin: {lith}"),
        "en": ("Overall similarity: {score} · Uncertainty: {interval} · "
               "Criteria used: {n}/{total} · Ground: {lith}"),
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
        "tr": ("Bir ölçütün hücresi boşsa o ölçüt bu saha için "
               "hesaplanamamıştır. Bunun nedeni o sahanın ölçüm verisinin "
               "eksik olmasıdır. Zemin sütunundaki ✓ işareti, sahada "
               "referans sahayla aynı türde zemin bulunduğunu gösterir. "
               "Bu işaret yalnızca bilgilendirme amaçlıdır ve benzerlik "
               "puanına katkısı yoktur."),
        "en": ("An empty criterion cell means that criterion could not be "
               "computed for that site, because a required measurement is "
               "missing. A ✓ in the ground column means the site has the "
               "same ground type as the reference site. This mark is "
               "informational only and does not affect the score."),
    },
    # ── validation tab ───────────────────────────────────────────────────────
    "val_intro": {
        "tr": ("Bu sekme yöntemin sınavıdır. Ay'e benzediği önceden bilinen "
               "10 saha (Etna, Atacama, Haughton gibi) skorlayıcıya hangi "
               "sahanın bilinen analog olduğu gösterilmeden puanlanır. "
               "Sonra şuna bakılır: bilinen sahalar ilk 5'e girebiliyor mu? "
               "Girebiliyorsa yöntem gerçekten çalışıyor demektir."),
        "en": ("This tab is the method's exam. The 10 sites already known to "
               "resemble the Moon (Etna, Atacama, Haughton and similar) are "
               "scored without being told which one is a known analogue. We "
               "then check: can the known sites reach the top 5? If they "
               "can, the method actually works."),
    },
    "val_metric_label": {
        "tr": "Bilinen sahaların ilk 5'e girdiği karşılaştırma",
        "en": "Comparisons where a known site reached the top 5",
    },
    "val_metric_help": {
        "tr": ("Her ölçüt için 10 karşılaştırma yapılır, toplam 30. Sayı "
               "şunu gösterir: kaç karşılaştırmada bilinen bir saha "
               "ilk 5'e girdi."),
        "en": ("Each criterion runs 10 comparisons, 30 in total. The number "
               "shows how many comparisons had a known site in the top 5."),
    },
    "val_chart_caption": {
        "tr": ("Her ölçütte 10 karşılaştırma vardır. Çubuk, bilinen "
               "sahaların kaçında ilk 5'e girdiğini gösterir."),
        "en": ("Each criterion has 10 comparisons. The bar shows how many "
               "known sites reached the top 5."),
    },
    "val_col_site": {"tr": "Saha", "en": "Site"},
    "val_col_axis": {"tr": "Ölçüt", "en": "Criterion"},
    "val_col_rank": {"tr": "Sıralama", "en": "Rank"},
    "val_col_verdict": {"tr": "Değerlendirme", "en": "Verdict"},
    "val_verdict_yes": {
        "tr": "✓ İlk 5'e girdi. Yöntem bu sahayı bu ölçütte öne çıkardı.",
        "en": "✓ Reached the top 5. The method ranked this site up on this criterion.",
    },
    "val_verdict_no": {
        "tr": "İlk 5'e girmedi.",
        "en": "Did not reach the top 5.",
    },
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
    "vis_col_moon_opt": {"tr": "Ay Optik Görüntü", "en": "Moon Optical Image"},
    "vis_col_moon_relief": {
        "tr": "Ay Yükselti Bağlamı",
        "en": "Moon Elevation Context",
    },
    "vis_col_earth": {
        "tr": "Dünya Aday Saha Görüntüsü",
        "en": "Earth Candidate Site Image",
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
