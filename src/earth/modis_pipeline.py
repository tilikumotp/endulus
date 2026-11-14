"""Earth MODIS feature extraction pipeline (MOD11A2.061 annual mean temp_amplitude & MCD43A3.061 albedo)."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import struct
from typing import Any
import zlib

import numpy as np
import pyproj
import requests
from rasterio.io import MemoryFile

MOD11A2_SRC = "MOD11A2.061_annual_mean"
MCD43A3_SRC = "MCD43A3.061"
CMR_GRANULES_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"
MODIS_SINU_TILE_M = 1111950.5196666666
MODIS_SINU_PROJ4 = "+proj=sinu +R=6371007.181 +nadgrids=@null +wktext"
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


def _process_single_composite(
    item: dict[str, Any],
    sas_token: str,
    lat: float,
    lon: float,
) -> dict[str, Any] | None:
    """Download and extract valid 3x3 pixel day/night LST pairs from one MOD11A2.061 composite."""
    try:
        day_url = f"{item['assets']['LST_Day_1km']['href']}?{sas_token}"
        night_url = f"{item['assets']['LST_Night_1km']['href']}?{sas_token}"
        b_day = requests.get(day_url, timeout=25).content
        b_night = requests.get(night_url, timeout=25).content

        with MemoryFile(b_day) as m_d, MemoryFile(b_night) as m_n:
            with m_d.open() as src_d, m_n.open() as src_n:
                crs_str = src_d.crs.to_proj4() or str(src_d.crs)
                shape_tuple = (src_d.height, src_d.width)
                res_tuple = (round(abs(src_d.res[0]), 2), round(abs(src_d.res[1]), 2))
                tf = pyproj.Transformer.from_crs("EPSG:4326", src_d.crs, always_xy=True)
                cx, cy = tf.transform(lon, lat)
                row, col = src_d.index(cx, cy)
                win = (
                    (max(0, row - 1), min(src_d.height, row + 2)),
                    (max(0, col - 1), min(src_d.width, col + 2)),
                )
                w_d = src_d.read(1, window=win).astype(np.float64)
                w_n = src_n.read(1, window=win).astype(np.float64)

                valid = (w_d > 0) & (w_n > 0)
                if not np.any(valid):
                    return None
                d_k = w_d[valid] * 0.02
                n_k = w_n[valid] * 0.02
                diff = d_k - n_k
                pos = diff > 0
                if not np.any(pos):
                    return None
                return {
                    "id": item["id"],
                    "amps": diff[pos].tolist(),
                    "days_k": d_k[pos].tolist(),
                    "nights_k": n_k[pos].tolist(),
                    "crs_str": crs_str,
                    "shape": shape_tuple,
                    "res": res_tuple,
                }
    except Exception:
        return None


def fetch_mod11a2_temp_amplitude(
    site_id: str,
    lat: float,
    lon: float,
    raw_dir: Path = Path("data/raw/earth"),
    datetime_range: str = "2024-01-01/2024-12-31",
    max_composites: int = 24,
) -> dict[str, Any]:
    """Extract annual-cycle diurnal temperature amplitude (LST_Day - LST_Night, K) from Terra MOD11A2.061."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    cache_file = raw_dir / f"{site_id}_mod11a2_061_annual_2024.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))

    tr = pyproj.Transformer.from_crs("EPSG:4326", MODIS_SINU_PROJ4, always_xy=True)
    x_s, y_s = tr.transform(lon, lat)
    h_idx = int((x_s + 18.0 * MODIS_SINU_TILE_M) // MODIS_SINU_TILE_M)
    v_idx = int((9.0 * MODIS_SINU_TILE_M - y_s) // MODIS_SINU_TILE_M)
    tile_id = f"h{h_idx:02d}v{v_idx:02d}"

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
            "limit": 250,
        },
        timeout=15,
    )
    stac_resp.raise_for_status()
    features = stac_resp.json().get("features", [])
    all_terra = sorted(
        [
            it
            for it in features
            if it["id"].startswith("MOD11A2.") and f".{tile_id}." in it["id"]
        ],
        key=lambda x: x["id"],
    )
    if len(all_terra) > max_composites:
        idx = np.linspace(0, len(all_terra) - 1, max_composites, dtype=int)
        terra_items = [all_terra[i] for i in idx]
    else:
        terra_items = all_terra

    amps: list[float] = []
    days_k: list[float] = []
    nights_k: list[float] = []
    granule_ids: list[str] = []
    crs_str = ""
    shape_tuple: tuple[int, int] = (0, 0)
    res_tuple: tuple[float, float] = (0.0, 0.0)

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [
            pool.submit(_process_single_composite, it, sas_token, lat, lon)
            for it in terra_items
        ]
        for fut in futures:
            res = fut.result()
            if res is not None:
                amps.extend(res["amps"])
                days_k.extend(res["days_k"])
                nights_k.extend(res["nights_k"])
                granule_ids.append(res["id"])
                crs_str = res["crs_str"]
                shape_tuple = res["shape"]
                res_tuple = res["res"]

    if not amps:
        raise RuntimeError(f"No valid MOD11A2.061 day/night pairs found for {site_id}")

    amps_arr = np.asarray(amps, dtype=np.float64)
    result = {
        "site_id": site_id,
        "datetime_range": datetime_range,
        "temp_amplitude": float(np.mean(amps_arr)),
        "temp_amplitude_sd": float(np.std(amps_arr, ddof=1)) if amps_arr.size > 1 else 1.0,
        "temp_amplitude_src": MOD11A2_SRC,
        "temp_amplitude_res_m": 1000.0,
        "lst_day_mean_k": float(np.mean(days_k)),
        "lst_night_mean_k": float(np.mean(nights_k)),
        "n_valid_samples": int(amps_arr.size),
        "n_valid_composites": len(granule_ids),
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


def _extract_mcd43a3_window(
    sess: requests.Session,
    token: str,
    tile_id: str,
    lat: float,
    lon: float,
    r_in: int,
    col: int,
    sig: bytes,
    temporal: str,
    max_granules: int,
) -> tuple[list[float], list[str]]:
    """Query CMR and extract valid 5x5 Albedo_BSA_shortwave pixels for a given temporal window."""
    cmr_resp = sess.get(
        CMR_GRANULES_URL,
        params={
            "short_name": "MCD43A3",
            "version": "061",
            "point": f"{lon},{lat}",
            "temporal": temporal,
            "page_size": 100,
        },
        timeout=20,
    )
    cmr_resp.raise_for_status()
    entries = [
        e for e in cmr_resp.json().get("feed", {}).get("entry", []) if f".{tile_id}." in e["title"]
    ]
    if not entries:
        return [], []

    if len(entries) > max_granules:
        idx = np.linspace(0, len(entries) - 1, max_granules, dtype=int)
        chosen = [entries[i] for i in idx]
    else:
        chosen = entries

    vals: list[float] = []
    granule_ids: list[str] = []
    auth_hdr = {"Authorization": f"Bearer {token}"}

    for ent in chosen:
        hdf_urls = [
            link["href"]
            for link in ent.get("links", [])
            if link.get("href", "").endswith(".hdf") and link.get("href", "").startswith("https://")
        ]
        if not hdf_urls:
            continue
        hdf_url = hdf_urls[0]
        r_probe = sess.get(hdf_url, headers={**auth_hdr, "Range": "bytes=0-0"}, timeout=20)
        if r_probe.status_code not in (200, 206):
            continue
        total_len = int(r_probe.headers["Content-Range"].split("/")[-1])

        pos = -1
        b0 = 0
        mid = b""
        for frac_lo, frac_hi in ((0.44, 0.52), (0.30, 0.65), (0.10, 0.90)):
            b0, b1 = int(frac_lo * total_len), int(frac_hi * total_len)
            mid = sess.get(
                hdf_url, headers={**auth_hdr, "Range": f"bytes={b0}-{b1}"}, timeout=45
            ).content
            pos = mid.find(sig)
            if pos != -1:
                break
        if pos == -1:
            continue

        comp_slice = mid[pos + 16 : pos + 16 + 350000]
        raw_strip = zlib.decompressobj().decompress(comp_slice)
        if len(raw_strip) < 480000:
            c_start = b0 + pos + 16
            c_end = min(total_len - 1, c_start + 350000)
            comp_slice = sess.get(
                hdf_url, headers={**auth_hdr, "Range": f"bytes={c_start}-{c_end}"}, timeout=35
            ).content
            raw_strip = zlib.decompressobj().decompress(comp_slice)
        if len(raw_strip) < 480000:
            continue
        strip = np.frombuffer(raw_strip[:480000], dtype=">i2").reshape(100, 2400)
        win = strip[max(0, r_in - 2) : min(100, r_in + 3), max(0, col - 2) : min(2400, col + 3)]
        valid = win[(win >= 0) & (win < 32767)].astype(np.float64) * 0.001
        if valid.size > 0:
            vals.extend(valid.tolist())
            granule_ids.append(ent["title"])

    return vals, granule_ids


def fetch_mcd43a3_albedo(
    site_id: str,
    lat: float,
    lon: float,
    raw_dir: Path = Path("data/raw/earth"),
    temporal: str = "2024-07-01T00:00:00Z,2024-08-31T23:59:59Z",
    max_granules: int = 4,
) -> dict[str, Any] | None:
    """Extract broadband shortwave black-sky albedo (Albedo_BSA_shortwave, DN * 0.001, 500m) from MCD43A3.061."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    cache_file = raw_dir / f"{site_id}_mcd43a3_061.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))

    token = _load_dotenv_token("EARTHDATA_TOKEN")
    if not token:
        return None

    tr = pyproj.Transformer.from_crs("EPSG:4326", MODIS_SINU_PROJ4, always_xy=True)
    x, y = tr.transform(lon, lat)
    h_idx = int((x + 18.0 * MODIS_SINU_TILE_M) // MODIS_SINU_TILE_M)
    v_idx = int((9.0 * MODIS_SINU_TILE_M - y) // MODIS_SINU_TILE_M)
    tile_id = f"h{h_idx:02d}v{v_idx:02d}"
    ulx = (h_idx - 18.0) * MODIS_SINU_TILE_M
    uly = (9.0 - v_idx) * MODIS_SINU_TILE_M
    px_m = MODIS_SINU_TILE_M / 2400.0
    col = int((x - ulx) / px_m)
    row = int((uly - y) / px_m)
    y_chk = row // 100
    r_in = row % 100

    # Albedo_BSA_shortwave is DataField_20 (SDS ref=458); 100x2400 strip y_chk has tag=40 ref=457+y_chk
    c_ref = 457 + y_chk
    sig = b"\x00\x03\x00\x00\x00\x07S\x00" + struct.pack(">H", c_ref) + b"\x00\x00\x00\x04\x00\x04"

    south_summer = "2024-01-01T00:00:00Z,2024-02-28T23:59:59Z"
    windows = [south_summer, temporal] if lat < -45.0 else [temporal, south_summer]

    sess = requests.Session()
    vals: list[float] = []
    granule_ids: list[str] = []
    used_temporal = windows[0]
    for win_temp in windows:
        vals, granule_ids = _extract_mcd43a3_window(
            sess, token, tile_id, lat, lon, r_in, col, sig, win_temp, max_granules
        )
        if vals:
            used_temporal = win_temp
            break

    if not vals:
        return None

    arr = np.asarray(vals, dtype=np.float64)
    result = {
        "site_id": site_id,
        "tile_id": tile_id,
        "temporal": used_temporal,
        "albedo": float(np.mean(arr)),
        "albedo_sd": max(float(np.std(arr, ddof=1)), 1e-4) if arr.size > 1 else 0.01,
        "albedo_src": MCD43A3_SRC,
        "albedo_res_m": 500.0,
        "n_valid_samples": int(arr.size),
        "n_valid_granules": len(granule_ids),
        "granules": granule_ids,
        "native_shape": [2400, 2400],
        "native_res_m": [round(px_m, 2), round(px_m, 2)],
        "crs_proj4": MODIS_SINU_PROJ4,
    }
    cache_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
