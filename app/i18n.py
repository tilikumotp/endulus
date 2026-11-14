"""Bilingual UI strings for app/main.py (Person 4).

Jury-facing display strings in Turkish and English. Code/data identifiers
(site_id, slope_mean, role values in the parquets, module/function names,
scientific units) stay English by design — AGENTS.md §5 data contract and
the pytest / validate_contract suites depend on them (never translate).
Formatted templates use str.format() placeholders.
"""

from __future__ import annotations

AXIS_LABELS = {
    "tr": {"mobility": "Mobilite", "thermal": "Termal", "surface": "Yüzey"},
    "en": {"mobility": "Mobility", "thermal": "Thermal", "surface": "Surface"},
}

MISSION_LABELS = {
    "tr": {
        "default": "Dengeli (tüm eksenler eşit)",
        "rover_mobility": "Rover mobilite testi",
        "isru_ice": "ISRU / buz araması",
        "radar_calibration": "Yeraltı radar kalibrasyonu",
    },
    "en": {
        "default": "Balanced (all axes equal)",
        "rover_mobility": "Rover mobility test",
        "isru_ice": "ISRU / ice prospecting",
        "radar_calibration": "Subsurface radar calibration",
    },
}

ROLE_LABELS = {
    "tr": {"validation": "doğrulama (bilinen analog)", "candidate": "aday"},
    "en": {"validation": "validation (known analogue)", "candidate": "candidate"},
}

BREAKDOWN = {
    "en": (
        "**Where the analogy breaks down** — no Earth site can reproduce:\n"
        "- **Gravity:** Moon ~1/6 g, Mars ~3/8 g (regolith mechanics, dust settling)\n"
        "- **Vacuum / thin atmosphere:** no Earth surface has <= 1 Pa pressure\n"
        "- **Radiation:** no magnetosphere-free, ozone-free chronic particle flux\n"
        "- **Diurnal cycle:** lunar day ≈ 29.5 Earth days\n"
        "- **Regolith composition:** lunar/Martian mineralogy differs from any Earth rock\n\n"
        "**Qualitative v1 factors (tracked, NOT in the numeric score — AGENTS.md §2):**\n"
        "- **Water ice / permanently shadowed regions (PSR):** Earth has no "
        "permanently shadowed, cryogenically cold terrain\n"
        "- **Lava tubes / subsurface caves:** presence is site-specific; assessed "
        "qualitatively from geology maps only\n"
        "- **Electrostatic dust / wind:** lunar electrostatic dust levitation has "
        "no Earth counterpart; Earth wind is a different (stronger) process\n\n"
        "Use Earth analogs only for the matched axes; validate the rest in lab/simulation."
    ),
    "tr": (
        "**Analojinin kırıldığı noktalar** — hiçbir Dünya sahası şunları yeniden üretemez:\n"
        "- **Yerçekimi:** Ay ~1/6 g, Mars ~3/8 g (regolit mekaniği, toz çökelmesi)\n"
        "- **Vakum / ince atmosfer:** Dünya yüzeyinde ≤ 1 Pa basınç yoktur\n"
        "- **Radyasyon:** manyetosfersiz ve ozonsuz kronik parçacık akısı yoktur\n"
        "- **Gün-gece döngüsü:** Ay'da bir gün ≈ 29,5 Dünya günü\n"
        "- **Regolit bileşimi:** Ay/Mars mineralojisi hiçbir Dünya kayaç türüne benzemez\n\n"
        "**Nitel (v1) etkenler (izlenir, sayısal skorda YOK — AGENTS.md §2):**\n"
        "- **Su buzu / kalıcı gölgeli bölgeler (PSR):** Dünya'da kalıcı gölgeli, "
        "kriyojenik soğuk arazi yoktur\n"
        "- **Lav tüpleri / yeraltı mağaraları:** varlık sahaya özgüdür; yalnızca "
        "jeoloji haritalarından nitel olarak değerlendirilir\n"
        "- **Elektrostatik toz / rüzgâr:** Ay'daki elektrostatik toz süspanasyonunun "
        "Dünya karşılığı yoktur; Dünya rüzgârı farklı (daha güçlü) bir süreçtir\n\n"
        "Dünya analoglarını yalnızca eşleşen eksenler için kullanın; kalanını "
        "laboratuvarda/simülasyonda doğrulayın."
    ),
}

I18N = {
    "en": {
        "app_title": "Moon / Mars ↔ Earth Analog Finder",
        "app_caption": (
            "Compare mobility, thermal and surface similarity indices. "
            "Scores are not probabilities."
        ),
        "thermal_data_note": (
            "Thermal scores currently use `temp_amplitude` only; "
            "`thermal_inertia` is unavailable for all current Moon/Earth sites."
        ),
        "settings": "Settings",
        "ref_body": "Reference body · Moon",
        "ref_site": "Reference site",
        "site_meta": (
            "`site_id`: {sid} · lat {lat:.2f}°, lon {lon:.2f}° · lithology: {lith}"
        ),
        "mission_uc": "Mission / use case",
        "top_n": "Top Earth sites shown",
        "thr": "Portfolio coverage threshold",
        "thr_help": (
            "Coverage threshold on the similarity index; it is not a "
            "calibrated probability."
        ),
        "ref_meas": "Reference measurements · {ref}",
        "ref_meas_note": (
            "`temp_amplitude` is the diurnal-cycle surface temperature range. "
            "Feature sources and native resolutions are shown above."
        ),
        "tabs": [
            "Map", "Radar", "Scores", "Validation", "Portfolio", "Analogy limits",
        ],
        "map_top": (
            "**Top {n} Earth sites for {ref}** · Marker size and colour encode "
            "the mission-weighted similarity index."
        ),
        "map_caption": (
            "Blue outline = known validation analogue. Candidate marker size "
            "and colour encode the mission-weighted similarity index (0–1)."
        ),
        "map_fallback": "pydeck not installed — falling back to st.map.",
        "tt_role": "Role", "tt_score": "Similarity index",
        "score_interval": "90% MC interval", "tt_lith": "Lithology",
        "radar_intro": (
            "Per-axis similarity indices (0–1). Lines show the 5th–95th "
            "Monte Carlo uncertainty percentiles."
        ),
        "radar_overall": (
            "Overall index: **{score:.2f}** [{interval}] ({n} axes used) "
            "· lithology: {lith}"
        ),
        "q95": "95th percentile",
        "q05": "5th percentile",
        "table_intro": (
            "Mission-weighted overall similarity index and per-axis indices. "
            "Brackets show 5th–95th Monte Carlo uncertainty percentiles."
        ),
        "filter_role": "Filter by role",
        "filter_help": (
            "validation = known analogues (blind check) · candidate = test "
            "candidates, never confirmed analogues."
        ),
        "col_site": "Site", "col_role": "Role",
        "col_lith": "Lithology", "col_overall": "Overall index",
        "matches_ref": "{lith} (matches reference)",
        "table_caption": (
            "— = axis not scoreable because required features are missing; "
            "if uncertainty is unavailable, only the point index is shown. "
            "Scores are similarity indices, not probabilities. Lithology is "
            "qualitative and is not included in the numeric score."
        ),
        "val_intro": (
            "Blind ranking diagnostic (`run_blind_validation`): roles never "
            "enter the scorer. This v1 check compares each validation site "
            "against every axis (rank ≤ {k} of {n}); it is descriptive, not a "
            "pass/fail claim. Define citation-backed expected site–axis pairs "
            "before claiming validation."
        ),
        "val_metric": "Validation pairs in top-k",
        "rank_axis": "Rank (1 = best)",
        "val_col_site": "Site", "val_col_axis": "Axis",
        "val_col_rank": "Rank", "val_col_nsites": "Sites scored",
        "port_intro": (
            "Greedy set-cover portfolio (heuristic; exact minimum site count "
            "when covering ≤3 axes; leader's `select_portfolio`): selects "
            "a compact portfolio of Earth sites covering the maximum number of "
            "axes with index ≥ **{thr:.2f}**. Greedy is fast and transparent "
            "for larger axis sets; axes no site "
            "covers must be validated in lab/simulation."
        ),
        "port_none": (
            "No Earth site reaches index {thr:.2f} on any axis — lower the "
            "threshold in the sidebar."
        ),
        "col_pick": "Pick", "col_covers": "Covers (index ≥ threshold)",
        "uncovered": "**Uncovered axes:** ",
        "covered_all": "none — all axes covered",
        "inspect": "Inspect candidate site",
        "inspect_help": (
            "Feature-gap breakdown for any candidate, not only the top one."
        ),
        "visual_head": "Visual and topographic context · {ref} vs {cand}",
        "moon_opt": "Moon Optical Context",
        "moon_topo": "Moon Topographic / Relief Context",
        "earth_opt": "Earth Candidate Optical Context",
        "wac_cap": (
            "{ref} — LRO WAC orthomosaic (~30×30 km window, display ~71 m/px; "
            "centered on {lat:.2f}°, {lon:.2f}°)"
        ),
        "wac_err": "Lunar WAC preview unavailable ({err}).",
        "wms_moon_only": (
            "Live lunar South Pole WMS applies to Moon reference sites only."
        ),
        "src_wac": (
            "Imagery source: NASA LRO Wide Angle Camera (WAC) via USGS "
            "Astrogeology WMS."
        ),
        "lola_cap": (
            "{ref} — LOLA shaded relief (~30×30 km window; DEM feature "
            "extraction radius = {rad:.0f} m)"
        ),
        "lola_err": "Lunar LOLA preview unavailable ({err}).",
        "src_lola": (
            "Relief preview: NASA LRO LOLA via USGS Astrogeology WMS. "
            "Numeric features come from row `*_src`."
        ),
        "esri_cap": (
            "{cand} ({lat:.4f}°, {lon:.4f}°) — ~{km:.1f}×{km:.1f} km window "
            "(analysis radius = {rad:.0f} m)"
        ),
        "esri_err": "Esri imagery preview unavailable ({err}).",
        "src_esri": (
            "**Optical preview source:** Esri World Imagery (Esri, Maxar, "
            "Earthstar Geographics). Note: numeric scores use the satellite "
            "datasets listed below (`*_src`), not this optical preview."
        ),
        "wv_link": "Open region in NASA EOSDIS Worldview",
        "gmaps_link": "Google Maps Satellite",
        "quant_head": "Quantitative context for the imagery above — ",
        "quant_range": "90% MC uncertainty interval [{lo:.2f}, {hi:.2f}]",
        "uncertainty_unavailable": "uncertainty interval unavailable",
        "quant_tail": (
            "\n\nVisual similarity alone is not enough: compare the orbital "
            "imagery above against the quantitative per-axis scores, "
            "uncertainty intervals, and instrument resolutions below."
        ),
        "gaps_head": "Feature gaps: {cand} vs {ref} (leader's `axis_gaps`)",
        "gaps_none": "No comparable features for this site.",
        "gaps_caption": (
            "|z_diff| large → biggest physical mismatch (sort order: largest "
            "first). `*_src` = dataset per AGENTS.md §5; `*_res_m` = native "
            "resolution — a coarse product (e.g. ~1 km MODIS) cannot resolve "
            "a 500 m site even when the DEM is 30 m."
        ),
        "footer": (
            "NASA Space Apps 2026 · Moon South Pole ↔ Earth Multi-Axis "
            "Analog Scorer"
        ),
    },
    "tr": {
        "app_title": "Ay / Mars ↔ Dünya Analog Bulucu",
        "app_caption": (
            "Mobilite, termal ve yüzey benzerlik indekslerini karşılaştırır. "
            "Skorlar olasılık değildir."
        ),
        "thermal_data_note": (
            "Termal skorlar şu anda yalnızca `temp_amplitude` kullanıyor; "
            "mevcut Ay/Dünya sahalarının hiçbirinde `thermal_inertia` verisi yok."
        ),
        "settings": "Ayarlar",
        "ref_body": "Referans gök cismi · Ay",
        "ref_site": "Referans saha",
        "site_meta": (
            "`site_id`: {sid} · enlem {lat:.2f}°, boylam {lon:.2f}° · "
            "litoloji: {lith}"
        ),
        "mission_uc": "Görev / kullanım senaryosu",
        "top_n": "Gösterilecek Dünya sahası sayısı",
        "thr": "Portföy kapsama eşiği",
        "thr_help": (
            "Benzerlik indeksi için kapsama eşiği; kalibre edilmiş bir "
            "olasılık değildir."
        ),
        "ref_meas": "Referans ölçümler · {ref}",
        "ref_meas_note": (
            "`temp_amplitude`, bir gün-gece döngüsündeki yüzey sıcaklık "
            "genliğidir. Özellik kaynakları ve özgün çözünürlükler yukarıda."
        ),
        "tabs": [
            "Harita", "Radar", "Skorlar", "Kör Doğrulama", "Minimal Portföy",
            "Analoji Sınırları",
        ],
        "map_top": (
            "**{ref} için ilk {n} Dünya sahası** · İşaretçi boyutu ve rengi "
            "görev-ağırlıklı benzerlik indeksini kodlar."
        ),
        "map_caption": (
            "Mavi çerçeve = bilinen doğrulama analoğu. Aday işaretçilerin "
            "boyutu ve rengi görev-ağırlıklı benzerlik indeksini kodlar (0–1)."
        ),
        "map_fallback": "pydeck kurulu değil — st.map'e düşülüyor.",
        "tt_role": "Rol", "tt_score": "Benzerlik indeksi",
        "score_interval": "%90 Monte Carlo aralığı", "tt_lith": "Litoloji",
        "radar_intro": (
            "Eksen bazlı benzerlik indeksleri (0–1). Çizgiler 5.–95. "
            "Monte Carlo belirsizlik yüzdeliklerini gösterir."
        ),
        "radar_overall": (
            "Genel indeks: **{score:.2f}** [{interval}] ({n} eksen kullanıldı) "
            "· litoloji: {lith}"
        ),
        "q95": "95. yüzdelik",
        "q05": "5. yüzdelik",
        "table_intro": (
            "Görev-ağırlıklı genel benzerlik indeksi ve eksen bazlı indeksler. "
            "Köşeli parantezler 5.–95. Monte Carlo belirsizlik yüzdeliklerini "
            "gösterir."
        ),
        "filter_role": "Role göre filtrele",
        "filter_help": (
            "validation = bilinen analoglar (kör denetim) · candidate = test "
            "adayları, asla doğrulanmış analog değiller."
        ),
        "col_site": "Saha", "col_role": "Rol",
        "col_lith": "Litoloji", "col_overall": "Genel indeks",
        "matches_ref": "{lith} (referansla eşleşiyor)",
        "table_caption": (
            "— = gerekli özellikler eksik olduğu için eksen skorlanamıyor; "
            "belirsizlik yoksa yalnızca nokta indeksi gösterilir. "
            "Skorlar olasılık değil benzerlik indeksidir. Litoloji nitel bir "
            "kolondur ve sayısal skora dahil değildir."
        ),
        "val_intro": (
            "Kör sıralama tanılaması (`run_blind_validation`): roller "
            "skorlayıcıya girmez. Bu v1 kontrolü her doğrulama sahasını her "
            "eksenle karşılaştırır (sıra ≤ {k}/{n}); betimseldir, başarı "
            "iddiası değildir. Doğrulama iddiasından önce kaynaklı saha–eksen "
            "eşleşmeleri belirlenmelidir."
        ),
        "val_metric": "Top-k içindeki doğrulama çiftleri",
        "rank_axis": "Sıra (1 = en iyi)",
        "val_col_site": "Saha", "val_col_axis": "Eksen",
        "val_col_rank": "Sıra", "val_col_nsites": "Skorlanan saha",
        "port_intro": (
            "Açgözlü küme-kapama portföyü (sezgisel; ≤3 eksende tam minimum "
            "saha sayısı; `select_portfolio`): indeksi ≥ **{thr:.2f}** olan "
            "eksen sayısını en çoklayan kompakt bir Dünya sahası seçer. "
            "Daha fazla eksende hızlı ve şeffaf bir sezgiseldir; hiçbir sahanın "
            "kapsamadığı eksenler laboratuvarda/simülasyonda doğrulanmalıdır."
        ),
        "port_none": (
            "Hiçbir Dünya sahası hiçbir eksende {thr:.2f} indeksine ulaşmıyor — "
            "kenar çubuğundaki eşiği düşürün."
        ),
        "col_pick": "Seçim", "col_covers": "Kapsadığı eksenler (indeks ≥ eşik)",
        "uncovered": "**Kapsanmayan eksenler:** ",
        "covered_all": "yok — tüm eksenler kapsandı",
        "inspect": "İncelenecek aday saha",
        "inspect_help": (
            "Yalnızca ilk sıradaki değil, herhangi bir adayın özellik-fark "
            "dökümü."
        ),
        "visual_head": "Görsel ve topografik bağlam · {ref} vs {cand}",
        "moon_opt": "Ay Optik Bağlam",
        "moon_topo": "Ay Topografik / Kabartma Bağlam",
        "earth_opt": "Dünya Aday Optik Bağlam",
        "wac_cap": (
            "{ref} — LRO WAC ortomozaik (~30×30 km pencere, görüntü ~71 m/px; "
            "merkez {lat:.2f}°, {lon:.2f}°)"
        ),
        "wac_err": "Ay WAC önizlemesi alınamadı ({err}).",
        "wms_moon_only": (
            "Canlı Ay Güney Kutbu WMS yalnızca Ay referans sahalarına "
            "uygulanır."
        ),
        "src_wac": (
            "Görüntü kaynağı: NASA LRO Geniş Açı Kamera (WAC), USGS "
            "Astrogeology WMS üzerinden."
        ),
        "lola_cap": (
            "{ref} — LOLA kabartma gölgeleme (~30×30 km pencere; DEM özellik "
            "çıkarım yarıçapı = {rad:.0f} m)"
        ),
        "lola_err": "Ay LOLA önizlemesi alınamadı ({err}).",
        "src_lola": (
            "Kabartma önizlemesi: NASA LRO LOLA, USGS Astrogeology WMS "
            "üzerinden. Sayısal özellikler satır bazlı `*_src` alanlarından "
            "gelir."
        ),
        "esri_cap": (
            "{cand} ({lat:.4f}°, {lon:.4f}°) — ~{km:.1f}×{km:.1f} km pencere "
            "(analiz yarıçapı = {rad:.0f} m)"
        ),
        "esri_err": "Esri görüntü önizlemesi alınamadı ({err}).",
        "src_esri": (
            "**Optik önizleme kaynağı:** Esri World Imagery (Esri, Maxar, "
            "Earthstar Geographics). Not: sayısal skorlar aşağıda listelenen "
            "uydu veri setlerini (`*_src`) kullanır; bu optik önizlemeyi değil."
        ),
        "wv_link": "NASA EOSDIS Worldview'de bölgeyi aç",
        "gmaps_link": "Google Maps Uydu",
        "quant_head": "Yukarıdaki görüntülerin sayısal bağlamı — ",
        "quant_range": "%90 Monte Carlo belirsizlik aralığı [{lo:.2f}, {hi:.2f}]",
        "uncertainty_unavailable": "belirsizlik aralığı hesaplanamıyor",
        "quant_tail": (
            "\n\nGörsel benzerlik tek başına yeterli değildir: yukarıdaki "
            "yörünge görüntülerini aşağıdaki eksen bazlı sayısal skorlar, "
            "belirsizlik aralıkları ve enstrüman çözünürlükleriyle "
            "karşılaştırın."
        ),
        "gaps_head": "Özellik farkları: {cand} vs {ref} (`axis_gaps`)",
        "gaps_none": "Bu saha için karşılaştırılabilir özellik yok.",
        "gaps_caption": (
            "|z_fark| büyük → en büyük fiziksel uyumsuzluk (sıralama: en "
            "büyük önce). `*_src` = AGENTS.md §5'e göre veri seti; "
            "`*_res_m` = özgün çözünürlük — kaba bir ürün (ör. ~1 km MODIS), "
            "DEM 30 m olsa bile 500 m'lik bir sahayı çözemez."
        ),
        "footer": (
            "NASA Space Apps 2026 · Ay Güney Kutbu ↔ Dünya Çok Eksenli "
            "Analog Skorlayıcı"
        ),
    },
}


def get(lang: str) -> dict:
    """Return the UI string dict for a language code ("tr" or "en")."""
    return I18N.get(lang, I18N["en"])
