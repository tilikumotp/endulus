import { useEffect, useRef } from "react";
import type { DemTile } from "../types";

interface Props {
  tile: DemTile | undefined;
  title: string;
  subtitle: string;
  accentColor: string;
  azimuthDeg: number;
  exaggeration: number;
  onAzimuthChange: (nextDeg: number) => void;
}

/**
 * Interactive orthographic 3D terrain relief canvas rendered directly from
 * verified LRO LOLA (5 m/px) or Copernicus/NASADEM (30 m/px) grids.
 */
export function Terrain3DCanvas({
  tile,
  title,
  subtitle,
  accentColor,
  azimuthDeg,
  exaggeration,
  onAzimuthChange,
}: Props) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const dragRef = useRef<{ active: boolean; startX: number; startAz: number }>({
    active: false,
    startX: 0,
    startAz: azimuthDeg,
  });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !tile) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const W = 520;
    const H = 340;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);

    const grid = tile.grid;
    const n = grid.length;
    const halfW = tile.half_width_m || 1000;
    const spanZ = Math.max(tile.relief_m, 20);

    const az = (azimuthDeg * Math.PI) / 180;
    const tilt = (32 * Math.PI) / 180;
    const cosA = Math.cos(az);
    const sinA = Math.sin(az);
    const sinT = Math.sin(tilt);
    const cosT = Math.cos(tilt);

    const xyScale = 135;
    const zScale = (58 * exaggeration) / spanZ;
    const cx = W * 0.5;
    const cy = H * 0.56;

    // Project grid vertices to screen coordinates + rotated depth
    const pts: { sx: number; sy: number; depth: number; elev: number }[][] = [];
    for (let r = 0; r < n; r++) {
      const rowPts: { sx: number; sy: number; depth: number; elev: number }[] = [];
      const ny = (r / (n - 1) - 0.5) * 2; // -1..1
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

    // Build quads sorted back-to-front by centroid depth
    const quads: {
      r: number;
      c: number;
      depth: number;
      shade: number;
      relElev: number;
    }[] = [];

    const light = [-0.55, -0.55, 0.63]; // NW illumination vector

    for (let r = 0; r < n - 1; r++) {
      for (let c = 0; c < n - 1; c++) {
        const dzdx = ((grid[r][c + 1] - grid[r][c]) / ((2 * halfW) / (n - 1))) * exaggeration;
        const dzdy = ((grid[r + 1][c] - grid[r][c]) / ((2 * halfW) / (n - 1))) * exaggeration;
        const nxV = -dzdx;
        const nyV = -dzdy;
        const nzV = 1;
        const len = Math.hypot(nxV, nyV, nzV) || 1;
        const dot = (nxV * light[0] + nyV * light[1] + nzV * light[2]) / len;
        const shade = Math.max(0.14, Math.min(1, 0.36 + dot * 0.68));
        const depth =
          (pts[r][c].depth + pts[r][c + 1].depth + pts[r + 1][c + 1].depth + pts[r + 1][c].depth) *
          0.25;
        quads.push({
          r,
          c,
          depth,
          shade,
          relElev: (grid[r][c] + grid[r + 1][c + 1]) / (2 * spanZ),
        });
      }
    }

    quads.sort((a, b) => a.depth - b.depth);

    const isMoon = tile.body === "moon";
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

      const lum = Math.round(28 + q.shade * 165);
      if (isMoon) {
        ctx.fillStyle = `rgb(${lum - 2}, ${lum}, ${Math.min(255, lum + 10)})`;
      } else {
        const warm = Math.round(q.relElev * 24);
        ctx.fillStyle = `rgb(${Math.min(255, lum + warm)}, ${Math.min(255, lum + 4)}, ${Math.max(18, lum - 10)})`;
      }
      ctx.fill();
      ctx.strokeStyle = "rgba(11, 13, 20, 0.08)";
      ctx.lineWidth = 0.25;
      ctx.stroke();
    }

    // Draw r = 1000 m measurement perimeter ring directly onto terrain surface
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
    ctx.lineWidth = 1.6;
    ctx.stroke();
  }, [tile, azimuthDeg, exaggeration, accentColor]);

  return (
    <div className="rounded-xl border hairline bg-[#11141c] p-4 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h4 className="text-[14px] font-medium text-[#eef0f5]">{title}</h4>
          <p className="text-[12px] text-[#7a8296] font-mono tabular">{subtitle}</p>
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
            dragRef.current = { active: true, startX: e.clientX, startAz: azimuthDeg };
            (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
          }}
          onPointerMove={(e) => {
            if (!dragRef.current.active) return;
            const dx = e.clientX - dragRef.current.startX;
            const next = ((dragRef.current.startAz + dx * 0.6) % 360 + 360) % 360;
            onAzimuthChange(Math.round(next));
          }}
          onPointerUp={() => {
            dragRef.current.active = false;
          }}
        />
      </div>
    </div>
  );
}
