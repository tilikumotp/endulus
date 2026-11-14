import { useEffect, useMemo, useRef, useState } from "react";
import type { DemTile, Lang } from "../types";

export type TerrainColorMode = "elevation" | "slope" | "contour";

interface Props {
  tile: DemTile | undefined;
  title: string;
  subtitle: string;
  accentColor: string;
  azimuthDeg: number;
  pitchDeg: number;
  zoom: number;
  exaggeration: number;
  colorMode: TerrainColorMode;
  lang: Lang;
  onAzimuthChange: (nextDeg: number) => void;
  onPitchChange: (nextPitch: number) => void;
  onZoomChange: (nextZoom: number) => void;
}

interface ProbeHit {
  xMeters: number;
  yMeters: number;
  elevMeters: number;
  slopeDeg: number;
  sx: number;
  sy: number;
}

interface ProjectedQuad {
  r: number;
  c: number;
  cxScreen: number;
  cyScreen: number;
  depth: number;
  shade: number;
  relElev: number;
  slopeDeg: number;
  elevMeters: number;
}

/**
 * Interactive 2-axis orthographic 3D terrain relief canvas rendered directly
 * from verified 5 m/px LRO LOLA and 30 m/px Copernicus/NASADEM DEM grids.
 */
export function Terrain3DCanvas({
  tile,
  title,
  subtitle,
  accentColor,
  azimuthDeg,
  pitchDeg,
  zoom,
  exaggeration,
  colorMode,
  lang,
  onAzimuthChange,
  onPitchChange,
  onZoomChange,
}: Props) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const hitIndexRef = useRef<ProjectedQuad[]>([]);
  const [probe, setProbe] = useState<ProbeHit | null>(null);

  const dragRef = useRef<{
    active: boolean;
    startX: number;
    startY: number;
    startAz: number;
    startPitch: number;
  }>({
    active: false,
    startX: 0,
    startY: 0,
    startAz: azimuthDeg,
    startPitch: pitchDeg,
  });

  // Precompute cell slopes in true physical degrees once per DEM tile
  const slopesGrid = useMemo(() => {
    if (!tile) return [];
    const grid = tile.grid;
    const n = grid.length;
    const cellM = (2 * (tile.half_width_m || 1000)) / Math.max(1, n - 1);
    const out: number[][] = [];
    for (let r = 0; r < n - 1; r++) {
      const row: number[] = [];
      for (let c = 0; c < n - 1; c++) {
        const dzdx = (grid[r][c + 1] - grid[r][c]) / cellM;
        const dzdy = (grid[r + 1][c] - grid[r][c]) / cellM;
        const deg = (Math.atan(Math.hypot(dzdx, dzdy)) * 180) / Math.PI;
        row.push(deg);
      }
      out.push(row);
    }
    return out;
  }, [tile]);

  // Attach native non-passive wheel listener so mouse wheel zooms terrain smoothly without scrolling page
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const handleWheel = (e: WheelEvent) => {
      e.preventDefault();
      const delta = e.deltaY > 0 ? -0.08 : 0.08;
      const next = Math.max(0.75, Math.min(1.75, Math.round((zoom + delta) * 100) / 100));
      onZoomChange(next);
    };
    canvas.addEventListener("wheel", handleWheel, { passive: false });
    return () => canvas.removeEventListener("wheel", handleWheel);
  }, [zoom, onZoomChange]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !tile) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const W = 540;
    const H = 360;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);

    const grid = tile.grid;
    const n = grid.length;
    const halfW = tile.half_width_m || 1000;
    const spanZ = Math.max(tile.relief_m, 20);

    const az = (azimuthDeg * Math.PI) / 180;
    const tilt = (pitchDeg * Math.PI) / 180;
    const cosA = Math.cos(az);
    const sinA = Math.sin(az);
    const sinT = Math.sin(tilt);
    const cosT = Math.cos(tilt);

    const xyScale = 132 * zoom;
    const zScale = ((62 * exaggeration) / spanZ) * zoom;
    const cx = W * 0.5;
    const cy = H * 0.56;

    // Draw subtle ground skirt shadow plane underneath DEM slab
    const corners: [number, number][] = [
      [-1, -1],
      [1, -1],
      [1, 1],
      [-1, 1],
    ];
    ctx.beginPath();
    corners.forEach(([nx, ny], idx) => {
      const xr = nx * cosA - ny * sinA;
      const yr = nx * sinA + ny * cosA;
      const sx = cx + xr * xyScale;
      const sy = cy + yr * xyScale * sinT + spanZ * 0.35 * zScale * cosT;
      if (idx === 0) ctx.moveTo(sx, sy);
      else ctx.lineTo(sx, sy);
    });
    ctx.closePath();
    ctx.strokeStyle = "rgba(238, 240, 245, 0.08)";
    ctx.lineWidth = 1;
    ctx.stroke();

    // Project grid vertices
    const pts: { sx: number; sy: number; depth: number; elev: number }[][] = [];
    for (let r = 0; r < n; r++) {
      const rowPts: { sx: number; sy: number; depth: number; elev: number }[] = [];
      const ny = (r / (n - 1) - 0.5) * 2;
      for (let c = 0; c < n; c++) {
        const nx = (c / (n - 1) - 0.5) * 2;
        const elev = grid[r][c];
        const xr = nx * cosA - ny * sinA;
        const yr = nx * sinA + ny * cosA;
        const sx = cx + xr * xyScale;
        const sy = cy + yr * xyScale * sinT - (elev - spanZ * 0.35) * zScale * cosT;
        rowPts.push({ sx, sy, depth: yr, elev });
      }
      pts.push(rowPts);
    }

    // Build quads sorted back-to-front
    const quads: ProjectedQuad[] = [];
    const light = [-0.55, -0.55, 0.63];

    for (let r = 0; r < n - 1; r++) {
      for (let c = 0; c < n - 1; c++) {
        const cellM = (2 * halfW) / (n - 1);
        const dzdx = ((grid[r][c + 1] - grid[r][c]) / cellM) * exaggeration;
        const dzdy = ((grid[r + 1][c] - grid[r][c]) / cellM) * exaggeration;
        const nxV = -dzdx;
        const nyV = -dzdy;
        const nzV = 1;
        const len = Math.hypot(nxV, nyV, nzV) || 1;
        const dot = (nxV * light[0] + nyV * light[1] + nzV * light[2]) / len;
        const shade = Math.max(0.18, Math.min(1, 0.36 + dot * 0.66));

        const p0 = pts[r][c];
        const p1 = pts[r][c + 1];
        const p2 = pts[r + 1][c + 1];
        const p3 = pts[r + 1][c];
        const elevMid = (grid[r][c] + grid[r + 1][c + 1]) * 0.5;

        quads.push({
          r,
          c,
          cxScreen: (p0.sx + p1.sx + p2.sx + p3.sx) * 0.25,
          cyScreen: (p0.sy + p1.sy + p2.sy + p3.sy) * 0.25,
          depth: (p0.depth + p1.depth + p2.depth + p3.depth) * 0.25,
          shade,
          relElev: Math.max(0, Math.min(1, elevMid / spanZ)),
          slopeDeg: slopesGrid[r]?.[c] ?? 0,
          elevMeters: elevMid,
        });
      }
    }

    quads.sort((a, b) => a.depth - b.depth);
    hitIndexRef.current = quads;

    const isMoon = tile.body === "moon";
    const contourStep = spanZ >= 250 ? 25 : spanZ >= 90 ? 10 : 5;

    for (const q of quads) {
      const p0 = pts[q.r][q.c];
      const p1 = pts[q.r][q.c + 1];
      const p2 = pts[q.r + 1][q.c + 1];
      const p3 = pts[q.r + 1][q.c];

      ctx.beginPath();
      ctx.moveTo(p0.sx, p0.sy);
      ctx.lineTo(p1.sx, p1.sy);
      ctx.lineTo(p2.sx, p2.sy);
      ctx.lineTo(p3.sx, p3.sy);
      ctx.closePath();

      if (colorMode === "slope") {
        const s = q.slopeDeg;
        const lit = 0.55 + q.shade * 0.55;
        if (s < 10) {
          ctx.fillStyle = `rgb(${Math.round(45 * lit)}, ${Math.round(168 * lit)}, ${Math.round(115 * lit)})`;
        } else if (s <= 20) {
          ctx.fillStyle = `rgb(${Math.round(205 * lit)}, ${Math.round(148 * lit)}, ${Math.round(45 * lit)})`;
        } else {
          ctx.fillStyle = `rgb(${Math.round(220 * lit)}, ${Math.round(68 * lit)}, ${Math.round(74 * lit)})`;
        }
      } else if (colorMode === "contour") {
        const e0 = Math.floor(grid[q.r][q.c] / contourStep);
        const e1 = Math.floor(grid[q.r][q.c + 1] / contourStep);
        const e2 = Math.floor(grid[q.r + 1][q.c] / contourStep);
        const isLine = e0 !== e1 || e0 !== e2;
        const base = Math.round(22 + q.shade * 128 + q.relElev * 36);
        if (isLine) {
          ctx.fillStyle = isMoon ? "#8cb4ff" : "#76dfb1";
        } else {
          ctx.fillStyle = `rgb(${base}, ${base + 3}, ${Math.min(255, base + 10)})`;
        }
      } else {
        const lum = Math.round(24 + q.shade * 165);
        if (isMoon) {
          const ridge = Math.round(q.relElev * 24);
          ctx.fillStyle = `rgb(${Math.min(255, lum + ridge - 2)}, ${Math.min(255, lum + ridge)}, ${Math.min(255, lum + ridge + 12)})`;
        } else {
          const warm = Math.round(q.relElev * 34);
          ctx.fillStyle = `rgb(${Math.min(255, lum + warm)}, ${Math.min(255, lum + Math.round(warm * 0.45))}, ${Math.max(18, lum - 12)})`;
        }
      }

      ctx.fill();
      ctx.strokeStyle = colorMode === "contour" ? "rgba(7, 8, 13, 0.14)" : "rgba(11, 13, 20, 0.08)";
      ctx.lineWidth = 0.25;
      ctx.stroke();
    }

    // r = 1000 m perimeter ring on terrain
    const rNorm = Math.min(0.95, 1000 / halfW);
    const segs = 64;
    ctx.beginPath();
    for (let i = 0; i <= segs; i++) {
      const th = (i / segs) * Math.PI * 2;
      const nx = Math.cos(th) * rNorm;
      const ny = Math.sin(th) * rNorm;
      const gi = Math.max(0, Math.min(n - 1, Math.round(((ny + 1) * 0.5) * (n - 1))));
      const gj = Math.max(0, Math.min(n - 1, Math.round(((nx + 1) * 0.5) * (n - 1))));
      const elev = grid[gi][gj] + spanZ * 0.02;
      const xr = nx * cosA - ny * sinA;
      const yr = nx * sinA + ny * cosA;
      const sx = cx + xr * xyScale;
      const sy = cy + yr * xyScale * sinT - (elev - spanZ * 0.35) * zScale * cosT;
      if (i === 0) ctx.moveTo(sx, sy);
      else ctx.lineTo(sx, sy);
    }
    ctx.strokeStyle = accentColor;
    ctx.lineWidth = 1.7;
    ctx.stroke();

    // Draw probe reticle on hovered terrain coordinate
    if (probe) {
      ctx.beginPath();
      ctx.arc(probe.sx, probe.sy, 4.5, 0, Math.PI * 2);
      ctx.strokeStyle = "#eef0f5";
      ctx.lineWidth = 1.5;
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(probe.sx, probe.sy, 1.8, 0, Math.PI * 2);
      ctx.fillStyle = accentColor;
      ctx.fill();
    }

    // Compass North indicator in bottom-right corner
    const compX = W - 28;
    const compY = H - 28;
    const nxComp = -Math.sin(az) * 12;
    const nyComp = -Math.cos(az) * 12 * Math.max(0.35, sinT);
    ctx.beginPath();
    ctx.arc(compX, compY, 16, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(17, 20, 28, 0.85)";
    ctx.fill();
    ctx.strokeStyle = "rgba(238, 240, 245, 0.14)";
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(compX, compY);
    ctx.lineTo(compX + nxComp, compY + nyComp);
    ctx.strokeStyle = accentColor;
    ctx.lineWidth = 1.8;
    ctx.stroke();

    ctx.fillStyle = "#eef0f5";
    ctx.font = '600 9px "IBM Plex Mono", monospace';
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("N", compX + nxComp * 1.45, compY + nyComp * 1.45);
  }, [tile, azimuthDeg, pitchDeg, zoom, exaggeration, colorMode, accentColor, slopesGrid, probe]);

  const updateProbeFromPointer = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || !tile || hitIndexRef.current.length === 0) return;
    const rect = canvas.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 540;
    const y = ((e.clientY - rect.top) / rect.height) * 360;

    let best: ProjectedQuad | null = null;
    let bestD2 = 160;
    for (const q of hitIndexRef.current) {
      const d2 = (q.cxScreen - x) * (q.cxScreen - x) + (q.cyScreen - y) * (q.cyScreen - y);
      if (d2 < bestD2) {
        bestD2 = d2;
        best = q;
      }
    }

    if (!best) {
      if (probe) setProbe(null);
      return;
    }

    const n = tile.grid.length;
    const halfW = tile.half_width_m || 1000;
    const xM = ((best.c / (n - 1)) - 0.5) * 2 * halfW;
    const yM = (0.5 - (best.r / (n - 1))) * 2 * halfW;
    setProbe({
      xMeters: xM,
      yMeters: yM,
      elevMeters: best.elevMeters,
      slopeDeg: best.slopeDeg,
      sx: best.cxScreen,
      sy: best.cyScreen,
    });
  };

  return (
    <div className="rounded-xl border hairline bg-[#11141c] p-4 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h4 className="text-[14px] font-medium text-[#eef0f5] truncate">{title}</h4>
          <p className="text-[12px] text-[#7a8296] font-mono tabular truncate">{subtitle}</p>
        </div>
        {tile && (
          <span className="text-[11px] font-mono tabular text-[#a3a9b8] px-2.5 py-1 rounded bg-[#1a1e28] border hairline whitespace-nowrap shrink-0">
            {tile.native_res_m} m/px · Δ{tile.relief_m.toFixed(0)} m
          </span>
        )}
      </div>

      <div className="relative rounded-lg overflow-hidden bg-[#07080d] border hairline">
        <canvas
          ref={canvasRef}
          className="w-full h-auto block cursor-grab active:cursor-grabbing touch-none"
          onPointerDown={(e) => {
            dragRef.current = {
              active: true,
              startX: e.clientX,
              startY: e.clientY,
              startAz: azimuthDeg,
              startPitch: pitchDeg,
            };
            (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
          }}
          onPointerMove={(e) => {
            if (dragRef.current.active) {
              const dx = e.clientX - dragRef.current.startX;
              const dy = e.clientY - dragRef.current.startY;
              const nextAz = ((dragRef.current.startAz + dx * 0.65) % 360 + 360) % 360;
              const nextPitch = Math.max(16, Math.min(72, Math.round(dragRef.current.startPitch + dy * 0.3)));
              onAzimuthChange(Math.round(nextAz));
              onPitchChange(nextPitch);
              return;
            }
            updateProbeFromPointer(e);
          }}
          onPointerUp={() => {
            dragRef.current.active = false;
          }}
          onPointerLeave={() => {
            dragRef.current.active = false;
            setProbe(null);
          }}
        />

        {/* Corner telemetry probe readout */}
        <div className="absolute top-2.5 left-2.5 px-2.5 py-1 rounded-md bg-[#07080d]/85 border hairline text-[10.5px] font-mono tabular text-[#c7cddb] pointer-events-none whitespace-nowrap">
          {probe
            ? `Δh +${probe.elevMeters.toFixed(0)} m · ${
                lang === "tr" ? "Eğim" : "Slope"
              } ${probe.slopeDeg.toFixed(1)}° · (${Math.round(probe.xMeters)} m, ${Math.round(probe.yMeters)} m)`
            : lang === "tr"
              ? "Sürükle: döndür · Tekerlek: yakınlaştır · İmleç: eğim oku"
              : "Drag: orbit/tilt · Wheel: zoom · Hover: elevation & slope"}
        </div>

        {/* Slope colormap quick legend when active */}
        {colorMode === "slope" && (
          <div className="absolute bottom-2.5 left-2.5 px-2.5 py-1 rounded-md bg-[#07080d]/85 border hairline text-[10.5px] font-mono flex items-center gap-3 pointer-events-none">
            <span className="inline-flex items-center gap-1 text-[#4cc38a]">
              <span className="w-2 h-2 rounded-sm bg-[#3ea77a]" />
              &lt;10°
            </span>
            <span className="inline-flex items-center gap-1 text-[#d9a441]">
              <span className="w-2 h-2 rounded-sm bg-[#d49b38]" />
              10–20°
            </span>
            <span className="inline-flex items-center gap-1 text-[#e5484d]">
              <span className="w-2 h-2 rounded-sm bg-[#e04e53]" />
              &gt;20°
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
