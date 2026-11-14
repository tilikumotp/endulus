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
    note_tr: "Termal eksen askıda olduğundan bu profilde Yüzey ekseni 2:1 baskındır",
    note_en: "With thermal suspended, Surface carries 2:1 effective weight here",
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
  { id: "validation", tr: "Sıra tanısı ve sınırlar", en: "Rank diagnostic and limits" },
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

export const JURY_STORY_STEPS: Record<
  Lang,
  { step: string; title: string; metric: string; body: string }[]
> = {
  tr: [
    {
      step: "01",
      title: "Doğrulanmış yörünge ve uydu verisi",
      metric: "45 saha · 0 yapay veri",
      body: "5 Ay Güney Kutbu krateri NASA LRO LOLA 5 m yükseklik modeliyle, 40 Dünya sahası Copernicus/NASADEM 30 m ve MODIS 500 m ürünleriyle aynı r = 1000 m çapta ölçüldü",
    },
    {
      step: "02",
      title: "Termal eksende bilimsel dürüstlük",
      metric: "Karar #30 · 2 aktif eksen",
      body: "Ay'da 29.5 günlük vakumlu döngü ile Dünya'da 24 saatlik atmosferli döngü farklı fiziksel tanımlar verdiği için termal eksen zorlama puanlanmadan askıya alındı",
    },
    {
      step: "03",
      title: "Eksen bazlı puanlama ve belirsizlik",
      metric: "200 Monte Carlo çekilişi",
      body: "Tek bir genel puan kusurları gizlediği için Mobilite ve Yüzey eksenleri ayrı hesaplandı; görev seçildikçe sıralama anlık güncellenir ve P5–P95 belirsizlik aralığı gösterilir",
    },
    {
      step: "04",
      title: "Bilinen sahalar ve saha sınırları",
      metric: "51/51 test · yerel atlaslar",
      body: "Etna, Atacama ve Haughton gibi 10 bilinen analog etiket verilmeden sınandı; Türkiye sahaları (Hasandağı, Karapınar, Karacadağ) doğrulanmış analog yerine test adayı olarak raporlandı",
    },
  ],
  en: [
    {
      step: "01",
      title: "Verified orbital and Earth telemetry",
      metric: "45 sites · 0 mock rows",
      body: "Five Lunar South Pole targets measured from NASA LRO LOLA 5 m DEM and 40 Earth sites from Copernicus/NASADEM 30 m and MODIS 500 m inside an identical r = 1000 m window",
    },
    {
      step: "02",
      title: "Scientific honesty on thermal cycling",
      metric: "Decision #30 · 2 active axes",
      body: "A 29.5-day vacuum lunar cycle and a 24-hour atmospheric Earth cycle follow incompatible physical definitions, so the thermal axis was deliberately suspended in v1",
    },
    {
      step: "03",
      title: "Per-axis scoring with uncertainty",
      metric: "200 Monte Carlo draws",
      body: "Single composite ranks hide mismatches, so Mobility and Surface are scored separately, reweighted by mission profile, and bracketed with P5–P95 percentile ranges",
    },
    {
      step: "04",
      title: "Blind rank diagnostics and field limits",
      metric: "51/51 tests · offline assets",
      body: "Ten established analogues (Etna, Atacama, Haughton) are audited blind against DOI expectations while Turkish fields (Hasandağı, Karapınar, Karacadağ) are flagged as test candidates",
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
      "Görev profili Gezgin Araç Testi'ne geçince (Mobilite 2x) sıralama anında değişir ve Hasandağı Keçikaleçik #1 sıraya çıkar. Sağdaki portföy sürgüsü ise eşiği aşan en küçük saha grubunu hesaplar.",
    enSpeech:
      "Switching to Rover Mobility (2x) elevates Hasandağı Keçikaleçik cleanly to #1, while the live threshold slider computes the minimal test-site portfolio.",
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
    trTitle: "05 · 3B LOLA DEM, kesitler ve uydu",
    enTitle: "05 · 3D LOLA DEM, transects & satellite",
    trSpeech:
      "5 m/px NASA LRO LOLA ve 30 m/px Copernicus GLO-30 yüzeyleri, ±1100 m Doğu-Batı / Kuzey-Güney profilleri ve %0 bulutlu 10 m Sentinel-2 görüntüleri tamamen çevrimdışı sunulur.",
    enSpeech:
      "Real 5 m/px LRO LOLA vs 30 m/px Copernicus surfaces, ±1100 m W–E/S–N transects and 10 m Sentinel-2 L2A patches run fully offline.",
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
    trCap: "Etna (22.74°, albedo 0.047) eğimde Shackleton'a yakın olsa da koyu Mare albedosu nedeniyle parlak kutup regolithinden (0.147) ayrışır",
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
    navStory: "Bugün ne yaptık",
    navWorkbench: "Canlı gözlemevi",
    navValidation: "Sıra tanısı",
    navFigures: "Figürler ve kaynakça",
    heroTitle: "Ay Güney Kutbu için çok eksenli Dünya analogu seçimi",
    heroBody: "Hiçbir Dünya sahası Ay koşullarını tek başına karşılayamaz. Bu platform beş Artemis III aday Ay bölgesini kırk Dünya sahasıyla arazi mobilitesi ve yüzey parlaklığı eksenlerinde ayrı ayrı puanlar, her sonuca belirsizlik ve fiziksel sınır ekler.",
    heroPrimaryCta: "Gözlemevini aç",
    heroSecondaryCta: "Jüri özetini oku",
    moonRegionLabel: "Ay referans krateri",
    missionLabel: "Görev profili",
    filterLabel: "Saha havuzu",
    searchPlaceholder: "Saha, ID veya litoloji ara",
    selectedEarthLabel: "Seçili Dünya sahası",
    portfolioTitle: "0.70 eşiğinde çevrimdışı kapsam",
    portfolioCovered: "Kapsanan eksenler",
    portfolioUncovered: "Kapsam dışı / laboratuvar",
    storySectionTitle: "Jüriye 4 adımda bugün kurulan sistem",
    storySectionSub: "Doğrulanmış yörünge verilerine, tek saf siyah temaya ve 51 otomatik teste dayanır",
    tourBadge: "Jüri sunum turu",
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
    azimuth: "Kamera açısı",
    dragHint: "Döndürmek için yüzeyi sürükleyin",
    orbitalMoonTitle: "NASA LRO LOLA 5 m kabartma ve eğim sınıfları",
    orbitalEarthTitle: "ESA Sentinel-2 L2A 10 m gerçek uydu görüntüsü",
    validationIntro: "40 sahanın tamamı ölçeklemeye katılır; bu tablo bağımsız test değil, ön-kayıtlı DOI literatürüyle betimsel sıra tanısıdır",
    whySplitTitle: "Bilinen analoglar neden ayrışır",
    etnaExplain: "Etna Cisternazza Shackleton kenarıyla eğimde örtüşür (22.74° vs 18.50°, Mobilite #3/40), fakat 0.047 koyu bazalt albedosu nedeniyle 0.147 parlaklıktaki kutup regolitinden Yüzey'de (#37/40) ayrılır.",
    atacamaExplain: "Atacama (2.65°) ve Haughton (3.51°) düz Mars test sahalarıdır. Shackleton'da alt sıralarda görünürken, daha yatık Faustini Kenarı (5.20°) seçildiğinde Mobilite ekseninde Svalbard #3 (0.759), Mauna Loa #5 (0.733), Haughton #6 (0.727) ve Atacama #8 (0.723) konumuna yükselirler.",
    karacadagExplain: "Karacadağ Kollubaba Faustini'de #2 (0.761) ve Shackleton'da #10 (0.419) skor alır; ancak az çalışılmış bir saha olduğu için doğrulanmış analog olarak değil, nicel test adayı olarak sınıflandırılır.",
    limitsTitle: "8 boyutlu analoji kapsamı ve fiziksel sınırlar",
    bibMoonTitle: "Emirhan (p2-moonmars) · Ay Güney Kutbu veri ve makaleleri",
    bibEarthTitle: "Eray (p3-earth) · Dünya uydu ürünleri ve kalibrasyon",
    bibTableTitle: "40 sahanın koordinat ve akademik kaynakçası",
    bibSearchPlaceholder: "Yazar, DOI veya saha ara",
  },
  en: {
    brand: "Endülüs",
    subtitleTag: "NASA Space Apps 2026",
    navStory: "What we built",
    navWorkbench: "Live observatory",
    navValidation: "Rank diagnostic",
    navFigures: "Figures and references",
    heroTitle: "Multi-axis Earth analogue selection for lunar south pole bases",
    heroBody: "No single terrestrial site reproduces lunar conditions on every axis. This workbench scores five Artemis III candidate Moon sites against forty Earth field sites across terrain mobility and surface albedo with Monte Carlo uncertainty.",
    heroPrimaryCta: "Open workbench",
    heroSecondaryCta: "Read jury summary",
    moonRegionLabel: "Lunar reference crater",
    missionLabel: "Mission profile",
    filterLabel: "Site pool",
    searchPlaceholder: "Search site, ID or lithology",
    selectedEarthLabel: "Selected Earth site",
    portfolioTitle: "Offline coverage at 0.70 threshold",
    portfolioCovered: "Covered axes",
    portfolioUncovered: "Uncovered / laboratory",
    storySectionTitle: "How the system works in four steps",
    storySectionSub: "Backed by verified orbital telemetry, single dark theme and 51 automated tests",
    tourBadge: "Jury guided tour",
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
    azimuth: "Camera orbit",
    dragHint: "Drag surface to orbit",
    orbitalMoonTitle: "NASA LRO LOLA 5 m relief and slope hazard",
    orbitalEarthTitle: "ESA Sentinel-2 L2A 10 m orbital view",
    validationIntro: "All 40 sites enter Z-scaling without role labels; this is a descriptive rank diagnostic against pre-registered DOIs, not an independent holdout",
    whySplitTitle: "Why established analogues separate physically",
    etnaExplain: "Etna Cisternazza matches Shackleton's steep slope (22.74° vs 18.50°, Mobility #3/40) yet separates on dark basalt albedo (0.047 vs 0.147, Surface #37/40).",
    atacamaExplain: "Atacama (2.65°) and Haughton (3.51°) are flat Mars-type plains. Under gentler Faustini Rim (5.20°), they rise cleanly on Mobility: Svalbard #3 (0.759), Mauna Loa #5 (0.733), Haughton #6 (0.727) and Atacama #8 (0.723).",
    karacadagExplain: "Karacadağ Kollubaba reaches #2 at Faustini (0.761) and #10 at Shackleton (0.419), yet as a lesser-studied basalt plateau it is presented strictly as a quantitative test candidate, never a confirmed analogue.",
    limitsTitle: "8-dimension analogy coverage and physical limits",
    bibMoonTitle: "Emirhan (p2-moonmars) · Lunar South Pole data and literature",
    bibEarthTitle: "Eray (p3-earth) · Earth satellite products and calibration",
    bibTableTitle: "40-site coordinate and citation ledger",
    bibSearchPlaceholder: "Search author, DOI or site",
  },
};
