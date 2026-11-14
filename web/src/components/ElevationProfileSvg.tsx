import type { DemTile, Lang } from "../types";

interface Props {
  moonTile: DemTile | undefined;
  earthTile: DemTile | undefined;
  moonName: string;
  earthName: string;
  lang: Lang;
}

/**
 * Dual-transect (West-East & South-North) elevation cross-section plot comparing
 * 5 m/px LRO LOLA Moon relief against 30 m/px Copernicus/NASADEM Earth relief.
 */
export function ElevationProfileSvg({
  moonTile,
  earthTile,
  moonName,
  earthName,
  lang,
}: Props) {
  if (!moonTile || !earthTile) return null;

  const panels = [
    {
      title: lang === "tr" ? "Doğu–Batı kesiti (Δz)" : "West–East transect (Δz)",
      mx: moonTile.profile_we_m,
      mz: moonTile.profile_we_dz_m,
      ex: earthTile.profile_we_m,
      ez: earthTile.profile_we_dz_m,
    },
    {
      title: lang === "tr" ? "Kuzey–Güney kesiti (Δz)" : "South–North transect (Δz)",
      mx: moonTile.profile_sn_m,
      mz: moonTile.profile_sn_dz_m,
      ex: earthTile.profile_sn_m,
      ez: earthTile.profile_sn_dz_m,
    },
  ];

  const W = 400;
  const H = 165;
  const padL = 42;
  const padR = 14;
  const padT = 14;
  const padB = 26;

  return (
    <div className="rounded-xl border hairline bg-[#11141c] p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h4 className="text-[14px] font-medium text-[#eef0f5]">
            {lang === "tr"
              ? "Merkez çap boyunca yükseklik kesitleri (±1100 m)"
              : "Centerline elevation cross-sections (±1100 m)"}
          </h4>
          <p className="text-[12px] text-[#7a8296] mt-0.5">
            {lang === "tr"
              ? "Taralı alan r = 1000 m analiz sınırını gösterir"
              : "Shaded bracket marks the r = 1000 m analysis perimeter"}
          </p>
        </div>

        <div className="flex items-center gap-4 text-[11.5px]">
          <span className="flex items-center gap-1.5 text-[#a3a9b8]">
            <span className="w-3 h-0.5 bg-[#4c8bf5]" />
            {moonName} (5 m)
          </span>
          <span className="flex items-center gap-1.5 text-[#a3a9b8]">
            <span className="w-3 h-0.5 bg-[#4cc38a]" />
            {earthName} (30 m)
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        {panels.map((p) => {
          const allZ = [...p.mz, ...p.ez, 0];
          const minZ = Math.min(...allZ);
          const maxZ = Math.max(...allZ);
          const pad = Math.max(20, (maxZ - minZ) * 0.1);
          const yMin = minZ - pad;
          const yMax = maxZ + pad;

          const toX = (m: number) =>
            padL + ((m + 1110) / 2220) * (W - padL - padR);
          const toY = (z: number) =>
            padT + ((yMax - z) / (yMax - yMin || 1)) * (H - padT - padB);

          const mPath = p.mx
            .map((x, i) => `${i === 0 ? "M" : "L"}${toX(x).toFixed(1)},${toY(p.mz[i]).toFixed(1)}`)
            .join(" ");
          const ePath = p.ex
            .map((x, i) => `${i === 0 ? "M" : "L"}${toX(x).toFixed(1)},${toY(p.ez[i]).toFixed(1)}`)
            .join(" ");

          const yZero = toY(0);
          const xNeg1k = toX(-1000);
          const xPos1k = toX(1000);

          return (
            <div key={p.title} className="rounded-lg border hairline bg-[#07080d] p-3">
              <div className="text-[12px] font-medium text-[#c7cddb] mb-2">{p.title}</div>
              <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto block">
                <rect
                  x={xNeg1k}
                  y={padT}
                  width={xPos1k - xNeg1k}
                  height={H - padT - padB}
                  fill="rgba(238,240,245,0.025)"
                />
                <line
                  x1={xNeg1k}
                  y1={padT}
                  x2={xNeg1k}
                  y2={H - padB}
                  stroke="rgba(238,240,245,0.12)"
                  strokeDasharray="3 3"
                />
                <line
                  x1={xPos1k}
                  y1={padT}
                  x2={xPos1k}
                  y2={H - padB}
                  stroke="rgba(238,240,245,0.12)"
                  strokeDasharray="3 3"
                />
                <line
                  x1={padL}
                  y1={yZero}
                  x2={W - padR}
                  y2={yZero}
                  stroke="rgba(238,240,245,0.14)"
                  strokeWidth={1}
                />

                <path d={mPath} fill="none" stroke="#4c8bf5" strokeWidth={1.8} />
                <path d={ePath} fill="none" stroke="#4cc38a" strokeWidth={1.8} />

                <text x={padL - 5} y={padT + 8} textAnchor="end" fill="#7a8296" fontSize={9.5} className="font-mono">
                  {Math.round(maxZ)} m
                </text>
                <text x={padL - 5} y={H - padB} textAnchor="end" fill="#7a8296" fontSize={9.5} className="font-mono">
                  {Math.round(minZ)} m
                </text>
                <text x={xNeg1k} y={H - 8} textAnchor="middle" fill="#7a8296" fontSize={9.5} className="font-mono">
                  -1 km
                </text>
                <text x={toX(0)} y={H - 8} textAnchor="middle" fill="#7a8296" fontSize={9.5} className="font-mono">
                  0
                </text>
                <text x={xPos1k} y={H - 8} textAnchor="middle" fill="#7a8296" fontSize={9.5} className="font-mono">
                  +1 km
                </text>
              </svg>
            </div>
          );
        })}
      </div>
    </div>
  );
}
