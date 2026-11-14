import { useEffect, useMemo, useState } from "react";
import {
  ArrowDownUp,
  BookOpen,
  ChevronLeft,
  ChevronRight,
  Compass,
  ExternalLink,
  Layers,
  MapPin,
  Mountain,
  Play,
  Search,
  ShieldAlert,
  SlidersHorizontal,
  X,
} from "lucide-react";
import { AlbedoSensitivitySvg } from "./components/AlbedoSensitivitySvg";
import { ElevationProfileSvg } from "./components/ElevationProfileSvg";
import { LunarGlyphCanvas } from "./components/LunarGlyphCanvas";
import { PortfolioOptimizerCard } from "./components/PortfolioOptimizerCard";
import { RadarCompareSvg } from "./components/RadarCompareSvg";
import { ScoreBarsChart, type ChartAxisMode } from "./components/ScoreBarsChart";
import { Terrain3DCanvas } from "./components/Terrain3DCanvas";
import { WorldMapSvg } from "./components/WorldMapSvg";
import {
  ANALYSIS_FIGURES,
  FEATURE_NAMES,
  FILTERS,
  JURY_DEMO_TOUR,
  JURY_STORY_STEPS,
  LITHOLOGY_NAMES,
  MISSIONS,
  UI_COPY,
  WORKBENCH_TABS,
} from "./i18n";
import type {
  AppDataPayload,
  DemArchive,
  EarthSite,
  FilterKey,
  Lang,
  MissionKey,
  SiteScoreRow,
  WorkbenchTab,
} from "./types";

type TableSortKey = "rank" | "mob_rank" | "surf_rank";
type MoonAtlasMode = "hillshade" | "hazard" | "plate";

export default function App() {
  const [data, setData] = useState<AppDataPayload | null>(null);
  const [dem, setDem] = useState<DemArchive | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [lang, setLang] = useState<Lang>("tr");
  const [moonId, setMoonId] = useState<string>("moon_shackleton_rim");
  const [mission, setMission] = useState<MissionKey>("default");
  const [filter, setFilter] = useState<FilterKey>("all");
  const [search, setSearch] = useState<string>("");
  const [selectedEarthId, setSelectedEarthId] = useState<string>("earth_karapinar_meke");
  const [workbenchTab, setWorkbenchTab] = useState<WorkbenchTab>("overview");
  const [chartMode, setChartMode] = useState<ChartAxisMode>("overall");
  const [sortKey, setSortKey] = useState<TableSortKey>("rank");
  const [portfolioThreshold, setPortfolioThreshold] = useState<number>(0.7);
  const [tourIdx, setTourIdx] = useState<number | null>(null);

  const [azimuthDeg, setAzimuthDeg] = useState<number>(42);
  const [exaggeration, setExaggeration] = useState<number>(2.0);
  const [moonAtlasLayer, setMoonAtlasLayer] = useState<MoonAtlasMode>("hillshade");
  const [bibSearch, setBibSearch] = useState<string>("");
  const [lightbox, setLightbox] = useState<{ src: string; title: string } | null>(null);

  useEffect(() => {
    Promise.all([
      fetch("/data/app_data.json").then((r) => {
        if (!r.ok) throw new Error(`app_data HTTP ${r.status}`);
        return r.json() as Promise<AppDataPayload>;
      }),
      fetch("/data/dem_3d.json").then((r) => {
        if (!r.ok) throw new Error(`dem_3d HTTP ${r.status}`);
        return r.json() as Promise<DemArchive>;
      }),
    ])
      .then(([appJson, demJson]) => {
        setData(appJson);
        setDem(demJson);
      })
      .catch((err: unknown) => {
        setLoadError(err instanceof Error ? err.message : String(err));
      });
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setLightbox(null);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const copy = UI_COPY[lang];

  const sitesById = useMemo(() => {
    const map: Record<string, EarthSite> = {};
    if (!data) return map;
    for (const s of data.earth_sites) map[s.site_id] = s;
    return map;
  }, [data]);

  const activeMoon = useMemo(() => {
    if (!data) return null;
    return data.moon_refs.find((m) => m.site_id === moonId) ?? data.moon_refs[0];
  }, [data, moonId]);

  const activeScores = useMemo(() => {
    if (!data) return [];
    return data.comparisons[moonId]?.[mission] ?? [];
  }, [data, moonId, mission]);

  const scoresById = useMemo(() => {
    const map: Record<string, SiteScoreRow> = {};
    for (const r of activeScores) map[r.site_id] = r;
    return map;
  }, [activeScores]);

  const filteredRows = useMemo(() => {
    const q = search.trim().toLowerCase();
    const list = activeScores.filter((r) => {
      const s = sitesById[r.site_id];
      if (!s) return false;
      if (filter === "tr" && !s.is_tr) return false;
      if (filter === "validation" && s.role !== "validation") return false;
      if (filter === "global" && (s.role === "validation" || s.is_tr)) return false;
      if (!q) return true;
      return `${s.site_id} ${s.name} ${s.short} ${s.lithology}`.toLowerCase().includes(q);
    });
    return [...list].sort((a, b) => a[sortKey] - b[sortKey]);
  }, [activeScores, sitesById, filter, search, sortKey]);

  const filteredSitesForMap = useMemo(() => {
    if (!data) return [];
    const allowed = new Set(filteredRows.map((r) => r.site_id));
    return data.earth_sites.filter((s) => allowed.has(s.site_id));
  }, [data, filteredRows]);

  const selectedEarth = sitesById[selectedEarthId] ?? data?.earth_sites[0] ?? null;
  const selectedScore = selectedEarth ? scoresById[selectedEarth.site_id] : undefined;
  const selectedGaps =
    data && selectedEarth ? data.gaps[moonId]?.[selectedEarth.site_id] ?? [] : [];

  const validationRows = useMemo(() => {
    if (!data) return [];
    return activeScores
      .filter((r) => sitesById[r.site_id]?.role === "validation")
      .sort((a, b) => a.mob_rank - b.mob_rank);
  }, [activeScores, sitesById]);

  const craterSensitivity = useMemo(() => {
    if (!data) return [];
    return data.albedo_sensitivity.filter((r) => r.ref_site_id === moonId);
  }, [data, moonId]);

  const filteredBibSites = useMemo(() => {
    if (!data) return [];
    const q = bibSearch.trim().toLowerCase();
    return data.earth_sites.filter((s) => {
      if (!q) return true;
      return `${s.site_id} ${s.name} ${s.citation} ${s.dem_src}`.toLowerCase().includes(q);
    });
  }, [data, bibSearch]);

  const applyTourStep = (index: number) => {
    const safe = ((index % JURY_DEMO_TOUR.length) + JURY_DEMO_TOUR.length) % JURY_DEMO_TOUR.length;
    const step = JURY_DEMO_TOUR[safe];
    setTourIdx(safe);
    setMoonId(step.moonId);
    setMission(step.mission);
    setFilter("all");
    setSelectedEarthId(step.earthId);
    setWorkbenchTab(step.tab);
  };

  if (loadError) {
    return (
      <div className="min-h-screen flex items-center justify-center p-8 text-[#eef0f5] bg-[#0b0d14]">
        <div className="max-w-md rounded-xl border hairline bg-[#11141c] p-6">
          <h1 className="text-[18px] font-medium">Veri yüklenemedi</h1>
          <p className="text-[14px] text-[#a3a9b8] mt-2 font-mono">{loadError}</p>
        </div>
      </div>
    );
  }

  if (!data || !activeMoon || !selectedEarth) {
    return (
      <div className="min-h-screen flex items-center justify-center p-8 bg-[#0b0d14]">
        <div className="text-[14px] font-mono text-[#7a8296]">
          NASA LRO LOLA / Copernicus DEM telemetry loading
        </div>
      </div>
    );
  }

  const stories = JURY_STORY_STEPS[lang];
  const moonName = lang === "tr" ? activeMoon.name_tr : activeMoon.name_en;
  const activeTour = tourIdx !== null ? JURY_DEMO_TOUR[tourIdx] : null;

  return (
    <div className="min-h-screen flex flex-col bg-[#0b0d14] text-[#eef0f5]">
      {/* Top instrument navigation bar */}
      <header className="sticky top-0 z-40 h-14 bg-[#07080d]/95 border-b hairline backdrop-blur-sm">
        <div className="max-w-[1400px] mx-auto h-full px-5 sm:px-6 flex items-center justify-between gap-4">
          <div className="flex items-center gap-6 min-w-0">
            <a href="#" className="flex items-center gap-2.5 text-[#eef0f5] font-medium text-[15px] shrink-0">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                <circle cx="10" cy="10" r="8" stroke="#eef0f5" strokeWidth="1.4" />
                <path d="M12.6 4.6a5.6 5.6 0 1 0 0 10.8 4.4 4.4 0 1 1 0-10.8Z" fill="#4c8bf5" />
                <line x1="2" y1="10" x2="5" y2="10" stroke="#7a8296" strokeWidth="1.2" />
                <line x1="15" y1="10" x2="18" y2="10" stroke="#7a8296" strokeWidth="1.2" />
              </svg>
              <span>{copy.brand}</span>
              <span className="hidden sm:inline text-[12px] font-mono text-[#7a8296] pl-2 border-l hairline">
                {copy.subtitleTag}
              </span>
            </a>

            <nav className="hidden md:flex items-center gap-1 text-[13.5px]">
              <a
                href="#story"
                className="px-3 py-1.5 rounded-lg text-[#a3a9b8] hover:text-[#eef0f5] hover:bg-[#1a1e28]/60 transition-colors duration-150"
              >
                {copy.navStory}
              </a>
              <a
                href="#observatory"
                onClick={() => setWorkbenchTab("overview")}
                className="px-3 py-1.5 rounded-lg text-[#a3a9b8] hover:text-[#eef0f5] hover:bg-[#1a1e28]/60 transition-colors duration-150"
              >
                {copy.navWorkbench}
              </a>
              <a
                href="#observatory"
                onClick={() => setWorkbenchTab("validation")}
                className="px-3 py-1.5 rounded-lg text-[#a3a9b8] hover:text-[#eef0f5] hover:bg-[#1a1e28]/60 transition-colors duration-150"
              >
                {copy.navValidation}
              </a>
              <a
                href="#observatory"
                onClick={() => setWorkbenchTab("figures")}
                className="px-3 py-1.5 rounded-lg text-[#a3a9b8] hover:text-[#eef0f5] hover:bg-[#1a1e28]/60 transition-colors duration-150"
              >
                {copy.navFigures}
              </a>
            </nav>
          </div>

          <div className="flex items-center gap-2.5 shrink-0">
            <button
              type="button"
              onClick={() => {
                applyTourStep(0);
                document.getElementById("observatory")?.scrollIntoView({ behavior: "smooth" });
              }}
              className="hidden sm:inline-flex items-center gap-1.5 h-8 px-3 rounded-lg bg-[#11141c] border hairline text-[12px] font-medium text-[#eef0f5] hover:border-[#4c8bf5]/60 transition-colors duration-150"
            >
              <Play className="w-3.5 h-3.5 text-[#4c8bf5]" strokeWidth={1.6} />
              <span>{copy.tourBadge}</span>
            </button>

            <div className="inline-flex rounded-lg p-0.5 bg-[#11141c] border hairline text-[12px]">
              {(["tr", "en"] as Lang[]).map((code) => (
                <button
                  key={code}
                  type="button"
                  onClick={() => setLang(code)}
                  className={`px-2.5 py-1 rounded-md font-medium transition-colors duration-150 ${
                    lang === code ? "active-highlight text-[#eef0f5]" : "text-[#7a8296] hover:text-[#eef0f5]"
                  }`}
                >
                  {code === "tr" ? "Türkçe" : "English"}
                </button>
              ))}
            </div>
          </div>
        </div>
      </header>

      {/* Hero split: left calm problem + telemetry controls, right pure borderless LOLA contour canvas */}
      <section className="max-w-[1400px] mx-auto w-full px-5 sm:px-6 pt-8 pb-8 lg:pt-10 lg:pb-10 border-b hairline">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10 items-center">
          <div className="lg:col-span-7 flex flex-col items-start">
            <div className="enter-rise enter-delay-1 inline-flex items-center gap-2.5 text-[12px] font-mono tabular text-[#7a8296] mb-4">
              <span>{data.meta.moon_count} {lang === "tr" ? "Ay bölgesi" : "Moon sites"}</span>
              <span className="text-[#2b3245]">/</span>
              <span>{data.meta.earth_count} {lang === "tr" ? "Dünya sahası" : "Earth sites"}</span>
              <span className="text-[#2b3245]">/</span>
              <span className="text-[#4cc38a]">{data.meta.tests_passed} {lang === "tr" ? "test · 0 yapay veri" : "tests · 0 mock"}</span>
            </div>

            <h1 className="enter-rise enter-delay-2 text-[34px] sm:text-[42px] font-medium leading-[1.09] tracking-[-0.025em] text-[#eef0f5] max-w-[19ch]">
              {copy.heroTitle}
            </h1>

            <p className="enter-rise enter-delay-3 mt-4 text-[15px] sm:text-[16.5px] leading-[1.6] text-[#a3a9b8] max-w-[38rem]">
              {copy.heroBody}
            </p>

            <div className="enter-rise enter-delay-4 mt-6 flex flex-wrap items-center gap-3">
              <a
                href="#observatory"
                className="h-10 px-5 rounded-lg bg-[#eef0f5] text-[#07080d] text-[13.5px] font-medium inline-flex items-center gap-2 hover:bg-white transition-colors duration-150"
              >
                <Compass className="w-4 h-4 text-[#07080d]" strokeWidth={1.5} />
                <span>{copy.heroPrimaryCta}</span>
              </a>
              <button
                type="button"
                onClick={() => {
                  applyTourStep(0);
                  document.getElementById("observatory")?.scrollIntoView({ behavior: "smooth" });
                }}
                className="h-10 px-5 rounded-lg bg-[#1a1e28] border hairline-strong text-[#eef0f5] text-[13.5px] font-medium inline-flex items-center gap-2 hover:bg-[#232836] transition-colors duration-150"
              >
                <Play className="w-3.5 h-3.5 text-[#4c8bf5]" strokeWidth={1.6} />
                <span>{lang === "tr" ? "Jüri sunum turunu başlat" : "Start guided jury tour"}</span>
              </button>
              <a
                href="#story"
                className="h-10 px-4 rounded-lg border hairline text-[#a3a9b8] hover:text-[#eef0f5] text-[13.5px] font-medium inline-flex items-center transition-colors duration-150"
              >
                {copy.heroSecondaryCta}
              </a>
            </div>

            {/* Clean uniform 5-crater selector strip + telemetry */}
            <div className="mt-7 pt-5 border-t hairline w-full">
              <div className="flex flex-wrap gap-1.5 mb-4">
                {data.moon_refs.map((m) => {
                  const fullLabel = lang === "tr" ? m.name_tr : m.name_en;
                  const shortPill = fullLabel
                    .replace(" (Shackleton–de Gerlache)", "")
                    .replace(" Krateri Kenarı", " Kenarı")
                    .replace(" Crater Rim A", " Rim A")
                    .replace(" Crater Rim", " Rim");
                  return (
                    <button
                      key={m.site_id}
                      type="button"
                      onClick={() => setMoonId(m.site_id)}
                      className={`px-2.5 py-1.5 rounded-lg text-[11.5px] font-medium border transition-colors duration-150 ${
                        m.site_id === moonId
                          ? "active-highlight border-[#4c8bf5]/55 text-[#eef0f5]"
                          : "hairline text-[#7a8296] hover:text-[#eef0f5] hover:bg-[#11141c]"
                      }`}
                    >
                      {shortPill}
                    </button>
                  );
                })}
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-[13px] font-mono tabular">
                <div className="px-3 py-2 rounded-lg bg-[#11141c] border hairline">
                  <div className="text-[#7a8296] text-[11px] font-sans">{FEATURE_NAMES.slope_mean[lang]}</div>
                  <div className="text-[#eef0f5] mt-0.5 font-medium">{activeMoon.slope_mean.toFixed(2)}°</div>
                </div>
                <div className="px-3 py-2 rounded-lg bg-[#11141c] border hairline">
                  <div className="text-[#7a8296] text-[11px] font-sans">{FEATURE_NAMES.relief[lang]}</div>
                  <div className="text-[#eef0f5] mt-0.5 font-medium">{activeMoon.relief.toFixed(1)} m</div>
                </div>
                <div className="px-3 py-2 rounded-lg bg-[#11141c] border hairline">
                  <div className="text-[#7a8296] text-[11px] font-sans">{FEATURE_NAMES.roughness[lang]}</div>
                  <div className="text-[#eef0f5] mt-0.5 font-medium">{activeMoon.roughness.toFixed(1)} m</div>
                </div>
                <div className="px-3 py-2 rounded-lg bg-[#11141c] border hairline">
                  <div className="text-[#7a8296] text-[11px] font-sans">{FEATURE_NAMES.albedo[lang]}</div>
                  <div className="text-[#eef0f5] mt-0.5 font-medium">{activeMoon.albedo.toFixed(3)}</div>
                </div>
              </div>
            </div>
          </div>

          <div className="lg:col-span-5 flex flex-col items-center lg:items-end">
            <LunarGlyphCanvas imageSrc={activeMoon.thumb_img} alt={moonName} />
            <div className="mt-2 flex items-center justify-between flex-wrap gap-x-4 gap-y-1 w-full max-w-[460px] text-[11.5px] font-mono tabular text-[#7a8296]">
              <span>
                {moonName} · {activeMoon.lat.toFixed(2)}°, {activeMoon.lon.toFixed(2)}°
              </span>
              <span>{activeMoon.dem_src}</span>
            </div>
          </div>
        </div>
      </section>

      {/* Jury Story Strip — 4 clear pillars */}
      <section id="story" className="max-w-[1400px] mx-auto w-full px-5 sm:px-6 py-8 border-b hairline">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3 mb-5">
          <div>
            <h2 className="text-[20px] font-medium text-[#eef0f5]">{copy.storySectionTitle}</h2>
            <p className="text-[13.5px] text-[#7a8296] mt-0.5">{copy.storySectionSub}</p>
          </div>
          <span className="text-[12px] font-mono tabular text-[#7a8296]">
            v1 · {data.meta.moon_count}×{data.meta.earth_count}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {stories.map((st) => (
            <article
              key={st.step}
              className="rounded-xl border hairline bg-[#11141c] p-4 flex flex-col justify-between gap-3"
            >
              <div>
                <div className="flex items-center justify-between text-[11.5px] font-mono tabular text-[#7a8296] mb-2.5">
                  <span>{st.step}</span>
                  <span className="text-[#4c8bf5]">{st.metric}</span>
                </div>
                <h3 className="text-[14.5px] font-medium text-[#eef0f5] mb-1.5">{st.title}</h3>
                <p className="text-[12.5px] leading-[1.55] text-[#a3a9b8]">{st.body}</p>
              </div>
            </article>
          ))}
        </div>
      </section>

      {/* Main Interactive Observatory Workbench */}
      <section id="observatory" className="max-w-[1400px] mx-auto w-full px-5 sm:px-6 py-8 flex-1">
        {/* Interactive Jury Guided Tour Strip */}
        <div className="rounded-xl border hairline bg-[#11141c] p-4 mb-6">
          <div className="flex items-center justify-between gap-3 flex-wrap">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[12px] font-mono text-[#4c8bf5] px-2 py-0.5 rounded bg-[#4c8bf5]/12 border border-[#4c8bf5]/30">
                {copy.tourBadge}
              </span>
              {JURY_DEMO_TOUR.map((step, i) => (
                <button
                  key={step.id}
                  type="button"
                  onClick={() => applyTourStep(i)}
                  className={`px-2.5 py-1 rounded-lg text-[12px] font-medium border transition-colors duration-150 ${
                    tourIdx === i
                      ? "active-highlight border-[#4c8bf5]/55 text-[#eef0f5]"
                      : "border-transparent text-[#7a8296] hover:text-[#eef0f5] hover:bg-[#1a1e28]/60"
                  }`}
                >
                  {lang === "tr" ? step.trTitle : step.enTitle}
                </button>
              ))}
            </div>

            {activeTour && (
              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  onClick={() => applyTourStep((tourIdx ?? 0) - 1)}
                  className="p-1.5 rounded-lg bg-[#07080d] border hairline text-[#a3a9b8] hover:text-[#eef0f5]"
                  aria-label="Previous step"
                >
                  <ChevronLeft className="w-4 h-4" strokeWidth={1.5} />
                </button>
                <span className="text-[12px] font-mono tabular text-[#7a8296] px-1">
                  {(tourIdx ?? 0) + 1}/{JURY_DEMO_TOUR.length}
                </span>
                <button
                  type="button"
                  onClick={() => applyTourStep((tourIdx ?? 0) + 1)}
                  className="p-1.5 rounded-lg bg-[#07080d] border hairline text-[#a3a9b8] hover:text-[#eef0f5]"
                  aria-label="Next step"
                >
                  <ChevronRight className="w-4 h-4" strokeWidth={1.5} />
                </button>
                <button
                  type="button"
                  onClick={() => setTourIdx(null)}
                  className="p-1.5 rounded-lg bg-[#07080d] border hairline text-[#7a8296] hover:text-[#eef0f5]"
                  aria-label="Close tour"
                >
                  <X className="w-4 h-4" strokeWidth={1.5} />
                </button>
              </div>
            )}
          </div>

          {activeTour && (
            <p className="mt-3 pt-3 border-t hairline text-[13px] leading-relaxed text-[#c7cddb]">
              {lang === "tr" ? activeTour.trSpeech : activeTour.enSpeech}
            </p>
          )}
        </div>

        <div className="flex flex-col lg:flex-row gap-6 items-start">
          {/* Sticky 272px Observatory Control Rail */}
          <aside className="w-full lg:w-[272px] shrink-0 lg:sticky lg:top-[72px] rounded-xl border hairline bg-[#07080d] p-4 flex flex-col gap-5">
            {/* Search */}
            <div className="relative">
              <Search
                className="w-4 h-4 text-[#7a8296] absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none"
                strokeWidth={1.5}
              />
              <input
                id="site-search"
                name="siteSearch"
                type="search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={copy.searchPlaceholder}
                className="w-full h-9 pl-9 pr-3 rounded-lg bg-[#11141c] border hairline text-[13px] text-[#eef0f5] placeholder:text-[#7a8296] focus:outline-none focus:border-[#4c8bf5]"
              />
            </div>

            {/* Lunar Crater Group */}
            <div>
              <div className="text-[12px] text-[#7a8296] px-2 mb-1.5 flex items-center gap-2">
                <Compass className="w-4 h-4 text-[#7a8296]" strokeWidth={1.5} />
                <span>{copy.moonRegionLabel}</span>
              </div>
              <div className="flex flex-col gap-1">
                {data.moon_refs.map((m) => (
                  <button
                    key={m.site_id}
                    type="button"
                    onClick={() => setMoonId(m.site_id)}
                    className={`h-8 px-3 rounded-lg text-left text-[12.5px] transition-colors duration-150 truncate ${
                      m.site_id === moonId
                        ? "active-highlight text-[#eef0f5] font-medium"
                        : "text-[#a3a9b8] hover:text-[#eef0f5] hover:bg-[#11141c]"
                    }`}
                  >
                    {lang === "tr" ? m.name_tr : m.name_en}
                  </button>
                ))}
              </div>
            </div>

            {/* Mission Profile Group */}
            <div>
              <div className="text-[12px] text-[#7a8296] px-2 mb-1.5 flex items-center gap-2">
                <SlidersHorizontal className="w-4 h-4 text-[#7a8296]" strokeWidth={1.5} />
                <span>{copy.missionLabel}</span>
              </div>
              <div className="flex flex-col gap-1">
                {(Object.keys(MISSIONS) as MissionKey[]).map((mk) => (
                  <button
                    key={mk}
                    type="button"
                    onClick={() => setMission(mk)}
                    className={`h-8 px-3 rounded-lg text-left text-[12.5px] transition-colors duration-150 truncate ${
                      mk === mission
                        ? "active-highlight text-[#eef0f5] font-medium"
                        : "text-[#a3a9b8] hover:text-[#eef0f5] hover:bg-[#11141c]"
                    }`}
                  >
                    {MISSIONS[mk][lang]}
                  </button>
                ))}
              </div>
              <p className="text-[11.5px] text-[#7a8296] px-2 mt-1.5 leading-snug">
                {lang === "tr" ? MISSIONS[mission].note_tr : MISSIONS[mission].note_en}
              </p>
            </div>

            {/* Site Filter Group */}
            <div>
              <div className="text-[12px] text-[#7a8296] px-2 mb-1.5 flex items-center gap-2">
                <MapPin className="w-4 h-4 text-[#7a8296]" strokeWidth={1.5} />
                <span>{copy.filterLabel}</span>
              </div>
              <div className="flex flex-col gap-1">
                {(Object.keys(FILTERS) as FilterKey[]).map((fk) => (
                  <button
                    key={fk}
                    type="button"
                    onClick={() => setFilter(fk)}
                    className={`h-8 px-3 rounded-lg text-left text-[12.5px] transition-colors duration-150 ${
                      fk === filter
                        ? "active-highlight text-[#eef0f5] font-medium"
                        : "text-[#a3a9b8] hover:text-[#eef0f5] hover:bg-[#11141c]"
                    }`}
                  >
                    {FILTERS[fk][lang]}
                  </button>
                ))}
              </div>
            </div>

            {/* Selected Earth Site Inspector Card */}
            <div className="rounded-lg border hairline bg-[#11141c] p-3 text-[12px] flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className="text-[#7a8296]">{copy.selectedEarthLabel}</span>
                <span
                  className={`text-[10.5px] font-mono px-1.5 py-0.5 rounded ${
                    selectedEarth.role === "validation"
                      ? "bg-[#4c8bf5]/15 text-[#4c8bf5]"
                      : "bg-[#4cc38a]/15 text-[#4cc38a]"
                  }`}
                >
                  {selectedEarth.role === "validation"
                    ? lang === "tr"
                      ? "Doğrulama"
                      : "Validation"
                    : lang === "tr"
                      ? "Aday"
                      : "Candidate"}
                </span>
              </div>
              <div className="text-[13.5px] font-medium text-[#eef0f5] leading-snug">
                {selectedEarth.short}
              </div>
              <div className="font-mono tabular text-[11px] text-[#a3a9b8]">
                {selectedEarth.lat.toFixed(3)}°, {selectedEarth.lon.toFixed(3)}° ·{" "}
                {LITHOLOGY_NAMES[selectedEarth.lithology]?.[lang] ?? selectedEarth.lithology}
              </div>
              {selectedScore && (
                <div className="grid grid-cols-3 gap-2 pt-2 border-t hairline font-mono tabular">
                  <div>
                    <div className="text-[#7a8296] text-[10px]">
                      {lang === "tr" ? "Genel" : "Score"}
                    </div>
                    <div className="text-[#eef0f5]">
                      {selectedScore.score.toFixed(3)}
                    </div>
                  </div>
                  <div>
                    <div className="text-[#7a8296] text-[10px]">
                      {lang === "tr" ? "Mobilite" : "Mob"}
                    </div>
                    <div className="text-[#eef0f5]">#{selectedScore.mob_rank}</div>
                  </div>
                  <div>
                    <div className="text-[#7a8296] text-[10px]">
                      {lang === "tr" ? "Yüzey" : "Surf"}
                    </div>
                    <div className="text-[#eef0f5]">#{selectedScore.surf_rank}</div>
                  </div>
                </div>
              )}
              <div className="pt-2 border-t hairline text-[11px] font-mono text-[#7a8296] truncate">
                {selectedEarth.dem_src} · {selectedEarth.albedo_src}
              </div>
            </div>
          </aside>

          {/* Main Stage */}
          <div className="flex-1 w-full min-w-0 flex flex-col gap-5">
            {/* Workbench View Tabs */}
            <div className="flex items-center justify-between gap-4 flex-wrap pb-3 border-b hairline">
              <div className="inline-flex flex-wrap gap-1 rounded-xl p-1 bg-[#11141c] border hairline">
                {WORKBENCH_TABS.map((tb) => {
                  const Icon =
                    tb.id === "overview"
                      ? Compass
                      : tb.id === "terrain"
                        ? Mountain
                        : tb.id === "validation"
                          ? ShieldAlert
                          : BookOpen;
                  return (
                    <button
                      key={tb.id}
                      type="button"
                      onClick={() => setWorkbenchTab(tb.id)}
                      className={`h-9 px-3.5 rounded-lg text-[13px] font-medium inline-flex items-center gap-2 transition-colors duration-150 ${
                        workbenchTab === tb.id
                          ? "active-highlight text-[#eef0f5]"
                          : "text-[#7a8296] hover:text-[#eef0f5]"
                      }`}
                    >
                      <Icon className="w-4 h-4 shrink-0" strokeWidth={1.5} />
                      <span>{tb[lang]}</span>
                    </button>
                  );
                })}
              </div>

              <div className="text-[12px] font-mono tabular text-[#7a8296]">
                {moonName} · {filteredRows.length} / {data.earth_sites.length}{" "}
                {lang === "tr" ? "saha" : "sites"}
              </div>
            </div>

            {/* VIEW 1: MAP + BARS + RADAR + PORTFOLIO + MULTI-CRATER MATRIX + GAPS + TABLE */}
            {workbenchTab === "overview" && (
              <div className="flex flex-col gap-5">
                <WorldMapSvg
                  sites={filteredSitesForMap}
                  scoresById={scoresById}
                  selectedId={selectedEarth.site_id}
                  onSelect={(sid) => setSelectedEarthId(sid)}
                  lang={lang}
                  zoomTurkeyLabel={copy.mapZoomTurkey}
                  zoomGlobalLabel={copy.mapZoomGlobal}
                />

                <ScoreBarsChart
                  rows={filteredRows}
                  sitesById={sitesById}
                  selectedId={selectedEarth.site_id}
                  onSelect={(sid) => setSelectedEarthId(sid)}
                  mode={chartMode}
                  onModeChange={setChartMode}
                  title={copy.chartTitle}
                  note={copy.chartNote}
                  modeLabels={{
                    overall: copy.modeOverall,
                    mobility: copy.modeMobility,
                    surface: copy.modeSurface,
                  }}
                  lang={lang}
                />

                {/* Paired Radar Comparison & Interactive Portfolio Optimizer */}
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
                  <RadarCompareSvg
                    moon={activeMoon}
                    earth={selectedEarth}
                    allMoon={data.moon_refs}
                    allEarth={data.earth_sites}
                    scoreRow={selectedScore}
                    lang={lang}
                  />

                  <PortfolioOptimizerCard
                    rows={activeScores}
                    sitesById={sitesById}
                    moonName={moonName}
                    threshold={portfolioThreshold}
                    onThresholdChange={setPortfolioThreshold}
                    onSelectSite={(sid) => setSelectedEarthId(sid)}
                    lang={lang}
                  />
                </div>

                {/* Cross-Crater Top Winners Matrix */}
                <div className="rounded-xl border hairline bg-[#11141c] p-5">
                  <div className="flex items-center justify-between gap-3 flex-wrap mb-3">
                    <div>
                      <h3 className="text-[15px] font-medium text-[#eef0f5]">
                        {lang === "tr"
                          ? "Beş Artemis III Ay kraterinde ilk 3 eşleşme"
                          : "Top 3 matches across all five Artemis III regions"}
                      </h3>
                      <p className="text-[12px] text-[#7a8296] mt-0.5">
                        {lang === "tr"
                          ? "Hücreye tıklayarak hedef krateri ve Dünya sahasını anında seçin"
                          : "Click any cell to jump directly to that Lunar crater and Earth site"}
                      </p>
                    </div>
                    <span className="text-[11.5px] font-mono text-[#7a8296]">
                      {MISSIONS[mission][lang]}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
                    {data.moon_refs.map((m) => {
                      const top3 = (data.comparisons[m.site_id]?.[mission] ?? []).slice(0, 3);
                      const isCurMoon = m.site_id === moonId;
                      return (
                        <div
                          key={m.site_id}
                          className={`rounded-lg border p-3 flex flex-col gap-2 ${
                            isCurMoon
                              ? "border-[#4c8bf5]/55 bg-[#151a27]"
                              : "hairline bg-[#07080d]"
                          }`}
                        >
                          <button
                            type="button"
                            onClick={() => setMoonId(m.site_id)}
                            className="text-left text-[12px] font-medium text-[#eef0f5] hover:text-[#4c8bf5] truncate"
                          >
                            {lang === "tr" ? m.name_tr : m.name_en}
                          </button>
                          <div className="text-[11px] font-mono tabular text-[#7a8296]">
                            {m.slope_mean.toFixed(1)}° · alb {m.albedo.toFixed(3)}
                          </div>
                          <div className="flex flex-col gap-1 pt-1 border-t hairline">
                            {top3.map((r, idx) => {
                              const es = sitesById[r.site_id];
                              if (!es) return null;
                              return (
                                <button
                                  key={r.site_id}
                                  type="button"
                                  onClick={() => {
                                    setMoonId(m.site_id);
                                    setSelectedEarthId(r.site_id);
                                  }}
                                  className="text-left text-[11.5px] flex items-center justify-between gap-2 py-0.5 text-[#a3a9b8] hover:text-[#eef0f5]"
                                >
                                  <span className="truncate">
                                    {idx + 1}. {es.short}
                                  </span>
                                  <span className="font-mono tabular text-[#eef0f5] shrink-0">
                                    {r.score.toFixed(3)}
                                  </span>
                                </button>
                              );
                            })}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Feature Gaps Panel */}
                <div className="rounded-xl border hairline bg-[#11141c] p-5">
                  <div className="flex items-center justify-between gap-3 flex-wrap mb-3">
                    <h3 className="text-[15px] font-medium text-[#eef0f5]">
                      {copy.gapsTitle}: {moonName} ↔ {selectedEarth.short}
                    </h3>
                    <span className="text-[12px] font-mono text-[#7a8296]">
                      r = 1000 m · {activeMoon.dem_src} vs {selectedEarth.dem_src}
                    </span>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-[13px] border-collapse">
                      <thead>
                        <tr className="border-b hairline text-[#7a8296] text-left">
                          <th className="py-2 pr-4 font-normal">
                            {lang === "tr" ? "Ölçüt" : "Criterion"}
                          </th>
                          <th className="py-2 pr-4 font-normal text-right">
                            {lang === "tr" ? "Ay değeri" : "Lunar value"}
                          </th>
                          <th className="py-2 pr-4 font-normal text-right">
                            {lang === "tr" ? "Dünya değeri" : "Earth value"}
                          </th>
                          <th className="py-2 pr-4 font-normal text-right">
                            {lang === "tr" ? "Fark" : "Difference"}
                          </th>
                          <th className="py-2 font-normal text-right">
                            {lang === "tr" ? "Standart fark (z)" : "Std diff (z)"}
                          </th>
                        </tr>
                      </thead>
                      <tbody className="font-mono tabular">
                        {selectedGaps.map((g) => {
                          const fn = FEATURE_NAMES[g.feature];
                          const absZ = Math.abs(g.z_diff ?? 0);
                          return (
                            <tr key={g.feature} className="border-b hairline last:border-b-0">
                              <td className="py-2.5 pr-4 font-sans text-[#eef0f5]">
                                {fn ? fn[lang] : g.feature}
                                <span className="text-[#7a8296] text-[11px] ml-1.5 font-mono">
                                  ({fn?.unit ?? ""})
                                </span>
                              </td>
                              <td className="py-2.5 pr-4 text-right text-[#a3a9b8]">
                                {g.moon_val !== null ? g.moon_val.toFixed(2) : "NaN"}
                              </td>
                              <td className="py-2.5 pr-4 text-right text-[#a3a9b8]">
                                {g.earth_val !== null ? g.earth_val.toFixed(2) : "NaN"}
                              </td>
                              <td className="py-2.5 pr-4 text-right text-[#eef0f5]">
                                {g.diff !== null ? g.diff.toFixed(2) : "—"}
                              </td>
                              <td
                                className={`py-2.5 text-right ${
                                  absZ < 0.5
                                    ? "text-[#4cc38a]"
                                    : absZ > 1.3
                                      ? "text-[#e5484d]"
                                      : "text-[#a3a9b8]"
                                }`}
                              >
                                {g.z_diff !== null ? g.z_diff.toFixed(2) : "—"}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Full Interactive Table */}
                <div className="rounded-xl border hairline bg-[#11141c] overflow-hidden">
                  <div className="px-5 py-3.5 border-b hairline flex items-center justify-between flex-wrap gap-3">
                    <h3 className="text-[14px] font-medium text-[#eef0f5]">
                      {lang === "tr" ? "Tüm sahalar tablosu" : "All sites score table"}
                    </h3>
                    <div className="flex items-center gap-2 text-[12px]">
                      <ArrowDownUp className="w-3.5 h-3.5 text-[#7a8296]" strokeWidth={1.5} />
                      {(
                        [
                          ["rank", lang === "tr" ? "Genel sıra" : "Overall rank"],
                          ["mob_rank", lang === "tr" ? "Mobilite sıra" : "Mobility rank"],
                          ["surf_rank", lang === "tr" ? "Yüzey sıra" : "Surface rank"],
                        ] as [TableSortKey, string][]
                      ).map(([k, label]) => (
                        <button
                          key={k}
                          type="button"
                          onClick={() => setSortKey(k)}
                          className={`px-2.5 py-1 rounded border transition-colors duration-150 ${
                            sortKey === k
                              ? "active-highlight border-[#4c8bf5]/40 text-[#eef0f5]"
                              : "hairline text-[#7a8296] hover:text-[#eef0f5]"
                          }`}
                        >
                          {label}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className="max-h-[420px] overflow-auto">
                    <table className="w-full text-[13px] border-collapse">
                      <thead className="sticky top-0 bg-[#07080d] z-10">
                        <tr className="border-b hairline text-[#7a8296] text-left">
                          <th className="py-2.5 px-4 font-normal">#</th>
                          <th className="py-2.5 px-4 font-normal">
                            {lang === "tr" ? "Dünya sahası" : "Earth site"}
                          </th>
                          <th className="py-2.5 px-4 font-normal text-right whitespace-nowrap">
                            {lang === "tr" ? "Genel (P5–P95)" : "Score (P5–P95)"}
                          </th>
                          <th className="py-2.5 px-4 font-normal text-right">
                            {lang === "tr" ? "Mobilite" : "Mobility"}
                          </th>
                          <th className="py-2.5 px-4 font-normal text-right">
                            {lang === "tr" ? "Yüzey" : "Surface"}
                          </th>
                          <th className="py-2.5 px-4 font-normal text-right">
                            {lang === "tr" ? "Eğim / Albedo" : "Slope / Albedo"}
                          </th>
                          <th className="py-2.5 px-4 font-normal">
                            {lang === "tr" ? "Litoloji" : "Lithology"}
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredRows.map((r) => {
                          const s = sitesById[r.site_id];
                          if (!s) return null;
                          const isSel = s.site_id === selectedEarth.site_id;
                          return (
                            <tr
                              key={r.site_id}
                              onClick={() => setSelectedEarthId(s.site_id)}
                              className={`border-b hairline cursor-pointer transition-colors duration-150 ${
                                isSel ? "bg-[#4c8bf5]/12" : "hover:bg-[#1a1e28]/60"
                              }`}
                            >
                              <td className="py-2.5 px-4 font-mono tabular text-[#a3a9b8]">
                                #{r.rank}
                              </td>
                              <td className="py-2.5 px-4">
                                <div className="flex items-center gap-2">
                                  <span
                                    className={`w-2 h-2 rounded-full shrink-0 ${
                                      s.role === "validation"
                                        ? "bg-[#4c8bf5]"
                                        : s.is_tr
                                          ? "bg-[#4cc38a]"
                                          : "bg-[#7a8296]"
                                    }`}
                                  />
                                  <span className="text-[#eef0f5]">{s.short}</span>
                                </div>
                              </td>
                              <td className="py-2.5 px-4 text-right font-mono tabular text-[#eef0f5] whitespace-nowrap">
                                {r.score.toFixed(3)}{" "}
                                {r.ci_lo !== null && r.ci_hi !== null && (
                                  <span className="text-[#7a8296]">
                                    [{r.ci_lo.toFixed(2)}–{r.ci_hi.toFixed(2)}
                                    {r.widened ? "*" : ""}]
                                  </span>
                                )}
                              </td>
                              <td className="py-2.5 px-4 text-right font-mono tabular text-[#a3a9b8] whitespace-nowrap">
                                {r.mob.toFixed(3)} (#{r.mob_rank})
                              </td>
                              <td className="py-2.5 px-4 text-right font-mono tabular text-[#a3a9b8] whitespace-nowrap">
                                {r.surf.toFixed(3)} (#{r.surf_rank})
                              </td>
                              <td className="py-2.5 px-4 text-right font-mono tabular text-[#a3a9b8] whitespace-nowrap">
                                {s.slope_mean.toFixed(1)}° / {s.albedo.toFixed(3)}
                              </td>
                              <td className="py-2.5 px-4 text-[#7a8296]">
                                {LITHOLOGY_NAMES[s.lithology]?.[lang] ?? s.lithology}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* VIEW 2: 3D DEM + W-E / S-N PROFILES + OFFLINE ORBITAL SATELLITE IMAGERY */}
            {workbenchTab === "terrain" && (
              <div className="flex flex-col gap-5">
                <div className="rounded-xl border hairline bg-[#11141c] p-4 flex items-center justify-between flex-wrap gap-4">
                  <div className="flex items-center gap-6 flex-wrap">
                    <label className="flex items-center gap-3 text-[13px] text-[#a3a9b8]">
                      <span>{copy.exaggeration}</span>
                      <input
                        type="range"
                        min="1"
                        max="3"
                        step="0.25"
                        value={exaggeration}
                        onChange={(e) => setExaggeration(parseFloat(e.target.value))}
                        className="accent-[#4c8bf5]"
                      />
                      <span className="font-mono tabular text-[#eef0f5] w-10">
                        {exaggeration.toFixed(1)}x
                      </span>
                    </label>

                    <label className="flex items-center gap-3 text-[13px] text-[#a3a9b8]">
                      <span>{copy.azimuth}</span>
                      <input
                        type="range"
                        min="0"
                        max="359"
                        step="1"
                        value={azimuthDeg}
                        onChange={(e) => setAzimuthDeg(parseInt(e.target.value, 10))}
                        className="accent-[#4c8bf5]"
                      />
                      <span className="font-mono tabular text-[#eef0f5] w-10">
                        {azimuthDeg}°
                      </span>
                    </label>
                  </div>

                  <div className="flex items-center gap-2 text-[11.5px]">
                    {[0, 42, 135, 225].map((ang) => (
                      <button
                        key={ang}
                        type="button"
                        onClick={() => setAzimuthDeg(ang)}
                        className={`px-2 py-1 rounded border font-mono ${
                          azimuthDeg === ang
                            ? "active-highlight border-[#4c8bf5]/50 text-[#eef0f5]"
                            : "hairline text-[#7a8296] hover:text-[#eef0f5]"
                        }`}
                      >
                        {ang}°
                      </button>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                  <Terrain3DCanvas
                    tile={dem?.[activeMoon.site_id]}
                    title={`${copy.demTitleMoon} · ${moonName}`}
                    subtitle={`${activeMoon.dem_src} · 51×51 · r = 1000 m`}
                    accentColor="#4c8bf5"
                    azimuthDeg={azimuthDeg}
                    exaggeration={exaggeration}
                    onAzimuthChange={setAzimuthDeg}
                  />

                  <Terrain3DCanvas
                    tile={dem?.[selectedEarth.site_id]}
                    title={`${copy.demTitleEarth} · ${selectedEarth.short}`}
                    subtitle={`${selectedEarth.dem_src} · 51×51 · r = 1000 m`}
                    accentColor="#4cc38a"
                    azimuthDeg={azimuthDeg}
                    exaggeration={exaggeration}
                    onAzimuthChange={setAzimuthDeg}
                  />
                </div>

                <ElevationProfileSvg
                  moonTile={dem?.[activeMoon.site_id]}
                  earthTile={dem?.[selectedEarth.site_id]}
                  moonName={moonName}
                  earthName={selectedEarth.short}
                  lang={lang}
                />

                {/* Offline Orbital Imagery Comparison */}
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                  <div className="rounded-xl border hairline bg-[#11141c] p-4 flex flex-col gap-3">
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <div>
                        <h4 className="text-[14px] font-medium text-[#eef0f5]">
                          {copy.orbitalMoonTitle}
                        </h4>
                        <p className="text-[12px] text-[#7a8296] font-mono tabular">
                          {moonName} · 2.2 × 2.2 km · {activeMoon.dem_res_m} m/px
                        </p>
                      </div>
                      <div className="inline-flex rounded-lg p-0.5 bg-[#07080d] border hairline text-[11px]">
                        {(
                          [
                            ["hillshade", lang === "tr" ? "Kabartma" : "Hillshade"],
                            ["hazard", lang === "tr" ? "Eğim sınıfı" : "Slope bins"],
                            ["plate", lang === "tr" ? "3-panel kesit" : "3-panel plate"],
                          ] as [MoonAtlasMode, string][]
                        ).map(([modeKey, lbl]) => (
                          <button
                            key={modeKey}
                            type="button"
                            onClick={() => setMoonAtlasLayer(modeKey)}
                            className={`px-2.5 py-1 rounded ${
                              moonAtlasLayer === modeKey
                                ? "active-highlight text-[#eef0f5]"
                                : "text-[#7a8296] hover:text-[#eef0f5]"
                            }`}
                          >
                            {lbl}
                          </button>
                        ))}
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() =>
                        setLightbox({
                          src:
                            moonAtlasLayer === "hillshade"
                              ? activeMoon.hillshade_img
                              : moonAtlasLayer === "hazard"
                                ? activeMoon.hazard_img
                                : activeMoon.atlas_plate_img,
                          title: `${moonName} · LRO LOLA 5 m/px`,
                        })
                      }
                      className="rounded-lg overflow-hidden bg-[#07080d] border hairline aspect-[4/3] block cursor-zoom-in"
                    >
                      <img
                        src={
                          moonAtlasLayer === "hillshade"
                            ? activeMoon.hillshade_img
                            : moonAtlasLayer === "hazard"
                              ? activeMoon.hazard_img
                              : activeMoon.atlas_plate_img
                        }
                        alt={moonName}
                        className="w-full h-full object-contain"
                      />
                    </button>

                    {activeMoon.pct_lt10deg !== null && (
                      <div className="grid grid-cols-3 gap-2 text-[12px] font-mono tabular text-[#a3a9b8]">
                        <div className="px-2.5 py-1.5 rounded bg-[#07080d] border hairline">
                          <span className="text-[#7a8296] block text-[10px]">&lt;10°</span>
                          {activeMoon.pct_lt10deg.toFixed(1)}%
                        </div>
                        <div className="px-2.5 py-1.5 rounded bg-[#07080d] border hairline">
                          <span className="text-[#7a8296] block text-[10px]">10–20°</span>
                          {activeMoon.pct_10_20deg?.toFixed(1)}%
                        </div>
                        <div className="px-2.5 py-1.5 rounded bg-[#07080d] border hairline">
                          <span className="text-[#7a8296] block text-[10px]">&gt;20°</span>
                          {activeMoon.pct_gt20deg?.toFixed(1)}%
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="rounded-xl border hairline bg-[#11141c] p-4 flex flex-col gap-3">
                    <div>
                      <h4 className="text-[14px] font-medium text-[#eef0f5]">
                        {copy.orbitalEarthTitle}
                      </h4>
                      <p className="text-[12px] text-[#7a8296] font-mono tabular">
                        {selectedEarth.short} · {selectedEarth.s2_date ? selectedEarth.s2_date.slice(0, 10) : "Sentinel-2 L2A"} ·{" "}
                        {selectedEarth.s2_cloud_pct !== null
                          ? `${selectedEarth.s2_cloud_pct.toFixed(1)}% ${lang === "tr" ? "bulut" : "cloud"}`
                          : "10 m/px"}
                      </p>
                    </div>

                    <button
                      type="button"
                      onClick={() =>
                        setLightbox({
                          src: selectedEarth.atlas_img,
                          title: `${selectedEarth.short} · ESA Sentinel-2 L2A (10 m/px)`,
                        })
                      }
                      className="rounded-lg overflow-hidden bg-[#07080d] border hairline aspect-[4/3] block cursor-zoom-in"
                    >
                      <img
                        src={selectedEarth.atlas_img}
                        alt={selectedEarth.name}
                        className="w-full h-full object-cover"
                      />
                    </button>

                    <div className="px-3 py-2 rounded bg-[#07080d] border hairline text-[11px] font-mono text-[#7a8296] truncate">
                      Scene: {selectedEarth.s2_scene || selectedEarth.site_id}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* VIEW 3: RANK DIAGNOSTIC + ALBEDO SENSITIVITY + MIXED-PIXEL AUDIT + 8 LIMITS */}
            {workbenchTab === "validation" && (
              <div className="flex flex-col gap-5">
                <div className="rounded-xl border hairline bg-[#11141c] p-5">
                  <h3 className="text-[15px] font-medium text-[#eef0f5] mb-1">
                    {copy.whySplitTitle}
                  </h3>
                  <p className="text-[13px] text-[#7a8296] mb-4">{copy.validationIntro}</p>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-[13px] leading-[1.55]">
                    <div className="rounded-lg border hairline bg-[#07080d] p-4">
                      <div className="text-[12px] font-mono text-[#4c8bf5] mb-1.5">
                        Etna Cisternazza
                      </div>
                      <p className="text-[#a3a9b8]">{copy.etnaExplain}</p>
                    </div>
                    <div className="rounded-lg border hairline bg-[#07080d] p-4">
                      <div className="text-[12px] font-mono text-[#4c8bf5] mb-1.5">
                        Atacama &amp; Haughton → Faustini
                      </div>
                      <p className="text-[#a3a9b8]">{copy.atacamaExplain}</p>
                    </div>
                    <div className="rounded-lg border hairline bg-[#07080d] p-4">
                      <div className="text-[12px] font-mono text-[#4cc38a] mb-1.5">
                        Karacadağ Kollubaba
                      </div>
                      <p className="text-[#a3a9b8]">{copy.karacadagExplain}</p>
                    </div>
                  </div>
                </div>

                {/* 10-Site DOI Rank Diagnostic Table */}
                <div className="rounded-xl border hairline bg-[#11141c] overflow-hidden">
                  <div className="px-5 py-3.5 border-b hairline flex items-center justify-between">
                    <h3 className="text-[14px] font-medium text-[#eef0f5]">
                      {lang === "tr"
                        ? "Bilinen 10 doğrulama sahası sıra tanısı (Mobilite # artan)"
                        : "10 established validation sites rank diagnostic"}
                    </h3>
                    <span className="text-[12px] font-mono text-[#7a8296]">{moonName}</span>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-[13px] border-collapse">
                      <thead>
                        <tr className="border-b hairline text-[#7a8296] text-left bg-[#07080d]">
                          <th className="py-2.5 px-4 font-normal">
                            {lang === "tr" ? "Doğrulama sahası" : "Validation site"}
                          </th>
                          <th className="py-2.5 px-4 font-normal text-right">
                            {lang === "tr" ? "Mobilite #" : "Mobility #"}
                          </th>
                          <th className="py-2.5 px-4 font-normal text-right">
                            {lang === "tr" ? "Genel #" : "Overall #"}
                          </th>
                          <th className="py-2.5 px-4 font-normal text-right">
                            {lang === "tr" ? "Yüzey #" : "Surface #"}
                          </th>
                          <th className="py-2.5 px-4 font-normal">
                            {lang === "tr" ? "Beklenen (E1)" : "Expected (E1)"}
                          </th>
                          <th className="py-2.5 px-4 font-normal">
                            {lang === "tr" ? "Buz (E8)" : "Ice (E8)"}
                          </th>
                          <th className="py-2.5 px-4 font-normal">
                            {lang === "tr" ? "Kaynak (DOI)" : "Reference (DOI)"}
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {validationRows.map((r) => {
                          const s = sitesById[r.site_id];
                          if (!s) return null;
                          const v = s.validation;
                          return (
                            <tr
                              key={r.site_id}
                              onClick={() => setSelectedEarthId(s.site_id)}
                              className="border-b hairline hover:bg-[#1a1e28]/60 cursor-pointer"
                            >
                              <td className="py-2.5 px-4 text-[#eef0f5] font-medium">{s.short}</td>
                              <td className="py-2.5 px-4 text-right font-mono tabular text-[#eef0f5]">
                                {r.mob_rank}
                              </td>
                              <td className="py-2.5 px-4 text-right font-mono tabular text-[#a3a9b8]">
                                {r.rank}
                              </td>
                              <td className="py-2.5 px-4 text-right font-mono tabular text-[#a3a9b8]">
                                {r.surf_rank}
                              </td>
                              <td className="py-2.5 px-4 font-mono text-[12px] text-[#a3a9b8]">
                                {v?.expected_v1 ?? "—"}
                              </td>
                              <td className="py-2.5 px-4 text-[#a3a9b8]">
                                {lang === "tr" ? v?.ice_e8 : v?.ice_e8_en}
                              </td>
                              <td className="py-2.5 px-4">
                                {v?.source_url ? (
                                  <a
                                    href={v.source_url}
                                    target="_blank"
                                    rel="noreferrer"
                                    onClick={(e) => e.stopPropagation()}
                                    className="inline-flex items-center gap-1 text-[12px] text-[#4c8bf5] hover:underline"
                                  >
                                    <span>{v.source_label}</span>
                                    <ExternalLink className="w-3 h-3" strokeWidth={1.5} />
                                  </a>
                                ) : (
                                  <span className="text-[12px] text-[#7a8296]">{v?.source_label}</span>
                                )}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Albedo Sensitivity Curve (src/moon_mars/albedo_sensitivity.py) */}
                <AlbedoSensitivitySvg
                  rows={craterSensitivity}
                  sitesById={sitesById}
                  moonName={moonName}
                  lang={lang}
                  onSelectEarth={(sid) => setSelectedEarthId(sid)}
                />

                {/* 1 km Mixed-Pixel & NASADEM Fallback Audit (src/earth/mixed_pixel.py) */}
                <div className="rounded-xl border hairline bg-[#11141c] p-5 flex flex-col gap-3">
                  <div className="flex items-start justify-between gap-3 flex-wrap">
                    <div>
                      <h3 className="text-[14px] font-medium text-[#eef0f5]">
                        {lang === "tr"
                          ? "1 km karma piksel ve DEM kaynak kalibrasyon denetimi"
                          : "1 km mixed-pixel and DEM calibration audit"}
                      </h3>
                      <p className="text-[12px] text-[#7a8296] mt-0.5">
                        {lang === "tr"
                          ? "ESA WorldCover 10 m ve Sentinel-2 10 m incelemesi: kaba 500 m albedo / 1 km LST piksellerindeki su, tarım ve step karışımları raporlanır (Ağrı N39E044 karosu için NASADEM EGM96 yedeği kullanılmıştır)"
                          : "ESA WorldCover 10 m and Sentinel-2 10 m audit flagging coarse pixel water, vegetation or crop dilution (with NASADEM EGM96 fallback on Ağrı)"}
                      </p>
                    </div>
                    <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-[#07080d] border hairline text-[#a3a9b8]">
                      ESA WorldCover 10 m + Sentinel-2 L2A
                    </span>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-[12px] border-collapse">
                      <thead>
                        <tr className="border-b hairline text-[#7a8296] text-left bg-[#07080d]">
                          <th className="py-2 px-3 font-normal">{lang === "tr" ? "Denetlenen saha" : "Audited site"}</th>
                          <th className="py-2 px-3 font-normal">{lang === "tr" ? "Sınıf" : "Flag"}</th>
                          <th className="py-2 px-3 font-normal text-right">WC çıplak</th>
                          <th className="py-2 px-3 font-normal text-right">WC su</th>
                          <th className="py-2 px-3 font-normal text-right">WC bitki/tarım</th>
                          <th className="py-2 px-3 font-normal text-right">S2 çıplak / kar</th>
                        </tr>
                      </thead>
                      <tbody className="font-mono tabular">
                        {data.mixed_pixel_audit.slice(0, 6).map((m) => (
                          <tr
                            key={m.site_id}
                            onClick={() => {
                              if (sitesById[m.site_id]) setSelectedEarthId(m.site_id);
                            }}
                            className="border-b hairline last:border-b-0 hover:bg-[#1a1e28]/60 cursor-pointer"
                          >
                            <td className="py-2 px-3 font-sans text-[#eef0f5]">
                              <div>{sitesById[m.site_id]?.short ?? m.label}</div>
                              <div className="text-[11px] text-[#7a8296]">{m.note}</div>
                            </td>
                            <td className="py-2 px-3 whitespace-nowrap">
                              <span
                                className={`px-2 py-0.5 rounded text-[10.5px] ${
                                  m.rule_is_mixed
                                    ? "bg-[#d9a441]/15 text-[#d9a441]"
                                    : "bg-[#4cc38a]/15 text-[#4cc38a]"
                                }`}
                              >
                                {m.rule_flag}
                              </span>
                            </td>
                            <td className="py-2 px-3 text-right text-[#eef0f5]">{m.wc_bare_pct.toFixed(1)}%</td>
                            <td className="py-2 px-3 text-right text-[#a3a9b8]">{m.wc_water_pct.toFixed(1)}%</td>
                            <td className="py-2 px-3 text-right text-[#a3a9b8]">
                              {(m.wc_veg_pct + m.wc_crop_pct).toFixed(1)}%
                            </td>
                            <td className="py-2 px-3 text-right text-[#a3a9b8] whitespace-nowrap">
                              {m.s2_bare_or_dark_pct.toFixed(1)}% / {m.s2_snow_pct.toFixed(1)}%
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* 8-Dimension Scorecard */}
                <div className="rounded-xl border hairline bg-[#11141c] p-5">
                  <div className="flex items-center gap-2 mb-4">
                    <Layers className="w-4 h-4 text-[#7a8296]" strokeWidth={1.5} />
                    <h3 className="text-[15px] font-medium text-[#eef0f5]">{copy.limitsTitle}</h3>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3">
                    {data.dimensions[lang].map((row, i) => {
                      const vals = Object.values(row);
                      const [dimName, status, source, note] = vals;
                      const isActive = status.toLowerCase().includes("aktif") || status.toLowerCase().includes("active");
                      const isSusp = status.toLowerCase().includes("kullan") || status.toLowerCase().includes("lab") || status.toLowerCase().includes("omitted");
                      return (
                        <div
                          key={i}
                          className="rounded-lg border hairline bg-[#07080d] p-3.5 flex flex-col justify-between gap-2"
                        >
                          <div>
                            <div
                              className={`text-[11px] font-mono mb-1 ${
                                isActive
                                  ? "text-[#4cc38a]"
                                  : isSusp
                                    ? "text-[#e5484d]"
                                    : "text-[#7a8296]"
                              }`}
                            >
                              {status}
                            </div>
                            <div className="text-[13px] font-medium text-[#eef0f5]">{dimName}</div>
                            <div className="text-[12px] text-[#a3a9b8] mt-1 leading-snug">{note}</div>
                          </div>
                          <div className="text-[11px] font-mono text-[#7a8296] pt-2 border-t hairline">
                            {source}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* VIEW 4: 5 HIGH-RES REPORT FIGURES + EMIRHAN/ERAY BIBLIOGRAPHY */}
            {workbenchTab === "figures" && (
              <div className="flex flex-col gap-5">
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                  {ANALYSIS_FIGURES.map((fig, idx) => {
                    const title = lang === "tr" ? fig.trTitle : fig.enTitle;
                    const cap = lang === "tr" ? fig.trCap : fig.enCap;
                    return (
                      <div
                        key={fig.file}
                        className={`rounded-xl border hairline bg-[#11141c] p-4 flex flex-col gap-3 ${
                          idx === 0 ? "xl:col-span-2" : ""
                        }`}
                      >
                        <div className="flex items-center justify-between gap-2">
                          <h3 className="text-[14px] font-medium text-[#eef0f5]">{title}</h3>
                          <button
                            type="button"
                            onClick={() => setLightbox({ src: fig.file, title })}
                            className="text-[12px] text-[#4c8bf5] hover:underline shrink-0"
                          >
                            {lang === "tr" ? "Tam ekran" : "Inspect"}
                          </button>
                        </div>
                        <button
                          type="button"
                          onClick={() => setLightbox({ src: fig.file, title })}
                          className="rounded-lg overflow-hidden bg-[#07080d] border hairline cursor-zoom-in block text-left"
                        >
                          <img src={fig.file} alt={title} className="w-full h-auto block" />
                        </button>
                        <p className="text-[12px] text-[#a3a9b8] leading-relaxed">{cap}</p>
                      </div>
                    );
                  })}
                </div>

                {/* Consolidated Emirhan & Eray Datasets + Papers */}
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                  <div className="rounded-xl border hairline bg-[#11141c] p-5">
                    <h3 className="text-[14px] font-medium text-[#eef0f5] mb-3">
                      {copy.bibMoonTitle}
                    </h3>
                    <ul className="space-y-2 text-[12px] text-[#a3a9b8] leading-relaxed">
                      {(lang === "tr" ? data.bibliography.moon_tr : data.bibliography.moon_en).map(
                        (item, idx) => (
                          <li key={idx} className="pb-2 border-b hairline last:border-b-0">
                            {item}
                          </li>
                        )
                      )}
                    </ul>
                  </div>

                  <div className="rounded-xl border hairline bg-[#11141c] p-5">
                    <h3 className="text-[14px] font-medium text-[#eef0f5] mb-3">
                      {copy.bibEarthTitle}
                    </h3>
                    <ul className="space-y-2 text-[12px] text-[#a3a9b8] leading-relaxed">
                      {(lang === "tr" ? data.bibliography.earth_tr : data.bibliography.earth_en).map(
                        (item, idx) => (
                          <li key={idx} className="pb-2 border-b hairline last:border-b-0">
                            {item}
                          </li>
                        )
                      )}
                    </ul>
                  </div>
                </div>

                {/* 40-Site Searchable Citation Table */}
                <div className="rounded-xl border hairline bg-[#11141c] overflow-hidden">
                  <div className="px-5 py-3.5 border-b hairline flex items-center justify-between flex-wrap gap-3">
                    <h3 className="text-[14px] font-medium text-[#eef0f5]">{copy.bibTableTitle}</h3>
                    <input
                      id="bib-search"
                      name="bibSearch"
                      type="search"
                      value={bibSearch}
                      onChange={(e) => setBibSearch(e.target.value)}
                      placeholder={copy.bibSearchPlaceholder}
                      className="h-8 px-3 rounded-lg bg-[#07080d] border hairline text-[12px] text-[#eef0f5] placeholder:text-[#7a8296] focus:outline-none focus:border-[#4c8bf5] min-w-[240px]"
                    />
                  </div>
                  <div className="max-h-[380px] overflow-auto">
                    <table className="w-full text-[12px] border-collapse">
                      <thead className="sticky top-0 bg-[#07080d]">
                        <tr className="border-b hairline text-[#7a8296] text-left">
                          <th className="py-2.5 px-4 font-normal">
                            {lang === "tr" ? "Saha" : "Site"}
                          </th>
                          <th className="py-2.5 px-4 font-normal">
                            {lang === "tr" ? "Koordinat / DEM" : "Coords / DEM"}
                          </th>
                          <th className="py-2.5 px-4 font-normal">
                            {lang === "tr" ? "Akademik kaynak" : "Citation"}
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredBibSites.map((s) => (
                          <tr key={s.site_id} className="border-b hairline last:border-b-0">
                            <td className="py-2.5 px-4 text-[#eef0f5] font-medium align-top">
                              {s.short}
                              <div className="font-mono text-[11px] text-[#7a8296] mt-0.5">
                                {s.site_id}
                              </div>
                            </td>
                            <td className="py-2.5 px-4 font-mono tabular text-[#a3a9b8] align-top whitespace-nowrap">
                              {s.lat.toFixed(4)}°, {s.lon.toFixed(4)}°
                              <div className="text-[#7a8296]">{s.dem_src}</div>
                            </td>
                            <td className="py-2.5 px-4 text-[#a3a9b8] leading-relaxed align-top">
                              {s.citation}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Clean Technical Footer */}
      <footer className="border-t hairline bg-[#07080d] mt-10">
        <div className="max-w-[1400px] mx-auto px-5 sm:px-6 py-5 flex flex-col sm:flex-row items-center justify-between gap-3 text-[12px] text-[#7a8296]">
          <div>
            Endülüs · NASA Space Apps 2026 · {data.meta.moon_count} Ay × {data.meta.earth_count} Dünya · 0 MOCK
          </div>
          <div className="font-mono">
            NASA LRO LOLA 5 m · Copernicus GLO-30 · ESA Sentinel-2 L2A · MODIS MCD43A3
          </div>
        </div>
      </footer>

      {/* Lightbox Modal for High-Res Plots & Satellite Tiles */}
      {lightbox && (
        <div
          className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-6"
          onClick={() => setLightbox(null)}
        >
          <div
            className="max-w-6xl w-full bg-[#11141c] border hairline-strong rounded-xl p-4 flex flex-col gap-3"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between">
              <span className="text-[14px] font-medium text-[#eef0f5]">{lightbox.title}</span>
              <button
                type="button"
                onClick={() => setLightbox(null)}
                className="p-1.5 rounded-lg bg-[#1a1e28] text-[#eef0f5] hover:bg-[#252b38]"
              >
                <X className="w-4 h-4" strokeWidth={1.5} />
              </button>
            </div>
            <img
              src={lightbox.src}
              alt={lightbox.title}
              className="w-full max-h-[82vh] object-contain rounded-lg bg-[#07080d]"
            />
          </div>
        </div>
      )}
    </div>
  );
}
