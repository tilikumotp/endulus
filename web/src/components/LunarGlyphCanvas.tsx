import { useEffect, useRef } from "react";

interface Props {
  imageSrc: string;
  alt: string;
}

const CHARS = " .·:+*#";

/**
 * Pure orbital 5 m/px LOLA contour telemetry renderer:
 * samples borderless elevation tiles (`thumbs/moon/*.png`) with zero axis text artifacts,
 * adds an exact r = 1000 m measurement perimeter and compass ticks over #0b0d14.
 */
export function LunarGlyphCanvas({ imageSrc, alt }: Props) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let cancelled = false;
    let rafId = 0;
    let visible = true;
    const img = new Image();
    img.src = imageSrc;

    const io = new IntersectionObserver(
      ([entry]) => {
        visible = entry.isIntersecting;
      },
      { threshold: 0.05 }
    );
    io.observe(canvas);

    img.onload = () => {
      if (cancelled) return;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const cssW = 460;
      const cssH = 420;
      canvas.width = Math.round(cssW * dpr);
      canvas.height = Math.round(cssH * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      const cell = 7;
      const cols = Math.floor(cssW / cell);
      const rows = Math.floor(cssH / cell);

      const samplerCanvas = document.createElement("canvas");
      samplerCanvas.width = cols;
      samplerCanvas.height = rows;
      const sctx = samplerCanvas.getContext("2d", { willReadFrequently: true });
      if (!sctx) return;
      sctx.drawImage(img, 0, 0, cols, rows);
      const pixels = sctx.getImageData(0, 0, cols, rows).data;

      const atlas = document.createElement("canvas");
      atlas.width = cell * CHARS.length;
      atlas.height = cell;
      const pen = atlas.getContext("2d");
      if (!pen) return;
      pen.font = `500 ${cell + 1}px "IBM Plex Mono", monospace`;
      pen.textAlign = "center";
      pen.textBaseline = "middle";
      pen.fillStyle = "#ffffff";
      [...CHARS].forEach((ch, idx) => {
        pen.fillText(ch, idx * cell + cell / 2, cell / 2);
      });

      const cx = cols / 2;
      const cy = rows / 2;
      const maxR = Math.min(cx, cy) * 0.94;
      const rimRCols = Math.min(cx, cy) * 0.72;

      const cells: {
        x: number;
        y: number;
        light: number;
        seed: number;
        color: string;
      }[] = [];

      for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
          const dist = Math.hypot(x - cx, y - cy);
          const edgeFade = Math.max(0, 1 - Math.pow(dist / maxR, 2.2));
          if (edgeFade <= 0.01) continue;
          const i = (y * cols + x) * 4;
          const lum =
            (0.2126 * pixels[i] + 0.7152 * pixels[i + 1] + 0.0722 * pixels[i + 2]) / 255;
          const light = lum * edgeFade;
          if (light < 0.07) continue;

          const nearRim = Math.abs(dist - rimRCols) < 1.1;
          const tint = nearRim
            ? "rgba(76, 139, 245, 0.85)"
            : `rgba(${Math.round(156 + light * 82)}, ${Math.round(168 + light * 72)}, ${Math.round(192 + light * 54)}, ${(0.22 + light * 0.62).toFixed(2)})`;
          cells.push({
            x,
            y,
            light,
            seed: ((x * 73856093) ^ (y * 19349663)) % 1000,
            color: tint,
          });
        }
      }

      const glyphBuf = document.createElement("canvas");
      glyphBuf.width = cell;
      glyphBuf.height = cell;
      const gctx = glyphBuf.getContext("2d");
      if (!gctx) return;

      const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      let last = 0;
      let step = 0;

      const cxPx = cssW * 0.5;
      const cyPx = cssH * 0.5;
      const imgSize = Math.min(cssW, cssH) * 0.84;
      const radiusPx = Math.min(cssW, cssH) * 0.36;

      const renderFrame = (tick: number) => {
        ctx.clearRect(0, 0, cssW, cssH);

        // Circular clipped raw LOLA hillshade softly embedded in center
        ctx.save();
        ctx.beginPath();
        ctx.arc(cxPx, cyPx, imgSize * 0.5, 0, Math.PI * 2);
        ctx.clip();
        ctx.globalAlpha = 0.38;
        ctx.drawImage(img, cxPx - imgSize * 0.5, cyPx - imgSize * 0.5, imgSize, imgSize);
        ctx.restore();

        // Telemetry glyphs over topography
        for (const c of cells) {
          const shimmer =
            !reduceMotion && Math.sin(c.seed * 0.13 + tick * 0.42) > 0.945 ? 1 : 0;
          const pick = Math.min(
            CHARS.length - 1,
            Math.max(1, Math.floor(c.light * (CHARS.length - 1)) + shimmer)
          );
          gctx.globalCompositeOperation = "copy";
          gctx.drawImage(atlas, pick * cell, 0, cell, cell, 0, 0, cell, cell);
          gctx.globalCompositeOperation = "source-in";
          gctx.fillStyle = c.color;
          gctx.fillRect(0, 0, cell, cell);
          ctx.drawImage(glyphBuf, c.x * cell, c.y * cell);
        }

        // Radial feather into page canvas (#0b0d14)
        const rad = ctx.createRadialGradient(
          cxPx,
          cyPx,
          radiusPx * 0.65,
          cxPx,
          cyPx,
          imgSize * 0.54
        );
        rad.addColorStop(0, "rgba(11, 13, 20, 0)");
        rad.addColorStop(0.75, "rgba(11, 13, 20, 0.55)");
        rad.addColorStop(1, "#0b0d14");
        ctx.fillStyle = rad;
        ctx.fillRect(0, 0, cssW, cssH);

        // Precision measurement reticle overlay (r = 1000 m circle + cardinal ticks)
        ctx.save();
        ctx.strokeStyle = "rgba(76, 139, 245, 0.72)";
        ctx.lineWidth = 1.25;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.arc(cxPx, cyPx, radiusPx, 0, Math.PI * 2);
        ctx.stroke();
        ctx.setLineDash([]);

        ctx.strokeStyle = "rgba(238, 240, 245, 0.22)";
        ctx.lineWidth = 1;
        // Crosshair ticks
        ctx.beginPath();
        ctx.moveTo(cxPx - 10, cyPx);
        ctx.lineTo(cxPx + 10, cyPx);
        ctx.moveTo(cxPx, cyPx - 10);
        ctx.lineTo(cxPx, cyPx + 10);
        ctx.stroke();

        // Scale tag: r = 1000 m
        ctx.font = '500 11px "IBM Plex Mono", monospace';
        ctx.fillStyle = "#a3a9b8";
        ctx.textAlign = "right";
        ctx.fillText("r = 1000 m · 5 m/px", cssW - 14, cssH - 12);
        ctx.restore();
      };

      renderFrame(0);
      if (reduceMotion) return;

      const loop = (now: number) => {
        rafId = requestAnimationFrame(loop);
        if (!visible || now - last < 125) return; // calm 8 fps telemetry tick
        last = now;
        renderFrame(++step);
      };
      rafId = requestAnimationFrame(loop);
    };

    return () => {
      cancelled = true;
      cancelAnimationFrame(rafId);
      io.disconnect();
    };
  }, [imageSrc]);

  return (
    <canvas
      ref={canvasRef}
      role="img"
      aria-label={alt}
      className="w-full max-w-[460px] h-auto block select-none"
    />
  );
}
