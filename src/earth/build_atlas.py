"""Build a cloud-free 512x512 Sentinel-2 L2A WebP atlas for all Earth sites (Madde E5)."""
from __future__ import annotations

import json
import math
import shutil
import socket
import struct
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
import requests
from PIL import Image
from pyproj import Transformer
from rasterio.io import MemoryFile
from rasterio.windows import Window

from src.earth.modis_pipeline import _make_retrying_session
from src.earth.sites import VERIFIED_EARTH_SITES

STAC_SEARCH_URL = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
S2_SAS_URL = "https://planetarycomputer.microsoft.com/api/sas/v1/token/sentinel-2-l2a"
COLLECTION = "sentinel-2-l2a"
TARGET_PX = 512
MAX_TOTAL_BYTES = 3_000_000
LOCAL_CLOUD_MAX_PCT = 2.0
VALID_RGB_MIN_PCT = 98.0


def _assert_dns(host: str = "planetarycomputer.microsoft.com") -> None:
    """Fail immediately if DNS resolution is unavailable."""
    try:
        socket.getaddrinfo(host, 443)
    except OSError as exc:
        raise RuntimeError(f"DNS resolution failed for {host}: {exc}") from exc


def _read_cog_rgb_or_band(
    sess: requests.Session,
    url: str,
    bands: list[int],
    win: Window,
) -> np.ndarray:
    """Read an exact pixel Window from a Planetary Computer COG via HTTP Range."""
    r_hdr = sess.get(url, headers={"Range": "bytes=0-65535"}, timeout=(10, 20))
    r_hdr.raise_for_status()
    hdr = bytearray(r_hdr.content)

    magic = bytes(hdr[:4])
    is_big = magic == b"II+\x00"
    if not (magic == b"II*\x00" or is_big):
        raise RuntimeError(f"Unsupported TIFF magic: {magic!r}")

    hdr_sz = 8 if is_big else 2
    ent_sz = 20 if is_big else 12
    ent_fmt = "<HHQQ" if is_big else "<HHII"
    ptr_fmt, ptr_sz = ("Q", 8) if is_big else ("I", 4)

    ifd_off = struct.unpack("<Q" if is_big else "<I", hdr[8:16] if is_big else hdr[4:8])[0]
    if ifd_off + hdr_sz > len(hdr):
        r_ext = sess.get(url, headers={"Range": f"bytes=0-{ifd_off + 65536}"}, timeout=(10, 20))
        r_ext.raise_for_status()
        hdr = bytearray(r_ext.content)

    n_entries = struct.unpack("<Q" if is_big else "<H", hdr[ifd_off : ifd_off + hdr_sz])[0]
    tags: dict[int, tuple[int, int, int]] = {}
    for i in range(n_entries):
        pos = ifd_off + hdr_sz + i * ent_sz
        if pos + ent_sz > len(hdr):
            r_ext = sess.get(url, headers={"Range": f"bytes=0-{pos + 32768}"}, timeout=(10, 20))
            r_ext.raise_for_status()
            hdr = bytearray(r_ext.content)
        t, tp, cnt, val = struct.unpack(ent_fmt, hdr[pos : pos + ent_sz])
        tags[t] = (tp, cnt, val)

    img_w, img_h = tags[256][2], tags[257][2]
    tile_w, tile_h = tags[322][2], tags[323][2]
    _, n_tiles, off_pos = tags[324]
    _, _, cnt_pos = tags[325]

    end_needed = max(off_pos + ptr_sz * n_tiles, cnt_pos + ptr_sz * n_tiles)
    if end_needed > len(hdr):
        r_ext = sess.get(url, headers={"Range": f"bytes=0-{end_needed + 4096}"}, timeout=(10, 20))
        r_ext.raise_for_status()
        hdr = bytearray(r_ext.content)

    # Terminate next IFD chain so GDAL ignores overviews cleanly
    struct.pack_into(f"<{ptr_fmt}", hdr, ifd_off + hdr_sz + n_entries * ent_sz, 0)

    orig_offsets = list(struct.unpack(f"<{n_tiles}{ptr_fmt}", hdr[off_pos : off_pos + ptr_sz * n_tiles]))
    orig_counts = list(struct.unpack(f"<{n_tiles}{ptr_fmt}", hdr[cnt_pos : cnt_pos + ptr_sz * n_tiles]))

    r0 = max(0, int(win.row_off))
    c0 = max(0, int(win.col_off))
    r1 = min(img_h, int(win.row_off + win.height))
    c1 = min(img_w, int(win.col_off + win.width))
    clipped_win = Window(c0, r0, c1 - c0, r1 - r0)

    n_tx = math.ceil(img_w / tile_w)
    needed = {
        ty * n_tx + tx
        for ty in range(r0 // tile_h, (r1 - 1) // tile_h + 1)
        for tx in range(c0 // tile_w, (c1 - 1) // tile_w + 1)
    }

    new_offsets = [0] * n_tiles
    new_counts = [0] * n_tiles
    payload = bytearray()
    for idx in sorted(needed):
        t_off, t_cnt = orig_offsets[idx], orig_counts[idx]
        if t_cnt == 0:
            continue
        r_chk = sess.get(url, headers={"Range": f"bytes={t_off}-{t_off + t_cnt - 1}"}, timeout=(10, 20))
        r_chk.raise_for_status()
        chunk = r_chk.content
        new_offsets[idx] = len(hdr) + len(payload)
        new_counts[idx] = len(chunk)
        payload.extend(chunk)

    struct.pack_into(f"<{n_tiles}{ptr_fmt}", hdr, off_pos, *new_offsets)
    struct.pack_into(f"<{n_tiles}{ptr_fmt}", hdr, cnt_pos, *new_counts)

    with MemoryFile(bytes(hdr) + bytes(payload)) as mem:
        with mem.open() as src:
            return src.read(bands, window=clipped_win)


def _site_pixel_in_item(item: dict[str, Any], lat: float, lon: float) -> tuple[int, int, int, int] | None:
    """Return (row10, col10, h10, w10) of (lat, lon) inside the item's 10m visual grid."""
    vis = item.get("assets", {}).get("visual", {})
    tf_vals = vis.get("proj:transform")
    shp = vis.get("proj:shape")
    epsg = item.get("properties", {}).get("proj:epsg")
    if not (tf_vals and shp and epsg):
        return None
    px, py = Transformer.from_crs("EPSG:4326", f"EPSG:{int(epsg)}", always_xy=True).transform(lon, lat)
    a, _, c, _, e, f = tf_vals[:6]
    col = int(round((px - c) / a))
    row = int(round((py - f) / e))
    return row, col, int(shp[0]), int(shp[1])


def _search_windows_for_site(lat: float) -> list[tuple[str, str]]:
    """Return seasonal STAC datetime windows ordered by clearest dry summer first."""
    if lat >= 0.0:
        return [
            ("north_peak_summer_2024", "2024-07-01/2024-09-20"),
            ("north_shoulder_2024", "2024-05-15/2024-10-31"),
            ("full_year_2024", "2024-01-01/2024-12-31"),
            ("full_year_2023", "2023-01-01/2023-12-31"),
        ]
    return [
        ("south_summer_2023_24", "2023-12-01/2024-03-15"),
        ("full_year_2024", "2024-01-01/2024-12-31"),
        ("full_year_2023", "2023-01-01/2023-12-31"),
    ]


def _fetch_site_patch(
    site: dict[str, Any],
    s2_tok: str,
    stage_dir: Path,
) -> tuple[dict[str, Any], Path | None]:
    """Fetch a verified cloudless 512x512 RGB patch into stage_dir, raising on any network error."""
    site_id = site["site_id"]
    lat = float(site["lat"])
    lon = float(site["lon"])
    is_evap = site.get("lithology_class") == "evaporite"
    sess = _make_retrying_session()

    half = TARGET_PX // 2
    seen_ids: set[str] = set()

    for win_label, dt_range in _search_windows_for_site(lat):
        resp = sess.post(
            STAC_SEARCH_URL,
            json={
                "collections": [COLLECTION],
                "intersects": {"type": "Point", "coordinates": [lon, lat]},
                "datetime": dt_range,
                "query": {"eo:cloud_cover": {"lt": 20}},
                "limit": 60,
            },
            timeout=(10, 20),
        )
        resp.raise_for_status()
        feats = resp.json().get("features", [])

        candidates: list[tuple[float, float, dict[str, Any], tuple[int, int, int, int]]] = []
        for it in feats:
            sid = it.get("id")
            if not sid or sid in seen_ids:
                continue
            seen_ids.add(sid)
            rc = _site_pixel_in_item(it, lat, lon)
            if rc is None:
                continue
            r, c, h, w = rc
            is_interior = (r >= half) and (r + half <= h) and (c >= half) and (c + half <= w)
            if not is_interior:
                continue
            props = it.get("properties", {})
            cc_val = props.get("eo:cloud_cover")
            cc_sort = float(cc_val) if cc_val is not None else 999.0
            snow_val = props.get("s2:snow_ice_percentage")
            snow_sort = 0.0 if (is_evap or snow_val is None) else float(snow_val)
            # Prefer both low tile snow (for non-evaporite sites) and low tile cloud cover
            candidates.append((snow_sort * 0.5 + cc_sort, cc_sort, it, rc))

        candidates.sort(key=lambda t: (t[0], t[1], str(t[2].get("id", ""))))

        for _, _, it, (r, c, _, _) in candidates[:8]:
            assets = it.get("assets", {})
            if "visual" not in assets or "SCL" not in assets:
                continue

            scl_win = Window(c // 2 - half // 2, r // 2 - half // 2, TARGET_PX // 2, TARGET_PX // 2)
            scl_url = f"{assets['SCL']['href']}?{s2_tok}"
            scl = _read_cog_rgb_or_band(sess, scl_url, [1], scl_win)[0]
            if scl.size == 0:
                continue
            valid_scl_pct = 100.0 * float(np.mean(scl != 0))
            local_cloud_pct = 100.0 * float(np.mean(np.isin(scl, [8, 9, 10])))
            if valid_scl_pct < VALID_RGB_MIN_PCT or local_cloud_pct > LOCAL_CLOUD_MAX_PCT:
                continue

            vis_win = Window(c - half, r - half, TARGET_PX, TARGET_PX)
            vis_url = f"{assets['visual']['href']}?{s2_tok}"
            rgb_chw = _read_cog_rgb_or_band(sess, vis_url, [1, 2, 3], vis_win)
            if rgb_chw.shape != (3, TARGET_PX, TARGET_PX):
                continue

            rgb_hwc = np.transpose(rgb_chw, (1, 2, 0))
            valid_rgb_pct = 100.0 * float(np.mean(np.any(rgb_hwc > 0, axis=2)))
            if valid_rgb_pct < VALID_RGB_MIN_PCT:
                continue

            png_path = stage_dir / f"{site_id}.png"
            Image.fromarray(rgb_hwc, mode="RGB").save(png_path, format="PNG")

            props = it.get("properties", {})
            dt_val = props.get("datetime")
            cc_raw = props.get("eo:cloud_cover")
            meta = {
                "site_id": site_id,
                "name": site["name"],
                "role": site["role"],
                "lat": lat,
                "lon": lon,
                "file": f"{site_id}.webp",
                "acquisition_date": str(dt_val) if dt_val else "yok",
                "tile_cloud_cover_pct": round(float(cc_raw), 2) if cc_raw is not None else "yok",
                "local_cloud_pct": round(local_cloud_pct, 2),
                "scene_id": str(it.get("id")) if it.get("id") else "yok",
                "collection": str(it.get("collection") or COLLECTION),
                "search_window": win_label,
                "width_px": TARGET_PX,
                "height_px": TARGET_PX,
            }
            return meta, png_path

    skipped_meta = {
        "site_id": site_id,
        "reason": f"No scene met interior 512x512 >=98% valid and local_cloud <= {LOCAL_CLOUD_MAX_PCT}%",
        "acquisition_date": "yok",
        "tile_cloud_cover_pct": "yok",
        "scene_id": "yok",
        "collection": COLLECTION,
    }
    return skipped_meta, None


def build_earth_atlas(out_dir: Path = Path("data/processed/earth_atlas")) -> dict[str, Any]:
    """Generate 512x512 cloudless Sentinel-2 WebP images and metadata atomically."""
    _assert_dns("planetarycomputer.microsoft.com")
    _assert_dns("sentinel2l2a01.blob.core.windows.net")

    sess = _make_retrying_session()
    tok_resp = sess.get(S2_SAS_URL, timeout=(10, 15))
    tok_resp.raise_for_status()
    s2_tok = tok_resp.json()["token"]

    sites = list(VERIFIED_EARTH_SITES)
    total_sites = len(sites)

    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        png_stage = tmp_path / "png_stage"
        webp_stage = tmp_path / "webp_stage"
        png_stage.mkdir(parents=True, exist_ok=True)
        webp_stage.mkdir(parents=True, exist_ok=True)

        results: dict[str, tuple[dict[str, Any], Path | None]] = {}
        with ThreadPoolExecutor(max_workers=4) as pool:
            futs = {pool.submit(_fetch_site_patch, s, s2_tok, png_stage): s["site_id"] for s in sites}
            done_n = 0
            for fut in as_completed(futs):
                sid = futs[fut]
                meta, png_p = fut.result()  # Raises immediately on DNS/HTTP/network errors
                results[sid] = (meta, png_p)
                done_n += 1
                status = f"OK {meta['scene_id']} (cc={meta['tile_cloud_cover_pct']}%, loc_cld={meta['local_cloud_pct']}%)" if png_p else "SKIPPED"
                print(f"[{done_n}/{total_sites}] {sid}: {status}", flush=True)

        included_items: list[tuple[dict[str, Any], Path]] = []
        skipped: list[dict[str, Any]] = []
        for s in sites:
            sid = s["site_id"]
            meta, png_p = results[sid]
            if png_p is not None:
                included_items.append((meta, png_p))
            else:
                skipped.append(meta)

        # Pick highest WebP quality (without resampling) keeping total directory size <= 3 MB
        chosen_q = None
        for q in range(94, 29, -2):
            webp_bytes = 0
            for f in webp_stage.glob("*.webp"):
                f.unlink()
            for meta, png_p in included_items:
                out_w = webp_stage / meta["file"]
                with Image.open(png_p) as im:
                    im.save(out_w, format="WEBP", quality=q, method=6)
                sz = out_w.stat().st_size
                meta["size_bytes"] = sz
                webp_bytes += sz
            meta_payload = {
                "collection": COLLECTION,
                "resolution_m": 10.0,
                "footprint_m": [TARGET_PX * 10, TARGET_PX * 10],
                "webp_quality": q,
                "included_count": len(included_items),
                "skipped_count": len(skipped),
                "skipped_sites": skipped,
                "sites": [m for m, _ in included_items],
            }
            meta_txt = json.dumps(meta_payload, ensure_ascii=False, indent=2)
            tot_bytes = webp_bytes + len(meta_txt.encode("utf-8"))
            print(f"[quality={q}] webp_bytes={webp_bytes:,} total_with_meta={tot_bytes:,}", flush=True)
            if tot_bytes <= MAX_TOTAL_BYTES:
                chosen_q = q
                (webp_stage / "metadata.json").write_text(meta_txt, encoding="utf-8")
                break

        if chosen_q is None:
            raise RuntimeError(f"Could not compress {len(included_items)} WebPs under {MAX_TOTAL_BYTES} bytes without resampling")

        # Atomically replace final directory only after full clean build
        out_dir.parent.mkdir(parents=True, exist_ok=True)
        if out_dir.exists():
            shutil.rmtree(out_dir)
        shutil.copytree(webp_stage, out_dir)

    final_files = sorted(out_dir.iterdir(), key=lambda p: p.name)
    total_dir_bytes = sum(p.stat().st_size for p in final_files)
    webp_list = [p for p in final_files if p.suffix == ".webp"]
    mean_kb = (sum(p.stat().st_size for p in webp_list) / max(1, len(webp_list))) / 1024.0
    print(
        f"\nDONE earth_atlas: {len(webp_list)} webp + 1 metadata.json ({len(final_files)} files total), "
        f"mean={mean_kb:.1f} KB/webp, total={total_dir_bytes:,} B ({total_dir_bytes / (1024*1024):.3f} MiB / {total_dir_bytes / 1e6:.3f} MB), "
        f"skipped={len(skipped)}, quality={chosen_q}",
        flush=True,
    )
    return {
        "webp_count": len(webp_list),
        "total_bytes": total_dir_bytes,
        "quality": chosen_q,
        "skipped_sites": skipped,
    }


if __name__ == "__main__":
    build_earth_atlas()
