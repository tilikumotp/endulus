"""Axis definitions shared by the scoring modules (leader-owned)."""
from __future__ import annotations

# Each axis maps to the numeric feature columns (contract sec 5) it scores.
AXES: dict[str, list[str]] = {
    "mobility": ["slope_mean", "slope_p90", "roughness", "relief"],
    "thermal": ["temp_amplitude", "thermal_inertia"],
    "surface": ["albedo"],
}

# v0 mission presets for the app's mission selector (relative axis weights;
# normalization happens in combine_axes). Leader tunes after real-data trials.
MISSION_PRESETS: dict[str, dict[str, float]] = {
    "default": {"mobility": 1.0, "thermal": 1.0, "surface": 1.0},
    "rover_mobility": {"mobility": 2.0, "thermal": 0.5, "surface": 1.0},
    "isru_ice": {"mobility": 0.5, "thermal": 2.0, "surface": 1.0},
    "radar_calibration": {"mobility": 1.0, "thermal": 1.0, "surface": 2.0},
}
