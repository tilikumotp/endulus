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
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

MOD11A2_SRC = "MOD11A2.061_annual_mean"
MCD43A3_SRC = "MCD43A3.061"
MCD43A4_LIANG_SRC = "MCD43A4.061_Liang2001"
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


def _make_retrying_session() -> requests.Session:
    """Create a requests.Session configured with bounded exponential backoff retries."""
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=0.8,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
        raise_on_status=False,
    )
    sess = requests.Session()
    adapter = HTTPAdapter(max_retries=retry, pool_connections=16, pool_maxsize=16)
    sess.mount("https://", adapter)
    sess.mount("http://", adapter)
    return sess


def _process_single_composite(
    item: dict[str, Any],
    sas_token: str,
    lat: float,
    lon: float,
    sess: requests.Session | None = None,
) -> dict[str, Any] | None:
    """Download and extract valid 3x3 pixel day/night LST pairs from one MOD11A2.061 composite with QC_Day/QC_Night mask."""
    http = sess if sess is not None else _make_retrying_session()
    try:
        day_url = f"{item['assets']['LST_Day_1km']['href']}?{sas_token}"
        night_url = f"{item['assets']['LST_Night_1km']['href']}?{sas_token}"
        qc_d_url = f"{item['assets']['QC_Day']['href']}?{sas_token}"
        qc_n_url = f"{item['assets']['QC_Night']['href']}?{sas_token}"
        r_day = http.get(day_url, timeout=25)
        r_night = http.get(night_url, timeout=25)
        r_qcd = http.get(qc_d_url, timeout=25)
        r_qcn = http.get(qc_n_url, timeout=25)
        for resp in (r_day, r_night, r_qcd, r_qcn):
            resp.raise_for_status()
        b_day, b_night, b_qcd, b_qcn = r_day.content, r_night.content, r_qcd.content, r_qcn.content

        with (
            MemoryFile(b_day) as m_d,
            MemoryFile(b_night) as m_n,
            MemoryFile(b_qcd) as m_qd,
            MemoryFile(b_qcn) as m_qn,
        ):
            with (
                m_d.open() as src_d,
                m_n.open() as src_n,
                m_qd.open() as src_qd,
                m_qn.open() as src_qn,
            ):
                crs_str = src_d.crs.to_proj4() or str(src_d.crs)
                shape_tuple = (src_d.height, src_d.width)
                res_tuple = (round(abs(src_d.res[0]), 2), round(abs(src_d.res[1]), 2))
                tf = pyproj.Transformer.from_crs("EPSG:4326", src_d.crs, always_xy=True)
                cx, cy = tf.transform(lon, lat)
                row, col = src_d.index(cx, cy)
                if not (0 <= row < src_d.height and 0 <= col < src_d.width):
                    return None
                win = (
                    (max(0, row - 1), min(src_d.height, row + 2)),
                    (max(0, col - 1), min(src_d.width, col + 2)),
                )
                w_d = src_d.read(1, window=win).astype(np.float64)
                w_n = src_n.read(1, window=win).astype(np.float64)
                qc_d = src_qd.read(1, window=win).astype(np.uint16)
                qc_n = src_qn.read(1, window=win).astype(np.uint16)

                # MOD11A2.061: valid DN range 7500..65535, scale 0.02 K, Mandatory QA bits 0-1 <= 1
                valid = (
                    (w_d >= 7500)
                    & (w_n >= 7500)
                    & ((qc_d & 0b11) <= 1)
                    & ((qc_n & 0b11) <= 1)
                )
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
    except Exception as exc:
        print(f"  [WARN] MOD11A2 composite {item.get('id', '?')} failed: {exc}", flush=True)
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

    sess = _make_retrying_session()
    sas_resp = sess.get(PC_MODIS_SAS_URL, timeout=15)
    sas_resp.raise_for_status()
    sas_token = sas_resp.json()["token"]

    stac_resp = sess.post(
        PC_STAC_SEARCH_URL,
        json={
            "collections": ["modis-11A2-061"],
            "query": {
                "modis:horizontal-tile": {"eq": h_idx},
                "modis:vertical-tile": {"eq": v_idx},
            },
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
            pool.submit(_process_single_composite, it, sas_token, lat, lon, sess)
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


def fetch_mcd43a4_nbar_albedo_liang2001(
    site_id: str,
    lat: float,
    lon: float,
    raw_dir: Path = Path("data/raw/earth"),
    datetime_range: str = "2024-07-01/2024-08-31",
    max_granules: int = 4,
) -> dict[str, Any] | None:
    """Derive broadband shortwave albedo from Planetary Computer MCD43A4.061 NBAR via Liang (2001) with QA<=1 & NDSI<0.40."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    cache_file = raw_dir / f"{site_id}_mcd43a4_liang2001.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))

    tr = pyproj.Transformer.from_crs("EPSG:4326", MODIS_SINU_PROJ4, always_xy=True)
    x_s, y_s = tr.transform(lon, lat)
    h_idx = int((x_s + 18.0 * MODIS_SINU_TILE_M) // MODIS_SINU_TILE_M)
    v_idx = int((9.0 * MODIS_SINU_TILE_M - y_s) // MODIS_SINU_TILE_M)
    tile_id = f"h{h_idx:02d}v{v_idx:02d}"

    sess = _make_retrying_session()
    sas_resp = sess.get(PC_MODIS_SAS_URL, timeout=15)
    sas_resp.raise_for_status()
    sas_token = sas_resp.json()["token"]

    south_summer = "2024-01-01/2024-02-28"
    windows = [south_summer, datetime_range] if lat < -45.0 else [datetime_range, south_summer]

    vals: list[float] = []
    ndsi_vals: list[float] = []
    n_snow_masked = 0
    n_qa_valid = 0
    granule_ids: list[str] = []
    used_window = windows[0]

    for win_dt in windows:
        stac_resp = sess.post(
            PC_STAC_SEARCH_URL,
            json={
                "collections": ["modis-43A4-061"],
                "query": {
                    "modis:horizontal-tile": {"eq": h_idx},
                    "modis:vertical-tile": {"eq": v_idx},
                },
                "datetime": win_dt,
                "limit": 60,
            },
            timeout=15,
        )
        if stac_resp.status_code != 200:
            continue
        features = sorted(
            [
                it
                for it in stac_resp.json().get("features", [])
                if f".{tile_id}." in it["id"]
            ],
            key=lambda it: it["id"],
        )
        if not features:
            continue
        idx = np.linspace(0, len(features) - 1, min(len(features), max_granules), dtype=int)
        chosen = [features[i] for i in idx]

        for item in chosen:
            try:
                bands: dict[int, np.ndarray] = {}
                qas: dict[int, np.ndarray] = {}
                for b in (1, 2, 3, 4, 5, 6, 7):
                    b_url = f"{item['assets'][f'Nadir_Reflectance_Band{b}']['href']}?{sas_token}"
                    q_url = f"{item['assets'][f'BRDF_Albedo_Band_Mandatory_Quality_Band{b}']['href']}?{sas_token}"
                    with (
                        MemoryFile(sess.get(b_url, timeout=25).content) as mb,
                        MemoryFile(sess.get(q_url, timeout=25).content) as mq,
                    ):
                        with mb.open() as sb, mq.open() as sq:
                            tf = pyproj.Transformer.from_crs("EPSG:4326", sb.crs, always_xy=True)
                            cx, cy = tf.transform(lon, lat)
                            r0, c0 = sb.index(cx, cy)
                            win = (
                                (max(0, r0 - 2), min(sb.height, r0 + 3)),
                                (max(0, c0 - 2), min(sb.width, c0 + 3)),
                            )
                            bands[b] = sb.read(1, window=win).astype(np.float64)
                            qas[b] = sq.read(1, window=win).astype(np.uint8)

                qa_ok = np.ones_like(bands[1], dtype=bool)
                for b in (1, 2, 3, 4, 5, 6, 7):
                    qa_ok &= (bands[b] >= 0) & (bands[b] < 32767) & (qas[b] <= 1)
                if not np.any(qa_ok):
                    continue
                n_qa_valid += int(np.sum(qa_ok))

                rho = {b: bands[b][qa_ok] * 0.0001 for b in (1, 2, 3, 4, 5, 6, 7)}
                ndsi = (rho[4] - rho[6]) / np.maximum(rho[4] + rho[6], 1e-6)
                ndsi_vals.extend(ndsi.tolist())
                snow_free = ndsi < 0.40
                n_snow_masked += int(np.sum(~snow_free))
                if not np.any(snow_free):
                    continue

                # Liang (2001, Remote Sensing of Environment 76:213-238) Eq. 9 MODIS shortwave broadband conversion
                alpha_sw = (
                    0.160 * rho[1][snow_free]
                    + 0.291 * rho[2][snow_free]
                    + 0.243 * rho[3][snow_free]
                    + 0.116 * rho[4][snow_free]
                    + 0.112 * rho[5][snow_free]
                    + 0.081 * rho[7][snow_free]
                    - 0.0015
                )
                alpha_sw = alpha_sw[(alpha_sw > 0.0) & (alpha_sw <= 1.0)]
                if alpha_sw.size > 0:
                    vals.extend(alpha_sw.tolist())
                    granule_ids.append(item["id"])
            except Exception:
                continue
        if vals:
            used_window = win_dt
            break

    if not vals:
        return None

    arr = np.asarray(vals, dtype=np.float64)
    result = {
        "site_id": site_id,
        "tile_id": tile_id,
        "temporal": used_window,
        "albedo": float(np.mean(arr)),
        "albedo_sd": max(float(np.std(arr, ddof=1)), 1e-4) if arr.size > 1 else 0.01,
        "albedo_src": MCD43A4_LIANG_SRC,
        "albedo_res_m": 500.0,
        "formula": "Liang (2001) alpha_sw = 0.160*B1 + 0.291*B2 + 0.243*B3 + 0.116*B4 + 0.112*B5 + 0.081*B7 - 0.0015",
        "qa_filter": "BRDF_Albedo_Band_Mandatory_Quality_Band1..7 <= 1",
        "snow_mask": "NDSI = (B4 - B6)/(B4 + B6) < 0.40",
        "ndsi_mean": float(np.mean(ndsi_vals)) if ndsi_vals else float("nan"),
        "n_qa_valid_pixels": n_qa_valid,
        "n_snow_masked_pixels": n_snow_masked,
        "n_valid_samples": int(arr.size),
        "n_valid_granules": len(granule_ids),
        "granules": granule_ids,
    }
    cache_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def check_mcd43a3_access() -> tuple[bool, str]:
    """Check whether MCD43A3.061 is accessible via Planetary Computer or EARTHDATA_TOKEN."""
    sess = _make_retrying_session()
    r_pc = sess.get(
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
        return fetch_mcd43a4_nbar_albedo_liang2001(
            site_id=site_id, lat=lat, lon=lon, raw_dir=raw_dir
        )

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

    sess = _make_retrying_session()
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
