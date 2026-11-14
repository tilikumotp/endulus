import type { EarthSite, MissionKey, MoonRef, SiteScoreRow } from "./types";

export type AxisName = "mobility" | "surface";

export const PRESET_WEIGHTS: Record<MissionKey, { wMob: number; wSurf: number }> = {
  default: { wMob: 1.0, wSurf: 1.0 },
  rover_mobility: { wMob: 2.0, wSurf: 1.0 },
  radar_calibration: { wMob: 1.0, wSurf: 2.0 },
};

/**
 * Compute live custom-weighted composite scores from base axis scores and intervals.
 * Mirrors `src/scoring/similarity.py::combine_axes` normalized weighted mean.
 */
export function computeWeightedScores(
  baseRows: SiteScoreRow[],
  wMob: number,
  wSurf: number
): SiteScoreRow[] {
  const safeMob = Math.max(0, wMob);
  const safeSurf = Math.max(0, wSurf);
  const sumW = safeMob + safeSurf;
  const wm = sumW > 0 ? safeMob / sumW : 0.5;
  const ws = sumW > 0 ? safeSurf / sumW : 0.5;

  const updated = baseRows.map((r) => {
    const score = wm * r.mob + ws * r.surf;

    let ci_lo: number | null = null;
    let ci_hi: number | null = null;
    let widened = false;

    if (ws === 0 && r.mob_lo !== null && r.mob_hi !== null) {
      ci_lo = r.mob_lo;
      ci_hi = r.mob_hi;
      widened = r.mob_widened;
    } else if (wm === 0 && r.surf_lo !== null && r.surf_hi !== null) {
      ci_lo = r.surf_lo;
      ci_hi = r.surf_hi;
      widened = r.surf_widened;
    } else if (
      r.mob_lo !== null &&
      r.mob_hi !== null &&
      r.surf_lo !== null &&
      r.surf_hi !== null
    ) {
      const mLo = Math.max(0, r.mob - r.mob_lo);
      const mHi = Math.max(0, r.mob_hi - r.mob);
      const sLo = Math.max(0, r.surf - r.surf_lo);
      const sHi = Math.max(0, r.surf_hi - r.surf);
      const loHalf = Math.hypot(wm * mLo, ws * sLo);
      const hiHalf = Math.hypot(wm * mHi, ws * sHi);
      ci_lo = Math.max(0, Math.min(score, score - loHalf));
      ci_hi = Math.min(1, Math.max(score, score + hiHalf));
      widened = r.mob_widened || r.surf_widened;
    }

    return {
      ...r,
      score,
      ci_lo,
      ci_hi,
      widened,
    };
  });

  updated.sort((a, b) => {
    if (Math.abs(b.score - a.score) > 1e-12) return b.score - a.score;
    return a.site_id.localeCompare(b.site_id);
  });

  return updated.map((r, idx) => ({
    ...r,
    rank: idx + 1,
  }));
}

export interface PortfolioResult {
  selected: {
    site_id: string;
    coveredAxes: AxisName[];
    row: SiteScoreRow;
  }[];
  covered: AxisName[];
  uncovered: AxisName[];
  bestPerAxis: Record<AxisName, { site_id: string; score: number } | null>;
}

/**
 * Exact TypeScript port of `src/scoring/portfolio.py::select_portfolio`
 * over active axes `["mobility", "surface"]` at dynamic coverage threshold `minScore`.
 */
export function selectPortfolio(
  rows: SiteScoreRow[],
  minScore: number,
  axes: AxisName[] = ["mobility", "surface"]
): PortfolioResult {
  const remaining = new Set<AxisName>(axes);
  const chosen = new Set<string>();
  const rowById: Record<string, SiteScoreRow> = {};
  for (const r of rows) rowById[r.site_id] = r;

  const bestPerAxis: Record<AxisName, { site_id: string; score: number } | null> = {
    mobility: null,
    surface: null,
  };
  for (const ax of axes) {
    let best: { site_id: string; score: number } | null = null;
    for (const r of rows) {
      const val = ax === "mobility" ? r.mob : r.surf;
      if (!best || val > best.score) best = { site_id: r.site_id, score: val };
    }
    bestPerAxis[ax] = best;
  }

  const selected: PortfolioResult["selected"] = [];
  while (remaining.size > 0) {
    const candidates: { sid: string; coveredNew: AxisName[]; scoreSum: number; row: SiteScoreRow }[] = [];
    const remSorted = [...remaining].sort();
    for (const r of rows) {
      if (chosen.has(r.site_id)) continue;
      const coveredNew: AxisName[] = [];
      let sum = 0;
      for (const ax of remSorted) {
        const val = ax === "mobility" ? r.mob : r.surf;
        if (val >= minScore) {
          coveredNew.push(ax);
          sum += val;
        }
      }
      if (coveredNew.length > 0) {
        candidates.push({ sid: r.site_id, coveredNew, scoreSum: sum, row: r });
      }
    }
    if (candidates.length === 0) break;

    candidates.sort((a, b) => {
      if (b.coveredNew.length !== a.coveredNew.length) {
        return b.coveredNew.length - a.coveredNew.length;
      }
      if (Math.abs(b.scoreSum - a.scoreSum) > 1e-12) {
        return b.scoreSum - a.scoreSum;
      }
      return a.sid.localeCompare(b.sid);
    });

    const pick = candidates[0];
    chosen.add(pick.sid);
    for (const ax of pick.coveredNew) remaining.delete(ax);
    selected.push({
      site_id: pick.sid,
      coveredAxes: pick.coveredNew,
      row: rowById[pick.sid],
    });
  }

  const uncovered = [...remaining].sort() as AxisName[];
  const covered = axes.filter((ax) => !remaining.has(ax));
  return { selected, covered, uncovered, bestPerAxis };
}

/**
 * Min-max normalized radial values [0..1] across all 45 sites (5 Moon + 40 Earth)
 * so both Moon reference and selected Earth site plot on an honest shared radar scale.
 */
export function normalizeRadarAxes(
  moon: MoonRef,
  earth: EarthSite,
  allMoon: MoonRef[],
  allEarth: EarthSite[],
  scoreRow: SiteScoreRow | undefined
) {
  const keys = ["slope_mean", "slope_p90", "roughness", "relief", "albedo"] as const;
  return keys.map((k) => {
    const vals: number[] = [];
    for (const m of allMoon) {
      const v = m[k];
      if (typeof v === "number" && Number.isFinite(v)) vals.push(v);
    }
    for (const e of allEarth) {
      const v = e[k];
      if (typeof v === "number" && Number.isFinite(v)) vals.push(v);
    }
    const min = Math.min(...vals);
    const max = Math.max(...vals);
    const span = max - min || 1;
    const mRaw = moon[k] ?? 0;
    const eRaw = earth[k] ?? 0;
    return {
      key: k,
      moonRaw: mRaw,
      earthRaw: eRaw,
      moonNorm: Math.max(0.06, Math.min(1, (mRaw - min) / span)),
      earthNorm: Math.max(0.06, Math.min(1, (eRaw - min) / span)),
      mobScore: scoreRow?.mob ?? 0,
      surfScore: scoreRow?.surf ?? 0,
    };
  });
}
