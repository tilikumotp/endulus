import { selectPortfolio } from "../scoring";
import type { EarthSite, Lang, SiteScoreRow } from "../types";

interface Props {
  rows: SiteScoreRow[];
  sitesById: Record<string, EarthSite>;
  moonName: string;
  threshold: number;
  onThresholdChange: (next: number) => void;
  onSelectSite: (siteId: string) => void;
  lang: Lang;
}

/**
 * Interactive greedy set-cover portfolio optimizer backed directly by `rows`:
 * shows the minimal Earth test-site team covering the most axes at `threshold`.
 */
export function PortfolioOptimizerCard({
  rows,
  sitesById,
  moonName,
  threshold,
  onThresholdChange,
  onSelectSite,
  lang,
}: Props) {
  const result = selectPortfolio(rows, threshold, ["mobility", "surface"]);

  const axisName = (ax: "mobility" | "surface") =>
    ax === "mobility"
      ? lang === "tr"
        ? "Mobilite"
        : "Mobility"
      : lang === "tr"
        ? "Yüzey"
        : "Surface";

  return (
    <div className="rounded-xl border hairline bg-[#11141c] p-5 flex flex-col justify-between gap-4">
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <h3 className="text-[15px] font-medium text-[#eef0f5]">
            {lang === "tr"
              ? "Kompakt test sahası portföyü"
              : "Compact test-site portfolio"}
          </h3>
          <p className="text-[12px] text-[#7a8296] mt-0.5">
            {lang === "tr"
              ? `${moonName} için eşiği aşan en küçük saha kümesi`
              : `Minimal site team exceeding threshold on ${moonName}`}
          </p>
        </div>

        <span className="text-[12px] font-mono tabular px-2.5 py-1 rounded bg-[#07080d] border hairline text-[#eef0f5]">
          {lang === "tr" ? "Eşik:" : "Min:"} {threshold.toFixed(2)}
        </span>
      </div>

      {/* Live threshold slider */}
      <div className="rounded-lg border hairline bg-[#07080d] p-3 flex flex-col gap-2">
        <div className="flex items-center justify-between text-[11.5px] font-mono tabular text-[#a3a9b8]">
          <span>0.50</span>
          <span className="text-[#4c8bf5]">
            {lang === "tr" ? "Sezgisel benzerlik eşiği" : "Similarity threshold"}:{" "}
            {threshold.toFixed(2)}
          </span>
          <span>0.90</span>
        </div>
        <input
          type="range"
          min="0.50"
          max="0.90"
          step="0.05"
          value={threshold}
          onChange={(e) => onThresholdChange(parseFloat(e.target.value))}
          aria-label={lang === "tr" ? "Portföy kapsam eşiği" : "Portfolio coverage threshold"}
          className="w-full accent-[#4c8bf5] cursor-pointer"
        />
      </div>

      {/* Selected site team */}
      <div className="flex flex-col gap-2">
        {result.selected.length > 0 ? (
          result.selected.map((pick, i) => {
            const site = sitesById[pick.site_id];
            if (!site) return null;
            return (
              <button
                key={pick.site_id}
                type="button"
                onClick={() => onSelectSite(pick.site_id)}
                className="w-full text-left px-3 py-2.5 rounded-lg bg-[#07080d] border hairline hover:border-[#4c8bf5]/50 transition-colors duration-150 flex items-center justify-between gap-3"
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  <span className="text-[11px] font-mono text-[#4c8bf5] w-5 shrink-0">
                    #{i + 1}
                  </span>
                  <span className="text-[13px] font-medium text-[#eef0f5] truncate">
                    {site.short}
                  </span>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  {pick.coveredAxes.map((ax) => (
                    <span
                      key={ax}
                      className="text-[11px] font-mono px-2 py-0.5 rounded bg-[#4cc38a]/15 text-[#4cc38a] border border-[#4cc38a]/30"
                    >
                      {axisName(ax)} {(ax === "mobility" ? pick.row.mob : pick.row.surf).toFixed(2)}
                    </span>
                  ))}
                </div>
              </button>
            );
          })
        ) : (
          <div className="px-3 py-2.5 rounded-lg bg-[#07080d] border hairline text-[12px] text-[#7a8296]">
            {lang === "tr"
              ? "Bu eşikte hiçbir saha tek bir ekseni tam karşılamıyor"
              : "No single site reaches this threshold"}
          </div>
        )}
      </div>

      {/* Uncovered & laboratory fallback disclosure */}
      <div className="pt-2 border-t hairline text-[12px] flex flex-col gap-1.5">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <span className="text-[#7a8296]">
            {lang === "tr" ? "Laboratuvara / simülasyona kalan:" : "Left for lab / simulation:"}
          </span>
          <span className="font-mono text-[#e5484d]">
            {[
              ...result.uncovered.map((a) => axisName(a)),
              lang === "tr" ? "Termal (askıda)" : "Thermal (suspended)",
            ].join(" · ")}
          </span>
        </div>
        {result.bestPerAxis.mobility && result.uncovered.includes("mobility") && (
          <div className="text-[11.5px] text-[#7a8296]">
            {lang === "tr" ? "Havuzdaki en yüksek Mobilite:" : "Best pool Mobility:"}{" "}
            <button
              type="button"
              onClick={() => onSelectSite(result.bestPerAxis.mobility!.site_id)}
              className="text-[#4c8bf5] hover:underline font-medium"
            >
              {sitesById[result.bestPerAxis.mobility.site_id]?.short} (
              {result.bestPerAxis.mobility.score.toFixed(3)})
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
