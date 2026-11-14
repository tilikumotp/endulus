"""Earth MODIS feature extraction pipeline (MOD11A2.061 temp_amplitude & MCD43A3.061 albedo)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import numpy as np
import pyproj
import requests
from rasterio.io import MemoryFile

MOD11A2_SRC = "MOD11A2.061"
MCD43A3_SRC = "MCD43A3.061"
PC_STAC_SEARCH_URL = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
PC_MODIS_SAS_URL = (
    "https://planetarycomputer.microsoft.com/api/sas/v1/token/modiseuwest/modis-061-cogs"
)


def _load_dotenv_token(key: str = "EARTHDATA_TOKEN") -> str | None:
    """Read an environment variable from os.environ or a local .env file if present."""
    if os.environ.get(key):
        return os.environ[key].strip()
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line_s = line.strip()
            if line_s.startswith(f"{key}="):
                return line_s.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def fetch_mod11a2_temp_amplitude(
    site_id: str,
    lat: float,
    lon: float,
    raw_dir: Path = Path("data/raw/earth"),
    datetime_range: str = "2025-06-01/2025-08-31",
    max_composites: int = 4,
) -> dict[str, Any]:
    """Extract diurnal temperature amplitude (LST_Day - LST_Night, K) from Terra MOD11A2.061 COGs."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    cache_file = raw_dir / f"{site_id}_mod11a2_061.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))

    sess = requests.Session()
    sas_resp = sess.get(PC_MODIS_SAS_URL, timeout=15)
    sas_resp.raise_for_status()
    sas_token = sas_resp.json()["token"]

    stac_resp = sess.post(
        PC_STAC_SEARCH_URL,
        json={
            "collections": ["modis-11A2-061"],
            "intersects": {"type": "Point", "coordinates": [lon, lat]},
            "datetime": datetime_range,
            "limit": 20,
        },
        timeout=15,
    )
    stac_resp.raise_for_status()
    features = stac_resp.json().get("features", [])
    terra_items = sorted(
        [it for it in features if it["id"].startswith("MOD11A2.")],
        key=lambda x: x["id"],
    )[:max_composites]

    amps: list[float] = []
    days_k: list[float] = []
    nights_k: list[float] = []
    granule_ids: list[str] = []
    crs_str = ""
    shape_tuple: tuple[int, int] = (0, 0)
    res_tuple: tuple[float, float] = (0.0, 0.0)

    for it in terra_items:
        day_url = f"{it['assets']['LST_Day_1km']['href']}?{sas_token}"
        night_url = f"{it['assets']['LST_Night_1km']['href']}?{sas_token}"
        b_day = sess.get(day_url, timeout=20).content
        b_night = sess.get(night_url, timeout=20).content

        with MemoryFile(b_day) as m_d, MemoryFile(b_night) as m_n:
            with m_d.open() as src_d, m_n.open() as src_n:
                crs_str = src_d.crs.to_proj4() or str(src_d.crs)
                shape_tuple = (src_d.height, src_d.width)
                res_tuple = (round(abs(src_d.res[0]), 2), round(abs(src_d.res[1]), 2))
                tf = pyproj.Transformer.from_crs("EPSG:4326", src_d.crs, always_xy=True)
                cx, cy = tf.transform(lon, lat)
                row, col = src_d.index(cx, cy)
                win = ((max(0, row - 1), min(src_d.height, row + 2)), (max(0, col - 1), min(src_d.width, col + 2)))
                w_d = src_d.read(1, window=win).astype(np.float64)
                w_n = src_n.read(1, window=win).astype(np.float64)

                valid = (w_d > 0) & (w_n > 0)
                if np.any(valid):
                    d_k = w_d[valid] * 0.02
                    n_k = w_n[valid] * 0.02
                    diff = d_k - n_k
                    pos = diff > 0
                    if np.any(pos):
                        amps.extend(diff[pos].tolist())
                        days_k.extend(d_k[pos].tolist())
                        nights_k.extend(n_k[pos].tolist())
                        granule_ids.append(it["id"])

    if not amps:
        raise RuntimeError(f"No valid MOD11A2.061 day/night pairs found for {site_id}")

    amps_arr = np.asarray(amps, dtype=np.float64)
    result = {
        "site_id": site_id,
        "temp_amplitude": float(np.mean(amps_arr)),
        "temp_amplitude_sd": float(np.std(amps_arr, ddof=1)) if amps_arr.size > 1 else 1.0,
        "temp_amplitude_src": MOD11A2_SRC,
        "temp_amplitude_res_m": 1000.0,
        "lst_day_mean_k": float(np.mean(days_k)),
        "lst_night_mean_k": float(np.mean(nights_k)),
        "n_valid_samples": int(amps_arr.size),
        "granules": granule_ids,
        "native_shape": list(shape_tuple),
        "native_res_m": list(res_tuple),
        "crs_proj4": crs_str,
    }
    cache_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def check_mcd43a3_access() -> tuple[bool, str]:
    """Check whether MCD43A3.061 is accessible via Planetary Computer or EARTHDATA_TOKEN."""
    r_pc = requests.get(
        "https://planetarycomputer.microsoft.com/api/stac/v1/collections/modis-43A3-061",
        timeout=10,
    )
    if r_pc.status_code == 200:
        return True, "Planetary Computer modis-43A3-061 available"

    token = _load_dotenv_token("EARTHDATA_TOKEN")
    if token:
        return True, "EARTHDATA_TOKEN present in environment/.env"

    return (
        False,
        "Planetary Computer does not host modis-43A3-061 (HTTP 404; only MCD43A4 NBAR exists), "
        "and NASA LP DAAC (s3://lp-prod-protected/MCD43A3.061) requires EARTHDATA_TOKEN (HTTP 302 to urs.earthdata.nasa.gov).",
    )
