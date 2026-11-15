import type { Lang, MissionKey, WorkbenchTab } from "./types";

export const MISSIONS: Record<
  MissionKey,
  { tr: string; en: string; ratio: string; note_tr: string; note_en: string }
> = {
  default: {
    tr: "Dengeli rover testi",
    en: "Balanced rover test",
    ratio: "50/50",
    note_tr:
      "Sürüş yeteneği ve yüzey parlaklığı eşit (%50 / %50) değerlendirilir; genel rover uyumu için başlangıç noktasıdır.",
    note_en:
      "Terrain driveability and surface brightness carry equal weight (50% / 50%) for general rover fit.",
  },
  rover_mobility: {
    tr: "Tırmanma ve tekerlek testi",
    en: "Climb & wheel test",
    ratio: "67/33",
    note_tr:
      "Tekerlek tutuşu ve tırmanma testleri için eğim, pürüzlülük ve rölyef (%67) yüzey parlaklığının iki katı öne çıkar.",
    note_en:
      "Slope, roughness and elevation relief carry 2x weight (67%) for wheel traction and climb trials.",
  },
  optical_survey: {
    tr: "Optik kamera ve güneş paneli testi",
    en: "Optical camera & solar panel test",
    ratio: "33/67",
    note_tr:
      "Navigasyon kamerasının kontrast/pozlama dengesi ve güneş panellerine düşen yansıyan ışık için yüzey parlaklığı albedo (%67) eğime göre iki kat öne çıkar.",
    note_en:
      "Surface brightness (albedo, 67%) carries 2x weight over slope: it drives nav-camera contrast/exposure and light reflected onto solar panels.",
  },
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
  regolith_permafrost: { tr: "Donmuş toprak (permafrost)", en: "Frozen ground (permafrost)" },
  regolith: { tr: "Ay regoliti", en: "Lunar regolith" },
};

export const CHALLENGE_STORY: Record<
  Lang,
  { tag: string; title: string; points: string[] }[]
> = {
  tr: [
    {
      tag: "01 · Sorun",
      title: "Dünya'da Ay'ın birebir aynısı tek bir yer yok",
      points: [
        "Artemis III'ün ineceği Ay Güney Kutbu hem dik krater yamaçlarına (18.5°) hem de açık renkli tozlu bir yüzeye sahiptir.",
        "Bilinen ünlü sahalardan Atacama ve Haughton çok düzdür; dik eğimli Etna'nın taşı ise Ay toprağına göre çok koyudur.",
        "Sahalara tek bir genel puan vermek bu farkları gizler ve mühendisleri yanlış yerde araç test etmeye yönlendirebilir.",
      ],
    },
    {
      tag: "02 · Karşılaştığımız Zorluklar",
      title: "Veriler aynı ölçüde değildi ve sıcaklıklar kıyaslanamıyordu",
      points: [
        "Ay haritaları her 5 metrede bir detay verirken Dünya uydu verisi 30 metrede bir çiziliyor; yüksek dağlarda (Ağrı gibi) eksik kalan yerler için yedek uydu verisi kullanmak gerekti.",
        "Ay'da bir gün yaklaşık 1 ay sürerken Dünya'da 24 saat sürer. Sıcaklık döngüleri fiziksel olarak uyuşmadığı için yanıltıcı sıcaklık kıyaslaması yapmadık.",
        "Bazı uydu piksellerinin içine su veya bitki örtüsü de karıştığı için sadece çıplak zemin özelliklerini dikkatle ayırdık.",
      ],
    },
    {
      tag: "03 · Çözümümüz",
      title: "Araç sürüşünü ve zemin dokusunu ayrı ölçtük, seçimi esnek yaptık",
      points: [
        "5 Ay kraterini ve Dünya'daki 40 test sahasını tamamen aynı büyüklükteki 1 km yarıçaplı daireler içinde ölçtük.",
        "Her saha için araç sürüşüne uygunluk (Mobilite) ve yüzey parlaklığı (Yüzey) ayrı ayrı puanlandı, yanına hata payı eklendi.",
        "Görev türüne göre (örneğin sadece gezgin araç testi) ağırlıklar kaydırılarak Türkiye'dekiler dahil en uygun test sahaları şeffafça sıralanır.",
      ],
    },
  ],
  en: [
    {
      tag: "01 · The Problem",
      title: "No single place on Earth matches the Moon in every respect",
      points: [
        "Lunar south pole sites combine steep crater walls (18.5°) with bright highland regolith reflectance.",
        "Famous analogues like Atacama and Haughton are mostly flat plains, while steep Mt. Etna has much darker volcanic basalt.",
        "Giving each site one blended number hides these physical mismatches before field testing.",
      ],
    },
    {
      tag: "02 · Data Obstacles",
      title: "Different map resolutions and incompatible day-night heat cycles",
      points: [
        "Lunar satellite DEMs sample every 5 meters while global Earth DEMs sample every 30 meters, with backup DEMs needed on high peaks like Mount Ararat.",
        "A lunar day lasts nearly one Earth month vs 24 hours on Earth, so forcing a direct temperature score would mislead engineers.",
        "Water or desert vegetation can mix into coarse satellite pixels, requiring clean separation of bare terrain.",
      ],
    },
    {
      tag: "03 · Our Solution",
      title: "Score mobility and surface separately with live mission weights",
      points: [
        "All 5 lunar craters and 40 Earth sites are measured over identical 1 km radius circular windows.",
        "Terrain driveability (Mobility) and brightness (Surface) receive separate scores and clear uncertainty ranges.",
        "Engineers shift mission weights live to see which global or Turkish test sites fit their exact hardware test.",
      ],
    },
  ],
};

export type ExampleJumpKey =
  | "rover_hasandagi"
  | "faustini_haughton"
  | "radar_meke"
  | "terrain_slope";

export const SOLUTION_EXAMPLES: Record<
  Lang,
  {
    action: ExampleJumpKey;
    tag: string;
    title: string;
    example: string;
    linkLabel: string;
  }[]
> = {
  tr: [
    {
      action: "rover_hasandagi",
      tag: "Çözüm 01 · Görev Ağırlığı",
      title: "Hasandağı Gezgin Testi'nde nasıl 1. sıraya çıkar?",
      example:
        "Dengeli modda düz sahalar yüzünden geri kalan dik volkanik yamaçlar, 'Gezgin araç testi' seçilince eğim ağırlığı iki katına çıkar ve Türkiye'den Hasandağı Keçikaleçik 40 saha arasından #1 sıraya yükselir.",
      linkLabel: "bkz. Hasandağı #1 sıralamasını canlı gör",
    },
    {
      action: "faustini_haughton",
      tag: "Çözüm 02 · Krater Seçimi",
      title: "Atacama ve Haughton neden krater değiştirince yükselir?",
      example:
        "Shackleton krateri çok diktir (18.5°), bu yüzden düz çöl/buz sahaları alt sırada kalır. Daha yatık Faustini Kenarı (5.2°) seçildiğinde ikisi de gezgin aracı mobilitesi sıralamasında ilk 10'a döner: Haughton #6, Atacama #8.",
      linkLabel: "bkz. Faustini & Haughton uyumuna git",
    },
    {
      action: "radar_meke",
      tag: "Çözüm 03 · Eksen Ayrıştırma",
      title: "Karapınar Meke ve Etna farkını nasıl gizlemedik?",
      example:
        "Etna eğimde Shackleton'a çok yakındır ama koyu siyah taşı Ay toprağından farklıdır. Mobilite ve Yüzey skorlarını ayırdığımız için Meke Yüzey'de #1 öne çıkarken her fark net görünür.",
      linkLabel: "bkz. Meke radar ve fiziksel farklar tablosunu aç",
    },
    {
      action: "terrain_slope",
      tag: "Çözüm 04 · 3B Arazi & Uydu",
      title: "Sayılar tek başına yetmediğinde arazi şeklini nasıl gösterdik?",
      example:
        "Mühendis sahaya gitmeden krater eğim tehlikesini (<10°, 10–20°, >20°) 3 boyutlu kabartmada döndürerek görebilir ve gerçek uydu görüntüsünü yan yana inceleyebilir.",
      linkLabel: "bkz. 3B eğim tehlikesi ve uydu görünümünü aç",
    },
  ],
  en: [
    {
      action: "rover_hasandagi",
      tag: "Solved 01 · Mission Shift",
      title: "How Hasandağı climbs to #1 for rover tests",
      example:
        "Selecting Rover Mobility doubles terrain steepness weight, immediately elevating Turkey's steep Hasandağı Keçikaleçik volcanic apron to #1 out of 40 sites.",
      linkLabel: "See Hasandağı at #1 live",
    },
    {
      action: "faustini_haughton",
      tag: "Solved 02 · Crater Fit",
      title: "Why Haughton & Atacama rise on Faustini",
      example:
        "Flat Mars analogues trail on steep Shackleton (18.5°), yet recover cleanly into the Mobility top 10 when gentler Faustini Rim (5.2°) is chosen.",
      linkLabel: "Jump to Faustini & Haughton view",
    },
    {
      action: "radar_meke",
      tag: "Solved 03 · Split Transparency",
      title: "Showing why Meke Crater leads Surface while Etna differs",
      example:
        "Keeping Mobility and Surface separate prevents Etna's dark mare basalt from hiding behind its slope match, while spotlighting Karapınar Meke's #1 reflectance fit.",
      linkLabel: "Open Meke radar & physical gap breakdown",
    },
    {
      action: "terrain_slope",
      tag: "Solved 04 · 3D Slope Hazard",
      title: "Inspecting real 3D relief & orbital imagery side by side",
      example:
        "Interactive 3D DEM meshes highlight safe (<10°) vs steep (>20°) rover slopes next to real cloudless Sentinel-2 satellite views.",
      linkLabel: "Open 3D slope hazard inspector",
    },
  ],
};

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
      "Hiçbir Dünya sahası Ay koşullarını tek başına karşılayamaz. Bu platform beş Artemis III aday Ay bölgesini kırk Dünya sahasıyla arazi mobilitesi ve yüzey parlaklığı eksenlerinde ayrı ayrı puanlar, her sonuca hata payı ve fiziksel bağlam ekler.",
    heroPrimaryCta: "Gözlemevini aç",
    moonRegionLabel: "Ay referans krateri",
    missionLabel: "Görev profili ve özel ağırlık",
    earthPickerLabel: "Saha seçici",
    searchPlaceholder: "Saha, ID veya litoloji ara",
    selectedEarthLabel: "Seçili Dünya sahası",
    mapZoomGlobal: "Küresel görünüm",
    mapZoomTurkey: "Türkiye odağı (14 aday)",
    chartTitle: "Eksen puanları ve belirsizlik aralığı",
    chartNote: "Puanlar 0–1 sıralama indeksidir, olasılık değildir",
    modeOverall: "Genel",
    modeMobility: "Mobilite",
    modeSurface: "Yüzey",
    gapsTitle: "Özellik bazlı fiziksel farklar (Ay vs Dünya)",
    gapsShareCol: "Mesafe payı",
    gapsShareHint: "Skoru aşağı çeken ölçüt en uzun çubuk. Pay, ölçütün kendi eksenindeki uzaklığa katkısıdır (z² payı); eksenler genel puana görev ağırlığıyla girer. Yüzey ekseni tek ölçütlüdür (albedo), bu yüzden payı %100 görünür.",
    guideTitle: "Bilgi:",
    guideStep1: "Bir Ay hedef bölgesi seçin (sol menü) — Artemis III aday bölgelerinden biri skorumuzun referansı olur.",
    guideStep2: "Dünya sahaları benzerlik indeksiyle sıralanır: 1'e yakın = Ay bölgesine daha çok benziyor. Köşeli parantezdeki aralık ölçüm hatasından gelen belirsizliktir.",
    guideStep3: "Görev profili değiştirerek (tırmanma testi, optik kamera testi) aynı verinin farklı ağırlıkla nasıl yeniden sıralandığını görün — puanlar 0–1 indekstir, olasılık değildir.",
    demTitleMoon: "Ay 3B arazi (5 m/px LRO LOLA)",
    demTitleEarth: "Dünya 3B arazi (30 m/px uydu DEM)",
    exaggeration: "Dikey abartı",
    azimuth: "Yön açısı",
    pitch: "Bakış eğimi",
    zoom: "Yakınlaştırma",
    orbitalMoonTitle: "NASA LRO LOLA 5 m kabartma ve eğim sınıfları",
    orbitalEarthTitle: "ESA Sentinel-2 L2A 10 m gerçek uydu görüntüsü",
    validationIntro:
      "Bu bölümde projede çözdüğümüz temel sorunu, veri toplarken yaşadığımız zorlukları ve daha önce uzay çalışmalarında kullanılmış 10 ünlü test sahasının toprak türü ve koordinatlarıyla sıralamamızdaki yerini görebilirsiniz.",
    whySplitTitle: "Sorun, zorluklar ve geliştirdiğimiz çözüm",
    limitsTitle: "Somut örneklerle neyi nasıl çözdük?",
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
      "No single terrestrial site reproduces lunar conditions on every axis. This workbench scores five Artemis III candidate Moon sites against forty Earth field sites across terrain mobility and surface albedo with clear uncertainty ranges.",
    heroPrimaryCta: "Open observatory",
    moonRegionLabel: "Lunar reference crater",
    missionLabel: "Mission profile & custom weights",
    earthPickerLabel: "Site picker",
    searchPlaceholder: "Search site, ID or lithology",
    selectedEarthLabel: "Selected Earth site",
    mapZoomGlobal: "Global view",
    mapZoomTurkey: "Turkey focus (14 candidates)",
    chartTitle: "Axis scores and uncertainty intervals",
    chartNote: "Scores are 0–1 ranking indices, not probabilities",
    modeOverall: "Overall",
    modeMobility: "Mobility",
    modeSurface: "Surface",
    gapsTitle: "Feature-level physical gaps (Moon vs Earth)",
    gapsShareCol: "Distance share",
    gapsShareHint: "Longest bar = the criterion pulling the score down most. The share is the feature's contribution within its own axis (z² share); axes enter the overall score through mission weights. The surface axis has a single criterion (albedo), hence its 100% share.",
    guideTitle: "Info:",
    guideStep1: "Pick a Moon target region (left panel) — one of the Artemis III candidate regions becomes the reference of the ranking.",
    guideStep2: "Earth sites are ranked by a similarity index: closer to 1 = more Moon-like. The bracketed range is the uncertainty from measurement error.",
    guideStep3: "Switch the mission profile (climb & wheel test, optical camera test) to see the same data re-ranked with different weights — scores are a 0–1 index, not a probability.",
    demTitleMoon: "Lunar 3D terrain (5 m/px LRO LOLA)",
    demTitleEarth: "Earth 3D terrain (30 m/px satellite DEM)",
    exaggeration: "Vertical exaggeration",
    azimuth: "Azimuth",
    pitch: "Tilt pitch",
    zoom: "Zoom",
    orbitalMoonTitle: "NASA LRO LOLA 5 m relief and slope hazard",
    orbitalEarthTitle: "ESA Sentinel-2 L2A 10 m orbital view",
    validationIntro:
      "Read a plain overview of the core challenge, our data hurdles, and where 10 classic space analogue sites rank alongside their soil/rock type and coordinates.",
    whySplitTitle: "Problem, hurdles and our solution",
    limitsTitle: "How we solved it: concrete live examples",
    bibMoonTitle: "Lunar South Pole orbital datasets and literature",
    bibEarthTitle: "Earth satellite products, calibration & validation sources",
    bibTableTitle: "40-site coordinate, DEM and academic citation ledger",
    bibSearchPlaceholder: "Search author, DOI, site or sensor",
  },
};
