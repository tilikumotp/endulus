"""Axis definitions shared by the scoring modules (leader-owned)."""
from __future__ import annotations

# Each axis maps to the numeric feature columns (contract sec 5) it scores.
AXES: dict[str, list[str]] = {
    "mobility": ["slope_mean", "slope_p90", "roughness", "relief"],
    "thermal": ["temp_amplitude", "thermal_inertia"],
    "surface": ["albedo"],
}
