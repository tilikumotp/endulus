import type { EarthSite, Lang, MoonRef, SiteScoreRow } from "../types";
import { normalizeRadarAxes } from "../scoring";
import { FEATURE_NAMES } from "../i18n";

interface Props {
  moon: MoonRef;
  earth: EarthSite;
  allMoon: MoonRef[];
  allEarth: EarthSite[];
  scoreRow: SiteScoreRow | undefined;
  lang: Lang;
}

/**
 * Multi-feature spider/radar chart comparing Lunar South Pole reference vs
 * selected Earth field site normalized honestly across all 45 sites in v1.
 */
export function RadarCompareSvg({ moon, earth, allMoon, allEarth, scoreRow, lang }: Props) {
  const axes = normalizeRadarAxes(moon, earth, allMoon, allEarth, scoreRow);
  const N = axes.length;
  const cx = 152;
  const cy = 128;
  const R = 78;

  const ptAt = (idx: number, val: number) => {
    const angle = -Math.PI / 2 + (idx / N) * Math.PI * 2;
    return {
      x: cx + Math.cos(angle) * R * val,
      y: cy + Math.sin(angle) * R * val,
      lx: cx + Math.cos(angle) * (R + 22),
      ly: cy + Math.sin(angle) * (R + 22),
    };
  };

  const moonPoly = axes
    .map((a, i) => {
      const p = ptAt(i, a.moonNorm);
      return `${p.x.toFixed(1)},${p.y.toFixed(1)}`;
    })
    .join(" ");

  const earthPoly = axes
    .map((a, i) => {
      const p = ptAt(i, a.earthNorm);
      return `${p.x.toFixed(1)},${p.y.toFixed(1)}`;
    })
    .join(" ");

  const shortAxisLabel: Record<string, { tr: string; en: string }> = {
    slope_mean: { tr: "Eğim", en: "Slope" },
    slope_p90: { tr: "Dik (p90)", en: "Steep p90" },
    roughness: { tr: "Pürüzlülük", en: "Rough" },
    relief: { tr: "Yükselti", en: "Relief" },
    albedo: { tr: "Albedo", en: "Albedo" },
  };

  return (
    <div className="rounded-xl border hairline bg-[#11141c] p-5 flex flex-col justify-between gap-4">
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <h3 className="text-[15px] font-medium text-[#eef0f5]">
            {lang === "tr" ? "Çok boyutlu radar karşılaştırması" : "Multi-feature radar comparison"}
          </h3>
          <p className="text-[12px] text-[#7a8296] mt-0.5">
            {lang === "tr"
              ? "45 saha havuzunda normalize edilmiş 5 fiziksel ölçüt"
              : "5 physical features normalized over the 45-site pool"}
          </p>
        </div>

        <div className="flex items-center gap-3 text-[11px]">
          <span className="flex items-center gap-1.5 text-[#a3a9b8]">
            <span className="w-2.5 h-0.5 bg-[#4c8bf5]" />
            {lang === "tr" ? "Ay" : "Moon"}
          </span>
          <span className="flex items-center gap-1.5 text-[#a3a9b8]">
            <span className="w-2.5 h-0.5 bg-[#4cc38a]" />
            {lang === "tr" ? "Dünya" : "Earth"}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-12 gap-4 items-center">
        <div className="sm:col-span-6 flex justify-center">
          <svg viewBox="0 0 296 254" className="w-full max-w-[290px] h-auto">
            {[0.25, 0.5, 0.75, 1.0].map((lvl) => {
              const pts = axes
                .map((_, i) => {
                  const p = ptAt(i, lvl);
                  return `${p.x.toFixed(1)},${p.y.toFixed(1)}`;
                })
                .join(" ");
              return (
                <polygon
                  key={lvl}
                  points={pts}
                  fill="none"
                  stroke="rgba(238,240,245,0.08)"
                  strokeWidth={1}
                />
              );
            })}

            {axes.map((a, i) => {
              const p = ptAt(i, 1);
              return (
                <g key={a.key}>
                  <line
                    x1={cx}
                    y1={cy}
                    x2={p.x}
                    y2={p.y}
                    stroke="rgba(238,240,245,0.1)"
                    strokeWidth={1}
                  />
                  <text
                    x={p.lx}
                    y={p.ly}
                    textAnchor={
                      Math.abs(p.lx - cx) < 12 ? "middle" : p.lx > cx ? "start" : "end"
                    }
                    dominantBaseline="central"
                    fill="#a3a9b8"
                    fontSize={10.5}
                    className="font-sans"
                  >
                    {shortAxisLabel[a.key]?.[lang] ?? a.key}
                  </text>
                </g>
              );
            })}

            <polygon
              points={moonPoly}
              fill="rgba(76, 139, 245, 0.16)"
              stroke="#4c8bf5"
              strokeWidth={1.6}
              strokeDasharray="4 3"
            />
            <polygon
              points={earthPoly}
              fill="rgba(76, 195, 138, 0.18)"
              stroke="#4cc38a"
              strokeWidth={1.8}
            />

            {axes.map((a, i) => {
              const pm = ptAt(i, a.moonNorm);
              const pe = ptAt(i, a.earthNorm);
              return (
                <g key={`pts-${a.key}`}>
                  <circle cx={pm.x} cy={pm.y} r={2.8} fill="#4c8bf5" />
                  <circle cx={pe.x} cy={pe.y} r={3.2} fill="#4cc38a" />
                </g>
              );
            })}
          </svg>
        </div>

        <div className="sm:col-span-6 flex flex-col gap-2 text-[12px]">
          {axes.map((a) => {
            const meta = FEATURE_NAMES[a.key];
            return (
              <div
                key={a.key}
                className="px-3 py-2 rounded-lg bg-[#07080d] border hairline flex items-center justify-between gap-2"
              >
                <span className="text-[#a3a9b8]">{meta?.[lang] ?? a.key}</span>
                <span className="font-mono tabular text-[11.5px] whitespace-nowrap">
                  <span className="text-[#4c8bf5]">{a.moonRaw.toFixed(a.key === "albedo" ? 3 : 1)}</span>
                  <span className="text-[#7a8296] mx-1.5">vs</span>
                  <span className="text-[#4cc38a]">{a.earthRaw.toFixed(a.key === "albedo" ? 3 : 1)}</span>
                </span>
              </div>
            );
          })}
          {scoreRow && (
            <div className="grid grid-cols-2 gap-2 pt-1 font-mono tabular text-[11px]">
              <div className="px-3 py-2 rounded bg-[#07080d] border hairline flex items-center justify-between">
                <span className="text-[#a3a9b8] font-sans">
                  {lang === "tr" ? "Mobilite" : "Mobility"}
                </span>
                <strong className="text-[#eef0f5]">{scoreRow.mob.toFixed(3)}</strong>
              </div>
              <div className="px-3 py-2 rounded bg-[#07080d] border hairline flex items-center justify-between">
                <span className="text-[#a3a9b8] font-sans">
                  {lang === "tr" ? "Yüzey" : "Surface"}
                </span>
                <strong className="text-[#eef0f5]">{scoreRow.surf.toFixed(3)}</strong>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
