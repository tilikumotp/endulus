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
        "tr": "🌕 Ay / Mars ↔ Dünya Benzer Bulucu",
        "en": "🌕 Moon / Mars ↔ Earth Analog Finder",
    },
    "subtitle": {
        "tr": ("NASA Space Apps 2026 · Ay'daki bir yeri Dünya'daki {n} sahayla "
               "üç konuda karşılaştırır: arazi ve eğim (mobilite), sıcaklık "
               "dalgalanması (termal), yüzey parlaklığı. Skor 0–1 arası bir "
               "benzerlik ölçüsüdür: 1'e yakın çok benzer, 0'a yakın çok "
               "farklı — olasılık değildir."),
        "en": ("NASA Space Apps 2026 · Compares one place on the Moon with {n} "
               "Earth sites on three topics: terrain & slope (mobility), "
               "temperature swings (thermal), surface brightness. The score "
               "is a 0–1 similarity measure: near 1 = very similar, near "
               "0 = very different — it is not a probability."),
    },
    "thermal_note": {
        "tr": ("Termal karşılaştırması şimdilik yalnızca sıcaklık "
               "dalgalanmasına dayanıyor; tozun ısı tutma özelliği "
               "(thermal inertia) verisi henüz yok."),
        "en": ("The thermal comparison currently relies on the temperature "
               "swing only; the thermal inertia measurement is not yet "
               "available."),
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
    "min_score_label": {
        "tr": "Portföy eşik değeri",
        "en": "Portfolio threshold",
    },
    "min_score_help": {
        "tr": "Bir saha, herhangi bir ölçütte bu skorun üzerindeyse o ölçütü "
              "kapsamaya sayılır.",
        "en": "A site counts as covering a criterion when its score on that "
              "criterion is at or above this value.",
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
        "tr": ("Seçili Ay bölgesine en çok benzeyen {n} Dünya sahası — nokta "
               "ne kadar büyük ve rengi yeşile yakınsa o sahaya o kadar çok "
               "benziyor."),
        "en": ("The {n} Earth sites most similar to the selected Moon region "
               "— the bigger the dot and the greener its colour, the more "
               "alike that site is."),
    },
    "map_caption": {
        "tr": ("Nokta boyutu ve rengi: görev ağırlıklı genel benzerlik "
               "(yeşil = çok benzer, kırmızı = az benzer). Mavi halkalı "
               "noktalar: Ay'e benzediği daha önceden bilinen sahalar "
               "(Etna, Atacama, Haughton…)."),
        "en": ("Dot size and colour: mission-weighted overall similarity "
               "(green = very similar, red = less similar). Blue-ringed dots: "
               "sites already known to resemble the Moon (Etna, Atacama, "
               "Haughton…)."),
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
    "filter_role": {"tr": "Role göre filtrele", "en": "Filter by role"},
    "filter_role_help": {
        "tr": ("Bilinen analog: Ay'e benzediği daha önceden kanıtlanmış "
               "sahalar. Aday saha: benzerliği denenmek üzere önerilen, "
               "kesinleşmemiş sahalar."),
        "en": ("Known analogue: sites already proven to resemble the Moon. "
               "Candidate: sites proposed for testing, not yet confirmed."),
    },
    "filter_lith": {"tr": "Zemine göre filtrele", "en": "Filter by ground type"},
    "filter_region": {"tr": "Bölge", "en": "Region"},
    "region_all": {"tr": "Tüm sahalar", "en": "All sites"},
    "region_turkey": {"tr": "Türkiye", "en": "Türkiye"},
    "region_other": {"tr": "Diğer ülkeler", "en": "Other countries"},
    "table_footer_caption": {
        "tr": ("— : o ölçüt bu sahada skorlanamadı (ölçüm eksik). Zemin "
               "sütunundaki ✓: saha, referans sahayla aynı zemin sınıfından — "
               "bu niteliksel bir bilgidir, sayısal skora girmez."),
        "en": ("— : that criterion could not be scored for this site "
               "(measurement missing). ✓ in the ground column: the site "
               "shares the reference site's ground class — a qualitative "
               "note that never enters the numeric score."),
    },
    # ── validation tab ───────────────────────────────────────────────────────
    "val_intro": {
        "tr": ("Bu sekme yöntemin kendi sınama testidir: Dünya'da Ay'e "
               "benzediği daha önceden bilinen sahalara (Etna, Atacama, "
               "Haughton gibi) skorlayıcı kimin en iyi dediğine bakarız. "
               "Skorlayıcı hangi sahanın 'bilinen analog' olduğunu bilmez — "
               "böylece yöntemin gerçekten çalıştığını, kendini kandırmadığını "
               "görürüz."),
        "en": ("This tab is the method's self-test: we ask the scorer which "
               "Earth sites it likes best and check whether the places already "
               "known to resemble the Moon (Etna, Atacama, Haughton) come out "
               "on top. The scorer never knows which site is a known analogue "
               "— that is how we see whether the method actually works."),
    },
    "val_metric_label": {
        "tr": "Bilinen analogların ilk-5'e girdiği karşılaştırmalar",
        "en": "Comparisons where a known analogue entered the top 5",
    },
    "val_metric_help": {
        "tr": ("'{a}/{b}' gibi bir değer: {b} saha–ölçüt karşılaştırmasından "
               "{a} tanesinde bilinen analog ilk 5'e girdi."),
        "en": ("A value like '{a}/{b}' means: of {b} site–criterion "
               "comparisons, {a} had a known analogue in the top 5."),
    },
    "val_rank_axis": {
        "tr": "Sıralama (1 = en iyi)",
        "en": "Rank (1 = best)",
    },
    "val_col_site": {"tr": "Saha", "en": "Site"},
    "val_col_axis": {"tr": "Ölçüt", "en": "Criterion"},
    "val_col_rank": {"tr": "Sıralama", "en": "Rank"},
    "val_col_nsites": {"tr": "Saha sayısı", "en": "Number of sites"},
    "val_col_topk": {"tr": "İlk 5'te", "en": "In top 5"},
    "val_yes": {"tr": "✓", "en": "✓"},
    "val_no": {"tr": "—", "en": "—"},
    # ── portfolio tab ────────────────────────────────────────────────────────
    "port_intro": {
        "tr": ("Tek bir Dünya sahası Ay'in her özelliğini temsil edemez. Bu "
               "tablo, sınırlı sayıda sahayı birlikte ziyaret ederek hangi "
               "özellikleri (arazi, sıcaklık, yüzey) hangi sahada test "
               "edebileceğinizi gösterir. Eşik değerini yükseltirseniz "
               "yalnızca en güçlü benzerlikler kalır."),
        "en": ("No single Earth site can stand in for every Moon property. "
               "This table shows which properties (terrain, temperature, "
               "surface) you can test at which site when visiting a small set "
               "of them together. Raise the threshold and only the strongest "
               "matches remain."),
    },
    "port_col_pick": {"tr": "Seçim", "en": "Pick"},
    "port_col_site": {"tr": "Saha", "en": "Site"},
    "port_col_covers": {
        "tr": "Bu sahada test edilebilecekler",
        "en": "What can be tested at this site",
    },
    "port_uncovered": {
        "tr": "Hiçbir sahada güçlü benzerlik bulunmayan özellikler: {list}",
        "en": "Properties no site matches strongly: {list}",
    },
    "port_uncovered_note": {
        "tr": ("Bunlar Dünya'da saha testiyle değil, laboratuvar/simülasyonla "
               "doğrulanmalıdır."),
        "en": ("These must be verified in the lab or in simulation, not at "
               "any Earth field site."),
    },
    "port_all_covered": {
        "tr": "Tüm ölçütler sahalarla kapsandı ✅",
        "en": "Every criterion is covered by the sites ✅",
    },
    "port_empty": {
        "tr": ("Bu eşikte hiçbir saha güçlü benzerliğe ulaşmıyor — eşik "
               "değerini düşürün."),
        "en": ("No site reaches a strong match at this threshold — lower it."),
    },
    # ── analogy limits tab ───────────────────────────────────────────────────
    "breakdown_notes": {
        "tr": (
            "⚠️ **Analojinin sınırları** — hiçbir Dünya sahası şunları "
            "yeniden üretemez:\n"
            "- **Yerçekimi:** Ay ~1/6 g, Mars ~3/8 g (regolit mekaniği, toz "
            "çökmesi)\n"
            "- **Vakum / seyrek atmosfer:** Dünya yüzeyinde 1 Pa'ya inen "
            "basınç yok\n"
            "- **Radyasyon:** Dünya'nın manyetik kalkanı ve ozon katmanı "
            "olmadan sürekli parçacık akışı yok\n"
            "- **Gün döngüsü:** bir Ay gündü ≈ 29,5 Dünya günü sürer\n"
            "- **Regolit bileşimi:** Ay ve Mars mineralleri hiçbir Dünya "
            "kayasına birebir benzemez\n\n"
            "**Nitel olarak değerlendirilen etkenler (sayısal skora girmez, "
            "ayrıca değerlendirilir):**\n"
            "- **Buz / sürekli gölgeli alanlar:** Dünya'da daima gölgeli, "
            "donmuş zemin yoktur\n"
            "- **Lav tüpleri / yer altı boşlukları:** sahaya özgüdür; "
            "yalnızca jeoloji haritalarından nitel değerlendirilir\n"
            "- **Elektrostatik toz:** Ay tozunun havaya kalkması Dünya'da "
            "karşılığı olmayan bir olaydır; Dünya rüzgârı farklı (güçlü) bir "
            "süreçtir\n\n"
            "Dünya sahalarını yalnızca uyuşan ölçütler için kullanın; "
            "gerisini laboratuvar/simülasyonda doğrulayın."
        ),
        "en": (
            "⚠️ **Limits of the analogy** — no Earth site can reproduce:\n"
            "- **Gravity:** Moon ~1/6 g, Mars ~3/8 g (regolith mechanics, "
            "dust settling)\n"
            "- **Vacuum / thin atmosphere:** no Earth surface reaches ≤ 1 Pa "
            "pressure\n"
            "- **Radiation:** no chronic particle flux without Earth's "
            "magnetic shield and ozone layer\n"
            "- **Day cycle:** one lunar day lasts ≈ 29.5 Earth days\n"
            "- **Regolith composition:** Moon and Mars minerals match no "
            "Earth rock one-to-one\n\n"
            "**Qualitatively assessed factors (not in the numeric score, "
            "evaluated separately):**\n"
            "- **Ice / permanently shadowed areas:** Earth has no "
            "permanently shadowed, frozen ground\n"
            "- **Lava tubes / subsurface cavities:** site-specific; judged "
            "qualitatively from geology maps only\n"
            "- **Electrostatic dust:** lunar dust levitation has no Earth "
            "counterpart; Earth wind is a different (stronger) process\n\n"
            "Use Earth sites only for the criteria they match; verify the "
            "rest in the lab or in simulation."
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
