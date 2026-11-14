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

# Plain crater / region names for Moon reference sites (no ROI / tile suffixes).
MOON_REF_NAMES: dict[str, dict[str, str]] = {
    "moon_shackleton_rim": {
        "tr": "Shackleton Krateri Kenarı",
        "en": "Shackleton Crater Rim",
    },
    "moon_connecting_ridge": {
        "tr": "Bağlantı Sırtı (Shackleton–de Gerlache)",
        "en": "Connecting Ridge (Shackleton–de Gerlache)",
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
        "tr": "Ay ↔ Dünya Benzer Koşullar Analizi",
        "en": "Moon ↔ Earth Similar-Conditions Analysis",
    },
    "subtitle": {
        "tr": ("Ay'da seçilen krater/bölgeyi arazi/eğim (Mobilite) ve yüzey "
               "parlaklığı (Yüzey) açısından Dünya'daki {n} sahayla karşılaştırır. "
               "Termal veri, Ay–Dünya günlük döngü tanım farkı nedeniyle "
               "hesaba katılmaz."),
        "en": ("Compares a selected Moon region against {n} Earth sites on "
               "terrain/slope (Mobility) and surface brightness (Surface). "
               "Thermal data is omitted due to diurnal definition mismatch."),
    },
    # ── sidebar ──────────────────────────────────────────────────────────────
    "settings_header": {"tr": "Ayarlar", "en": "Settings"},
    "body_moon": {"tr": "Ay", "en": "Moon"},
    "ref_site_label_moon": {
        "tr": "Ay referans krateri / bölgesi",
        "en": "Lunar reference crater / site",
    },
    "ref_site_caption": {
        "tr": "Enlem {lat}°, Boylam {lon}° · Zemin: {lith}",
        "en": "Latitude {lat}°, Longitude {lon}° · Ground: {lith}",
    },
    "ref_site_tooltip": {
        "tr": "Saha kodu: {site_id}",
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
        "tr": "Kaynak / buz potansiyeli (yüzey ağırlıklı)",
        "en": "Resource / ice prospecting (surface-weighted)",
    },
    "mission_isru_note": {
        "tr": "Buz kayıtları sayısal skora girmez; yalnızca arazi ve yüzey parlaklığı (ağırlıkla Yüzey) hesaplanır.",
        "en": "Ice records do not enter numeric scores; only terrain and surface brightness (surface-weighted) are scored.",
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
        "tr": "Referans bölge: {name} ({body})",
        "en": "Reference region: {name} ({body})",
    },
    "ref_expander": {
        "tr": "Referans bölgenin ölçümleri",
        "en": "Reference measurements",
    },
    "ref_col_feature": {"tr": "Ölçüt", "en": "Criterion"},
    "ref_col_value": {"tr": "Değer", "en": "Value"},
    "ref_col_unit": {"tr": "Birim", "en": "Unit"},
    "ref_col_sd": {"tr": "Belirsizlik (±)", "en": "Uncertainty (±)"},
    "ref_col_res": {"tr": "Çözünürlük (m)", "en": "Resolution (m)"},
    "ref_col_src": {"tr": "Kaynak", "en": "Source"},
    "ref_table_caption": {
        "tr": "Çevresel ortalama değerler, ölçüm belirsizliği (±) ve uydu piksel çözünürlüğü (m).",
        "en": "Local site averages, measurement uncertainty (±), and satellite pixel resolution (m).",
    },
    "ref_value_suspended": {
        "tr": "Kullanılmıyor",
        "en": "Omitted",
    },
    # ── tabs ─────────────────────────────────────────────────────────────────
    "tab_map": {"tr": "Harita", "en": "Map"},
    "tab_radar": {"tr": "Eksen Grafikleri", "en": "Axis Charts"},
    "tab_terrain": {"tr": "3D Arazi", "en": "3D Terrain"},
    "tab_table": {"tr": "Skor Tablosu", "en": "Score Table"},
    "tab_validation": {"tr": "Sıra Tanısı", "en": "Rank Diagnostic"},
    "tab_breakdown": {
        "tr": "Analojinin Sınırları",
        "en": "Limits of the Analogy",
    },
    # ── map tab ──────────────────────────────────────────────────────────────
    "map_heading": {
        "tr": ("Haritadaki her nokta bir Dünya sahasıdır. Büyük ve yeşil "
               "nokta seçili Ay bölgesine daha yakın, küçük ve kırmızı "
               "nokta daha uzaktır."),
        "en": ("Each dot is an Earth site. Larger, greener dots resemble the "
               "selected Moon region more closely; smaller, red dots less so."),
    },
    "map_caption": {
        "tr": ("Mavi halkalı noktalar literatürden bilinen 10 referans analog "
               "sahasıdır (bazıları koyu Ay bazaltı ya da düz Mars/permafrost "
               "sahası olduğu için dik ve parlak kutup kraterlerinde düşük "
               "sırada çıkabilir). İç renk genel benzerliği gösterir."),
        "en": ("Blue-ringed dots mark the 10 known literature benchmark sites "
               "(some are dark basalt or flat permafrost testbeds, so ranking "
               "lower on steep bright polar craters reflects physical mismatch)."),
    },
    "map_show_all_val": {
        "tr": "10 bilinen referans sahasını (mavi halka) haritada her zaman göster",
        "en": "Always show all 10 known benchmark sites (blue rings) on the map",
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
        "tr": "Mobilite ve Yüzey skorları (0–1) ile %5–%95 Monte Carlo belirsizlik aralığı.",
        "en": "Mobility and Surface scores (0–1) with 5th–95th Monte Carlo uncertainty bounds.",
    },
    "radar_line": {
        "tr": ("Genel: {score} · Aralık: {interval} · "
               "Mobilite: {mob} · Yüzey: {surf} · Zemin: {lith}"),
        "en": ("Overall: {score} · Range: {interval} · "
               "Mobility: {mob} · Surface: {surf} · Ground: {lith}"),
    },
    "uncertainty_unavailable": {
        "tr": "belirsizlik aralığı yok",
        "en": "interval unavailable",
    },
    "q95_label": {"tr": "üst sınır (%95)", "en": "upper bound (95%)"},
    "q05_label": {"tr": "alt sınır (%5)", "en": "lower bound (5%)"},
    "axis_mobility": {"tr": "Mobilite", "en": "Mobility"},
    "axis_thermal": {"tr": "Termal", "en": "Thermal"},
    "axis_surface": {"tr": "Yüzey", "en": "Surface"},
    "expanded_note": {
        "tr": "* İşaretli aralıklarda nokta skor P5–P95 dışında kaldığı için yalnızca gösterim sınırı genişletilmiştir.",
        "en": "* Starred intervals widen display bounds only where the point score sits outside raw P5–P95 draws.",
    },
    # ── 3D terrain tab ───────────────────────────────────────────────────────
    "body_earth": {"tr": "Dünya", "en": "Earth"},
    "terrain_intro": {
        "tr": "Seçili Ay bölgesi ile Dünya sahasının gerçek arazi yüzeyi yan yana gösterilir.",
        "en": "Elevation terrain of the selected Moon region and Earth site side by side.",
    },
    "terrain_pick": {
        "tr": "Sağda gösterilecek Dünya sahası",
        "en": "Earth site on the right",
    },
    "terrain_exag_label": {
        "tr": "Dikey abartı (×)",
        "en": "Vertical exaggeration (×)",
    },
    "terrain_exag_note": {
        "tr": "Dikey ölçek görsel netlik için çarpılmıştır.",
        "en": "Vertical scale is exaggerated for clarity.",
    },
    "terrain_orbit_label": {
        "tr": "Kamera açısı (derece)",
        "en": "Camera angle (degrees)",
    },
    "terrain_hover": {
        "tr": ("Sağa: %{x:.2f} km<br/>İleri: %{y:.2f} km"
               "<br/>Yükselti: %{z:.0f} m<extra></extra>"),
        "en": ("Right: %{x:.2f} km<br/>Forward: %{y:.2f} km"
               "<br/>Elevation: %{z:.0f} m<extra></extra>"),
    },
    "terrain_card_source": {
        "tr": "Kaynak: {src} · {res} m/piksel · Pencere: {km} km",
        "en": "Source: {src} · {res} m/px · Window: {km} km",
    },
    "terrain_card_stub": {
        "tr": "Örnek arazi · Kaynak: {src} · {res} m/piksel · {km} km",
        "en": "Sample terrain · Source: {src} · {res} m/px · {km} km",
    },
    "terrain_stub_note": {
        "tr": "Gerçek yükselti paftası bulunmayan sahalarda istatistiksel arazi yüzeyi gösterilir.",
        "en": "Where elevation tiles are absent, synthetic terrain from site stats is shown.",
    },
    # ── score table ──────────────────────────────────────────────────────────
    "table_caption": {
        "tr": "Görev ağırlıklı genel benzerlik ve ölçüt skorları (parantez içi belirsizlik aralığı).",
        "en": "Mission-weighted overall similarity and per-axis scores with uncertainty ranges.",
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
    "lith_match_tag": {"tr": " (eşleşiyor)", "en": " (match)"},
    "table_footer_caption": {
        "tr": "Tabloda Mobilite ve Yüzey skorları yer alır; 'eşleşiyor' ifadesi referans ile aynı kaya sınıfını belirtir ve skora girmez.",
        "en": "Table shows Mobility and Surface scores; '(match)' notes the same rock class as the reference without entering the score.",
    },
    # ── validation tab (10-row rank diagnostic) ──────────────────────────────
    "val_summary_note": {
        "tr": ("Bilinen 10 sahanın 40 saha içindeki sıralaması (sütun başlıklarına tıklayarak sıralayabilirsiniz). "
               "Literatürde 8/10 saha için arazi/mobilite beklentisi doğrulanmıştır."),
        "en": ("Ranking of the 10 known analogue sites within the 40-site pool (click column headers to sort). "
               "Primary literature documents Mobility expectations for 8/10 sites."),
    },
    "val_col_site": {"tr": "Doğrulama Sahası", "en": "Validation Site"},
    "val_col_overall_rank": {"tr": "Genel Sıra", "en": "Overall Rank"},
    "val_col_mob_rank": {"tr": "Mobilite Sırası", "en": "Mobility Rank"},
    "val_col_surf_rank": {"tr": "Yüzey Sırası", "en": "Surface Rank"},
    "val_col_expected": {"tr": "Beklenen Eksen", "en": "Expected Axis"},
    "val_col_ice": {"tr": "Buz / Permafrost", "en": "Ice / Permafrost"},
    "val_col_rationale": {"tr": "Gerekçe", "en": "Rationale"},
    "val_col_source": {"tr": "Kaynak (DOI/URL)", "en": "Source (DOI/URL)"},
    "val_exp_mobility": {"tr": "Mobilite (Kesin)", "en": "Mobility (Confirmed)"},
    "val_exp_thermal_only": {"tr": "Yalnız Termal", "en": "Thermal only"},
    "val_exp_none": {"tr": "Kaynak doğrulanamadı", "en": "No verified primary source"},
    # ── analogy limits tab ───────────────────────────────────────────────────
    "breakdown_notes": {
        "tr": (
            "Hiçbir Dünya sahası Ay'ın tüm koşullarını aynı anda sunmaz. "
            "Aşağıdaki koşullar sahada doğal olarak test edilemez:\n\n"
            "- **Yerçekimi:** Ay'da yerçekimi Dünya'nın altıda biridir; zemin çökmesi ve toz hareketi değişir.\n"
            "- **Atmosfer & Radyasyon:** Ay'da vakum ortamı vardır ve manyetik koruma yoktur.\n"
            "- **Gün Uzunluğu:** Bir Ay gündüz-gece döngüsü yaklaşık 29.5 Dünya günüdür.\n"
            "- **Malzeme & Buz:** Kalıcı gölge buzu ve elektrostatik toz yalnız laboratuvarda test edilir.\n\n"
            "Saha testlerini yalnızca uyuşan fiziksel eksenler için kullanın."
        ),
        "en": (
            "No Earth site reproduces all lunar conditions at once. "
            "The following conditions cannot be tested naturally in the field:\n\n"
            "- **Gravity:** Lunar gravity is ~1/6 g, altering regolith compaction and dust settling.\n"
            "- **Atmosphere & Radiation:** Hard vacuum with no magnetic-field shielding.\n"
            "- **Day Length:** One lunar synodic cycle lasts ~29.5 Earth days.\n"
            "- **Material & Ice:** Cryogenic PSR ice and electrostatic dust require vacuum chambers.\n\n"
            "Use terrestrial sites only for the matching physical criteria."
        ),
    },
    "inspect_label": {
        "tr": "İncelenecek Dünya sahası",
        "en": "Earth site to inspect",
    },
    "inspect_help": {
        "tr": "Listeden herhangi bir Dünya sahasını seçip ölçüt farklarını inceleyin.",
        "en": "Select any Earth site to inspect feature differences.",
    },
    # ── visual evidence panel ────────────────────────────────────────────────
    "vis_heading": {
        "tr": "Görsel ve Yükselti Bağlamı: {ref} vs {sel}",
        "en": "Visual & Elevation Context: {ref} vs {sel}",
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
        "tr": "Dünya Uydu Görüntüsü (10 m Sentinel-2)",
        "en": "Earth Satellite Image (10 m Sentinel-2)",
    },
    "vis_moon_hillshade_caption": {
        "tr": "{ref} — 5 m/px LRO LOLA kabartma ({lat}°, {lon}°)",
        "en": "{ref} — 5 m/px LRO LOLA hillshade ({lat}°, {lon}°)",
    },
    "vis_moon_hazard_caption": {
        "tr": "{ref} — Eğim sınıfları (<10° / 10–20° / >20°)",
        "en": "{ref} — Slope bins (<10° / 10–20° / >20°)",
    },
    "vis_moon_atlas_source": {
        "tr": "Yerel 5 m LRO LOLA atlası (görsel bağlam).",
        "en": "Local 5 m LRO LOLA atlas (visual context only).",
    },
    "vis_earth_s2_caption": {
        "tr": "{sel} — Sentinel-2 L2A 10 m · Tarih: {date} · Bulut: %{cloud}",
        "en": "{sel} — Sentinel-2 L2A 10 m · Date: {date} · Cloud: {cloud}%",
    },
    "vis_earth_s2_source": {
        "tr": "Yerel ESA Sentinel-2 L2A görüntüsü; skorlar aşağıdaki uydu ölçütlerinden hesaplanır.",
        "en": "Local ESA Sentinel-2 L2A imagery; scores come from the datasets below.",
    },
    "vis_atlas_expander": {
        "tr": "3 Panelli Ay LOLA Yükselti ve Kesit Atlasını Aç",
        "en": "Open 3-Panel Lunar LOLA Relief & Profile Atlas",
    },
    "vis_quant_suspended": {
        "tr": "**Termal:** bu sürümde kullanılmıyor",
        "en": "**Thermal:** omitted in this release",
    },
    "vis_wac_caption": {
        "tr": "{ref} — LRO WAC (~30×30 km, {lat}°, {lon}°)",
        "en": "{ref} — LRO WAC (~30×30 km, {lat}°, {lon}°)",
    },
    "vis_wac_error": {
        "tr": "Ay WAC önizlemesi alınamadı ({err}).",
        "en": "Lunar WAC preview unavailable ({err}).",
    },
    "vis_wac_source": {
        "tr": "Kaynak: NASA LRO WAC (USGS WMS).",
        "en": "Source: NASA LRO WAC (USGS WMS).",
    },
    "vis_lola_caption": {
        "tr": "{ref} — LOLA kabartma (yarıçap = {rad} m)",
        "en": "{ref} — LOLA shaded relief (radius = {rad} m)",
    },
    "vis_lola_error": {
        "tr": "Ay LOLA önizlemesi alınamadı ({err}).",
        "en": "Lunar LOLA preview unavailable ({err}).",
    },
    "vis_lola_source": {
        "tr": "Kaynak: NASA LRO LOLA (USGS WMS).",
        "en": "Source: NASA LRO LOLA (USGS WMS).",
    },
    "vis_earth_caption": {
        "tr": "{sel} ({lat}°, {lon}°) — ~{km}×{km} km",
        "en": "{sel} ({lat}°, {lon}°) — ~{km}×{km} km",
    },
    "vis_earth_error": {
        "tr": "Uydu önizlemesi alınamadı ({err}).",
        "en": "Satellite preview unavailable ({err}).",
    },
    "vis_earth_source": {
        "tr": "Önizleme: Esri World Imagery. Sayısal skorlar tabloda verilen veri setlerindendir.",
        "en": "Preview: Esri World Imagery. Numeric scores come from the datasets below.",
    },
    "vis_link_worldview": {
        "tr": "[NASA Worldview'de aç]({url})",
        "en": "[Open in NASA Worldview]({url})",
    },
    "vis_link_gmaps": {
        "tr": "[Google Maps Uydu]({url})",
        "en": "[Google Maps Satellite]({url})",
    },
    "vis_quant_head": {
        "tr": "Sayısal özet — ",
        "en": "Quantitative summary — ",
    },
    "vis_quant_line": {
        "tr": "**{axis}:** {score} ({lo}–{hi})",
        "en": "**{axis}:** {score} ({lo}–{hi})",
    },
    "vis_quant_msg": {
        "tr": "Görseller bağlam içindir; değerlendirmeyi sayısal skorlar ve çözünürlük tablosuyla birlikte yapın.",
        "en": "Images provide context only; interpret alongside numeric scores and sensor resolutions.",
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
        "tr": "Büyük fark (σ) daha yüksek fiziksel uyuşmazlığı gösterir; çözünürlük sütunu piksel boyutunu (m) verir.",
        "en": "Larger diff (σ) marks bigger physical mismatch; resolution gives pixel size in meters.",
    },
    "scorecard_heading": {
        "tr": "### 8 Boyutlu Kapsam ve Sınır Tablosu",
        "en": "### 8-Dimension Scope and Limits Scorecard",
    },
}

# 8-Dimension Challenge Scorecard (Analogy Limits tab).
DIMENSION_SCORECARD: dict[str, list[dict[str, str]]] = {
    "tr": [
        {
            "Boyut": "1. Topografya & Arazi (slope_mean, slope_p90, roughness, relief)",
            "Durum": "Aktif (Mobilite)",
            "Veri Kaynağı & Çözünürlük": "Ay: LRO LOLA PGDA (5 m/px) · Dünya: Copernicus GLO-30 / NASADEM (30 m/px)",
            "Sınır Notu": "Her ikisinde r = 1000 m ve metrik eğim; 5 m vs 30 m çözünürlük farkı.",
        },
        {
            "Boyut": "2. Yüzey Parlaklığı (albedo)",
            "Durum": "Aktif (Yüzey)",
            "Veri Kaynağı & Çözünürlük": "Ay: LRO LOLA 1064 nm eşdeğeri (1000 m) · Dünya: MODIS MCD43A3 (500 m)",
            "Sınır Notu": "Geniş bant güneş albedosuna hizalı; 500 m–1 km piksel.",
        },
        {
            "Boyut": "3. Sıcaklık Genliği & Termal Atalet",
            "Durum": "Kullanılmıyor",
            "Veri Kaynağı & Çözünürlük": "Ay: LRO Diviner (240 m) · Dünya: MODIS MOD11A2 (1000 m)",
            "Sınır Notu": "Ay–Dünya günlük döngü tanımı eşdeğer olmadığından dışarıda bırakıldı.",
        },
        {
            "Boyut": "4. Yüzey Litolojisi",
            "Durum": "Nitel (Skor dışı)",
            "Veri Kaynağı & Çözünürlük": "Jeoloji haritaları ve literatür",
            "Sınır Notu": "Mineral spektrumları skora katılmaz; tabloda bilgi amaçlı gösterilir.",
        },
        {
            "Boyut": "5. Su Buzu / Kalıcı Gölge & Permafrost",
            "Durum": "Nitel (Skor dışı)",
            "Veri Kaynağı & Çözünürlük": "Doğrulama sahaları literatür envanteri",
            "Sınır Notu": "Ay vakumlu kriyojenik buzu sahada test edilemez; laboratuvarda doğrulanır.",
        },
        {
            "Boyut": "6. Lav Tüpleri & Yeraltı Boşlukları",
            "Durum": "Nitel (Skor dışı)",
            "Veri Kaynağı & Çözünürlük": "Jeolojik literatür",
            "Sınır Notu": "Yalnızca bilgi amaçlı; sayısal radar verisi sonraki sürüme bırakıldı.",
        },
        {
            "Boyut": "7. Toz, Rüzgar & Elektrostatik Toz",
            "Durum": "Laboratuvar & Simülasyon",
            "Veri Kaynağı & Çözünürlük": "Saha gözlemleri + plazma toz odaları",
            "Sınır Notu": "Ay'daki elektrostatik toz davranışı vakum odası gerektirir.",
        },
        {
            "Boyut": "8. Yerçekimi (1/6 g), Vakum, Radyasyon & 29.5 Günlük Ay Günü",
            "Durum": "Laboratuvar & Simülasyon",
            "Veri Kaynağı & Çözünürlük": "Fiziksel sabitler",
            "Sınır Notu": "Hiçbir Dünya sahası bu koşulları doğal olarak üretemez.",
        },
    ],
    "en": [
        {
            "Dimension": "1. Topography & Terrain (slope_mean, slope_p90, roughness, relief)",
            "Status": "Active (Mobility)",
            "Data Source & Resolution": "Moon: LRO LOLA PGDA (5 m/px) · Earth: Copernicus GLO-30 / NASADEM (30 m/px)",
            "Limitation Note": "Uniform r = 1000 m and metric slope; 5 m vs 30 m resolution difference.",
        },
        {
            "Dimension": "2. Surface Brightness (albedo)",
            "Status": "Active (Surface)",
            "Data Source & Resolution": "Moon: LRO LOLA 1064 nm eq. (1000 m) · Earth: MODIS MCD43A3 (500 m)",
            "Limitation Note": "Aligned to broadband solar albedo; 500 m–1 km pixel footprint.",
        },
        {
            "Dimension": "3. Temperature Swing & Thermal Inertia",
            "Status": "Omitted",
            "Data Source & Resolution": "Moon: LRO Diviner (240 m) · Earth: MODIS MOD11A2 (1000 m)",
            "Limitation Note": "Omitted due to non-equivalent lunar vs terrestrial diurnal cycle definitions.",
        },
        {
            "Dimension": "4. Surface Lithology",
            "Status": "Qualitative (Unscored)",
            "Data Source & Resolution": "Geologic maps and literature",
            "Limitation Note": "Mineral spectra are not scored numerically; shown for reference.",
        },
        {
            "Dimension": "5. Water Ice / PSR & Permafrost",
            "Status": "Qualitative (Unscored)",
            "Data Source & Resolution": "Literature inventory for validation sites",
            "Limitation Note": "Cryogenic lunar vacuum ice requires laboratory chambers.",
        },
        {
            "Dimension": "6. Lava Tubes & Subsurface Cavities",
            "Status": "Qualitative (Unscored)",
            "Data Source & Resolution": "Geologic literature",
            "Limitation Note": "Contextual only; numeric SAR comparison planned later.",
        },
        {
            "Dimension": "7. Dust, Wind & Electrostatic Dust",
            "Status": "Lab & Simulation",
            "Data Source & Resolution": "Field records + plasma dust chambers",
            "Limitation Note": "Lunar electrostatic dust requires vacuum chamber testing.",
        },
        {
            "Dimension": "8. Gravity (1/6 g), Vacuum, Radiation & 29.5-Day Lunar Day",
            "Status": "Lab & Simulation",
            "Data Source & Resolution": "Physical constants",
            "Limitation Note": "No Earth site reproduces these conditions naturally.",
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
        "tr": "volkanik tüf",
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


def moon_ref_name(site_id: str, fallback: str = "", lang: str = DEFAULT_LANG) -> str:
    """Localized crater/region name for a Moon reference site without ROI suffixes."""
    return MOON_REF_NAMES.get(site_id, {}).get(lang) or fallback or site_id
