import type { AlbedoSensitivityRow, EarthSite, Lang } from "../types";

interface Props {
  rows: AlbedoSensitivityRow[];
  sitesById: Record<string, EarthSite>;
  moonName: string;
  lang: Lang;
  onSelectEarth: (siteId: string) => void;
}

/**
 * Interactive readout of `src/moon_mars/albedo_sensitivity.py`:
 * varies the LOLA 1064 nm-to-broadband factor c in [0.30..0.46] around nominal 0.38
 * and tracks Spearman rank stability and #1 winner transitions.
 */
export function AlbedoSensitivitySvg({
  rows,
  sitesById,
  moonName,
  lang,
  onSelectEarth,
}: Props) {
  if (!rows.length) return null;

  const W = 420;
  const H = 170;
  const padL = 42;
  const padR = 20;
  const padT = 18;
  const padB = 30;

  const xs = rows.map((_, i) => padL + (i / Math.max(1, rows.length - 1)) * (W - padL - padR));
  const minRho = Math.min(0.55, ...rows.map((r) => r.spearman_rho_overall));
  const toY = (rho: number) =>
    padT + ((1.02 - rho) / (1.02 - minRho)) * (H - padT - padB);

  const linePath = rows
    .map((r, i) => `${i === 0 ? "M" : "L"}${xs[i].toFixed(1)},${toY(r.spearman_rho_overall).toFixed(1)}`)
    .join(" ");

  return (
    <div className="rounded-xl border hairline bg-[#11141c] p-5 flex flex-col gap-4">
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <h4 className="text-[14px] font-medium text-[#eef0f5]">
            {lang === "tr"
              ? "LOLA albedo dönüşüm katsayısı duyarlılık testi"
              : "LOLA albedo conversion sensitivity test"}
          </h4>
          <p className="text-[12px] text-[#7a8296] mt-0.5">
            {lang === "tr"
              ? `${moonName} için c = 0.30–0.46 aralığında Spearman sıralama korelasyonu (ρ)`
              : `Spearman rank stability (ρ) for ${moonName} across c = 0.30–0.46`}
          </p>
        </div>
        <span className="text-[11px] font-mono text-[#7a8296] px-2.5 py-1 rounded bg-[#07080d] border hairline">
          Nominal c = 0.38 (Lucey 2014)
        </span>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 items-center">
        <div className="xl:col-span-5 rounded-lg border hairline bg-[#07080d] p-3">
          <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto block">
            {[0.6, 0.8, 1.0].map((v) => {
              const y = toY(v);
              return (
                <g key={v}>
                  <line
                    x1={padL}
                    y1={y}
                    x2={W - padR}
                    y2={y}
                    stroke="rgba(238,240,245,0.08)"
                    strokeDasharray="3 3"
                  />
                  <text x={padL - 6} y={y + 3} textAnchor="end" fill="#7a8296" fontSize={10} className="font-mono">
                    {v.toFixed(1)}
                  </text>
                </g>
              );
            })}

            <path d={linePath} fill="none" stroke="#4c8bf5" strokeWidth={2} />

            {rows.map((r, i) => {
              const x = xs[i];
              const y = toY(r.spearman_rho_overall);
              const isNom = Math.abs(r.factor - 0.38) < 0.005;
              return (
                <g key={r.factor}>
                  <circle
                    cx={x}
                    cy={y}
                    r={isNom ? 5.5 : 4}
                    fill={isNom ? "#4cc38a" : "#4c8bf5"}
                    stroke="#07080d"
                    strokeWidth={1.5}
                  />
                  <text
                    x={x}
                    y={y - 10}
                    textAnchor="middle"
                    fill="#eef0f5"
                    fontSize={9.5}
                    className="font-mono"
                  >
                    {r.spearman_rho_overall.toFixed(2)}
                  </text>
                  <text
                    x={x}
                    y={H - 8}
                    textAnchor="middle"
                    fill={isNom ? "#4cc38a" : "#7a8296"}
                    fontSize={10}
                    className="font-mono"
                  >
                    {r.factor.toFixed(2)}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        <div className="xl:col-span-7 overflow-x-auto">
          <table className="w-full text-[12px] border-collapse">
            <thead>
              <tr className="border-b hairline text-[#7a8296] text-left">
                <th className="py-2 pr-3 font-normal">c</th>
                <th className="py-2 pr-3 font-normal text-right">
                  {lang === "tr" ? "Ay alb." : "Moon alb."}
                </th>
                <th className="py-2 pr-3 font-normal text-right">Spearman ρ</th>
                <th className="py-2 font-normal">
                  {lang === "tr" ? "1. Sıra" : "#1 Winner"}
                </th>
              </tr>
            </thead>
            <tbody className="font-mono tabular">
              {rows.map((r) => {
                const winSite = sitesById[r.top1_site_id];
                const isNom = Math.abs(r.factor - 0.38) < 0.005;
                return (
                  <tr
                    key={r.factor}
                    onClick={() => onSelectEarth(r.top1_site_id)}
                    className={`border-b hairline last:border-b-0 cursor-pointer hover:bg-[#1a1e28]/60 ${
                      isNom ? "bg-[#4cc38a]/8" : ""
                    }`}
                  >
                    <td className="py-2 pr-3 text-[#eef0f5]">
                      {r.factor.toFixed(2)}
                      {isNom && (
                        <span className="ml-1.5 text-[10px] text-[#4cc38a]">nom</span>
                      )}
                    </td>
                    <td className="py-2 pr-3 text-right text-[#a3a9b8]">
                      {r.moon_albedo_scaled.toFixed(3)}
                    </td>
                    <td className="py-2 pr-3 text-right text-[#eef0f5]">
                      {r.spearman_rho_overall.toFixed(3)}
                    </td>
                    <td className="py-2 font-sans text-[#a3a9b8]">
                      {winSite?.short ?? r.top1_site_id}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
