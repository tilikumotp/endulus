import { useEffect, useMemo, useRef, useState } from "react";
import L from "leaflet";
import { feature } from "topojson-client";
import type { GeometryCollection, Topology } from "topojson-specification";
import type { EarthSite, Lang, SiteScoreRow } from "../types";

export type MapBasemapMode = "dark" | "satellite";
export type MapMetricMode = "overall" | "mobility" | "surface";

interface Props {
  sites: EarthSite[];
  scoresById: Record<string, SiteScoreRow>;
  selectedId: string;
  onSelect: (siteId: string) => void;
  onInspect3D?: (siteId: string) => void;
  metricMode: MapMetricMode;
  lang: Lang;
  zoomTurkeyLabel: string;
  zoomGlobalLabel: string;
}

function scoreFill(score: number): string {
  if (score >= 0.62) return "#4cc38a";
  if (score >= 0.45) return "#4c8bf5";
  if (score >= 0.3) return "#d9a441";
  return "#e5484d";
}

function metricValue(row: SiteScoreRow | undefined, mode: MapMetricMode): { val: number; rank: number } {
  if (!row) return { val: 0, rank: 99 };
  if (mode === "mobility") return { val: row.mob, rank: row.mob_rank };
  if (mode === "surface") return { val: row.surf, rank: row.surf_rank };
  return { val: row.score, rank: row.rank };
}

export function RealMapLeaflet({
  sites,
  scoresById,
  selectedId,
  onSelect,
  onInspect3D,
  metricMode,
  lang,
  zoomTurkeyLabel,
  zoomGlobalLabel,
}: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const tileLayerRef = useRef<L.TileLayer | null>(null);
  const labelLayerRef = useRef<L.TileLayer | null>(null);
  const markerGroupRef = useRef<L.LayerGroup | null>(null);
  const geoLayerRef = useRef<L.GeoJSON | null>(null);

  const onSelectRef = useRef(onSelect);
  const onInspect3DRef = useRef(onInspect3D);
  onSelectRef.current = onSelect;
  onInspect3DRef.current = onInspect3D;

  const [basemap, setBasemap] = useState<MapBasemapMode>("dark");
  const [viewMode, setViewMode] = useState<"global" | "turkey" | "site">("global");
  const [worldTopo, setWorldTopo] = useState<Topology | null>(null);

  const selectedSite = useMemo(
    () => sites.find((s) => s.site_id === selectedId) ?? sites[0],
    [sites, selectedId]
  );

  // Load offline GeoJSON landmasses from local TopoJSON so continents remain visible offline
  useEffect(() => {
    let active = true;
    fetch("/data/world-50m.json")
      .then((r) => r.json() as Promise<Topology>)
      .then((topo) => {
        if (active) setWorldTopo(topo);
      })
      .catch(() => {
        // Live raster tiles continue working normally even if TopoJSON fails
      });
    return () => {
      active = false;
    };
  }, []);

  // Initialize Leaflet map once
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = L.map(containerRef.current, {
      center: [24, 15],
      zoom: 2,
      minZoom: 1.5,
      maxZoom: 16,
      worldCopyJump: true,
      zoomControl: true,
      attributionControl: false,
    });

    L.control.attribution({ prefix: false, position: "bottomright" }).addTo(map);

    const landPane = map.createPane("landBase");
    landPane.style.zIndex = "210";
    landPane.style.pointerEvents = "none";

    const labelPane = map.createPane("labelsOverlay");
    labelPane.style.zIndex = "410";
    labelPane.style.pointerEvents = "none";

    markerGroupRef.current = L.layerGroup().addTo(map);
    mapRef.current = map;

    const ro = new ResizeObserver(() => {
      map.invalidateSize();
    });
    ro.observe(containerRef.current);

    return () => {
      ro.disconnect();
      map.remove();
      mapRef.current = null;
      tileLayerRef.current = null;
      labelLayerRef.current = null;
      markerGroupRef.current = null;
      geoLayerRef.current = null;
    };
  }, []);

  // Render offline vector continents underneath raster tiles
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !worldTopo || !worldTopo.objects.countries) return;
    if (geoLayerRef.current) {
      geoLayerRef.current.remove();
      geoLayerRef.current = null;
    }

    const countries = feature(
      worldTopo,
      worldTopo.objects.countries as GeometryCollection
    );

    const layer = L.geoJSON(countries, {
      pane: "landBase",
      interactive: false,
      style: (feat) => {
        const isTr =
          String(feat?.id) === "792" ||
          String((feat?.properties as { name?: string })?.name) === "Turkey";
        return {
          fillColor: isTr ? "#182235" : "#111521",
          fillOpacity: 0.72,
          color: isTr ? "rgba(76, 139, 245, 0.38)" : "rgba(238, 240, 245, 0.14)",
          weight: isTr ? 1.1 : 0.65,
        };
      },
    }).addTo(map);

    geoLayerRef.current = layer;
  }, [worldTopo]);

  // Switch tile layers cleanly between dark GIS basemap and true satellite imagery
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    if (tileLayerRef.current) {
      map.removeLayer(tileLayerRef.current);
      tileLayerRef.current = null;
    }
    if (labelLayerRef.current) {
      map.removeLayer(labelLayerRef.current);
      labelLayerRef.current = null;
    }

    if (basemap === "dark") {
      tileLayerRef.current = L.tileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        {
          maxZoom: 16,
          attribution: "Tiles &copy; Esri &mdash; Dark Gray Canvas",
        }
      ).addTo(map);
      labelLayerRef.current = L.tileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}",
        {
          maxZoom: 16,
          opacity: 0.78,
          pane: "labelsOverlay",
        }
      ).addTo(map);
    } else {
      tileLayerRef.current = L.tileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        {
          maxZoom: 18,
          attribution: "Tiles &copy; Esri &mdash; Earthstar Geographics",
        }
      ).addTo(map);
      labelLayerRef.current = L.tileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
        {
          maxZoom: 16,
          opacity: 0.72,
          pane: "labelsOverlay",
        }
      ).addTo(map);
    }
  }, [basemap]);

  // Update interactive telemetry markers & safe DOM popups
  useEffect(() => {
    const map = mapRef.current;
    const group = markerGroupRef.current;
    if (!map || !group) return;

    group.clearLayers();

    // Sort so selected site is painted cleanly on top
    const ordered = [...sites].sort((a, b) => {
      if (a.site_id === selectedId) return 1;
      if (b.site_id === selectedId) return -1;
      const ra = metricValue(scoresById[a.site_id], metricMode).rank;
      const rb = metricValue(scoresById[b.site_id], metricMode).rank;
      return rb - ra;
    });

    for (const s of ordered) {
      const row = scoresById[s.site_id];
      const { val, rank } = metricValue(row, metricMode);
      const isSel = s.site_id === selectedId;
      const fill = scoreFill(val);

      if (s.role === "validation") {
        L.circleMarker([s.lat, s.lon], {
          radius: isSel ? 12.5 : 8.5,
          color: "#4c8bf5",
          weight: isSel ? 2.2 : 1.5,
          opacity: 0.9,
          fill: false,
          interactive: false,
        }).addTo(group);
      }

      if (isSel) {
        L.circleMarker([s.lat, s.lon], {
          radius: 10.5,
          color: "#eef0f5",
          weight: 2,
          opacity: 0.95,
          fill: false,
          interactive: false,
        }).addTo(group);
      }

      const dot = L.circleMarker([s.lat, s.lon], {
        radius: isSel ? 6.5 : viewMode === "turkey" ? 5.8 : 4.8,
        fillColor: fill,
        fillOpacity: 0.95,
        color: "#07080d",
        weight: 1.5,
      });

      const cleanShort = s.short.replace(/\s*\(TR\)$/, "");
      dot.bindTooltip(`#${rank} · ${cleanShort} (${val.toFixed(3)})`, {
        direction: "top",
        offset: [0, -8],
        className: "endulus-tooltip",
      });

      const popupEl = document.createElement("div");
      popupEl.className = "min-w-[210px]";

      const badge = document.createElement("div");
      badge.className = "text-[10.5px] font-mono mb-1";
      badge.style.color = s.role === "validation" ? "#4c8bf5" : "#4cc38a";
      badge.textContent =
        s.role === "validation"
          ? lang === "tr"
            ? `Doğrulama analogu · #${rank}`
            : `Validation analogue · #${rank}`
          : lang === "tr"
            ? `${s.is_tr ? "Türkiye adayı" : "Küresel aday"} · #${rank}`
            : `${s.is_tr ? "Turkey candidate" : "Global candidate"} · #${rank}`;

      const heading = document.createElement("div");
      heading.className = "text-[13px] font-medium text-[#eef0f5] mb-1.5";
      heading.textContent = s.short;

      const stats = document.createElement("div");
      stats.className = "text-[11.5px] font-mono text-[#a3a9b8] space-y-0.5 mb-2.5";

      const line1 = document.createElement("div");
      line1.textContent = `${lang === "tr" ? "Genel" : "Overall"} ${(row?.score ?? 0).toFixed(3)} · ${
        lang === "tr" ? "Mob" : "Mob"
      } ${(row?.mob ?? 0).toFixed(3)} · ${lang === "tr" ? "Yüzey" : "Surf"} ${(row?.surf ?? 0).toFixed(3)}`;

      const line2 = document.createElement("div");
      line2.textContent = `${lang === "tr" ? "Eğim" : "Slope"} ${s.slope_mean.toFixed(1)}° · Albedo ${s.albedo.toFixed(3)}`;

      stats.appendChild(line1);
      stats.appendChild(line2);

      const btnRow = document.createElement("div");
      btnRow.className = "flex items-center gap-1.5";

      const flyBtn = document.createElement("button");
      flyBtn.type = "button";
      flyBtn.className =
        "px-2 py-1 rounded bg-[#1a1e28] border border-white/15 text-[11px] text-[#eef0f5] hover:border-[#4c8bf5]";
      flyBtn.textContent = lang === "tr" ? "Sahaya yakınlaş" : "Zoom in";
      flyBtn.onclick = () => {
        setBasemap("satellite");
        setViewMode("site");
        map.flyTo([s.lat, s.lon], 12, { duration: 0.75 });
      };

      const btn3d = document.createElement("button");
      btn3d.type = "button";
      btn3d.className =
        "px-2 py-1 rounded bg-[#4c8bf5]/20 border border-[#4c8bf5]/45 text-[11px] text-[#eef0f5]";
      btn3d.textContent = lang === "tr" ? "3B & uydu" : "3D & orbital";
      btn3d.onclick = () => {
        onInspect3DRef.current?.(s.site_id);
      };

      btnRow.appendChild(flyBtn);
      btnRow.appendChild(btn3d);

      popupEl.appendChild(badge);
      popupEl.appendChild(heading);
      popupEl.appendChild(stats);
      popupEl.appendChild(btnRow);

      dot.bindPopup(popupEl, { maxWidth: 260 });
      dot.on("click", () => {
        onSelectRef.current(s.site_id);
      });
      dot.addTo(group);
    }
  }, [sites, scoresById, selectedId, metricMode, lang, viewMode]);

  const handleGlobal = () => {
    setViewMode("global");
    mapRef.current?.flyTo([24, 15], 2, { duration: 0.65 });
  };

  const handleTurkey = () => {
    setViewMode("turkey");
    mapRef.current?.flyToBounds(
      [
        [35.7, 25.8],
        [42.2, 44.9],
      ],
      { padding: [24, 24], duration: 0.65 }
    );
  };

  const handleFlySelected = () => {
    if (!selectedSite) return;
    setViewMode("site");
    setBasemap("satellite");
    mapRef.current?.flyTo([selectedSite.lat, selectedSite.lon], 12, { duration: 0.75 });
  };

  return (
    <div className="rounded-xl border hairline bg-[#11141c] p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-2 flex-wrap">
          <h3 className="text-[14px] font-medium text-[#eef0f5]">
            {lang === "tr" ? "Dünya test sahaları GIS haritası" : "Earth test-site GIS map"}
          </h3>
          <span className="text-[12px] font-mono tabular text-[#7a8296]">
            {sites.length} {lang === "tr" ? "saha" : "sites"}
          </span>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          {/* Basemap toggle: Dark GIS vs Real Satellite */}
          <div className="inline-flex rounded-lg p-0.5 bg-[#07080d] border hairline text-[12px]">
            <button
              type="button"
              onClick={() => setBasemap("dark")}
              className={`px-2.5 py-1 rounded-md transition-colors duration-150 ${
                basemap === "dark" ? "active-highlight text-[#eef0f5]" : "text-[#7a8296] hover:text-[#eef0f5]"
              }`}
            >
              {lang === "tr" ? "Koyu harita" : "Dark GIS"}
            </button>
            <button
              type="button"
              onClick={() => setBasemap("satellite")}
              className={`px-2.5 py-1 rounded-md transition-colors duration-150 ${
                basemap === "satellite"
                  ? "active-highlight text-[#eef0f5]"
                  : "text-[#7a8296] hover:text-[#eef0f5]"
              }`}
            >
              {lang === "tr" ? "Uydu görüntüsü" : "Satellite"}
            </button>
          </div>

          {/* Camera region presets */}
          <div className="inline-flex rounded-lg p-0.5 bg-[#07080d] border hairline text-[12px]">
            <button
              type="button"
              onClick={handleGlobal}
              className={`px-2.5 py-1 rounded-md transition-colors duration-150 ${
                viewMode === "global"
                  ? "active-highlight text-[#eef0f5]"
                  : "text-[#7a8296] hover:text-[#eef0f5]"
              }`}
            >
              {zoomGlobalLabel}
            </button>
            <button
              type="button"
              onClick={handleTurkey}
              className={`px-2.5 py-1 rounded-md transition-colors duration-150 ${
                viewMode === "turkey"
                  ? "active-highlight text-[#eef0f5]"
                  : "text-[#7a8296] hover:text-[#eef0f5]"
              }`}
            >
              {zoomTurkeyLabel}
            </button>
            <button
              type="button"
              onClick={handleFlySelected}
              className={`px-2.5 py-1 rounded-md transition-colors duration-150 ${
                viewMode === "site"
                  ? "active-highlight text-[#4cc38a]"
                  : "text-[#a3a9b8] hover:text-[#eef0f5]"
              }`}
            >
              {lang === "tr" ? "Seçili sahaya uç" : "Fly to site"}
            </button>
          </div>
        </div>
      </div>

      {/* Real Interactive Leaflet Map Canvas */}
      <div className="relative rounded-lg overflow-hidden border hairline bg-[#07080d]">
        <div ref={containerRef} className="w-full h-[380px] sm:h-[420px]" />
      </div>

      {/* Clean Legend Strip */}
      <div className="flex items-center justify-between flex-wrap gap-3 text-[11px] text-[#7a8296] px-1">
        <div className="flex items-center flex-wrap gap-x-4 gap-y-1">
          <span className="inline-flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#4cc38a]" />
            <span>≥ 0.62</span>
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#4c8bf5]" />
            <span>0.45–0.62</span>
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#d9a441]" />
            <span>0.30–0.45</span>
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#e5484d]" />
            <span>&lt; 0.30</span>
          </span>
          <span className="inline-flex items-center gap-1.5 pl-2 border-l hairline">
            <span className="w-3 h-3 rounded-full border-2 border-[#4c8bf5]" />
            <span>{lang === "tr" ? "Doğrulama (10)" : "Validation (10)"}</span>
          </span>
        </div>

        <span className="font-mono text-[#a3a9b8]">
          {selectedSite
            ? `${selectedSite.short} · ${selectedSite.lat.toFixed(3)}°, ${selectedSite.lon.toFixed(3)}°`
            : ""}
        </span>
      </div>
    </div>
  );
}
