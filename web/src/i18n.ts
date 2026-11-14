import type { FilterKey, Lang, MissionKey, WorkbenchTab } from "./types";

export const MISSIONS: Record<
  MissionKey,
  { tr: string; en: string; note_tr: string; note_en: string }
> = {
  default: {
    tr: "Dengeli",
    en: "Balanced",
    note_tr: "Mobilite (1.0) ve Yüzey (1.0) eşit ağırlıklıdır",
    note_en: "Mobility (1.0) and Surface (1.0) carry equal weight",
  },
  rover_mobility: {
    tr: "Gezgin araç testi",
    en: "Rover mobility test",
    note_tr: "Arazi eğimi ve pürüzlülük iki kat ağırlıklıdır (Hasandağı ve Etna yükselir)",
    note_en: "Terrain slope and roughness carry 2x weight (Hasandağı and Etna climb)",
  },
  isru_ice: {
    tr: "Kaynak / buz (verisiz)",
    en: "Resource / ice (no ice data)",
    note_tr: "Yüzey parlaklığına odaklanır; buz/uçucular doğrudan laboratuvarda doğrulanır",
    note_en: "Focuses on surface brightness while ground ice remains lab-verified",
  },
  radar_calibration: {
    tr: "Yeraltı radar kalibrasyonu",
    en: "Subsurface radar calibration",
    note_tr: "Yüzey parlaklığı ve yüzey karakteri iki kat ağırlıklıdır",
    note_en: "Surface brightness and terrain scattering carry 2x weight",
  },
};

export const FILTERS: Record<FilterKey, { tr: string; en: string }> = {
  all: { tr: "Tüm sahalar (40)", en: "All sites (40)" },
  tr: { tr: "Türkiye adayları (14)", en: "Turkey candidates (14)" },
  validation: { tr: "Bilinen analoglar (10)", en: "Known analogues (10)" },
  global: { tr: "Küresel adaylar (16)", en: "Global candidates (16)" },
};

export const WORKBENCH_TABS: { id: WorkbenchTab; tr: string; en: string }[] = [
  { id: "overview", tr: "Skorlar ve harita", en: "Scores and map" },
  { id: "terrain", tr: "3B arazi ve uydu", en: "3D terrain and orbital" },
  { id: "validation", tr: "Zorluklar, çözüm ve sıra tanısı", en: "Challenges, solution & diagnostics" },
  { id: "figures", tr: "Figürler ve kaynakça", en: "Figures and bibliography" },
];

export const FEATURE_NAMES: Record<string, { tr: string; en: string; unit: string }> = {
  slope_mean: { tr: "Ortalama eğim", en: "Mean slope", unit: "°" },
  slope_p90: { tr: "Dik eğim (p90)", en: "Steep slope (p90)", unit: "°" },
  roughness: { tr: "Yüzey pürüzlülüğü", en: "Surface roughness", unit: "m" },
  relief: { tr: "Yükselti farkı", en: "Elevation relief", unit: "m" },
  albedo: { tr: "Geniş bant albedo", en: "Broadband albedo", unit: "0–1" },
};

export const LITHOLOGY_NAMES: Record<string, { tr: string; en: string }> = {
  basalt: { tr: "Bazalt", en: "Basalt" },
  pyroclastic_tuff: { tr: "Volkanik tüf", en: "Pyroclastic tuff" },
  evaporite: { tr: "Evaporit / tuz düzlüğü", en: "Evaporite" },
  impact_breccia: { tr: "Çarpma breşi", en: "Impact breccia" },
  regolith_permafrost: { tr: "Donmuş regolit (permafrost)", en: "Frozen regolith (permafrost)" },
  regolith: { tr: "Ay regoliti", en: "Lunar regolith" },
};

export const CHALLENGE_STORY: Record<
  Lang,
  { tag: string; title: string; points: string[] }[]
> = {
  tr: [
    {
      tag: "01 · NASA Challenge Sorunu",
      title: "Tek bir Dünya sahası Ay'ı bütünüyle taklit edemez",
      points: [
        "Ay Güney Kutbu'ndaki Artemis III aday sahaları dik krater duvarları (18.5°), yüksek kabartma ve düşük atmosferli parlaklık profili sunar.",
        "Dünya'daki klasik test sahalarından Atacama ve Haughton düz Mars düzlükleridir; dik eğimli Etna ise koyu bazalt rengiyle Ay'dan ayrılır.",
        "Tek bir genel sıralama bu ayrışmaları gizler ve saha mühendisliğini yanlış teste yönlendirebilir.",
      ],
    },
    {
      tag: "02 · Karşılaştığımız Veri ve Fizik Zorlukları",
      title: "Farklı çözünürlükler, uyumsuz döngüler ve karma pikseller",
      points: [
        "Ay verisi LRO LOLA ile 5 m/px iken küresel Dünya DEM ürünleri 30 m/px çözünürlüktedir (Ağrı Dağı'ndaki Copernicus tile boşluğu için NASADEM EGM96 yedeği devreye alındı).",
        "Ay'ın 29.5 günlük vakum sıcaklık döngüsü ile Dünya'nın 24 saatlik atmosferik döngüsü aynı fiziksel ölçüt olmadığı için termal sayı üretmek yerine bu ekseni askıya aldık.",
        "500 m MODIS piksellerine su, tarım veya gölge karışabildiğinden 10 m WorldCover + Sentinel-2 denetimi ekledik.",
      ],
    },
    {
      tag: "03 · Geliştirdiğimiz Çözüm",
      title: "Çok eksenli skorlama, belirsizlik aralığı ve asgari test portföyü",
      points: [
        "Her Ay krateri ve 40 Dünya sahası birebir aynı r = 1000 m metrik pencerede Mobilite ve Yüzey eksenlerinde ayrı ayrı puanlandı.",
        "Tüm ölçümlere 200 çekilişli Monte Carlo hata aralığı (P5–P95) bağlandı; görev profili ve özel eksen ağırlıklarıyla anlık yeniden hesaplama eklendi.",
        "Tek saha yetmediğinde belirlenen eşiği aşan en küçük Dünya test kümesi seçildi; Türkiye sahaları bilimsel dürüstlük gereği aday olarak konumlandı.",
      ],
    },
  ],
  en: [
    {
      tag: "01 · The NASA Challenge Problem",
      title: "No single Earth site reproduces Lunar conditions across every axis",
      points: [
        "Artemis III south pole targets combine steep crater walls (18.5°), deep relief and vacuum reflectance that no single terrestrial site matches.",
        "Classic Mars sites like Atacama and Haughton are relatively flat, whereas steep Mt. Etna differs sharply in dark mare-like basalt albedo.",
        "Reducing sites to a single composite score hides fatal physical mismatches before rover or lander field tests begin.",
      ],
    },
    {
      tag: "02 · Real Data & Physics Obstacles",
      title: "Resolution mismatches, non-equivalent thermal cycles & mixed pixels",
      points: [
        "Lunar LRO LOLA resolves 5 m/px while global Copernicus GLO-30 resolves 30 m/px (requiring a NASADEM EGM96 fallback on Mount Ararat where Copernicus lacked a tile).",
        "Because a 29.5-day vacuum lunar cycle and a 24-hour Earth diurnal cycle represent incompatible thermal physics, synthetic gap-filling was rejected.",
        "Coarse 500 m MODIS pixels can dilute surface reflectance with snow, crops or lakes, requiring 10 m Sentinel-2 L2A & WorldCover audits.",
      ],
    },
    {
      tag: "03 · Our Solution",
      title: "Per-axis telemetry, Monte Carlo uncertainty & compact portfolios",
      points: [
        "All 5 Moon craters and 40 Earth sites are projected to metric coordinates and measured over identical r = 1000 m circular windows.",
        "Scores separate Mobility and Surface independently, propagate uncertainty with 200 Monte Carlo draws, and adapt instantaneously to mission weight sliders.",
        "A greedy set-cover optimizer builds the smallest Earth test-site portfolio that covers target thresholds while keeping newly studied Turkish fields transparently flagged as candidates.",
      ],
    },
  ],
};

export const ACHIEVEMENT_PILLARS: Record<
  Lang,
  { badge: string; title: string; source: string; detail: string }[]
> = {
  tr: [
    {
      badge: "Mobilite Ekseni",
      title: "Eşit r = 1000 m metrik arazi ve eğim uyumu",
      source: "LRO LOLA 5 m · Copernicus GLO-30 / NASADEM 30 m",
      detail:
        "Tüm sahalar yerel metrik koordinatlara dönüştürülerek ortalama eğim, p90 dik eğim, pürüzlülük ve yükselti farkı üzerinden objektif kıyaslanır.",
    },
    {
      badge: "Yüzey Ekseni",
      title: "Geniş bant albedo ve duyarlılık testi",
      source: "LOLA 1064 nm · MODIS MCD43A3 (c = 0.30–0.46)",
      detail:
        "Kutup regoliti ile Dünya bazalt, tüf ve tuz düzlükleri arasındaki parlaklık uyumu dönüşüm faktörü duyarlılık testleriyle doğrulanır.",
    },
    {
      badge: "Belirsizlik & Kalite",
      title: "200 çekilişli Monte Carlo P5–P95 ve 10 m denetim",
      source: "ESA WorldCover 10 m · Sentinel-2 L2A · 51/51 test",
      detail:
        "Sıralamalar P5–P95 güven aralığıyla birlikte sunulur; 10 m uydu görüntüsüyle karma piksel taşıyan sahalar otomatik işaretlenir.",
    },
    {
      badge: "Görev & Portföy",
      title: "Asgari test kümesi ve çevrimdışı 3B atlas",
      source: "5 Ay krateri × 40 Dünya sahası · 0 yapay veri",
      detail:
        "Gezgin, radar ve denge profilleri ile tek tıkla 5 m / 10 m çevrimdışı uydu kesitleri ve asgari test portföyü canlı hesaplanır.",
    },
  ],
  en: [
    {
      badge: "Mobility Axis",
      title: "Metric r = 1000 m terrain geometry across Moon & Earth",
      source: "LRO LOLA 5 m · Copernicus GLO-30 / NASADEM 30 m",
      detail:
        "Reprojected into planar metric CRS so slope_mean, p90 steepness, roughness and elevation relief share exact physical definitions.",
    },
    {
      badge: "Surface Axis",
      title: "Broadband albedo harmonization & sensitivity curve",
      source: "LOLA 1064 nm · MODIS MCD43A3 (c = 0.30–0.46)",
      detail:
        "Measures highland regolith reflectance against basalt, tuff and evaporite fields, stress-tested across reflectance conversion factors.",
    },
    {
      badge: "Uncertainty & Audit",
      title: "200-draw Monte Carlo intervals & 10 m pixel screening",
      source: "ESA WorldCover 10 m · Sentinel-2 L2A · 51/51 tests",
      detail:
        "Every score publishes P5–P95 percentile uncertainty alongside automated 10 m landcover screening against water or vegetation mixing.",
    },
    {
      badge: "Mission & Portfolio",
      title: "Minimal test portfolio & offline 3D relief inspector",
      source: "5 Lunar craters × 40 Earth sites · 0 mock rows",
      detail:
        "Customizable mission weight sliders and greedy set-cover selection pair directly with offline 3D DEM meshes and Sentinel-2 imagery.",
    },
  ],
};

export const JURY_DEMO_TOUR: {
  id: string;
  moonId: string;
  mission: MissionKey;
  earthId: string;
  tab: WorkbenchTab;
  trTitle: string;
  enTitle: string;
  trSpeech: string;
  enSpeech: string;
}[] = [
  {
    id: "step1",
    moonId: "moon_shackleton_rim",
    mission: "default",
    earthId: "earth_karapinar_meke",
    tab: "overview",
    trTitle: "01 · Problem ve Shackleton seçimi",
    enTitle: "01 · Problem & Shackleton baseline",
    trSpeech:
      "Shackleton Kenarı 18.50° eğime ve 0.147 albedoya sahiptir. Dengeli modda Karapınar Meke Yüzey #1 (0.903) ile toplamda öne geçerken Mobilite açığı radar ve fark tablosunda net görülür.",
    enSpeech:
      "Shackleton Rim pairs 18.50° mean slope with 0.147 albedo. Under Balanced weights Karapınar Meke leads overall via Surface #1 (0.903), while its mobility gap remains transparent.",
  },
  {
    id: "step2",
    moonId: "moon_shackleton_rim",
    mission: "rover_mobility",
    earthId: "earth_hasandagi_kecekalecik",
    tab: "overview",
    trTitle: "02 · Görev ağırlığı: Hasandağı #1",
    enTitle: "02 · Mission shift: Hasandağı #1",
    trSpeech:
      "Görev profili Gezgin Araç Testi'ne geçince (Mobilite 2x) sıralama anında değişir ve Hasandağı Keçikaleçik #1 sıraya çıkar. Özel ağırlık sürgüleriyle kendi profilinizi test edebilirsiniz.",
    enSpeech:
      "Switching to Rover Mobility (2x) elevates Hasandağı Keçikaleçik cleanly to #1, and custom weight sliders let engineers test bespoke weighting profiles live.",
  },
  {
    id: "step3",
    moonId: "moon_faustini_rim",
    mission: "default",
    earthId: "earth_etna_cisternazza",
    tab: "validation",
    trTitle: "03 · Etna ayrışması ve Faustini kayması",
    enTitle: "03 · Etna split & Faustini recovery",
    trSpeech:
      "Dik Shackleton'da Mobilite #3 olan Etna (22.74°) koyu albedosu (0.047) nedeniyle Yüzey'de ayrışır. Daha yatık Faustini Kenarı'na geçince Svalbard #3, Haughton #6 ve Atacama #8 üst sıralara tırmanır.",
    enSpeech:
      "Steep Etna splits between Mobility #3 and dark mare albedo; switching to gentler Faustini (5.20°) immediately recovers Svalbard #3, Haughton #6 and Atacama #8.",
  },
  {
    id: "step4",
    moonId: "moon_shackleton_rim",
    mission: "default",
    earthId: "earth_karacadag_summit",
    tab: "validation",
    trTitle: "04 · Karacadağ adayı ve kalibrasyon",
    enTitle: "04 · Karacadağ discipline & calibration",
    trSpeech:
      "Karacadağ doğrulanmış analog değil nicel aday olarak etiketlenir. Alttaki duyarlılık testi LOLA 1064 nm dönüşümünü (c = 0.30–0.46) ve 10 m WorldCover + Sentinel-2 karma piksel denetimini gösterir.",
    enSpeech:
      "Karacadağ is kept strictly as a quantitative test candidate. Sensitivity curves test c in [0.30..0.46] while WorldCover + Sentinel-2 audits flag 1 km mixed-pixel risks.",
  },
  {
    id: "step5",
    moonId: "moon_shackleton_rim",
    mission: "default",
    earthId: "earth_karapinar_meke",
    tab: "terrain",
    trTitle: "05 · 3B LOLA DEM, eğim haritası ve uydu",
    enTitle: "05 · 3D LOLA DEM, slope map & satellite",
    trSpeech:
      "5 m/px NASA LRO LOLA ve 30 m/px Copernicus GLO-30 yüzeyleri; yükseklik, <10°/10–20°/>20° eğim tehlikesi ve kontur görünümleriyle anlık yükseklik-eğim sorgulama olanağı sunar.",
    enSpeech:
      "Real 5 m/px LRO LOLA vs 30 m/px Copernicus surfaces include elevation, slope hazard bins and contour modes with interactive point probing.",
  },
];

export const ANALYSIS_FIGURES: {
  file: string;
  trTitle: string;
  enTitle: string;
  trCap: string;
  enCap: string;
}[] = [
  {
    file: "/figures/fig01_shackleton_top15_axes.png",
    trTitle: "Figür 1 · Shackleton Kenarı ilk 15 saha ve eksen ayrışması",
    enTitle: "Figure 1 · Shackleton Rim top 15 sites and axis split",
    trCap: "Dengeli profilde Karapınar Meke (0.528, Yüzey #1 = 0.903) ilk sırada yer alırken Hasandağı Keçikaleçik Mobilite #1 (0.335) performansıyla ayrışır",
    enCap: "Karapınar Meke leads Balanced scoring (0.528, Surface #1 = 0.903) while Hasandağı leads Mobility (#1 = 0.335) on Shackleton's 18.50° terrain",
  },
  {
    file: "/figures/fig02_mission_reweighting.png",
    trTitle: "Figür 2 · Görev profiline göre sıra kayması",
    enTitle: "Figure 2 · Rank shifts under mission reweighting",
    trCap: "Gezgin araç modunda (Mobilite 2x) Hasandağı #3'ten #1'e yükselir; Etna Cisternazza #26'dan #17'ye çıkar",
    enCap: "Under 2x Mobility weighting, Hasandağı rises #3 to #1 and Etna Cisternazza moves #26 to #17",
  },
  {
    file: "/figures/fig03_moon_regions_heatmap.png",
    trTitle: "Figür 3 · Beş Ay Güney Kutbu bölgesinde ısı haritası",
    enTitle: "Figure 3 · Multi-axis heatmap across five Lunar South Pole sites",
    trCap: "Tek bir evrensel analog yoktur: dik Shackleton'da Hasandağı ve Karapınar, yatık Faustini'de Salda, Karacadağ Kollubaba ve Svalbard öne geçer",
    enCap: "No site dominates every crater: Hasandağı and Karapınar lead steep Shackleton while Salda, Karacadağ and Svalbard lead gentler Faustini",
  },
  {
    file: "/figures/fig04_physical_space_validation.png",
    trTitle: "Figür 4 · Fiziksel uzay ve 10 doğrulama sahası sıra tanısı",
    enTitle: "Figure 4 · Slope-albedo space and blind validation rank diagnostic",
    trCap: "Etna (22.74°, albedo 0.047) eğimde Shackleton'a yakın olsa da koyu Mare albedosu nedeniyle parlak kutup regolitinden (0.147) ayrışır",
    enCap: "Etna matches Shackleton slope (22.74° vs 18.50°) but separates cleanly on dark Mare albedo (0.047 vs 0.147)",
  },
  {
    file: "/figures/fig05_orbital_evidence_gallery.png",
    trTitle: "Figür 5 · Çevrimdışı 5 m LOLA ve 10 m Sentinel-2 L2A kanıtları",
    enTitle: "Figure 5 · Offline 5 m LOLA hillshade and 10 m Sentinel-2 L2A gallery",
    trCap: "Uygulama ağ bağımlılığı olmadan LRO LOLA 5 m kabartma/eğim haritalarını ve %0 bulutlu Sentinel-2 L2A uydu görüntülerini doğrudan sunar",
    enCap: "Local offline tiles combine 5 m LRO LOLA relief/slope bins with 0% cloud 10 m Sentinel-2 L2A imagery",
  },
];

export const UI_COPY: Record<Lang, Record<string, string>> = {
  tr: {
    brand: "Endülüs",
    subtitleTag: "NASA Space Apps 2026",
    navWorkbench: "Skorlar ve harita",
    navTerrain: "3B arazi ve uydu",
    navValidation: "Zorluklar ve sıra tanısı",
    navFigures: "Figürler ve kaynakça",
    heroTitle: "Ay Güney Kutbu için çok eksenli Dünya analogu seçimi",
    heroBody:
      "Hiçbir Dünya sahası Ay koşullarını tek başına karşılayamaz. Bu platform beş Artemis III aday Ay bölgesini kırk Dünya sahasıyla arazi mobilitesi ve yüzey parlaklığı eksenlerinde ayrı ayrı puanlar, her sonuca belirsizlik ve fiziksel sınır ekler.",
    heroPrimaryCta: "Gözlemevini aç",
    moonRegionLabel: "Ay referans krateri",
    missionLabel: "Görev profili ve özel ağırlık",
    filterLabel: "Saha havuzu",
    earthPickerLabel: "Hızlı Dünya sahası seçici (40)",
    searchPlaceholder: "Saha, ID veya litoloji ara",
    selectedEarthLabel: "Seçili Dünya sahası",
    tourBadge: "Sunum turu",
    mapZoomGlobal: "Küresel görünüm",
    mapZoomTurkey: "Türkiye odağı (14 aday)",
    chartTitle: "Eksen puanları ve Monte Carlo P5–P95 aralığı",
    chartNote: "Puanlar 0–1 sıralama indeksidir, olasılık değildir",
    modeOverall: "Genel",
    modeMobility: "Mobilite",
    modeSurface: "Yüzey",
    gapsTitle: "Özellik bazlı fiziksel farklar (Ay vs Dünya)",
    demTitleMoon: "Ay 3B arazi (5 m/px LRO LOLA)",
    demTitleEarth: "Dünya 3B arazi (30 m/px uydu DEM)",
    exaggeration: "Dikey abartı",
    azimuth: "Yön açısı",
    pitch: "Bakış eğimi",
    zoom: "Yakınlaştırma",
    orbitalMoonTitle: "NASA LRO LOLA 5 m kabartma ve eğim sınıfları",
    orbitalEarthTitle: "ESA Sentinel-2 L2A 10 m gerçek uydu görüntüsü",
    validationIntro:
      "40 sahanın tamamı Z-ölçeklemesine katılır; bilinen 10 doğrulama sahası (Etna, Atacama, Haughton vb.) ön-kayıtlı DOI literatürüyle karşılaştırılırken Karacadağ, Hasandağı ve Karapınar gibi az çalışılmış sahalar nicel test adayı olarak tutulur.",
    whySplitTitle: "Challenge sorunu, karşılaştığımız zorluklar ve çözümümüz",
    limitsTitle: "Neleri başardık? Aktif çözüm kapsamı",
    bibMoonTitle: "Ay Güney Kutbu yörünge veri setleri ve akademik literatür",
    bibEarthTitle: "Dünya uydu ürünleri, kalibrasyon ve doğrulama kaynakları",
    bibTableTitle: "40 sahanın koordinat, DEM ve akademik kaynakça dizini",
    bibSearchPlaceholder: "Yazar, DOI, saha veya uydu ara",
  },
  en: {
    brand: "Endülüs",
    subtitleTag: "NASA Space Apps 2026",
    navWorkbench: "Scores & map",
    navTerrain: "3D terrain & orbital",
    navValidation: "Challenges & validation",
    navFigures: "Figures & bibliography",
    heroTitle: "Multi-axis Earth analogue selection for lunar south pole bases",
    heroBody:
      "No single terrestrial site reproduces lunar conditions on every axis. This workbench scores five Artemis III candidate Moon sites against forty Earth field sites across terrain mobility and surface albedo with Monte Carlo uncertainty.",
    heroPrimaryCta: "Open observatory",
    moonRegionLabel: "Lunar reference crater",
    missionLabel: "Mission profile & custom weights",
    filterLabel: "Site pool",
    earthPickerLabel: "Quick Earth site selector (40)",
    searchPlaceholder: "Search site, ID or lithology",
    selectedEarthLabel: "Selected Earth site",
    tourBadge: "Guided tour",
    mapZoomGlobal: "Global view",
    mapZoomTurkey: "Turkey focus (14 candidates)",
    chartTitle: "Axis scores with Monte Carlo P5–P95 intervals",
    chartNote: "Scores are 0–1 ranking indices, not probabilities",
    modeOverall: "Overall",
    modeMobility: "Mobility",
    modeSurface: "Surface",
    gapsTitle: "Feature-level physical gaps (Moon vs Earth)",
    demTitleMoon: "Lunar 3D terrain (5 m/px LRO LOLA)",
    demTitleEarth: "Earth 3D terrain (30 m/px satellite DEM)",
    exaggeration: "Vertical exaggeration",
    azimuth: "Azimuth",
    pitch: "Tilt pitch",
    zoom: "Zoom",
    orbitalMoonTitle: "NASA LRO LOLA 5 m relief and slope hazard",
    orbitalEarthTitle: "ESA Sentinel-2 L2A 10 m orbital view",
    validationIntro:
      "All 40 sites enter Z-scaling without role labels; established analogues (Etna, Atacama, Haughton) are audited against pre-registered DOI literature while lesser-studied fields like Karacadağ remain quantitative candidates.",
    whySplitTitle: "Challenge framing, real obstacles & our engineering solution",
    limitsTitle: "What we achieved: active analytical scope",
    bibMoonTitle: "Lunar South Pole orbital datasets and literature",
    bibEarthTitle: "Earth satellite products, calibration & validation sources",
    bibTableTitle: "40-site coordinate, DEM and academic citation ledger",
    bibSearchPlaceholder: "Search author, DOI, site or sensor",
  },
};
