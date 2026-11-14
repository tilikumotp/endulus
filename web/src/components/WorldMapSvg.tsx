import { useEffect, useMemo, useState } from "react";
import { geoGraticule, geoGraticule10, geoMercator, geoNaturalEarth1, geoPath } from "d3-geo";
import { feature } from "topojson-client";
import type { Topology, GeometryCollection } from "topojson-specification";
import type { EarthSite, Lang, SiteScoreRow } from "../types";

interface Props {
  sites: EarthSite[];
  scoresById: Record<string, SiteScoreRow>;
  selectedId: string;
  onSelect: (siteId: string) => void;
  lang: Lang;
  zoomTurkeyLabel: string;
  zoomGlobalLabel: string;
}

interface ProjectedMarker {
  site: EarthSite;
  x: number;
  y: number;
  score: number;
  rank: number;
}

interface PlacedLabel {
  siteId: string;
  text: string;
  tx: number;
  ty: number;
  anchor: "start" | "end";
  mx: number;
  my: number;
  boxW: number;
}

function scoreFill(score: number): string {
  if (score >= 0.62) return "#4cc38a";
  if (score >= 0.45) return "#4c8bf5";
  if (score >= 0.3) return "#d9a441";
  return "#e5484d";
}

export function WorldMapSvg({
  sites,
  scoresById,
  selectedId,
  onSelect,
  lang,
  zoomTurkeyLabel,
  zoomGlobalLabel,
}: Props) {
  const [turkeyFocus, setTurkeyFocus] = useState(false);
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [worldTopo, setWorldTopo] = useState<Topology | null>(null);

  useEffect(() => {
    let active = true;
    fetch("/data/world-50m.json")
      .then((r) => r.json() as Promise<Topology>)
      .then((t) => {
        if (active) setWorldTopo(t);
      })
      .catch(() => {
        // Graticule + markers still render cleanly if TopoJSON fails
      });
    return () => {
      active = false;
    };
  }, []);

  const W = 840;
  const H = turkeyFocus ? 360 : 390;

  const { landFeatures, turkeyFeature, projection, pathGen } = useMemo(() => {
    const proj = turkeyFocus
      ? geoMercator().fitExtent(
          [
            [28, 22],
            [W - 28, H - 22],
          ],
          {
            type: "MultiPoint",
            coordinates: [
              [25.2, 35.6],
              [45.3, 42.3],
            ],
          }
        )
      : geoNaturalEarth1().fitExtent(
          [
            [12, 12],
            [W - 12, H - 12],
          ],
          { type: "Sphere" }
        );

    const pg = geoPath(proj);
    let lands: ReturnType<typeof feature> | null = null;
    let trFeat: ReturnType<typeof feature> | null = null;

    if (worldTopo && worldTopo.objects.countries) {
      const col = feature(
        worldTopo,
        worldTopo.objects.countries as GeometryCollection
      );
      lands = col;
      if ("features" in col) {
        const match = col.features.find(
          (f) => String(f.id) === "792" || String((f.properties as { name?: string })?.name) === "Turkey"
        );
        if (match) trFeat = match;
      }
    }

    return { landFeatures: lands, turkeyFeature: trFeat, projection: proj, pathGen: pg };
  }, [worldTopo, turkeyFocus, H]);

  const projectedMarkers: ProjectedMarker[] = useMemo(() => {
    const out: ProjectedMarker[] = [];
    for (const s of sites) {
      if (turkeyFocus && !s.is_tr) continue;
      const pt = projection([s.lon, s.lat]);
      if (!pt) continue;
      const [x, y] = pt;
      if (x < -12 || x > W + 12 || y < -12 || y > H + 12) continue;
      const row = scoresById[s.site_id];
      out.push({
        site: s,
        x,
        y,
        score: row?.score ?? 0,
        rank: row?.rank ?? 99,
      });
    }
    return out;
  }, [sites, turkeyFocus, projection, scoresById, H]);

  // Greedy collision-free label placer so overlapping labels never render broken text
  const placedLabels: PlacedLabel[] = useMemo(() => {
    const candidates = [...projectedMarkers].sort((a, b) => {
      if (a.site.site_id === selectedId) return -1;
      if (b.site.site_id === selectedId) return 1;
      return a.rank - b.rank;
    });

    const occupied: { x1: number; y1: number; x2: number; y2: number }[] = [];
    // Reserve circle area around markers first so labels don't sit on another dot
    for (const m of projectedMarkers) {
      occupied.push({ x1: m.x - 8, y1: m.y - 8, x2: m.x + 8, y2: m.y + 8 });
    }

    const labels: PlacedLabel[] = [];
    const maxLabels = turkeyFocus ? 14 : 6;

    const offsets: { dx: number; dy: number; anchor: "start" | "end" }[] = [
      { dx: 11, dy: -6, anchor: "start" },
      { dx: 11, dy: 14, anchor: "start" },
      { dx: -11, dy: -6, anchor: "end" },
      { dx: -11, dy: 14, anchor: "end" },
      { dx: 12, dy: -18, anchor: "start" },
      { dx: -12, dy: -18, anchor: "end" },
      { dx: 12, dy: 24, anchor: "start" },
      { dx: -12, dy: 24, anchor: "end" },
    ];

    for (const m of candidates) {
      if (labels.length >= maxLabels && m.site.site_id !== selectedId) continue;
      const cleanName = m.site.short.replace(/\s*\(TR\)$/, "");
      const text = turkeyFocus ? `${cleanName} (#${m.rank})` : cleanName;
      const boxW = Math.min(185, text.length * 6.4 + 10);
      const boxH = 17;

      for (const off of offsets) {
        const tx = m.x + off.dx;
        const ty = m.y + off.dy;
        const x1 = off.anchor === "start" ? tx - 4 : tx - boxW + 4;
        const x2 = x1 + boxW;
        const y1 = ty - 12;
        const y2 = y1 + boxH;

        if (x1 < 8 || x2 > W - 8 || y1 < 8 || y2 > H - 8) continue;

        const collides = occupied.some(
          (b) => !(x2 < b.x1 || x1 > b.x2 || y2 < b.y1 || y1 > b.y2)
        );
        if (!collides) {
          occupied.push({ x1, y1, x2, y2 });
          labels.push({
            siteId: m.site.site_id,
            text,
            tx,
            ty,
            anchor: off.anchor,
            mx: m.x,
            my: m.y,
            boxW,
          });
          break;
        }
      }
    }

    return labels;
  }, [projectedMarkers, selectedId, turkeyFocus, H]);

  const hovered = hoveredId ? sites.find((s) => s.site_id === hoveredId) : null;
  const hovScore = hovered ? scoresById[hovered.site_id] : null;
  const activeMarker = projectedMarkers.find((m) => m.site.site_id === selectedId);
  const graticulePath = useMemo(() => {
    const geom = turkeyFocus
      ? geoGraticule().step([2, 2]).extent([[22, 34], [48, 44]])()
      : geoGraticule10();
    return pathGen(geom) ?? "";
  }, [pathGen, turkeyFocus]);
  const spherePath = useMemo(() => pathGen({ type: "Sphere" }) ?? "", [pathGen]);
  const landsPath = useMemo(() => (landFeatures ? pathGen(landFeatures) ?? "" : ""), [landFeatures, pathGen]);
  const trPath = useMemo(() => (turkeyFeature ? pathGen(turkeyFeature) ?? "" : ""), [turkeyFeature, pathGen]);

  return (
    <div className="rounded-xl border hairline bg-[#11141c] p-4">
      <div className="flex items-center justify-between gap-3 flex-wrap mb-3">
        <div className="flex items-center gap-4 flex-wrap text-[12px] text-[#a3a9b8]">
          <span className="flex items-center gap-1.5">
            <span className="inline-block w-2.5 h-2.5 rounded-full border-2 border-[#4c8bf5] bg-[#11141c]" />
            {lang === "tr" ? "Bilinen analog (10)" : "Known analogue (10)"}
          </span>
          <span className="flex items-center gap-1.5">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-[#4cc38a]" />
            {lang === "tr" ? "Yüksek uyum (>=0.62)" : "High (>=0.62)"}
          </span>
          <span className="flex items-center gap-1.5">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-[#4c8bf5]" />
            {lang === "tr" ? "Orta-iyi (>=0.45)" : "Good (>=0.45)"}
          </span>
          <span className="flex items-center gap-1.5">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-[#d9a441]" />
            {lang === "tr" ? "Kısmi (0.30–0.45)" : "Partial (0.30–0.45)"}
          </span>
          <span className="flex items-center gap-1.5">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-[#e5484d]" />
            {lang === "tr" ? "Düşük (<0.30)" : "Low (<0.30)"}
          </span>
        </div>

        <button
          type="button"
          onClick={() => setTurkeyFocus((v) => !v)}
          className="px-3 py-1.5 rounded-lg text-[12px] font-medium border hairline bg-[#1a1e28] text-[#eef0f5] hover:border-[#4c8bf5]/50 transition-colors duration-150"
        >
          {turkeyFocus ? zoomGlobalLabel : zoomTurkeyLabel}
        </button>
      </div>

      <div className="relative rounded-lg overflow-hidden bg-[#07080d] border hairline">
        <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto block">
          {!turkeyFocus && spherePath && (
            <path d={spherePath} fill="#080a10" stroke="rgba(238,240,245,0.12)" strokeWidth={1} />
          )}

          {graticulePath && (
            <path
              d={graticulePath}
              fill="none"
              stroke="rgba(238,240,245,0.055)"
              strokeWidth={0.7}
            />
          )}

          {landsPath && (
            <path
              d={landsPath}
              fill="#151924"
              stroke="rgba(238,240,245,0.16)"
              strokeWidth={turkeyFocus ? 0.9 : 0.6}
            />
          )}

          {turkeyFocus && trPath && (
            <path
              d={trPath}
              fill="#1b2131"
              stroke="rgba(76, 139, 245, 0.45)"
              strokeWidth={1.1}
            />
          )}

          {/* Active site selection crosshair */}
          {activeMarker && (
            <g className="pointer-events-none">
              <line
                x1={activeMarker.x}
                y1={0}
                x2={activeMarker.x}
                y2={H}
                stroke="rgba(76, 139, 245, 0.28)"
                strokeDasharray="3 4"
              />
              <line
                x1={0}
                y1={activeMarker.y}
                x2={W}
                y2={activeMarker.y}
                stroke="rgba(76, 139, 245, 0.28)"
                strokeDasharray="3 4"
              />
            </g>
          )}

          {/* Marker points */}
          {projectedMarkers.map(({ site: s, x, y, score }) => {
            const isSel = s.site_id === selectedId;
            const isVal = s.role === "validation";
            return (
              <g
                key={s.site_id}
                className="cursor-pointer"
                onClick={() => onSelect(s.site_id)}
                onMouseEnter={() => setHoveredId(s.site_id)}
                onMouseLeave={() => setHoveredId(null)}
              >
                {isVal && (
                  <circle
                    cx={x}
                    cy={y}
                    r={isSel ? 11 : 8}
                    fill="none"
                    stroke="#4c8bf5"
                    strokeWidth={1.6}
                  />
                )}
                {isSel && (
                  <circle
                    cx={x}
                    cy={y}
                    r={13}
                    fill="none"
                    stroke="#eef0f5"
                    strokeWidth={1.25}
                  />
                )}
                <circle
                  cx={x}
                  cy={y}
                  r={isSel ? 6 : 4.5}
                  fill={scoreFill(score)}
                  stroke="#07080d"
                  strokeWidth={1.2}
                />
              </g>
            );
          })}

          {/* Collision-free decluttered site labels */}
          {placedLabels.map((lbl) => {
            const isSel = lbl.siteId === selectedId;
            const rectX = lbl.anchor === "start" ? lbl.tx - 4 : lbl.tx - lbl.boxW + 4;
            return (
              <g key={`lbl-${lbl.siteId}`} className="pointer-events-none">
                <line
                  x1={lbl.mx}
                  y1={lbl.my}
                  x2={lbl.tx}
                  y2={lbl.ty - 3}
                  stroke={isSel ? "rgba(238,240,245,0.45)" : "rgba(163,169,184,0.22)"}
                  strokeWidth={0.8}
                />
                <rect
                  x={rectX}
                  y={lbl.ty - 12}
                  width={lbl.boxW}
                  height={16}
                  rx={4}
                  fill="rgba(7, 8, 13, 0.84)"
                  stroke={isSel ? "rgba(76, 139, 245, 0.55)" : "rgba(238,240,245,0.08)"}
                  strokeWidth={0.8}
                />
                <text
                  x={lbl.tx}
                  y={lbl.ty}
                  textAnchor={lbl.anchor}
                  fill={isSel ? "#eef0f5" : "#c7cddb"}
                  fontSize={10.5}
                  className="font-sans"
                >
                  {lbl.text}
                </text>
              </g>
            );
          })}
        </svg>

        <div className="px-3 py-2 border-t hairline bg-[#11141c] flex items-center justify-between flex-wrap gap-2 text-[12px]">
          {hovered && hovScore ? (
            <>
              <span className="text-[#eef0f5] font-medium">
                {hovered.short}{" "}
                <span className="text-[#7a8296] font-mono">
                  ({hovered.lat.toFixed(2)}°, {hovered.lon.toFixed(2)}°)
                </span>
              </span>
              <span className="font-mono tabular text-[#a3a9b8]">
                #{hovScore.rank} · {hovScore.score.toFixed(3)} · Mob #{hovScore.mob_rank} · Yüzey #{hovScore.surf_rank}
              </span>
            </>
          ) : activeMarker ? (
            <>
              <span className="text-[#a3a9b8]">
                {lang === "tr" ? "Seçili işaret:" : "Selected marker:"}{" "}
                <strong className="text-[#eef0f5] font-medium">{activeMarker.site.short}</strong>
              </span>
              <span className="font-mono tabular text-[#7a8296]">
                #{activeMarker.rank} · {activeMarker.score.toFixed(3)} · {activeMarker.site.slope_mean.toFixed(1)}° · alb{" "}
                {activeMarker.site.albedo.toFixed(3)}
              </span>
            </>
          ) : (
            <span className="text-[#7a8296]">
              {lang === "tr"
                ? "Detay için haritadan bir sahaya tıklayın veya üzerine gelin"
                : "Click or hover a marker to inspect telemetry"}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
