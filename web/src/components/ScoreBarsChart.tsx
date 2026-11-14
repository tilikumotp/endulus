import type { EarthSite, Lang, SiteScoreRow } from "../types";

export type ChartAxisMode = "overall" | "mobility" | "surface";

interface Props {
  rows: SiteScoreRow[];
  sitesById: Record<string, EarthSite>;
  selectedId: string;
  onSelect: (siteId: string) => void;
  mode: ChartAxisMode;
  onModeChange: (m: ChartAxisMode) => void;
  title: string;
  note: string;
  modeLabels: { overall: string; mobility: string; surface: string };
  lang: Lang;
}

export function ScoreBarsChart({
  rows,
  sitesById,
  selectedId,
  onSelect,
  mode,
  onModeChange,
  title,
  note,
  modeLabels,
  lang,
}: Props) {
  const visible = rows.slice(0, 12);

  return (
    <div className="rounded-xl border hairline bg-[#11141c] p-5 flex flex-col gap-4">
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <h3 className="text-[15px] font-medium text-[#eef0f5]">{title}</h3>
          <p className="text-[12px] text-[#7a8296] mt-0.5">{note}</p>
        </div>

        <div className="inline-flex rounded-lg p-1 bg-[#07080d] border hairline">
          {(["overall", "mobility", "surface"] as ChartAxisMode[]).map((m) => (
            <button
              key={m}
              type="button"
              onClick={() => onModeChange(m)}
              className={`px-3 py-1 rounded-md text-[12px] font-medium transition-colors duration-150 ${
                mode === m
                  ? "active-highlight text-[#eef0f5]"
                  : "text-[#7a8296] hover:text-[#eef0f5]"
              }`}
            >
              {modeLabels[m]}
            </button>
          ))}
        </div>
      </div>

      <div className="flex flex-col gap-2">
        {visible.map((r, idx) => {
          const site = sitesById[r.site_id];
          if (!site) return null;

          const val = mode === "overall" ? r.score : mode === "mobility" ? r.mob : r.surf;
          const lo = mode === "overall" ? r.ci_lo : mode === "mobility" ? r.mob_lo : r.surf_lo;
          const hi = mode === "overall" ? r.ci_hi : mode === "mobility" ? r.mob_hi : r.surf_hi;
          const wid =
            mode === "overall" ? r.widened : mode === "mobility" ? r.mob_widened : r.surf_widened;
          const rankShown =
            mode === "overall" ? r.rank : mode === "mobility" ? r.mob_rank : r.surf_rank;

          const isSelected = r.site_id === selectedId;
          const isLead = idx === 0;
          const fill = isSelected || isLead ? "#4c8bf5" : "#4b5568";

          return (
            <button
              key={r.site_id}
              type="button"
              onClick={() => onSelect(r.site_id)}
              className={`w-full text-left px-3 py-2 rounded-lg border transition-colors duration-150 flex items-center gap-3 ${
                isSelected
                  ? "active-highlight border-[#4c8bf5]/45"
                  : "border-transparent hover:bg-[#1a1e28]/70"
              }`}
            >
              <span className="font-mono tabular text-[12px] text-[#7a8296] w-8 shrink-0">
                #{rankShown}
              </span>

              <div className="w-32 sm:w-48 shrink-0 flex items-center gap-2 min-w-0">
                <span
                  className={`w-2 h-2 rounded-full shrink-0 ${
                    site.role === "validation"
                      ? "bg-[#4c8bf5]"
                      : site.is_tr
                        ? "bg-[#4cc38a]"
                        : "bg-[#7a8296]"
                  }`}
                />
                <span className="text-[12.5px] sm:text-[13px] text-[#eef0f5] truncate">{site.short}</span>
              </div>

              <div className="flex-1 min-w-[60px] relative h-5 bg-[#07080d] rounded border hairline overflow-hidden">
                <div
                  className="h-full rounded-sm transition-[width,background-color] duration-300 ease-instrument"
                  style={{ width: `${Math.max(2, val * 100)}%`, backgroundColor: fill }}
                />
                {lo !== null && hi !== null && (
                  <>
                    <div
                      className="absolute top-1/2 -translate-y-1/2 h-[2px] bg-[#eef0f5]/80 pointer-events-none transition-[left,width,opacity] duration-300 ease-instrument"
                      style={{
                        left: `${Math.max(0, lo * 100)}%`,
                        width: `${Math.max(0.5, (hi - lo) * 100)}%`,
                      }}
                    />
                    <div
                      className="absolute top-1 bottom-1 w-[1.5px] bg-[#eef0f5]/90 pointer-events-none"
                      style={{ left: `${Math.max(0, lo * 100)}%` }}
                    />
                    <div
                      className="absolute top-1 bottom-1 w-[1.5px] bg-[#eef0f5]/90 pointer-events-none"
                      style={{ left: `${Math.min(99.5, hi * 100)}%` }}
                    />
                  </>
                )}
              </div>

              <div className="w-14 sm:w-36 text-right font-mono tabular text-[12px] shrink-0 whitespace-nowrap">
                <span className="text-[#eef0f5] font-medium">{val.toFixed(3)}</span>
                {lo !== null && hi !== null && (
                  <span className="hidden sm:inline text-[#7a8296] ml-1.5">
                    [{lo.toFixed(2)}–{hi.toFixed(2)}
                    {wid ? "*" : ""}]
                  </span>
                )}
              </div>
            </button>
          );
        })}
      </div>

      <div className="flex items-center justify-between flex-wrap gap-3 text-[11px] text-[#7a8296] pt-1 border-t hairline">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#4c8bf5]" />
            {lang === "tr" ? "Doğrulama (10)" : "Validation (10)"}
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#4cc38a]" />
            {lang === "tr" ? "Türkiye adayı (14)" : "Turkey candidate (14)"}
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#7a8296]" />
            {lang === "tr" ? "Küresel aday (16)" : "Global candidate (16)"}
          </span>
        </div>
        <span className="font-mono">
          {lang === "tr"
            ? "* Nokta tahminini kapsamak için genişletilen aralık"
            : "* Interval widened to enclose point estimate"}
        </span>
      </div>
    </div>
  );
}
