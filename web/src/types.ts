export type Lang = "tr" | "en";
export type MissionKey = "default" | "rover_mobility" | "isru_ice" | "radar_calibration";
export type FilterKey = "all" | "tr" | "validation" | "global";
export type WorkbenchTab = "overview" | "terrain" | "validation" | "figures";

export interface MoonRef {
  site_id: string;
  name_tr: string;
  name_en: string;
  lat: number;
  lon: number;
  lithology: string;
  slope_mean: number;
  slope_mean_sd: number;
  slope_p90: number;
  roughness: number;
  relief: number;
  albedo: number;
  albedo_sd: number;
  dem_src: string;
  dem_res_m: number;
  albedo_src: string;
  albedo_res_m: number;
  thumb_img: string;
  hillshade_img: string;
  hazard_img: string;
  atlas_plate_img: string;
  pct_lt10deg: number | null;
  pct_10_20deg: number | null;
  pct_gt20deg: number | null;
  elev_min_m: number | null;
  elev_max_m: number | null;
  portfolio_070: {
    selected: string[];
    covered: string[];
    uncovered: string[];
  };
}

export interface ValidationMeta {
  expected_v1: string;
  ice_e8: string;
  ice_e8_en: string;
  rationale_tr: string;
  rationale_en: string;
  source_label: string;
  source_url: string;
}

export interface EarthSite {
  site_id: string;
  name: string;
  short: string;
  role: "validation" | "candidate";
  is_tr: boolean;
  continent: string;
  lat: number;
  lon: number;
  lithology: string;
  slope_mean: number;
  slope_mean_sd: number | null;
  slope_p90: number;
  roughness: number;
  relief: number;
  albedo: number;
  albedo_sd: number | null;
  dem_src: string;
  dem_res_m: number;
  albedo_src: string;
  albedo_res_m: number;
  temp_amplitude: number | null;
  temp_src: string;
  citation: string;
  atlas_img: string;
  s2_scene: string;
  s2_date: string;
  s2_cloud_pct: number | null;
  validation: ValidationMeta | null;
}

export interface SiteScoreRow {
  site_id: string;
  score: number;
  ci_lo: number | null;
  ci_hi: number | null;
  widened: boolean;
  rank: number;
  mob: number;
  mob_lo: number | null;
  mob_hi: number | null;
  mob_widened: boolean;
  mob_rank: number;
  surf: number;
  surf_lo: number | null;
  surf_hi: number | null;
  surf_widened: boolean;
  surf_rank: number;
}

export interface FeatureGap {
  axis: string;
  feature: string;
  moon_val: number | null;
  earth_val: number | null;
  diff: number | null;
  z_diff: number | null;
}

export interface AlbedoSensitivityRow {
  ref_site_id: string;
  factor: number;
  moon_albedo_scaled: number;
  mean_surface_score_delta: number;
  mean_overall_score_delta: number;
  spearman_rho_overall: number;
  top1_site_id: string;
  top3_site_ids: string[];
  top1_candidate_id: string;
}

export interface MixedPixelAuditRow {
  site_id: string;
  label: string;
  lat: number;
  lon: number;
  wc_bare_pct: number;
  wc_water_pct: number;
  wc_snow_pct: number;
  wc_crop_pct: number;
  wc_veg_pct: number;
  wc_built_pct: number;
  wc_scene_id: string;
  s2_bare_or_dark_pct: number;
  s2_veg_pct: number;
  s2_water_pct: number;
  s2_snow_pct: number;
  s2_scene_id: string;
  mixed_pixel_flag: string;
  is_mixed: boolean;
  rule_is_mixed: boolean;
  rule_flag: string;
  note: string;
}

export interface AppDataPayload {
  meta: {
    moon_count: number;
    earth_count: number;
    validation_count: number;
    tr_candidate_count: number;
    global_candidate_count: number;
    active_axes: string[];
    suspended_axes: string[];
    tests_passed: string;
    mock_rows: number;
    albedo_factors: number[];
  };
  moon_refs: MoonRef[];
  earth_sites: EarthSite[];
  comparisons: Record<string, Record<MissionKey, SiteScoreRow[]>>;
  gaps: Record<string, Record<string, FeatureGap[]>>;
  albedo_sensitivity: AlbedoSensitivityRow[];
  mixed_pixel_audit: MixedPixelAuditRow[];
  dimensions: {
    tr: Record<string, string>[];
    en: Record<string, string>[];
  };
  bibliography: {
    moon_tr: string[];
    moon_en: string[];
    earth_tr: string[];
    earth_en: string[];
  };
}

export interface DemTile {
  body: "moon" | "earth";
  half_width_m: number;
  native_res_m: number;
  relief_m: number;
  grid: number[][];
  profile_we_m: number[];
  profile_we_dz_m: number[];
  profile_sn_m: number[];
  profile_sn_dz_m: number[];
}

export type DemArchive = Record<string, DemTile>;
