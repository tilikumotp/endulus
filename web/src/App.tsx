import { useEffect, useMemo, useState } from "react";
import {
  ArrowDown,
  ArrowDownUp,
  ArrowRight,
  ArrowUp,
  BookOpen,
  ChevronLeft,
  ChevronRight,
  Compass,
  ExternalLink,
  Mountain,
  RotateCcw,
  Search,
  ShieldCheck,
  SlidersHorizontal,
  X,
} from "lucide-react";
import { ElevationProfileSvg } from "./components/ElevationProfileSvg";
import { LunarGlyphCanvas } from "./components/LunarGlyphCanvas";
import { RadarCompareSvg } from "./components/RadarCompareSvg";
import { RealMapLeaflet } from "./components/RealMapLeaflet";
import { ScoreBarsChart, type ChartAxisMode } from "./components/ScoreBarsChart";
import { Terrain3DCanvas, type TerrainColorMode } from "./components/Terrain3DCanvas";
import {
  ANALYSIS_FIGURES,
  CHALLENGE_STORY,
  FEATURE_NAMES,
  LITHOLOGY_NAMES,
  MISSIONS,
  SOLUTION_EXAMPLES,
  UI_COPY,
  WORKBENCH_TABS,
  type ExampleJumpKey,
} from "./i18n";
import { computeWeightedScores, PRESET_WEIGHTS } from "./scoring";
import type {
  AppDataPayload,
  DemArchive,
  EarthSite,
  Lang,
  MissionKey,
  SiteScoreRow,
  WorkbenchTab,
} from "./types";

type TableSortCol =
  | "rank"
  | "name"
  | "score"
  | "mob"
  | "surf"
  | "slope_mean"
  | "albedo"
  | "relief"
  | "lithology";
type SortDir = "asc" | "desc";
type ValSortCol = "mob_rank" | "rank" | "surf_rank" | "name" | "lithology" | "slope_mean";
type MoonAtlasMode = "hillshade" | "hazard" | "plate";

function extractDoiUrl(text: string): string | null {
  const httpsMatch = text.match(/https?:\/\/[^\s,)]+/i);
  if (httpsMatch) return httpsMatch[0].replace(/[.)]+$/, "");
  const doiMatch = text.match(/\bDOI[:\s]*(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)/i);
  if (doiMatch) return `https://doi.org/${doiMatch[1].replace(/[.)]+$/, "")}`;
  return null;
}

function splitBibItem(text: string): { head: string; body: string } {
  const idx = text.indexOf(":");
  if (idx > 0 && idx < 78) {
    return {
      head: text.slice(0, idx).trim(),
      body: text.slice(idx + 1).trim(),
    };
  }
  return { head: "", body: text };
}

export default function App() {
  const [data, setData] = useState<AppDataPayload | null>(null);
  const [dem, setDem] = useState<DemArchive | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [lang, setLang] = useState<Lang>("en");
  const [moonId, setMoonId] = useState<string>("moon_shackleton_rim");
  const [mission, setMission] = useState<MissionKey>("default");
  const [wMob, setWMob] = useState<number>(PRESET_WEIGHTS.default.wMob);
  const [wSurf, setWSurf] = useState<number>(PRESET_WEIGHTS.default.wSurf);

  const [search, setSearch] = useState<string>("");
  const [selectedEarthId, setSelectedEarthId] = useState<string>("earth_karapinar_meke");
  const [workbenchTab, setWorkbenchTab] = useState<WorkbenchTab>("overview");
  const [chartMode, setChartMode] = useState<ChartAxisMode>("overall");
  const [maxBars, setMaxBars] = useState<number>(12);

  const [sortCol, setSortCol] = useState<TableSortCol>("rank");
  const [sortDir, setSortDir] = useState<SortDir>("asc");
  const [valSortCol, setValSortCol] = useState<ValSortCol>("mob_rank");
  const [valSortDir, setValSortDir] = useState<SortDir>("asc");

  // 3D Terrain interactive state
  const [azimuthDeg, setAzimuthDeg] = useState<number>(42);
  const [pitchDeg, setPitchDeg] = useState<number>(34);
  const [zoom3d, setZoom3d] = useState<number>(1.05);
  const [exaggeration, setExaggeration] = useState<number>(2.0);
  const [colorMode3d, setColorMode3d] = useState<TerrainColorMode>("elevation");
  const [autoRotate3d, setAutoRotate3d] = useState<boolean>(false);
  const [guideOpen, setGuideOpen] = useState<boolean>(true);
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

  useEffect(() => {
    if (!autoRotate3d || workbenchTab !== "terrain") return;
    let frameId = 0;
    let lastTs = performance.now();
    const tick = (now: number) => {
      const dt = (now - lastTs) / 1000;
      lastTs = now;
      setAzimuthDeg((prev) => (prev + dt * 16) % 360);
      frameId = requestAnimationFrame(tick);
    };
    frameId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frameId);
  }, [autoRotate3d, workbenchTab]);

  const copy = UI_COPY[lang];

  const isCustomWeights =
    Math.abs(wMob - PRESET_WEIGHTS[mission].wMob) > 0.01 ||
    Math.abs(wSurf - PRESET_WEIGHTS[mission].wSurf) > 0.01;

  const bothZeroWeights = wMob === 0 && wSurf === 0;
  const weightTotal = Math.max(0.01, wMob + wSurf);
  const mobPct = bothZeroWeights ? 50 : Math.round((wMob / weightTotal) * 100);
  const surfPct = 100 - mobPct;

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
    const basePreset = data.comparisons[moonId]?.[mission] ?? [];
    if (!isCustomWeights) return basePreset;
    const baseDefault = data.comparisons[moonId]?.default ?? basePreset;
    const axisDraws = data.comparisons[moonId]?.axis_draws;
    return computeWeightedScores(baseDefault, wMob, wSurf, axisDraws);
  }, [data, moonId, mission, isCustomWeights, wMob, wSurf]);

  const scoresById = useMemo(() => {
    const map: Record<string, SiteScoreRow> = {};
    for (const r of activeScores) map[r.site_id] = r;
    return map;
  }, [activeScores]);

  // Pool filter + search list (ranked by active composite score)
  const poolRows = useMemo(() => {
    const q = search.trim().toLowerCase();
    return activeScores.filter((r) => {
      const s = sitesById[r.site_id];
      if (!s) return false;
      if (!q) return true;
      return `${s.site_id} ${s.name} ${s.short} ${s.lithology}`.toLowerCase().includes(q);
    });
  }, [activeScores, sitesById, search]);

  // Full table bidirectional sorting across all key columns
  const tableRows = useMemo(() => {
    const mul = sortDir === "asc" ? 1 : -1;
    return [...poolRows].sort((a, b) => {
      const sa = sitesById[a.site_id];
      const sb = sitesById[b.site_id];
      if (!sa || !sb) return 0;
      switch (sortCol) {
        case "rank":
          return (a.rank - b.rank) * mul;
        case "score":
          return (a.score - b.score) * mul;
        case "mob":
          return (a.mob - b.mob) * mul;
        case "surf":
          return (a.surf - b.surf) * mul;
        case "slope_mean":
          return (sa.slope_mean - sb.slope_mean) * mul;
        case "albedo":
          return (sa.albedo - sb.albedo) * mul;
        case "relief":
          return (sa.relief - sb.relief) * mul;
        case "lithology":
          return sa.lithology.localeCompare(sb.lithology) * mul;
        case "name":
        default:
          return sa.short.localeCompare(sb.short) * mul;
      }
    });
  }, [poolRows, sitesById, sortCol, sortDir]);

  // Grouped site lists for instant one-click site dropdown selector
  const groupedPicker = useMemo(() => {
    if (!data) return { tr: [], validation: [], global: [] };
    const tr: { site: EarthSite; row: SiteScoreRow | undefined }[] = [];
    const validation: { site: EarthSite; row: SiteScoreRow | undefined }[] = [];
    const global: { site: EarthSite; row: SiteScoreRow | undefined }[] = [];
    for (const r of activeScores) {
      const site = sitesById[r.site_id];
      if (!site) continue;
      if (site.role === "validation") validation.push({ site, row: r });
      else if (site.is_tr) tr.push({ site, row: r });
      else global.push({ site, row: r });
    }
    return { tr, validation, global };
  }, [data, activeScores, sitesById]);

  const filteredSitesForMap = useMemo(() => {
    if (!data) return [];
    const allowed = new Set(poolRows.map((r) => r.site_id));
    return data.earth_sites.filter((s) => allowed.has(s.site_id));
  }, [data, poolRows]);

  const selectedEarth = sitesById[selectedEarthId] ?? data?.earth_sites[0] ?? null;
  const selectedScore = selectedEarth ? scoresById[selectedEarth.site_id] : undefined;
  const selectedGaps =
    data && selectedEarth ? data.gaps[moonId]?.[selectedEarth.site_id] ?? [] : [];

  const validationRows = useMemo(() => {
    if (!data) return [];
    const list = activeScores.filter((r) => sitesById[r.site_id]?.role === "validation");
    const mul = valSortDir === "asc" ? 1 : -1;
    return [...list].sort((a, b) => {
      const sa = sitesById[a.site_id];
      const sb = sitesById[b.site_id];
      if (!sa || !sb) return 0;
      if (valSortCol === "name") return sa.short.localeCompare(sb.short) * mul;
      if (valSortCol === "lithology") return sa.lithology.localeCompare(sb.lithology) * mul;
      if (valSortCol === "slope_mean") return (sa.slope_mean - sb.slope_mean) * mul;
      return (a[valSortCol] - b[valSortCol]) * mul;
    });
  }, [data, activeScores, sitesById, valSortCol, valSortDir]);

  const filteredBibSites = useMemo(() => {
    if (!data) return [];
    const q = bibSearch.trim().toLowerCase();
    return data.earth_sites.filter((s) => {
      if (!q) return true;
      return `${s.site_id} ${s.name} ${s.citation} ${s.dem_src} ${s.albedo_src}`
        .toLowerCase()
        .includes(q);
    });
  }, [data, bibSearch]);

  const handleMissionSelect = (mk: MissionKey) => {
    setMission(mk);
    setWMob(PRESET_WEIGHTS[mk].wMob);
    setWSurf(PRESET_WEIGHTS[mk].wSurf);
  };

  const handleSortClick = (col: TableSortCol, defaultDir: SortDir = "desc") => {
    if (sortCol === col) {
      setSortDir((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortCol(col);
      setSortDir(defaultDir);
    }
  };

  const handleValSortClick = (col: ValSortCol, defaultDir: SortDir = "asc") => {
    if (valSortCol === col) {
      setValSortDir((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setValSortCol(col);
      setValSortDir(defaultDir);
    }
  };

  const stepSelectedSite = (delta: number) => {
    if (poolRows.length === 0) return;
    const idx = poolRows.findIndex((r) => r.site_id === selectedEarthId);
    const nextIdx = idx < 0 ? 0 : (idx + delta + poolRows.length) % poolRows.length;
    setSelectedEarthId(poolRows[nextIdx].site_id);
  };

  const jumpToExample = (action: ExampleJumpKey) => {
    setSearch("");
    if (action === "rover_hasandagi") {
      setMoonId("moon_shackleton_rim");
      handleMissionSelect("rover_mobility");
      setSelectedEarthId("earth_hasandagi_kecekalecik");
      setChartMode("overall");
      setWorkbenchTab("overview");
      requestAnimationFrame(() => {
        document.getElementById("observatory")?.scrollIntoView({ behavior: "smooth" });
      });
    } else if (action === "faustini_haughton") {
      setMoonId("moon_faustini_rim");
      handleMissionSelect("default");
      setSelectedEarthId("earth_haughton_crater");
      setChartMode("mobility");
      setWorkbenchTab("overview");
      requestAnimationFrame(() => {
        document.getElementById("observatory")?.scrollIntoView({ behavior: "smooth" });
      });
    } else if (action === "radar_meke") {
      setMoonId("moon_shackleton_rim");
      handleMissionSelect("default");
      setSelectedEarthId("earth_karapinar_meke");
      setChartMode("surface");
      setWorkbenchTab("overview");
      setTimeout(() => {
        document.getElementById("radar-gaps-panel")?.scrollIntoView({ behavior: "smooth" });
      }, 60);
    } else {
      setMoonId("moon_shackleton_rim");
      setSelectedEarthId("earth_karapinar_meke");
      setColorMode3d("slope");
      setWorkbenchTab("terrain");
      requestAnimationFrame(() => {
        document.getElementById("observatory")?.scrollIntoView({ behavior: "smooth" });
      });
    }
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

  const moonName = lang === "tr" ? activeMoon.name_tr : activeMoon.name_en;

  const SortIndicator = ({ active, dir }: { active: boolean; dir: SortDir }) => {
    if (!active) return <ArrowDownUp className="w-3 h-3 text-[#555e73] inline ml-1" strokeWidth={1.5} />;
    return dir === "asc" ? (
      <ArrowUp className="w-3 h-3 text-[#4c8bf5] inline ml-1" strokeWidth={1.8} />
    ) : (
      <ArrowDown className="w-3 h-3 text-[#4c8bf5] inline ml-1" strokeWidth={1.8} />
    );
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#0b0d14] text-[#eef0f5] overflow-x-hidden">
      {/* Top instrument navigation bar */}
      <header className="sticky top-0 z-40 h-14 bg-[#07080d]/95 border-b hairline backdrop-blur-sm">
        <div className="max-w-[1400px] mx-auto h-full px-4 sm:px-6 flex items-center justify-between gap-4">
          <div className="flex items-center gap-5 min-w-0">
            <a href="#" className="flex items-center gap-2.5 text-[#eef0f5] font-medium text-[15px] shrink-0">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                <circle cx="10" cy="10" r="8" stroke="#eef0f5" strokeWidth="1.4" />
                <path d="M12.6 4.6a5.6 5.6 0 1 0 0 10.8 4.4 4.4 0 1 1 0-10.8Z" fill="#4c8bf5" />
                <line x1="2" y1="10" x2="5" y2="10" stroke="#7a8296" strokeWidth="1.2" />
                <line x1="15" y1="10" x2="18" y2="10" stroke="#7a8296" strokeWidth="1.2" />
              </svg>
              <span>{copy.brand}</span>
            </a>
          </div>

          <div className="flex items-center gap-2.5 shrink-0">
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
      <section className="max-w-[1400px] mx-auto w-full px-4 sm:px-6 pt-8 pb-8 lg:pt-10 lg:pb-10 border-b hairline">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10 items-center">
          <div className="lg:col-span-7 flex flex-col items-start min-w-0">
            <div className="enter-rise enter-delay-1 inline-flex items-center gap-2.5 text-[12px] font-mono tabular text-[#7a8296] mb-4 flex-wrap">
              <span>
                {data.meta.moon_count} {lang === "tr" ? "Ay bölgesi" : "Moon sites"}
              </span>
              <span className="text-[#2b3245]">/</span>
              <span>
                {data.meta.earth_count} {lang === "tr" ? "Dünya sahası" : "Earth sites"}
              </span>
              <span className="text-[#2b3245]">/</span>
              <span className="text-[#4c8bf5]">LRO LOLA · Copernicus DEM</span>
            </div>

            <h1 className="enter-rise enter-delay-2 text-[32px] sm:text-[42px] font-medium leading-[1.09] tracking-[-0.025em] text-[#eef0f5] max-w-[19ch]">
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
            </div>

            {/* Clean uniform 5-crater selector strip + telemetry */}
            <div className="mt-7 pt-5 border-t hairline w-full">
              <div className="flex items-center justify-between gap-2 mb-2 text-[11.5px] font-mono text-[#7a8296]">
                <span className="inline-flex items-center gap-1.5 text-[#a3a9b8]">
                  <Compass className="w-3.5 h-3.5 text-[#4c8bf5]" strokeWidth={1.6} />
                  <span>
                    {lang === "tr"
                      ? "Ay kraterleri (hedef bölge seçin)"
                      : "Lunar craters (select target region)"}
                  </span>
                </span>
                <span>{lang === "tr" ? "5 Güney Kutbu bölgesi" : "5 South Pole sites"}</span>
              </div>
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
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-[13px] font-mono tabular">
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

      {/* Main Interactive Observatory Workbench */}
      <section id="observatory" className="max-w-[1400px] mx-auto w-full px-4 sm:px-6 py-7 flex-1">
        <div className="flex flex-col lg:flex-row gap-6 items-start">
          {/* Sticky 284px Observatory Control Rail */}
          <aside className="w-full lg:w-[284px] shrink-0 lg:sticky lg:top-[72px] rounded-xl border hairline bg-[#07080d] p-4 flex flex-col gap-4">
            {/* 1. Effortless Quick Earth Site Picker (40 Sites Grouped + Stepper + Search) */}
            <div className="rounded-lg border hairline bg-[#11141c] p-3 flex flex-col gap-2.5">
              <div className="flex items-center justify-between gap-2">
                <label
                  htmlFor="quick-site-picker"
                  className="text-[11.5px] font-medium text-[#eef0f5]"
                >
                  {copy.earthPickerLabel}
                </label>
                <div className="flex items-center gap-1">
                  <button
                    type="button"
                    onClick={() => stepSelectedSite(-1)}
                    title={lang === "tr" ? "Önceki saha" : "Previous site"}
                    className="p-1 rounded bg-[#07080d] border hairline text-[#a3a9b8] hover:text-[#eef0f5]"
                  >
                    <ChevronLeft className="w-3.5 h-3.5" strokeWidth={1.6} />
                  </button>
                  <button
                    type="button"
                    onClick={() => stepSelectedSite(1)}
                    title={lang === "tr" ? "Sonraki saha" : "Next site"}
                    className="p-1 rounded bg-[#07080d] border hairline text-[#a3a9b8] hover:text-[#eef0f5]"
                  >
                    <ChevronRight className="w-3.5 h-3.5" strokeWidth={1.6} />
                  </button>
                </div>
              </div>

              <select
                id="quick-site-picker"
                value={selectedEarth.site_id}
                onChange={(e) => setSelectedEarthId(e.target.value)}
                className="w-full h-9 px-2.5 rounded-lg bg-[#07080d] border hairline-strong text-[12.5px] text-[#eef0f5] focus:outline-none focus:border-[#4c8bf5]"
              >
                <optgroup
                  label={
                    lang === "tr"
                      ? `Türkiye adayları (${groupedPicker.tr.length})`
                      : `Turkey candidates (${groupedPicker.tr.length})`
                  }
                >
                  {groupedPicker.tr.map(({ site, row }) => (
                    <option key={site.site_id} value={site.site_id}>
                      #{row?.rank ?? "-"} · {site.short.replace(/\s*\(TR\)$/, "")} · {row ? row.score.toFixed(3) : "—"}
                    </option>
                  ))}
                </optgroup>
                <optgroup
                  label={
                    lang === "tr"
                      ? `Bilinen analoglar (${groupedPicker.validation.length})`
                      : `Known analogues (${groupedPicker.validation.length})`
                  }
                >
                  {groupedPicker.validation.map(({ site, row }) => (
                    <option key={site.site_id} value={site.site_id}>
                      #{row?.rank ?? "-"} · {site.short} · {row ? row.score.toFixed(3) : "—"}
                    </option>
                  ))}
                </optgroup>
                <optgroup
                  label={
                    lang === "tr"
                      ? `Küresel adaylar (${groupedPicker.global.length})`
                      : `Global candidates (${groupedPicker.global.length})`
                  }
                >
                  {groupedPicker.global.map(({ site, row }) => (
                    <option key={site.site_id} value={site.site_id}>
                      #{row?.rank ?? "-"} · {site.short} · {row ? row.score.toFixed(3) : "—"}
                    </option>
                  ))}
                </optgroup>
              </select>

              {/* Quick Live Search with clickable instant matches */}
              <div className="relative">
                <Search
                  className="w-3.5 h-3.5 text-[#7a8296] absolute left-2.5 top-1/2 -translate-y-1/2 pointer-events-none"
                  strokeWidth={1.5}
                />
                <input
                  id="site-search"
                  name="siteSearch"
                  type="search"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder={copy.searchPlaceholder}
                  className="w-full h-8 pl-8 pr-2.5 rounded-lg bg-[#07080d] border hairline text-[12px] text-[#eef0f5] placeholder:text-[#7a8296] focus:outline-none focus:border-[#4c8bf5]"
                />
              </div>

              {search.trim().length > 0 && (
                <div className="flex flex-wrap gap-1 pt-0.5">
                  {poolRows.length > 0 ? (
                    poolRows.slice(0, 6).map((r) => {
                      const s = sitesById[r.site_id];
                      if (!s) return null;
                      return (
                        <button
                          key={r.site_id}
                          type="button"
                          onClick={() => setSelectedEarthId(s.site_id)}
                          className={`px-2 py-1 rounded text-[11px] truncate max-w-full border ${
                            s.site_id === selectedEarth.site_id
                              ? "border-[#4c8bf5] bg-[#4c8bf5]/20 text-[#eef0f5]"
                              : "hairline bg-[#07080d] text-[#a3a9b8] hover:text-[#eef0f5]"
                          }`}
                        >
                          #{r.rank} {s.short}
                        </button>
                      );
                    })
                  ) : (
                    <span className="text-[11px] text-[#7a8296]">
                      {lang === "tr" ? "Eşleşen saha bulunamadı" : "No matching site"}
                    </span>
                  )}
                </div>
              )}
            </div>

            {/* 2. Lunar Crater Group */}
            <div>
              <div className="text-[11.5px] text-[#7a8296] px-1 mb-1.5 flex items-center gap-1.5">
                <Compass className="w-3.5 h-3.5 text-[#7a8296]" strokeWidth={1.5} />
                <span>{copy.moonRegionLabel}</span>
              </div>
              <div className="flex flex-col gap-1">
                {data.moon_refs.map((m) => (
                  <button
                    key={m.site_id}
                    type="button"
                    onClick={() => setMoonId(m.site_id)}
                    className={`h-8 px-2.5 rounded-lg text-left text-[12.5px] transition-colors duration-150 truncate ${
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

            {/* 3. Mission Profile + Self-Explanatory Custom Weight Controls */}
            <div>
              <div className="flex items-center justify-between px-1 mb-1.5">
                <div className="text-[11.5px] text-[#7a8296] flex items-center gap-1.5">
                  <SlidersHorizontal className="w-3.5 h-3.5 text-[#7a8296]" strokeWidth={1.5} />
                  <span>{copy.missionLabel}</span>
                </div>
                {isCustomWeights && (
                  <button
                    type="button"
                    onClick={() => handleMissionSelect(mission)}
                    className="text-[10.5px] font-mono text-[#4c8bf5] hover:underline"
                  >
                    {lang === "tr" ? "Varsayılana dön" : "Reset preset"}
                  </button>
                )}
              </div>

              <div className="flex flex-col gap-1">
                {(Object.keys(MISSIONS) as MissionKey[]).map((mk) => {
                  const isActive = mk === mission && !isCustomWeights;
                  return (
                    <button
                      key={mk}
                      type="button"
                      onClick={() => handleMissionSelect(mk)}
                      className={`h-8 px-2.5 rounded-lg text-left text-[12px] transition-colors duration-150 flex items-center justify-between gap-2 ${
                        isActive
                          ? "active-highlight text-[#eef0f5] font-medium"
                          : "text-[#a3a9b8] hover:text-[#eef0f5] hover:bg-[#11141c]"
                      }`}
                    >
                      <span className="truncate">{MISSIONS[mk][lang]}</span>
                      <span
                        className={`text-[10px] font-mono tabular shrink-0 px-1.5 py-0.5 rounded ${
                          isActive
                            ? "bg-[#4c8bf5]/20 text-[#4c8bf5]"
                            : "bg-[#11141c] text-[#7a8296]"
                        }`}
                      >
                        {MISSIONS[mk].ratio}
                      </span>
                    </button>
                  );
                })}
              </div>

              {/* Plain-language explanation of active mode + live #1 site feedback */}
              <div className="mt-2 rounded-lg border hairline bg-[#11141c]/70 p-2.5 flex flex-col gap-2">
                <p className="text-[11px] leading-[1.45] text-[#a3a9b8]">
                  {isCustomWeights
                    ? lang === "tr"
                      ? `Özel ağırlık etkin (%${mobPct} arazi, %${surfPct} yüzey). Tüm 40 sahanın genel puanı bu orana göre anlık güncellenir.`
                      : `Custom ratio active (${mobPct}% terrain, ${surfPct}% surface). All 40 sites re-rank live.`
                    : lang === "tr"
                      ? MISSIONS[mission].note_tr
                      : MISSIONS[mission].note_en}
                </p>

                {activeScores[0] && sitesById[activeScores[0].site_id] && (
                  <button
                    type="button"
                    onClick={() => setSelectedEarthId(activeScores[0].site_id)}
                    className="w-full text-left px-2 py-1.5 rounded bg-[#07080d] border hairline hover:border-[#4c8bf5]/50 transition-colors flex items-center justify-between gap-2 text-[11px]"
                    title={
                      lang === "tr"
                        ? "1. sıradaki sahayı incelemek için tıklayın"
                        : "Click to inspect #1 site"
                    }
                  >
                    <span className="text-[#7a8296] shrink-0">
                      {lang === "tr" ? "Şu an #1:" : "Current #1:"}
                    </span>
                    <span className="text-[#eef0f5] font-medium truncate">
                      {sitesById[activeScores[0].site_id].short}
                    </span>
                    <span className="font-mono tabular text-[#4cc38a] shrink-0">
                      {activeScores[0].score.toFixed(3)}
                    </span>
                  </button>
                )}
              </div>

              {/* Interactive Custom Weight Sliders */}
              <div className="mt-2 rounded-lg border hairline bg-[#11141c] p-2.5 flex flex-col gap-2.5">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-[#eef0f5] font-medium">
                    {lang === "tr" ? "Özel eksen dengesi" : "Custom axis balance"}
                  </span>
                  <span className="font-mono tabular text-[#a3a9b8]">
                    <span className="text-[#4c8bf5]">{mobPct}%</span>
                    <span className="text-[#7a8296] mx-1">/</span>
                    <span className="text-[#4cc38a]">{surfPct}%</span>
                  </span>
                </div>

                {/* Proportional live ratio bar */}
                <div className="h-1.5 w-full rounded-full overflow-hidden bg-[#07080d] flex">
                  <div
                    className="h-full bg-[#4c8bf5] transition-all duration-150"
                    style={{ width: `${mobPct}%` }}
                  />
                  <div
                    className="h-full bg-[#4cc38a] transition-all duration-150"
                    style={{ width: `${surfPct}%` }}
                  />
                </div>

                <label className="flex flex-col gap-1 text-[11px]">
                  <div className="flex justify-between text-[#eef0f5]">
                    <span>{lang === "tr" ? "Mobilite (Arazi)" : "Mobility (Terrain)"}</span>
                    <span className="font-mono tabular text-[#4c8bf5]">{wMob.toFixed(2)}×</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="3"
                    step="0.25"
                    value={wMob}
                    onChange={(e) => setWMob(parseFloat(e.target.value))}
                    className="w-full accent-[#4c8bf5] cursor-pointer"
                  />
                  <span className="text-[10px] text-[#7a8296] leading-tight">
                    {lang === "tr"
                      ? "Eğim, dik yamaç (p90), pürüzlülük ve yükselti farkı"
                      : "Slope, steep grade (p90), roughness & relief"}
                  </span>
                </label>

                <label className="flex flex-col gap-1 text-[11px]">
                  <div className="flex justify-between text-[#eef0f5]">
                    <span>{lang === "tr" ? "Yüzey (Parlaklık)" : "Surface (Albedo)"}</span>
                    <span className="font-mono tabular text-[#4cc38a]">{wSurf.toFixed(2)}×</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="3"
                    step="0.25"
                    value={wSurf}
                    onChange={(e) => setWSurf(parseFloat(e.target.value))}
                    className="w-full accent-[#4cc38a] cursor-pointer"
                  />
                  <span className="text-[10px] text-[#7a8296] leading-tight">
                    {lang === "tr"
                      ? "Yüzey ışık yansıtma ve parlaklık uyumu (albedo)"
                      : "Surface reflectance & brightness fit (albedo)"}
                  </span>
                </label>

                {/* Quick 1-click extreme / balanced ratio buttons */}
                <div className="grid grid-cols-3 gap-1 pt-1 border-t hairline text-[10px] font-medium">
                  <button
                    type="button"
                    onClick={() => {
                      setWMob(1);
                      setWSurf(0);
                    }}
                    className={`py-1.5 px-1 rounded border whitespace-nowrap transition-colors ${
                      wMob > 0 && wSurf === 0
                        ? "border-[#4c8bf5]/60 bg-[#4c8bf5]/15 text-[#eef0f5]"
                        : "hairline bg-[#07080d] text-[#a3a9b8] hover:text-[#eef0f5]"
                    }`}
                  >
                    {lang === "tr" ? "%100 Arazi" : "100% Terrain"}
                  </button>
                  <button
                    type="button"
                    onClick={() => handleMissionSelect("default")}
                    className={`py-1.5 px-1 rounded border font-mono whitespace-nowrap transition-colors ${
                      !bothZeroWeights && Math.abs(mobPct - 50) <= 1
                        ? "border-[#eef0f5]/40 bg-[#1a1e28] text-[#eef0f5]"
                        : "hairline bg-[#07080d] text-[#a3a9b8] hover:text-[#eef0f5]"
                    }`}
                  >
                    50 / 50
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setWMob(0);
                      setWSurf(1);
                    }}
                    className={`py-1.5 px-1 rounded border whitespace-nowrap transition-colors ${
                      wSurf > 0 && wMob === 0
                        ? "border-[#4cc38a]/60 bg-[#4cc38a]/15 text-[#eef0f5]"
                        : "hairline bg-[#07080d] text-[#a3a9b8] hover:text-[#eef0f5]"
                    }`}
                  >
                    {lang === "tr" ? "%100 Yüzey" : "100% Surface"}
                  </button>
                </div>

                {bothZeroWeights && (
                  <p className="text-[10px] text-[#d9a441] leading-tight">
                    {lang === "tr"
                      ? "İki ağırlık da 0 olduğunda sistem otomatik %50/%50 dengeler."
                      : "When both weights are 0, scoring falls back to 50/50."}
                  </p>
                )}
              </div>
            </div>

            {/* 5. Selected Earth Site Inspector Card */}
            <div className="rounded-lg border hairline bg-[#11141c] p-3 text-[12px] flex flex-col gap-2">
              <div className="flex items-center justify-between gap-2">
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
              <div className="text-[13px] font-medium text-[#eef0f5] leading-snug">
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
              <button
                type="button"
                onClick={() => setWorkbenchTab("terrain")}
                className="mt-1 w-full h-7 rounded bg-[#1a1e28] border hairline text-[11.5px] text-[#eef0f5] hover:border-[#4c8bf5]/60 transition-colors duration-150"
              >
                {lang === "tr" ? "3B arazi ve uyduyu incele" : "Inspect 3D & orbital"}
              </button>
            </div>
          </aside>

          {/* Main Stage */}
          <div className="flex-1 w-full min-w-0 flex flex-col gap-5">
            {/* Workbench View Tabs */}
            <div className="flex items-center justify-between gap-3 flex-wrap pb-3 border-b hairline">
              <div className="flex flex-wrap gap-1 rounded-xl p-1 bg-[#11141c] border hairline w-full sm:w-auto">
                {WORKBENCH_TABS.map((tb) => {
                  const Icon =
                    tb.id === "overview"
                      ? Compass
                      : tb.id === "terrain"
                        ? Mountain
                        : tb.id === "validation"
                          ? ShieldCheck
                          : BookOpen;
                  return (
                    <button
                      key={tb.id}
                      type="button"
                      onClick={() => setWorkbenchTab(tb.id)}
                      className={`h-9 px-3 rounded-lg text-[12.5px] sm:text-[13px] font-medium inline-flex items-center gap-1.5 transition-colors duration-150 ${
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
                {moonName} · {poolRows.length} / {data.earth_sites.length}{" "}
                {lang === "tr" ? "saha" : "sites"}
                {isCustomWeights && (
                  <span className="ml-2 px-2 py-0.5 rounded bg-[#4c8bf5]/15 text-[#4c8bf5]">
                    {lang === "tr" ? "Özel ağırlık" : "Custom"}
                  </span>
                )}
              </div>
            </div>

            {/* VIEW 1: REAL GIS MAP + SCORE BARS + CLEAN 2-TAB SUBSWITCH + BIDIRECTIONAL TABLE */}
            {workbenchTab === "overview" && (
              <div className="flex flex-col gap-5">
                <details
                  open={guideOpen}
                  onToggle={(e) => setGuideOpen((e.target as HTMLDetailsElement).open)}
                  className="rounded-xl border hairline bg-[#11141c] px-5 py-3"
                >
                  <summary className="cursor-pointer text-[13.5px] font-medium text-[#eef0f5] flex items-center gap-2 select-none">
                    <Compass className="w-4 h-4 text-[#4c8bf5]" />
                    {copy.guideTitle}
                  </summary>
                  <ol className="mt-2.5 space-y-1.5 text-[12.5px] text-[#a3a9b8] list-decimal list-inside">
                    <li>{copy.guideStep1}</li>
                    <li>{copy.guideStep2}</li>
                    <li>{copy.guideStep3}</li>
                  </ol>
                </details>
                <RealMapLeaflet
                  sites={filteredSitesForMap}
                  scoresById={scoresById}
                  selectedId={selectedEarth.site_id}
                  onSelect={(sid) => setSelectedEarthId(sid)}
                  onInspect3D={(sid) => {
                    setSelectedEarthId(sid);
                    setWorkbenchTab("terrain");
                  }}
                  metricMode={chartMode}
                  lang={lang}
                  zoomTurkeyLabel={copy.mapZoomTurkey}
                  zoomGlobalLabel={copy.mapZoomGlobal}
                />

                <ScoreBarsChart
                  rows={poolRows}
                  sitesById={sitesById}
                  selectedId={selectedEarth.site_id}
                  onSelect={(sid) => setSelectedEarthId(sid)}
                  mode={chartMode}
                  onModeChange={setChartMode}
                  maxBars={maxBars}
                  onMaxBarsChange={setMaxBars}
                  title={copy.chartTitle}
                  note={copy.chartNote}
                  modeLabels={{
                    overall: copy.modeOverall,
                    mobility: copy.modeMobility,
                    surface: copy.modeSurface,
                  }}
                  lang={lang}
                />

                {/* Paired Radar Comparison & Physical Difference Gaps */}
                <div id="radar-gaps-panel" className="grid grid-cols-1 xl:grid-cols-12 gap-5">
                  <div className="xl:col-span-5">
                    <RadarCompareSvg
                      moon={activeMoon}
                      earth={selectedEarth}
                      allMoon={data.moon_refs}
                      allEarth={data.earth_sites}
                      scoreRow={selectedScore}
                      lang={lang}
                    />
                  </div>

                  <div className="xl:col-span-7 rounded-xl border hairline bg-[#11141c] p-5 flex flex-col justify-between">
                    <div className="flex items-center justify-between gap-3 flex-wrap mb-3">
                      <h3 className="text-[15px] font-medium text-[#eef0f5]">
                        {copy.gapsTitle}: {moonName} ↔ {selectedEarth.short}
                      </h3>
                      <span className="text-[11.5px] font-mono text-[#7a8296]">
                        r = 1000 m · {activeMoon.dem_src} vs {selectedEarth.dem_src}
                      </span>
                    </div>

                    <div className="overflow-x-auto">
                      <table className="w-full text-[13px] border-collapse">
                        <thead>
                          <tr className="border-b hairline text-[#7a8296] text-left">
                            <th className="py-2 pr-3 font-normal">
                              {lang === "tr" ? "Ölçüt" : "Criterion"}
                            </th>
                            <th className="py-2 pr-3 font-normal text-right">
                              {lang === "tr" ? "Ay" : "Moon"}
                            </th>
                            <th className="py-2 pr-3 font-normal text-right">
                              {lang === "tr" ? "Dünya" : "Earth"}
                            </th>
                            <th className="py-2 pr-3 font-normal text-right">
                              {lang === "tr" ? "Fark" : "Diff"}
                            </th>
                            <th className="py-2 pr-3 font-normal text-right">
                              {lang === "tr" ? "Standart fark (z)" : "Std (z)"}
                            </th>
                            <th className="py-2 font-normal text-right">
                              {copy.gapsShareCol}
                            </th>
                          </tr>
                        </thead>
                        <tbody className="font-mono tabular">
                          {selectedGaps.map((g) => {
                            const fn = FEATURE_NAMES[g.feature];
                            const absZ = Math.abs(g.z_diff ?? 0);
                            // Contribution of this feature to its axis distance:
                            // D = sqrt(mean(z_i^2)), so share_i = z_i^2 / sum_j z_j^2.
                            const axisRows = selectedGaps.filter(
                              (r) => r.axis === g.axis && r.z_diff !== null
                            );
                            const zSumSq = axisRows.reduce(
                              (acc, r) => acc + (r.z_diff ?? 0) ** 2,
                              0
                            );
                            const share =
                              zSumSq > 0 && g.z_diff !== null
                                ? ((g.z_diff ?? 0) ** 2 / zSumSq) * 100
                                : null;
                            return (
                              <tr key={g.feature} className="border-b hairline last:border-b-0">
                                <td className="py-2.5 pr-3 font-sans text-[#eef0f5]">
                                  {fn ? fn[lang] : g.feature}
                                  <span className="text-[#7a8296] text-[11px] ml-1.5 font-mono">
                                    ({fn?.unit ?? ""})
                                  </span>
                                </td>
                                <td className="py-2.5 pr-3 text-right text-[#a3a9b8]">
                                  {g.moon_val !== null ? g.moon_val.toFixed(2) : "NaN"}
                                </td>
                                <td className="py-2.5 pr-3 text-right text-[#a3a9b8]">
                                  {g.earth_val !== null ? g.earth_val.toFixed(2) : "NaN"}
                                </td>
                                <td className="py-2.5 pr-3 text-right text-[#eef0f5]">
                                  {g.diff !== null ? g.diff.toFixed(2) : "—"}
                                </td>
                                <td
                                  className={`py-2.5 pr-3 text-right ${
                                    absZ < 0.5
                                      ? "text-[#4cc38a]"
                                      : absZ > 1.3
                                        ? "text-[#e5484d]"
                                        : "text-[#a3a9b8]"
                                  }`}
                                >
                                  {g.z_diff !== null ? g.z_diff.toFixed(2) : "—"}
                                </td>
                                <td className="py-2.5 text-right">
                                  {share !== null && (
                                    <div className="flex items-center justify-end gap-2">
                                      <div className="w-16 h-1.5 rounded-full bg-[#1a1e28] overflow-hidden">
                                        <div
                                          className="h-full rounded-full bg-[#4c8bf5]"
                                          style={{ width: `${Math.min(100, share)}%` }}
                                        />
                                      </div>
                                      <span className="text-[#a3a9b8] text-[11.5px] w-9">
                                        {share.toFixed(0)}%
                                      </span>
                                      <span className="text-[#7a8296] text-[10.5px] w-14 text-left font-sans">
                                        {g.axis === "mobility"
                                          ? lang === "tr" ? "Mobilite" : "Mobility"
                                          : lang === "tr" ? "Yüzey" : "Surface"}
                                      </span>
                                    </div>
                                  )}
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                      <p className="text-[11.5px] text-[#7a8296] mt-2">
                        {copy.gapsShareHint}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Full Interactive Table with Bidirectional Asc/Desc Column Sorting */}
                <div className="rounded-xl border hairline bg-[#11141c] overflow-hidden">
                  <div className="px-5 py-3.5 border-b hairline flex items-center justify-between flex-wrap gap-3">
                    <div>
                      <h3 className="text-[14px] font-medium text-[#eef0f5]">
                        {lang === "tr" ? "Tüm sahalar tablosu" : "All sites score table"}
                      </h3>
                      <p className="text-[11.5px] text-[#7a8296]">
                        {lang === "tr"
                          ? "Artan / azalan sıralamak için herhangi bir sütun başlığına tıklayın"
                          : "Click any column header to sort ascending or descending"}
                      </p>
                    </div>
                    <div className="flex items-center gap-1.5 flex-wrap text-[12px]">
                      {(
                        [
                          ["rank", "asc", lang === "tr" ? "Genel sıra" : "Rank"],
                          ["mob", "desc", lang === "tr" ? "Mobilite" : "Mobility"],
                          ["surf", "desc", lang === "tr" ? "Yüzey" : "Surface"],
                          ["slope_mean", "desc", lang === "tr" ? "Eğim" : "Slope"],
                        ] as [TableSortCol, SortDir, string][]
                      ).map(([col, defDir, label]) => (
                        <button
                          key={col}
                          type="button"
                          onClick={() => handleSortClick(col, defDir)}
                          className={`px-2.5 py-1 rounded border transition-colors duration-150 inline-flex items-center ${
                            sortCol === col
                              ? "active-highlight border-[#4c8bf5]/45 text-[#eef0f5]"
                              : "hairline text-[#7a8296] hover:text-[#eef0f5]"
                          }`}
                        >
                          <span>{label}</span>
                          <SortIndicator active={sortCol === col} dir={sortDir} />
                        </button>
                      ))}
                      <button
                        type="button"
                        onClick={() => setSortDir((d) => (d === "asc" ? "desc" : "asc"))}
                        className="px-2.5 py-1 rounded border hairline bg-[#07080d] text-[#a3a9b8] hover:text-[#eef0f5] font-mono text-[11px]"
                      >
                        {sortDir === "asc"
                          ? lang === "tr"
                            ? "↑ Artan"
                            : "↑ Asc"
                          : lang === "tr"
                            ? "↓ Azalan"
                            : "↓ Desc"}
                      </button>
                    </div>
                  </div>
                  <div className="max-h-[440px] overflow-auto">
                    <table className="w-full text-[13px] border-collapse">
                      <thead className="sticky top-0 bg-[#07080d] z-10">
                        <tr className="border-b hairline text-[#7a8296] text-left select-none">
                          <th
                            onClick={() => handleSortClick("rank", "asc")}
                            className="py-2.5 px-4 font-normal cursor-pointer hover:text-[#eef0f5] whitespace-nowrap"
                          >
                            # <SortIndicator active={sortCol === "rank"} dir={sortDir} />
                          </th>
                          <th
                            onClick={() => handleSortClick("name", "asc")}
                            className="py-2.5 px-4 font-normal cursor-pointer hover:text-[#eef0f5] whitespace-nowrap"
                          >
                            {lang === "tr" ? "Dünya sahası" : "Earth site"}
                            <SortIndicator active={sortCol === "name"} dir={sortDir} />
                          </th>
                          <th
                            onClick={() => handleSortClick("score", "desc")}
                            className="py-2.5 px-4 font-normal text-right cursor-pointer hover:text-[#eef0f5] whitespace-nowrap"
                          >
                            {lang === "tr" ? "Genel (P5–P95)" : "Score (P5–P95)"}
                            <SortIndicator active={sortCol === "score"} dir={sortDir} />
                          </th>
                          <th
                            onClick={() => handleSortClick("mob", "desc")}
                            className="py-2.5 px-4 font-normal text-right cursor-pointer hover:text-[#eef0f5] whitespace-nowrap"
                          >
                            {lang === "tr" ? "Mobilite" : "Mobility"}
                            <SortIndicator active={sortCol === "mob"} dir={sortDir} />
                          </th>
                          <th
                            onClick={() => handleSortClick("surf", "desc")}
                            className="py-2.5 px-4 font-normal text-right cursor-pointer hover:text-[#eef0f5] whitespace-nowrap"
                          >
                            {lang === "tr" ? "Yüzey" : "Surface"}
                            <SortIndicator active={sortCol === "surf"} dir={sortDir} />
                          </th>
                          <th
                            onClick={() => handleSortClick("slope_mean", "desc")}
                            className="py-2.5 px-4 font-normal text-right cursor-pointer hover:text-[#eef0f5] whitespace-nowrap"
                          >
                            {lang === "tr" ? "Eğim °" : "Slope °"}
                            <SortIndicator active={sortCol === "slope_mean"} dir={sortDir} />
                          </th>
                          <th
                            onClick={() => handleSortClick("albedo", "desc")}
                            className="py-2.5 px-4 font-normal text-right cursor-pointer hover:text-[#eef0f5] whitespace-nowrap"
                          >
                            Albedo
                            <SortIndicator active={sortCol === "albedo"} dir={sortDir} />
                          </th>
                          <th
                            onClick={() => handleSortClick("lithology", "asc")}
                            className="py-2.5 px-4 font-normal cursor-pointer hover:text-[#eef0f5] whitespace-nowrap"
                          >
                            {lang === "tr" ? "Litoloji" : "Lithology"}
                            <SortIndicator active={sortCol === "lithology"} dir={sortDir} />
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {tableRows.map((r) => {
                          const s = sitesById[r.site_id];
                          if (!s) return null;
                          const isSel = s.site_id === selectedEarth.site_id;
                          return (
                            <tr
                              key={r.site_id}
                              onClick={() => setSelectedEarthId(s.site_id)}
                              className={`border-b hairline cursor-pointer transition-colors duration-150 ${
                                isSel ? "bg-[#4c8bf5]/14" : "hover:bg-[#1a1e28]/60"
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
                                {s.slope_mean.toFixed(1)}°
                              </td>
                              <td className="py-2.5 px-4 text-right font-mono tabular text-[#a3a9b8] whitespace-nowrap">
                                {s.albedo.toFixed(3)}
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

            {/* VIEW 2: UPGRADED INTERACTIVE 3D DEM + PROFILES + SATELLITE IMAGERY */}
            {workbenchTab === "terrain" && (
              <div className="flex flex-col gap-5">
                <div className="rounded-xl border hairline bg-[#11141c] p-4 flex flex-col gap-3.5">
                  <div className="flex items-center justify-between flex-wrap gap-3">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-[12px] text-[#7a8296]">
                        {lang === "tr" ? "3B yüzey görünümü:" : "3D surface layer:"}
                      </span>
                      <div className="inline-flex rounded-lg p-0.5 bg-[#07080d] border hairline text-[12px]">
                        {(
                          [
                            ["elevation", lang === "tr" ? "Yükseklik" : "Elevation"],
                            ["slope", lang === "tr" ? "Eğim tehlikesi" : "Slope hazard"],
                            ["contour", lang === "tr" ? "Kontur izleri" : "Contours"],
                          ] as [TerrainColorMode, string][]
                        ).map(([cm, lbl]) => (
                          <button
                            key={cm}
                            type="button"
                            onClick={() => setColorMode3d(cm)}
                            className={`px-3 py-1 rounded-md transition-colors duration-150 ${
                              colorMode3d === cm
                                ? "active-highlight text-[#eef0f5]"
                                : "text-[#7a8296] hover:text-[#eef0f5]"
                            }`}
                          >
                            {lbl}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 flex-wrap text-[12px]">
                      <button
                        type="button"
                        onClick={() => setAutoRotate3d((v) => !v)}
                        className={`px-2.5 py-1 rounded-lg border transition-colors duration-150 ${
                          autoRotate3d
                            ? "border-[#4cc38a]/50 bg-[#4cc38a]/15 text-[#4cc38a]"
                            : "hairline bg-[#07080d] text-[#a3a9b8] hover:text-[#eef0f5]"
                        }`}
                      >
                        {autoRotate3d
                          ? lang === "tr"
                            ? "Dönüşü durdur"
                            : "Stop orbit"
                          : lang === "tr"
                            ? "Otomatik döndür"
                            : "Auto orbit"}
                      </button>

                      {[0, 42, 135, 225].map((ang) => (
                        <button
                          key={ang}
                          type="button"
                          onClick={() => {
                            setAutoRotate3d(false);
                            setAzimuthDeg(ang);
                          }}
                          className={`px-2 py-1 rounded border font-mono ${
                            Math.round(azimuthDeg) === ang
                              ? "active-highlight border-[#4c8bf5]/50 text-[#eef0f5]"
                              : "hairline text-[#7a8296] hover:text-[#eef0f5]"
                          }`}
                        >
                          {ang}°
                        </button>
                      ))}

                      <button
                        type="button"
                        onClick={() => {
                          setAutoRotate3d(false);
                          setAzimuthDeg(42);
                          setPitchDeg(34);
                          setZoom3d(1.05);
                          setExaggeration(2.0);
                        }}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded border hairline bg-[#07080d] text-[#a3a9b8] hover:text-[#eef0f5]"
                      >
                        <RotateCcw className="w-3 h-3" strokeWidth={1.6} />
                        <span>{lang === "tr" ? "Sıfırla" : "Reset"}</span>
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-2 border-t hairline">
                    <label className="flex flex-col gap-1 text-[12px] text-[#a3a9b8]">
                      <div className="flex justify-between">
                        <span>{copy.exaggeration}</span>
                        <span className="font-mono tabular text-[#eef0f5]">{exaggeration.toFixed(1)}x</span>
                      </div>
                      <input
                        type="range"
                        min="1"
                        max="3.5"
                        step="0.25"
                        value={exaggeration}
                        onChange={(e) => setExaggeration(parseFloat(e.target.value))}
                        className="w-full accent-[#4c8bf5]"
                      />
                    </label>

                    <label className="flex flex-col gap-1 text-[12px] text-[#a3a9b8]">
                      <div className="flex justify-between">
                        <span>{copy.azimuth}</span>
                        <span className="font-mono tabular text-[#eef0f5]">{Math.round(azimuthDeg)}°</span>
                      </div>
                      <input
                        type="range"
                        min="0"
                        max="359"
                        step="1"
                        value={Math.round(azimuthDeg)}
                        onChange={(e) => {
                          setAutoRotate3d(false);
                          setAzimuthDeg(parseInt(e.target.value, 10));
                        }}
                        className="w-full accent-[#4c8bf5]"
                      />
                    </label>

                    <label className="flex flex-col gap-1 text-[12px] text-[#a3a9b8]">
                      <div className="flex justify-between">
                        <span>{copy.pitch}</span>
                        <span className="font-mono tabular text-[#eef0f5]">{pitchDeg}°</span>
                      </div>
                      <input
                        type="range"
                        min="16"
                        max="72"
                        step="1"
                        value={pitchDeg}
                        onChange={(e) => setPitchDeg(parseInt(e.target.value, 10))}
                        className="w-full accent-[#4c8bf5]"
                      />
                    </label>

                    <label className="flex flex-col gap-1 text-[12px] text-[#a3a9b8]">
                      <div className="flex justify-between">
                        <span>{copy.zoom}</span>
                        <span className="font-mono tabular text-[#eef0f5]">{zoom3d.toFixed(2)}x</span>
                      </div>
                      <input
                        type="range"
                        min="0.75"
                        max="1.75"
                        step="0.05"
                        value={zoom3d}
                        onChange={(e) => setZoom3d(parseFloat(e.target.value))}
                        className="w-full accent-[#4c8bf5]"
                      />
                    </label>
                  </div>
                </div>

                <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                  <Terrain3DCanvas
                    tile={dem?.[activeMoon.site_id]}
                    title={copy.demTitleMoon}
                    subtitle={`${moonName} · ${activeMoon.dem_src}`}
                    accentColor="#4c8bf5"
                    azimuthDeg={azimuthDeg}
                    pitchDeg={pitchDeg}
                    zoom={zoom3d}
                    exaggeration={exaggeration}
                    colorMode={colorMode3d}
                    lang={lang}
                    onAzimuthChange={(v) => {
                      setAutoRotate3d(false);
                      setAzimuthDeg(v);
                    }}
                    onPitchChange={setPitchDeg}
                    onZoomChange={setZoom3d}
                  />

                  <Terrain3DCanvas
                    tile={dem?.[selectedEarth.site_id]}
                    title={copy.demTitleEarth}
                    subtitle={`${selectedEarth.short} · ${selectedEarth.dem_src}`}
                    accentColor="#4cc38a"
                    azimuthDeg={azimuthDeg}
                    pitchDeg={pitchDeg}
                    zoom={zoom3d}
                    exaggeration={exaggeration}
                    colorMode={colorMode3d}
                    lang={lang}
                    onAzimuthChange={(v) => {
                      setAutoRotate3d(false);
                      setAzimuthDeg(v);
                    }}
                    onPitchChange={setPitchDeg}
                    onZoomChange={setZoom3d}
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

            {/* VIEW 3: CHALLENGES, SOLUTION, RANK DIAGNOSTIC & POSITIVE ACHIEVEMENTS */}
            {workbenchTab === "validation" && (
              <div className="flex flex-col gap-5">
                {/* Challenge Problem + Real Difficulties + Our Engineering Solution */}
                <div className="rounded-xl border hairline bg-[#11141c] p-5">
                  <h3 className="text-[16px] font-medium text-[#eef0f5] mb-1">
                    {copy.whySplitTitle}
                  </h3>
                  <p className="text-[13px] text-[#7a8296] mb-4 leading-relaxed">
                    {copy.validationIntro}
                  </p>

                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                    {CHALLENGE_STORY[lang].map((card, i) => (
                      <div
                        key={card.tag}
                        className="rounded-lg border hairline bg-[#07080d] p-4 flex flex-col gap-2.5"
                      >
                        <div
                          className={`text-[11px] font-mono ${
                            i === 0
                              ? "text-[#4c8bf5]"
                              : i === 1
                                ? "text-[#d9a441]"
                                : "text-[#4cc38a]"
                          }`}
                        >
                          {card.tag}
                        </div>
                        <h4 className="text-[14px] font-medium text-[#eef0f5] leading-snug">
                          {card.title}
                        </h4>
                        <ul className="space-y-2 text-[12.5px] leading-[1.55] text-[#a3a9b8]">
                          {card.points.map((pt, j) => (
                            <li key={j} className="flex gap-2">
                              <span className="text-[#4c8bf5] font-mono shrink-0">-</span>
                              <span>{pt}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 10-Site DOI Rank Diagnostic Table (Asc / Desc Sortable) */}
                <div className="rounded-xl border hairline bg-[#11141c] overflow-hidden">
                  <div className="px-5 py-3.5 border-b hairline flex items-center justify-between flex-wrap gap-2">
                    <h3 className="text-[14px] font-medium text-[#eef0f5]">
                      {lang === "tr"
                        ? "Bilinen 10 doğrulama sahası sıra tanısı"
                        : "10 established validation sites rank diagnostic"}
                    </h3>
                    <span className="text-[12px] font-mono text-[#7a8296]">{moonName}</span>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-[13px] border-collapse">
                      <thead>
                        <tr className="border-b hairline text-[#7a8296] text-left bg-[#07080d] select-none">
                          <th
                            onClick={() => handleValSortClick("name")}
                            className="py-2.5 px-4 font-normal cursor-pointer hover:text-[#eef0f5] whitespace-nowrap"
                          >
                            {lang === "tr" ? "Doğrulama sahası" : "Validation site"}
                            <SortIndicator active={valSortCol === "name"} dir={valSortDir} />
                          </th>
                          <th
                            onClick={() => handleValSortClick("mob_rank")}
                            className="py-2.5 px-4 font-normal text-right cursor-pointer hover:text-[#eef0f5] whitespace-nowrap"
                          >
                            {lang === "tr" ? "Mobilite #" : "Mobility #"}
                            <SortIndicator active={valSortCol === "mob_rank"} dir={valSortDir} />
                          </th>
                          <th
                            onClick={() => handleValSortClick("rank")}
                            className="py-2.5 px-4 font-normal text-right cursor-pointer hover:text-[#eef0f5] whitespace-nowrap"
                          >
                            {lang === "tr" ? "Genel #" : "Overall #"}
                            <SortIndicator active={valSortCol === "rank"} dir={valSortDir} />
                          </th>
                          <th
                            onClick={() => handleValSortClick("surf_rank")}
                            className="py-2.5 px-4 font-normal text-right cursor-pointer hover:text-[#eef0f5] whitespace-nowrap"
                          >
                            {lang === "tr" ? "Yüzey #" : "Surface #"}
                            <SortIndicator active={valSortCol === "surf_rank"} dir={valSortDir} />
                          </th>
                          <th
                            onClick={() => handleValSortClick("lithology")}
                            className="py-2.5 px-4 font-normal cursor-pointer hover:text-[#eef0f5] whitespace-nowrap"
                          >
                            {lang === "tr" ? "Toprak / Kayaç" : "Rock / Soil"}
                            <SortIndicator active={valSortCol === "lithology"} dir={valSortDir} />
                          </th>
                          <th className="py-2.5 px-4 font-normal text-right whitespace-nowrap">
                            {lang === "tr" ? "Enlem, Boylam" : "Lat, Lon"}
                          </th>
                          <th
                            onClick={() => handleValSortClick("slope_mean", "desc")}
                            className="py-2.5 px-4 font-normal text-right cursor-pointer hover:text-[#eef0f5] whitespace-nowrap"
                          >
                            {lang === "tr" ? "Eğim / Albedo" : "Slope / Albedo"}
                            <SortIndicator active={valSortCol === "slope_mean"} dir={valSortDir} />
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
                                #{r.mob_rank}
                              </td>
                              <td className="py-2.5 px-4 text-right font-mono tabular text-[#a3a9b8]">
                                #{r.rank}
                              </td>
                              <td className="py-2.5 px-4 text-right font-mono tabular text-[#a3a9b8]">
                                #{r.surf_rank}
                              </td>
                              <td className="py-2.5 px-4 text-[#a3a9b8]">
                                {LITHOLOGY_NAMES[s.lithology]?.[lang] ?? s.lithology}
                              </td>
                              <td className="py-2.5 px-4 text-right font-mono tabular text-[12px] text-[#a3a9b8] whitespace-nowrap">
                                {s.lat.toFixed(2)}°, {s.lon.toFixed(2)}°
                              </td>
                              <td className="py-2.5 px-4 text-right font-mono tabular text-[12px] text-[#a3a9b8] whitespace-nowrap">
                                {s.slope_mean.toFixed(1)}° / {s.albedo.toFixed(3)}
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

                {/* Concrete Interactive Examples with Clickable "bkz." Links to Live Solutions */}
                <div className="rounded-xl border hairline bg-[#11141c] p-5">
                  <div className="flex items-center gap-2 mb-4">
                    <ShieldCheck className="w-4 h-4 text-[#4cc38a]" strokeWidth={1.6} />
                    <h3 className="text-[15px] font-medium text-[#eef0f5]">{copy.limitsTitle}</h3>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {SOLUTION_EXAMPLES[lang].map((card) => (
                      <div
                        key={card.action}
                        className="rounded-lg border hairline bg-[#07080d] p-4 flex flex-col justify-between gap-3"
                      >
                        <div>
                          <div className="text-[11px] font-mono text-[#4cc38a] mb-1">
                            {card.tag}
                          </div>
                          <div className="text-[14px] font-medium text-[#eef0f5] leading-snug">
                            {card.title}
                          </div>
                          <p className="text-[12.5px] text-[#a3a9b8] mt-1.5 leading-relaxed">
                            {card.example}
                          </p>
                        </div>
                        <div className="pt-2.5 border-t hairline">
                          <button
                            type="button"
                            onClick={() => jumpToExample(card.action)}
                            className="inline-flex items-center gap-1.5 text-[12.5px] font-medium text-[#4c8bf5] hover:text-[#7db0ff] transition-colors duration-150"
                          >
                            <span>{card.linkLabel}</span>
                            <ArrowRight className="w-3.5 h-3.5" strokeWidth={1.8} />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>

                  <p className="mt-4 pt-3 border-t hairline text-[12px] text-[#7a8296]">
                    {lang === "tr"
                      ? "Fiziksel sınır notu: Düşük yerçekimi (1/6 g), vakum, radyasyon ve elektrostatik toz hiçbir Dünya sahasında doğal olarak bulunmadığı için bu koşullar laboratuvar testleriyle tamamlanır."
                      : "Physical boundary disclosure: Low gravity (1/6 g), vacuum, radiation and electrostatic dust cannot be reproduced naturally on Earth and are completed in laboratory test chambers."}
                  </p>
                </div>
              </div>
            )}

            {/* VIEW 4: CLEAN FIGURES & ACADEMIC BIBLIOGRAPHY (ZERO PERSONAL CREDITS) */}
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

                {/* Cleanly Formatted Lunar & Earth Data Sources + DOIs */}
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                  <div className="rounded-xl border hairline bg-[#11141c] p-5">
                    <h3 className="text-[14.5px] font-medium text-[#eef0f5] mb-3.5">
                      {copy.bibMoonTitle}
                    </h3>
                    <div className="space-y-2.5">
                      {(lang === "tr" ? data.bibliography.moon_tr : data.bibliography.moon_en).map(
                        (item, idx) => {
                          const { head, body } = splitBibItem(item);
                          const doiUrl = extractDoiUrl(item);
                          return (
                            <div
                              key={idx}
                              className="rounded-lg bg-[#07080d] border hairline p-3 text-[12px] leading-relaxed"
                            >
                              {head && (
                                <div className="font-mono text-[11px] text-[#4c8bf5] mb-1">
                                  {head}
                                </div>
                              )}
                              <div className="text-[#c7cddb]">{body}</div>
                              {doiUrl && (
                                <a
                                  href={doiUrl}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="mt-1.5 inline-flex items-center gap-1 text-[11px] font-mono text-[#4cc38a] hover:underline"
                                >
                                  <span>{doiUrl}</span>
                                  <ExternalLink className="w-3 h-3" strokeWidth={1.5} />
                                </a>
                              )}
                            </div>
                          );
                        }
                      )}
                    </div>
                  </div>

                  <div className="rounded-xl border hairline bg-[#11141c] p-5">
                    <h3 className="text-[14.5px] font-medium text-[#eef0f5] mb-3.5">
                      {copy.bibEarthTitle}
                    </h3>
                    <div className="space-y-2.5">
                      {(lang === "tr" ? data.bibliography.earth_tr : data.bibliography.earth_en).map(
                        (item, idx) => {
                          const { head, body } = splitBibItem(item);
                          const doiUrl = extractDoiUrl(item);
                          return (
                            <div
                              key={idx}
                              className="rounded-lg bg-[#07080d] border hairline p-3 text-[12px] leading-relaxed"
                            >
                              {head && (
                                <div className="font-mono text-[11px] text-[#4cc38a] mb-1">
                                  {head}
                                </div>
                              )}
                              <div className="text-[#c7cddb]">{body}</div>
                              {doiUrl && (
                                <a
                                  href={doiUrl}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="mt-1.5 inline-flex items-center gap-1 text-[11px] font-mono text-[#4c8bf5] hover:underline"
                                >
                                  <span>{doiUrl}</span>
                                  <ExternalLink className="w-3 h-3" strokeWidth={1.5} />
                                </a>
                              )}
                            </div>
                          );
                        }
                      )}
                    </div>
                  </div>
                </div>

                {/* 40-Site Searchable Coordinate, Sensor & Citation Ledger */}
                <div className="rounded-xl border hairline bg-[#11141c] overflow-hidden">
                  <div className="px-5 py-3.5 border-b hairline flex items-center justify-between flex-wrap gap-3">
                    <div>
                      <h3 className="text-[14px] font-medium text-[#eef0f5]">{copy.bibTableTitle}</h3>
                      <p className="text-[11.5px] text-[#7a8296] mt-0.5">
                        {lang === "tr"
                          ? `${filteredBibSites.length} / ${data.earth_sites.length} saha kaydı listeleniyor`
                          : `Showing ${filteredBibSites.length} / ${data.earth_sites.length} site records`}
                      </p>
                    </div>
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
                  <div className="max-h-[420px] overflow-auto">
                    <table className="w-full text-[12px] border-collapse">
                      <thead className="sticky top-0 bg-[#07080d]">
                        <tr className="border-b hairline text-[#7a8296] text-left">
                          <th className="py-2.5 px-4 font-normal">
                            {lang === "tr" ? "Saha" : "Site"}
                          </th>
                          <th className="py-2.5 px-4 font-normal">
                            {lang === "tr" ? "Koordinat / Sensör" : "Coords / Sensor"}
                          </th>
                          <th className="py-2.5 px-4 font-normal">
                            {lang === "tr" ? "Akademik kaynak" : "Citation"}
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredBibSites.map((s) => {
                          const doiUrl = s.validation?.source_url || extractDoiUrl(s.citation);
                          return (
                            <tr
                              key={s.site_id}
                              onClick={() => {
                                setSelectedEarthId(s.site_id);
                                setWorkbenchTab("overview");
                              }}
                              className="border-b hairline last:border-b-0 hover:bg-[#1a1e28]/60 cursor-pointer"
                            >
                              <td className="py-2.5 px-4 text-[#eef0f5] font-medium align-top">
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
                                  <span>{s.short}</span>
                                </div>
                                <div className="font-mono text-[11px] text-[#7a8296] mt-0.5 pl-4">
                                  {s.site_id}
                                </div>
                              </td>
                              <td className="py-2.5 px-4 font-mono tabular text-[#a3a9b8] align-top whitespace-nowrap">
                                <div>
                                  {s.lat.toFixed(4)}°, {s.lon.toFixed(4)}°
                                </div>
                                <div className="text-[#7a8296]">
                                  {s.dem_src} · {s.albedo_src}
                                </div>
                              </td>
                              <td className="py-2.5 px-4 text-[#a3a9b8] leading-relaxed align-top">
                                <div>{s.citation}</div>
                                {doiUrl && (
                                  <a
                                    href={doiUrl}
                                    target="_blank"
                                    rel="noreferrer"
                                    onClick={(e) => e.stopPropagation()}
                                    className="mt-1 inline-flex items-center gap-1 text-[11px] font-mono text-[#4c8bf5] hover:underline"
                                  >
                                    <span>{s.validation?.source_label || doiUrl}</span>
                                    <ExternalLink className="w-3 h-3" strokeWidth={1.5} />
                                  </a>
                                )}
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
          </div>
        </div>
      </section>

      {/* Clean Technical Footer */}
      <footer className="border-t hairline bg-[#07080d] mt-10">
        <div className="max-w-[1400px] mx-auto px-4 sm:px-6 py-5 flex flex-col sm:flex-row items-center justify-between gap-3 text-[12px] text-[#7a8296]">
          <div>
            Endülüs · NASA Space Apps 2026 · {data.meta.moon_count} Ay bölgesi × {data.meta.earth_count} Dünya sahası
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
