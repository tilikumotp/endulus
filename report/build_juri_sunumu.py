"""Build the 16:9 unslopped Turkish jury presentation (report/juri_sunumu_tr.pptx)."""
from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from PIL import Image

REPORT_DIR = Path(__file__).resolve().parent
if str(REPORT_DIR) not in sys.path:
    sys.path.insert(0, str(REPORT_DIR))

from build_juri_raporu import (
    FIG_DIR,
    ROOT,
    TURKISH_CANDIDATE_IDS,
    compute_all_metrics,
    short_label,
)

PPTX_PATH = REPORT_DIR / "juri_sunumu_tr.pptx"

EMU_PER_INCH = 914400
SLIDE_W = 12192000  # 13.333 in (16:9)
SLIDE_H = 6858000   # 7.500 in


def in_emu(inches: float) -> int:
    """Convert inches to integer OOXML EMUs."""
    return int(round(inches * EMU_PER_INCH))


def pt_sp(points: float) -> int:
    """Convert font size in points to OOXML hundredths of a point."""
    return int(round(points * 100))


def _run_xml(
    text: str,
    size_pt: float = 11.5,
    bold: bool = False,
    italic: bool = False,
    color: str = "171717",
    font: str = "Segoe UI",
) -> str:
    b_attr = "1" if bold else "0"
    i_attr = "1" if italic else "0"
    return (
        f'<a:r><a:rPr lang="tr-TR" sz="{pt_sp(size_pt)}" b="{b_attr}" i="{i_attr}" dirty="0">'
        f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
        f'<a:latin typeface="{font}"/>'
        f'<a:ea typeface="{font}"/>'
        f'<a:cs typeface="{font}"/>'
        f'</a:rPr><a:t>{escape(text)}</a:t></a:r>'
    )


@dataclass
class SlideBuilder:
    """Construct native DrawingML shapes, tables, lines, and images for one slide."""

    slide_num: int
    total_slides: int
    notes_text: str = ""

    def __post_init__(self) -> None:
        self.shapes: list[str] = []
        self.rels: list[tuple[str, str, str]] = [
            (
                "rId1",
                "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout",
                "../slideLayouts/slideLayout1.xml",
            )
        ]
        self._shape_id = 2
        self._img_idx = 0
        self.media_files: list[tuple[str, bytes]] = []

    def _next_id(self) -> int:
        sid = self._shape_id
        self._shape_id += 1
        return sid

    def add_line(
        self,
        x_in: float,
        y_in: float,
        w_in: float,
        h_in: float = 0.0,
        color: str = "D4D4D4",
        width_pt: float = 1.0,
    ) -> None:
        """Add a crisp horizontal or vertical rule line."""
        sid = self._next_id()
        w_emu = max(0, in_emu(w_in))
        h_emu = max(0, in_emu(h_in))
        ln_w = int(round(width_pt * 12700))
        self.shapes.append(
            f'<p:sp>'
            f'<p:nvSpPr><p:cNvPr id="{sid}" name="Line_{sid}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr>'
            f'<a:xfrm><a:off x="{in_emu(x_in)}" y="{in_emu(y_in)}"/><a:ext cx="{w_emu}" cy="{h_emu}"/></a:xfrm>'
            f'<a:prstGeom prst="line"><a:avLst/></a:prstGeom>'
            f'<a:ln w="{ln_w}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:ln>'
            f'</p:spPr>'
            f'</p:sp>'
        )

    def add_rect(
        self,
        x_in: float,
        y_in: float,
        w_in: float,
        h_in: float,
        fill_color: str | None = None,
        border_color: str | None = None,
        border_pt: float = 0.75,
        left_accent_pt: float = 0.0,
    ) -> None:
        """Add a crisp flat rectangle container (no rounded pills or drop shadows)."""
        sid = self._next_id()
        fill_xml = (
            f'<a:solidFill><a:srgbClr val="{fill_color}"/></a:solidFill>'
            if fill_color
            else "<a:noFill/>"
        )
        if border_color:
            ln_w = int(round(border_pt * 12700))
            ln_xml = f'<a:ln w="{ln_w}"><a:solidFill><a:srgbClr val="{border_color}"/></a:solidFill></a:ln>'
        else:
            ln_xml = "<a:ln><a:noFill/></a:ln>"

        self.shapes.append(
            f'<p:sp>'
            f'<p:nvSpPr><p:cNvPr id="{sid}" name="Rect_{sid}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr>'
            f'<a:xfrm><a:off x="{in_emu(x_in)}" y="{in_emu(y_in)}"/><a:ext cx="{in_emu(w_in)}" cy="{in_emu(h_in)}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            f'{fill_xml}{ln_xml}'
            f'</p:spPr>'
            f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>'
            f'</p:sp>'
        )
        if left_accent_pt > 0:
            self.add_line(x_in, y_in, 0.0, h_in, color="111111", width_pt=left_accent_pt)

    def add_textbox(
        self,
        x_in: float,
        y_in: float,
        w_in: float,
        h_in: float,
        paragraphs: list[dict[str, Any]],
        anchor: str = "t",
        pad_lr_in: float = 0.03,
        pad_tb_in: float = 0.02,
    ) -> None:
        """Add an editable multi-paragraph text box."""
        sid = self._next_id()
        p_xml_list: list[str] = []
        for p in paragraphs:
            align = p.get("align", "l")
            bullet = p.get("bullet", False)
            spc_aft = pt_sp(p.get("space_after_pt", 3.5))
            ln_pct = int(round(p.get("line_spacing", 1.18) * 100000))
            if bullet:
                ppr = (
                    f'<a:pPr algn="{align}" marL="200000" indent="-160000">'
                    f'<a:lnSpc><a:spcPct val="{ln_pct}"/></a:lnSpc>'
                    f'<a:spcAft><a:spcPts val="{spc_aft}"/></a:spcAft>'
                    f'<a:buFont typeface="Segoe UI"/><a:buChar char="&#8226;"/>'
                    f'</a:pPr>'
                )
            else:
                ppr = (
                    f'<a:pPr algn="{align}">'
                    f'<a:lnSpc><a:spcPct val="{ln_pct}"/></a:lnSpc>'
                    f'<a:spcAft><a:spcPts val="{spc_aft}"/></a:spcAft>'
                    f'<a:buNone/>'
                    f'</a:pPr>'
                )

            if "runs" in p:
                runs_xml = "".join(
                    _run_xml(
                        r["text"],
                        size_pt=r.get("size", 11.5),
                        bold=r.get("bold", False),
                        italic=r.get("italic", False),
                        color=r.get("color", "171717"),
                        font=r.get("font", "Segoe UI"),
                    )
                    for r in p["runs"]
                )
            else:
                runs_xml = _run_xml(
                    p.get("text", ""),
                    size_pt=p.get("size", 11.5),
                    bold=p.get("bold", False),
                    italic=p.get("italic", False),
                    color=p.get("color", "171717"),
                    font=p.get("font", "Segoe UI"),
                )
            p_xml_list.append(f"<a:p>{ppr}{runs_xml}</a:p>")

        lr = in_emu(pad_lr_in)
        tb = in_emu(pad_tb_in)
        self.shapes.append(
            f'<p:sp>'
            f'<p:nvSpPr><p:cNvPr id="{sid}" name="TextBox_{sid}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr>'
            f'<a:xfrm><a:off x="{in_emu(x_in)}" y="{in_emu(y_in)}"/><a:ext cx="{in_emu(w_in)}" cy="{in_emu(h_in)}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            f'<a:noFill/><a:ln><a:noFill/></a:ln>'
            f'</p:spPr>'
            f'<p:txBody>'
            f'<a:bodyPr wrap="square" lIns="{lr}" rIns="{lr}" tIns="{tb}" bIns="{tb}" anchor="{anchor}"/>'
            f'<a:lstStyle/>'
            f'{"".join(p_xml_list)}'
            f'</p:txBody>'
            f'</p:sp>'
        )

    def add_table(
        self,
        x_in: float,
        y_in: float,
        w_in: float,
        h_in: float,
        col_widths_in: list[float],
        headers: list[str],
        rows: list[list[str]],
        num_cols: set[int] | None = None,
        font_pt: float = 9.5,
        header_pt: float = 9.5,
        pad_tb_pt: float = 4.0,
    ) -> None:
        """Add an editable OOXML table with crisp monochrome hairline rules."""
        sid = self._next_id()
        num_cols = num_cols or set()
        pad_tb_emu = int(round(pad_tb_pt * 12700))
        pad_lr_emu = 70000

        def make_cell(
            text: str,
            is_header: bool,
            is_num: bool,
            row_idx: int,
            is_last_row: bool,
            bold_override: bool = False,
        ) -> str:
            align = "r" if is_num else "l"
            font = "Consolas" if is_num else "Segoe UI"
            sz = header_pt if is_header else font_pt
            bold = True if is_header else bold_override
            txt_col = "111111" if (is_header or bold_override) else "262626"
            bg = '<a:solidFill><a:srgbClr val="F5F5F5"/></a:solidFill>' if is_header else '<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'

            if is_header:
                top_ln = '<a:lnT w="15875"><a:solidFill><a:srgbClr val="111111"/></a:solidFill></a:lnT>'
                bot_ln = '<a:lnB w="15875"><a:solidFill><a:srgbClr val="111111"/></a:solidFill></a:lnB>'
            else:
                top_ln = '<a:lnT><a:noFill/></a:lnT>'
                bot_col = "111111" if is_last_row else "E0E0E0"
                bot_w = "12700" if is_last_row else "9525"
                bot_ln = f'<a:lnB w="{bot_w}"><a:solidFill><a:srgbClr val="{bot_col}"/></a:solidFill></a:lnB>'

            return (
                f'<a:tc>'
                f'<a:txBody><a:bodyPr/><a:lstStyle/>'
                f'<a:p><a:pPr algn="{align}"><a:buNone/></a:pPr>'
                f'{_run_xml(text, size_pt=sz, bold=bold, color=txt_col, font=font)}'
                f'</a:p></a:txBody>'
                f'<a:tcPr marL="{pad_lr_emu}" marR="{pad_lr_emu}" marT="{pad_tb_emu}" marB="{pad_tb_emu}" anchor="ctr">'
                f'<a:lnL><a:noFill/></a:lnL><a:lnR><a:noFill/></a:lnR>{top_ln}{bot_ln}{bg}'
                f'</a:tcPr>'
                f'</a:tc>'
            )

        grid_xml = "".join(f'<a:gridCol w="{in_emu(cw)}"/>' for cw in col_widths_in)
        n_rows = 1 + len(rows)
        row_h = max(210000, in_emu(h_in / n_rows))

        hdr_cells = "".join(
            make_cell(h, is_header=True, is_num=(c in num_cols), row_idx=0, is_last_row=False)
            for c, h in enumerate(headers)
        )
        tr_list = [f'<a:tr h="{row_h}">{hdr_cells}</a:tr>']
        for r_idx, row in enumerate(rows):
            is_last = r_idx == len(rows) - 1
            cells = "".join(
                make_cell(
                    val,
                    is_header=False,
                    is_num=(c in num_cols),
                    row_idx=r_idx + 1,
                    is_last_row=is_last,
                    bold_override=(c == 0 and len(col_widths_in) <= 5),
                )
                for c, val in enumerate(row)
            )
            tr_list.append(f'<a:tr h="{row_h}">{cells}</a:tr>')

        self.shapes.append(
            f'<p:graphicFrame>'
            f'<p:nvGraphicFramePr><p:cNvPr id="{sid}" name="Table_{sid}"/><p:cNvGraphicFramePr><a:graphicFrameLocks noGrp="1"/></p:cNvGraphicFramePr><p:nvPr/></p:nvGraphicFramePr>'
            f'<p:xfrm><a:off x="{in_emu(x_in)}" y="{in_emu(y_in)}"/><a:ext cx="{in_emu(w_in)}" cy="{in_emu(h_in)}"/></p:xfrm>'
            f'<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table">'
            f'<a:tbl><a:tblPr firstRow="1" bandRow="0"/>'
            f'<a:tblGrid>{grid_xml}</a:tblGrid>'
            f'{"".join(tr_list)}'
            f'</a:tbl></a:graphicData></a:graphic>'
            f'</p:graphicFrame>'
        )

    def add_image(
        self,
        img_path: Path,
        x_in: float,
        y_in: float,
        max_w_in: float,
        max_h_in: float,
        center_x: bool = True,
    ) -> float:
        """Embed PNG preserving exact pixel aspect ratio within bounding box."""
        with Image.open(img_path) as im:
            px_w, px_h = im.size
        aspect = px_w / px_h
        w_in = max_w_in
        h_in = w_in / aspect
        if h_in > max_h_in:
            h_in = max_h_in
            w_in = h_in * aspect

        draw_x = x_in + (max_w_in - w_in) / 2.0 if center_x else x_in
        self._img_idx += 1
        rid = f"rImg_{self.slide_num}_{self._img_idx}"
        media_name = f"s{self.slide_num}_img{self._img_idx}{img_path.suffix.lower()}"
        self.rels.append(
            (
                rid,
                "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
                f"../media/{media_name}",
            )
        )
        self.media_files.append((media_name, img_path.read_bytes()))

        sid = self._next_id()
        self.shapes.append(
            f'<p:pic>'
            f'<p:nvPicPr><p:cNvPr id="{sid}" name="Img_{sid}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
            f'<p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
            f'<p:spPr>'
            f'<a:xfrm><a:off x="{in_emu(draw_x)}" y="{in_emu(y_in)}"/><a:ext cx="{in_emu(w_in)}" cy="{in_emu(h_in)}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            f'</p:spPr>'
            f'</p:pic>'
        )
        return h_in

    def add_header(self, kicker: str, title: str) -> None:
        """Apply consistent white-paper pure-black top slide header."""
        self.add_line(0.55, 0.34, 12.23, 0.0, color="111111", width_pt=1.5)
        self.add_textbox(
            0.55, 0.38, 12.23, 0.24,
            [{"text": kicker, "size": 9.5, "color": "737373"}],
            pad_tb_in=0.0,
        )
        self.add_textbox(
            0.55, 0.61, 12.23, 0.44,
            [{"text": title, "size": 20.5, "bold": True, "color": "111111"}],
            pad_tb_in=0.0,
        )
        self.add_line(0.55, 1.07, 12.23, 0.0, color="E5E5E5", width_pt=0.75)

    def add_footer(self) -> None:
        """Apply restrained hairline slide footer."""
        self.add_line(0.55, 7.08, 12.23, 0.0, color="D4D4D4", width_pt=0.75)
        self.add_textbox(
            0.55, 7.12, 9.5, 0.24,
            [{"text": "NASA Space Apps 2026 · Ay Güney Kutbu Çok-Eksenli Test Sahası Değerlendirmesi · 0 MOCK", "size": 8.5, "color": "737373"}],
            pad_tb_in=0.0,
        )
        self.add_textbox(
            11.4, 7.12, 1.38, 0.24,
            [{"text": f"{self.slide_num} / {self.total_slides}", "size": 8.5, "color": "737373", "align": "r", "font": "Consolas"}],
            pad_tb_in=0.0,
        )

    def to_slide_xml(self) -> str:
        """Serialize complete OOXML slide."""
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
            'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
            '<p:cSld>'
            '<p:bg><p:bgPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>'
            '<p:spTree>'
            '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
            '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
            f'{"".join(self.shapes)}'
            '</p:spTree>'
            '</p:cSld>'
            '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>'
            '</p:sld>'
        )

    def to_rels_xml(self) -> str:
        """Serialize slide relationships XML."""
        items = "".join(
            f'<Relationship Id="{rid}" Type="{rtype}" Target="{target}"/>'
            for rid, rtype, target in self.rels
        )
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{items}</Relationships>'
        )


def build_slides(data: dict[str, Any]) -> list[SlideBuilder]:
    """Create all 10 concise, unslopped, data-verified jury slides."""
    n_slides = 10
    slides: list[SlideBuilder] = []

    sh = data["per_moon"]["moon_shackleton_rim"]
    sh_bal = sh["by_preset"]["default"].set_index("site_id")
    sh_mob = sh["by_preset"]["rover_mobility"].set_index("site_id")
    sh_rad = sh["by_preset"]["radar_calibration"].set_index("site_id")
    fa_bal = data["per_moon"]["moon_faustini_rim"]["by_preset"]["default"].set_index("site_id")
    ed_idx = data["earth_df"].set_index("site_id")

    sh_bv_df = sh["blind_val"]
    fa_bv_df = data["per_moon"]["moon_faustini_rim"]["blind_val"]
    sh_bv_mob = sh_bv_df[sh_bv_df["axis"] == "mobility"].set_index("site_id")["rank"]
    fa_bv_mob = fa_bv_df[fa_bv_df["axis"] == "mobility"].set_index("site_id")["rank"]

    # --- Slide 1: Cover / Core Proposition + Orbital Evidence ---
    s1 = SlideBuilder(1, n_slides, "Açılış: Tek saha Ay'ı kopyalayamaz; eksen ayrıştırma + belirsizlik yaklaşımı.")
    s1.add_line(0.55, 0.36, 12.23, 0.0, color="111111", width_pt=2.0)
    s1.add_textbox(
        0.55, 0.44, 12.23, 0.25,
        [{"text": "NASA Space Apps 2026 · Permanent Moon Base Locations and Mars", "size": 10.5, "color": "525252"}],
    )
    s1.add_textbox(
        0.55, 0.72, 12.23, 0.88,
        [
            {"text": "Ay Güney Kutbu İçin Çok-Eksenli Yeryüzü Test Sahası Değerlendirmesi", "size": 25.0, "bold": True, "color": "111111", "space_after_pt": 5},
            {"text": "Tekil puan aldatmacasını kıran, her skora ölçüm belirsizliği ve fiziksel kırılma sınırı bağlayan uydu tabanlı karar sistemi", "size": 12.5, "color": "404040"},
        ],
    )
    kpis = [
        ("5", "Artemis III Güney Kutbu referansı (LOLA 5 m/px)"),
        ("40", "Yeryüzü sahası (10 doğrulama, 30 test adayı)"),
        ("2 + 1", "v1 aktif eksen: Hareket, Yüzey (Termal askıda)"),
        ("0 / 51", "Sentetik (MOCK) satır / geçen birim test (pytest)"),
    ]
    s1.add_line(0.55, 1.78, 12.23, 0.0, color="111111", width_pt=1.0)
    s1.add_line(0.55, 2.55, 12.23, 0.0, color="D4D4D4", width_pt=0.75)
    for idx, (val, lbl) in enumerate(kpis):
        kx = 0.55 + idx * 3.08
        if idx > 0:
            s1.add_line(kx - 0.12, 1.85, 0.0, 0.62, color="E5E5E5", width_pt=0.75)
        s1.add_textbox(
            kx, 1.84, 2.88, 0.68,
            [
                {"text": val, "size": 21.0, "bold": True, "color": "111111", "font": "Consolas", "space_after_pt": 2},
                {"text": lbl, "size": 9.5, "color": "525252"},
            ],
        )
    s1.add_image(FIG_DIR / "fig1_orneklem_arazi.png", 0.55, 2.75, 12.23, 3.65)
    s1.add_textbox(
        0.55, 6.50, 12.23, 0.35,
        [{"text": "Gerçek uydu verisi: Shackleton Kenarı LRO LOLA 5 m/px kabartma & D–B kesiti (sol) ile Karapınar Meke, Hasandağı ve Etna 10 m Sentinel-2 L2A sahneleri (sağ)", "size": 9.5, "color": "525252"}],
    )
    s1.add_footer()
    slides.append(s1)

    # --- Slide 2: Problem -> Solution Matrix ---
    s2 = SlideBuilder(2, n_slides, "Temel gerekçe: her algoritmik seçimin çözdüğü somut mühendislik sorunu.")
    s2.add_header("Bölüm 1 · Yöntemsel Gerekçelendirme", "Hangi Sorunu Hangi Algoritmik Kararla Çözdük")
    s2.add_table(
        0.55, 1.25, 12.23, 4.95,
        [2.75, 3.30, 6.18],
        ["Klasik Yaklaşım Sorunu", "Uygulanan Algoritmik Çözüm", "Çözdüğü Fiziksel / İstatistiksel Problem"],
        [
            [
                "Ortalama skor aldatmacası",
                "Eksen ayrıştırma (Hareket, Yüzey, Termal)",
                "Etna Cisternazza Hareket ekseninde 40 saha içinde #3 (0.299) iken koyu tefra albedosu (0.047) yüzünden dengeli skorda #26'ya düşer; ayrıştırma rover test sahasını kurtarır",
            ],
            [
                "Kutupta derece gridi & makro eğim hatası",
                "Metrik CRS + np.linalg.lstsq düzlem arındırma",
                "89.78°S enleminde derece gridi eğimi bozar; ham yükseklik std'si ise tepe eğimini pürüzlülük sanır. Düzlem çıkarılarak yalnızca yerel mikro-rölyef ölçülür",
            ],
            [
                "Belirsizliği gizleyen nokta skor",
                "blake2b tohumlu 200 çekim MC + expanded_interval",
                "Her özelliğin uydu hata haritası (X_sd) skora yayılır; kar sınırındaki McMurdo (albedo_sd=0.096) geniş [0.088–0.513] P5–P95 bandıyla dürüstçe işaretlenir",
            ],
            [
                "Fiziksel rejim tutarsızlığı",
                "Bilinçli Termal Askıya Alma (Lider Kararı #30)",
                "Ay Güney Kutbu'nun 29.53 günlük vakumlu döngüsü (~187 K) ile Dünya'nın 24 saatlik atmosferli günlük döngüsü (2.7–29.3 K) aynı sayısal skora sokulmadı",
            ],
            [
                "Tek 'en iyi' saha saplantısı",
                "Açgözlü küme örtme (select_portfolio)",
                "En az saha ile tüm ulaşılabilir eksenleri örter; Dünya'da hiç ulaşılamayan eşikleri (ör. Shackleton Hareket >= 0.70) açık eksik olarak bildirir",
            ],
        ],
        font_pt=10.5,
        header_pt=10.5,
        pad_tb_pt=5.5,
    )
    s2.add_rect(0.55, 6.32, 12.23, 0.56, fill_color="F5F5F5", left_accent_pt=2.5)
    s2.add_textbox(
        0.72, 6.39, 11.95, 0.44,
        [{"runs": [
            {"text": "Tasarım ilkesi: ", "size": 10.5, "bold": True, "color": "111111"},
            {"text": "Her aşama aynı veri sözleşmesini (36 sütun, 0 MOCK) kullanır; skor hiçbir zaman fiziksel belirsizlikten daha kesinmiş gibi sunulmaz", "size": 10.5, "color": "262626"},
        ]}],
    )
    s2.add_footer()
    slides.append(s2)

    # --- Slide 3: Mathematical Design + 5 Moon References ---
    s3 = SlideBuilder(3, n_slides, "Matematiksel formülasyon ve 5 Artemis III Ay Güney Kutbu referansı.")
    s3.add_header("Bölüm 2 · Matematiksel Mimari", "Metrik Geometri, Düzlem Arındırma ve Üstel Skor Fonksiyonu")

    s3.add_rect(0.55, 1.20, 5.95, 2.55, border_color="D4D4D4")
    s3.add_textbox(
        0.72, 1.30, 5.60, 2.35,
        [
            {"text": "1. Metrik Projeksiyon ve lstsq Düzlem Arındırma", "size": 12.5, "bold": True, "color": "111111", "space_after_pt": 5},
            {"text": "Ay sahaları Polar Stereografik (R=1737.4 km), Dünya sahaları yerel UTM / UPS metrik projeksiyonda işlenir", "size": 10.5, "bullet": True, "space_after_pt": 4},
            {"text": "Ortak eğim tanımı: np.gradient -> arctan(hypot(dz/dx, dz/dy))", "size": 10.5, "bullet": True, "space_after_pt": 4},
            {"text": "Pürüzlülük: r = 1000 m çemberde en küçük kareler düzlemi (lstsq) çıkarıldıktan sonraki kalıntının standart sapması (ddof=1)", "size": 10.5, "bullet": True, "space_after_pt": 4},
            {"text": "Böylece Shackleton duvarının 18.5° makro eğimi 90.43 m mikro-pürüzlülüğe karışmadan ayrıştırılır", "size": 10.5, "bullet": True},
        ],
    )

    s3.add_rect(6.83, 1.20, 5.95, 2.55, border_color="D4D4D4")
    s3.add_textbox(
        7.00, 1.30, 5.60, 1.15,
        [
            {"text": "2. Üst-Sınırsız Z-Skoru ve exp(-D) Sıralama İndeksi", "size": 12.5, "bold": True, "color": "111111", "space_after_pt": 5},
            {"text": "Dünya evreni (n=40, ddof=0) ile Z-skoruna çevrilir; sert kesimli normalizasyonun aksine uç farklarda sıralama türevi ölmez", "size": 10.5, "bullet": True},
        ],
    )
    s3.add_rect(7.00, 2.40, 5.60, 0.72, fill_color="F5F5F5", left_accent_pt=2.0)
    s3.add_textbox(
        7.14, 2.46, 5.36, 0.62,
        [
            {"text": "D_axis = sqrt(mean_f(((x_earth - x_ref) / sigma_earth)^2))", "size": 9.5, "font": "Consolas", "color": "111111", "space_after_pt": 2},
            {"text": "S_axis = exp(-D_axis)  ->  (0, 1]   [olasılık değil, sıralama indeksi]", "size": 9.5, "font": "Consolas", "color": "111111"},
        ],
    )
    s3.add_textbox(
        7.00, 3.22, 5.60, 0.45,
        [{"text": "Birebir fiziksel eşleşmede 1.000 üretir; eksen ağırlıklı ortalaması genel skoru verir", "size": 10.0, "color": "525252"}],
    )

    s3.add_textbox(
        0.55, 3.88, 12.23, 0.30,
        [{"text": "Referans 5 Artemis III Ay Güney Kutbu Sahası (LRO LOLA PGDA 5 m/px, r = 1000 m)", "size": 11.5, "bold": True, "color": "111111"}],
    )
    moon_rows = [
        [
            short_label(str(r["site_id"])),
            f"{r['lat']:.2f}°, {r['lon']:.2f}°",
            f"{r['slope_mean']:.2f} ± {r['slope_mean_sd']:.2f}°",
            f"{r['slope_p90']:.2f}°",
            f"{r['roughness']:.2f} m",
            f"{r['relief']:.1f} m",
            f"{r['albedo']:.3f} ± {r['albedo_sd']:.3f}",
        ]
        for _, r in data["moon_df"].iterrows()
    ]
    s3.add_table(
        0.55, 4.22, 12.23, 2.65,
        [2.75, 1.95, 1.85, 1.25, 1.45, 1.35, 1.63],
        ["Ay Referans Sahası", "Koordinat", "Ort. Eğim ± sd", "P90 Eğim", "Pürüzlülük", "Rölyef", "Albedo ± sd"],
        moon_rows,
        num_cols={1, 2, 3, 4, 5, 6},
        font_pt=9.5,
        header_pt=9.5,
        pad_tb_pt=4.0,
    )
    s3.add_footer()
    slides.append(s3)

    # --- Slide 4: Uncertainty, Albedo Calibration & Audit Bars ---
    s4 = SlideBuilder(4, n_slides, "200 draw MC belirsizliği, 0.38 albedo kalibrasyon duyarlılığı ve veri denetim özeti.")
    s4.add_header("Bölüm 3 · Belirsizlik ve Sağlamlık", "Monte Carlo Yayılımı, Albedo Duyarlılığı ve Veri Bütünlüğü")

    s4.add_rect(0.55, 1.20, 5.95, 1.65, fill_color="F5F5F5", left_accent_pt=2.0)
    s4.add_textbox(
        0.72, 1.28, 5.65, 1.48,
        [
            {"text": "200 Çekimli Deterministik Monte Carlo (blake2b)", "size": 11.5, "bold": True, "color": "111111", "space_after_pt": 4},
            {"text": "PGDA klon hatası (slperr/toterr) + GLO-30 sigma_z_rel=1.0 m her adımda çekilir", "size": 10.0, "bullet": True, "space_after_pt": 3},
            {"text": "expanded_interval(): Doğrusal olmayan exp(-D) kaymasında noktayı [q05, q95] içinde tutar", "size": 10.0, "bullet": True},
        ],
    )

    s4.add_rect(6.83, 1.20, 5.95, 1.65, fill_color="F5F5F5", left_accent_pt=2.0)
    s4.add_textbox(
        7.00, 1.28, 5.65, 1.48,
        [
            {"text": "LOLA 1064 nm -> ×0.38 ve Termal Askıya Alma (Karar #30)", "size": 11.5, "bold": True, "color": "111111", "space_after_pt": 4},
            {"text": "c ∈ [0.34, 0.42] bandında 5 Ay bölgesinin tamamında Spearman ρ = 0.866–0.944 korunur", "size": 10.0, "bullet": True, "space_after_pt": 3},
            {"text": "Diviner (29.53 gün) ile MODIS (24 saat) farklı rejim olduğundan termal eksen v1'de NaN bırakıldı", "size": 10.0, "bullet": True},
        ],
    )

    s4.add_image(FIG_DIR / "fig6_albedo_ve_belirsizlik.png", 0.55, 2.98, 12.23, 3.85)
    s4.add_footer()
    slides.append(s4)

    # --- Slide 5: Data Verification, Resolution Gap & Mixed-Pixel Audit ---
    s5 = SlideBuilder(5, n_slides, "Veri doğruluğu: 0 MOCK, NASADEM fallback, 5 m vs 30 m sınırı ve 5 karışık piksel.")
    s5.add_header("Bölüm 4 · Veri Doğruluğu ve Ölçek Denetimi", "Uydu Ürünleri, Çözünürlük Uçurumu ve 10 m Karışık Piksel Denetimi")

    s5.add_rect(0.55, 1.18, 5.95, 1.68, border_color="D4D4D4")
    s5.add_textbox(
        0.72, 1.26, 5.65, 1.52,
        [
            {"text": "Doğrulanmış Uydu Envanteri (0/45 MOCK · 51 pytest)", "size": 11.5, "bold": True, "color": "111111", "space_after_pt": 4},
            {"text": "Ay: LRO LOLA PGDA v2021 (5 m) + LOLA LDAM 1064 nm (1000 m)", "size": 10.0, "bullet": True, "space_after_pt": 3},
            {"text": "Dünya DEM: 39/40 Copernicus GLO-30 (30 m, LE90<2 m) + 1 NASADEM (Ağrı N39 E044 404 yedeği)", "size": 10.0, "bullet": True, "space_after_pt": 3},
            {"text": "Dünya Albedo: MCD43A3.061 (500 m) + MCD43A4.061 Liang (2001) çapraz doğrulama", "size": 10.0, "bullet": True},
        ],
    )

    s5.add_rect(6.83, 1.18, 5.95, 1.68, border_color="D4D4D4")
    s5.add_textbox(
        7.00, 1.26, 5.65, 1.52,
        [
            {"text": "İki Açık Ölçek Kısıtı (Dürüst Sınır Beyanı)", "size": 11.5, "bold": True, "color": "111111", "space_after_pt": 4},
            {"text": "1) 5 m LOLA vs 30 m Dünya DEM (6× fark): 30 m piksel Ay ölçeğindeki bloklu mikro-rölyefi yumuşatır", "size": 10.0, "bullet": True, "space_after_pt": 3},
            {"text": "2) 500 m MODIS karışımı: 40 sahanın tamamı 10 m WorldCover + Sentinel-2 SCL ile taranıp 5 MIXED_* saha ayrıldı", "size": 10.0, "bullet": True},
        ],
    )

    s5.add_table(
        0.55, 2.98, 12.23, 3.85,
        [2.35, 1.75, 3.45, 4.68],
        ["Denetlenen Saha", "Bayrak", "10 m Örtü Payı (WorldCover / S2)", "Fiziksel Etki ve Yorum"],
        [
            ["Salda Gölü Terası (TR)", "MIXED_CROP+VEG", "Çıplak %2.0 · Tarım %40.2 · Bitki %55.9", "Dar hidromanyezit kıyı barı (~150 m) 500 m MODIS pikseli içinde yan kayaçla karışır"],
            ["Tuz Gölü Güney (TR)", "MIXED_WATER", "Çıplak/tuz %73.2 · Sığ su %26.8", "S2 SCL=11 (%17.6) parlak haliti yanlış kar görür; MCD43A3 (0.206) NDSI maskesiz olduğundan etkilenmez"],
            ["Svalbard Bockfjorden", "MIXED_WATER+VEG", "Çıplak %41.1 · Fiyort %15.5 · Tundra %43.1", "1 km pencerede fiyort suyu ve Arktik tundra albedoyu ve arşiv LST genliğini bastırır"],
            ["Süphan Güney Eteği (TR)", "MIXED_CROP+VEG", "Mera %79.2 · Tarım %18.4 · Çıplak %2.3", "Haziran yeşil (NDVI 0.251), Eylül kuru anız (bare_5 %99.8); yakında daha çıplak düşük eğim yok"],
            ["Meteor Crater (AZ)", "MIXED_VEG", "Çıplak %57.3 · Çöl çalısı %41.9", "Yaz S2 optikte %99.9 çıplak olsa da WorldCover %41.9 seyrek çalı işaretler"],
            ["Etna Cisternazza (Kontrol)", "PURE_TARGET", "Çıplak tefra %99.4 · Bitki %0.6", "Gerçek OSM Cisternazza kraterine (37.7257, 15.0084) taşındı; Şubat kar payı %22.0"],
        ],
        font_pt=9.2,
        header_pt=9.5,
        pad_tb_pt=4.0,
    )
    s5.add_footer()
    slides.append(s5)

    # --- Slide 6: Shackleton Results Top 15 & Decoupling ---
    s6 = SlideBuilder(6, n_slides, "Shackleton Kenarı ilk 15 saha, P5–P95 belirsizlik bantları ve #26 Etna örneği.")
    s6.add_header("Bölüm 5 · Shackleton Krater Kenarı Analizi", "Tek Skor Yerine Bağımsız Hareket ve Yüzey Ayrışması (İlk 15 + Etna)")

    s1_r = sh_bal.loc["earth_karapinar_meke"]
    s2_r = sh_bal.loc["earth_mcmurdo_wright_valley"]
    s3_r = sh_bal.loc["earth_hasandagi_kecekalecik"]
    et_r = sh_bal.loc["earth_etna_cisternazza"]
    cards6 = [
        ("#1 Karapınar Meke (TR)", f"Genel {s1_r['score']:.3f} · Yüzey {s1_r['surface']:.3f} (#1)", f"Hareket {s1_r['mobility']:.3f} — güçlü albedo, orta eğim"),
        ("#2 McMurdo Wright [Doğr.]", f"Genel {s2_r['score']:.3f} · [{s2_r['exp_lo']:.3f}–{s2_r['exp_hi']:.3f}]", "Yüksek albedo_sd (0.096) yüzünden geniş P5–P95 bandı"),
        ("#3 Hasandağı (TR)", f"Hareket {s3_r['mobility']:.3f} (#1) · Genel {s3_r['score']:.3f}", "40 saha içinde Shackleton'a en yakın eğim/rölyef profili"),
        (f"#{int(et_r['rank'])} Etna [Doğr.]", f"Hareket {et_r['mobility']:.3f} (#{int(sh_bv_mob['earth_etna_cisternazza'])}) · Yüzey {et_r['surface']:.3f}", "Taze siyah tefra (0.047) dengeli skorda Etna'yı aşağı çeker"),
    ]
    for i, (t1, t2, t3) in enumerate(cards6):
        cx = 0.55 + i * 3.09
        s6.add_rect(cx, 1.20, 2.95, 1.05, fill_color="F5F5F5", left_accent_pt=2.0)
        s6.add_textbox(
            cx + 0.10, 1.26, 2.78, 0.94,
            [
                {"text": t1, "size": 10.5, "bold": True, "color": "111111", "space_after_pt": 2},
                {"text": t2, "size": 9.5, "font": "Consolas", "color": "171717", "space_after_pt": 2},
                {"text": t3, "size": 8.8, "color": "525252"},
            ],
        )

    s6.add_image(FIG_DIR / "fig2_shackleton_eksenler.png", 0.55, 2.38, 12.23, 4.55)
    s6.add_footer()
    slides.append(s6)

    # --- Slide 7: Mission Weighting Slopegraph ---
    s7 = SlideBuilder(7, n_slides, "Görev profili değiştiğinde Shackleton sıralamasının evrimi.")
    s7.add_header("Bölüm 6 · Görev Duyarlılığı", "Görev Ağırlıkları Değiştiğinde Saha Önceliği Nasıl Yeniden Sıralanır")

    m1 = sh_mob.loc["earth_hasandagi_kecekalecik"]
    m2 = sh_mob.loc["earth_erciyes_kojugedigi"]
    me = sh_mob.loc["earth_etna_cisternazza"]
    rk1 = sh_rad.loc["earth_karapinar_meke"]
    rk3 = sh_rad.loc["earth_agri_dogubayazit_flow"]
    missions = [
        ("Dengeli Mod (1 : 1)", f"#1 Karapınar Meke ({sh_bal.loc['earth_karapinar_meke','score']:.3f}) · #2 McMurdo · #3 Hasandağı", "İki aktif ekseni eşit ağırlıkla değerlendiren referans baz"),
        ("Rover Hareket Modu (2 : 1)", f"#1 Hasandağı ({m1['score']:.3f}) · #2 Erciyes ({m2['score']:.3f}) · Etna #{int(et_r['rank'])}->#{int(me['rank'])}", "Eğim ve rölyef iki kat ağırlık alır; tekerlek/şasi test sahaları öne çıkar"),
        ("Radar / Yüzey Modu (1 : 2)", f"#1 Karapınar ({rk1['score']:.3f}) · #2 McMurdo · #3 Ağrı ({rk3['score']:.3f})", "Geniş bant yüzey yansıması öne çıkar; Etna 32. sıraya geriler"),
    ]
    for i, (mt, ms, md) in enumerate(missions):
        mx = 0.55 + i * 4.13
        s7.add_rect(mx, 1.20, 3.96, 1.12, border_color="D4D4D4")
        s7.add_textbox(
            mx + 0.12, 1.28, 3.72, 0.98,
            [
                {"text": mt, "size": 11.0, "bold": True, "color": "111111", "space_after_pt": 3},
                {"text": ms, "size": 9.3, "font": "Consolas", "color": "111111", "space_after_pt": 3},
                {"text": md, "size": 9.0, "color": "525252"},
            ],
        )

    s7.add_image(FIG_DIR / "fig3_gorev_duyarliligi.png", 0.55, 2.45, 12.23, 4.45)
    s7.add_footer()
    slides.append(s7)

    # --- Slide 8: 5 Moon Regions & Turkish Candidates + Novelty ---
    s8 = SlideBuilder(8, n_slides, "5 Ay bölgesinde skor haritası, Türkiye adayları ve Karacadağ dürüst değerlendirmesi.")
    s8.add_header("Bölüm 7 · Çok-Bölgeli Analiz ve Türkiye Adayları", "Beş Artemis III Bölgesinde Performans ve Literatür Konumlandırması")

    s8.add_image(FIG_DIR / "fig4_bes_bolge_isi.png", 0.55, 1.18, 12.23, 4.22)

    kz = ed_idx.loc["earth_karacadag_summit"]
    ko = ed_idx.loc["earth_karacadag_ovabag"]
    kz_sh = sh_bal.loc["earth_karacadag_summit"]
    kz_fa = fa_bal.loc["earth_karacadag_summit"]
    ko_sh = sh_bal.loc["earth_karacadag_ovabag"]

    s8.add_rect(0.55, 5.52, 5.95, 1.42, fill_color="F5F5F5", left_accent_pt=2.0)
    s8.add_textbox(
        0.72, 5.58, 5.65, 1.32,
        [
            {"text": "Türkiye Adaylarında Özgünlük Dürüstlüğü (AGENTS.md §7)", "size": 10.5, "bold": True, "color": "111111", "space_after_pt": 3},
            {"text": "Bilinen analoglar: Salda (NASA Perseverance/Jezero, Horgan 2020), Karapınar ve Tuz Gölü yeni keşif olarak sunulmaz", "size": 9.3, "bullet": True, "space_after_pt": 2},
            {"text": "Nicel adaylar: Hasandağı, Erciyes, Ağrı, Kula, Tendürek, Nemrut, Kapadokya 'aday test sahası' statüsündedir", "size": 9.3, "bullet": True},
        ],
    )

    s8.add_rect(6.83, 5.52, 5.95, 1.42, border_color="D4D4D4")
    s8.add_textbox(
        7.00, 5.58, 5.65, 1.32,
        [
            {"text": "Karacadağ Bulgusu (Zirve vs Ovabağ Ayrımı)", "size": 10.5, "bold": True, "color": "111111", "space_after_pt": 3},
            {"text": f"Zirve (Kollubaba, eğim {kz['slope_mean']:.2f}°): Dik Shackleton'da #{int(kz_sh['rank'])} ({kz_sh['score']:.3f}) iken düz Faustini'de #{int(kz_fa['rank'])} ({kz_fa['score']:.3f})", "size": 9.3, "bullet": True, "space_after_pt": 2},
            {"text": f"Ovabağ ({ko['slope_mean']:.2f}°, pür. {ko['roughness']:.1f} m): Aşırı düz olduğundan krater kenarlarıyla düşük uyumludur (Shackleton #{int(ko_sh['rank'])})", "size": 9.3, "bullet": True},
        ],
    )
    s8.add_footer()
    slides.append(s8)

    # --- Slide 9: Blind Validation, Greedy Portfolio & Breakdown Limits ---
    s9 = SlideBuilder(9, n_slides, "Rol-kör doğrulama sıra kayması, 0.70 portföy kapsamı ve yeryüzü fiziksel sınırları.")
    s9.add_header("Bölüm 8 · Kör Doğrulama, Portföy ve Fiziksel Kırılma Sınırları", "Literatür Tutarlılığı, Minimum Test Portföyü ve Kopyalanamayan Sınırlar")

    s9.add_image(FIG_DIR / "fig5_fiziksel_uzay_dogrulama.png", 0.55, 1.15, 12.23, 3.38)

    # Portfolio left
    port_rows = []
    for mid in ["moon_shackleton_rim", "moon_de_gerlache_rim", "moon_connecting_ridge", "moon_shackleton_peak", "moon_faustini_rim"]:
        pm = data["per_moon"][mid]
        sel = ", ".join(short_label(s).replace(" [Doğr.]", "").replace(" (TR)", "") for s in pm["portfolio_selected"])
        unc = "Yok" if not pm["portfolio_uncovered"] else "Hareket (<0.70)"
        port_rows.append([short_label(mid), sel, unc])

    s9.add_textbox(
        0.55, 4.62, 6.20, 0.25,
        [{"text": f"Açgözlü Portföy (Eşik = 0.70) · Shackleton Etna #{int(sh_bv_mob['earth_etna_cisternazza'])} vs Faustini Svalbard #{int(fa_bv_mob['earth_svalbard_bockfjorden'])}", "size": 9.8, "bold": True, "color": "111111"}],
    )
    s9.add_table(
        0.55, 4.90, 6.20, 2.02,
        [2.00, 2.65, 1.55],
        ["Ay Hedefi", "Seçilen Portföy", "Açık Eksen"],
        port_rows,
        font_pt=8.8,
        header_pt=9.0,
        pad_tb_pt=2.5,
    )

    # Physical limits right
    s9.add_textbox(
        6.98, 4.62, 5.80, 0.25,
        [{"text": "Yeryüzünün Kopyalayamadığı Fiziksel Sınırlar", "size": 9.8, "bold": True, "color": "111111"}],
    )
    s9.add_table(
        6.98, 4.90, 5.80, 2.02,
        [1.35, 1.45, 3.00],
        ["Parametre", "Ay Kutbu", "Dünya Kırılma Sınırı"],
        [
            ["Yerçekimi", "0.165 g", "1 g (6× fazla); tekerlek batması ve şasi yükü farklıdır"],
            ["Vakum / Toz", "~10^-12 torr", "Hava sönümlemesi & aşınmayan nemli/kil tozu"],
            ["Termal", "29.53 gün", "24 saat döngü; kriyojenik vakum şoku şarttır"],
            ["Ölçek / Buz", "5 m / PSR buz", "30 m Dünya DEM'i kayaları yumuşatır; v1'de buz verisi yok"],
        ],
        font_pt=8.8,
        header_pt=9.0,
        pad_tb_pt=2.5,
    )
    s9.add_footer()
    slides.append(s9)

    # --- Slide 10: Dual Interfaces, QA & Closing ---
    s10 = SlideBuilder(10, n_slides, "Kapanış: Canlı demo arayüzleri (Web Observatory ve Streamlit) ve sözleşme güvencesi.")
    s10.add_header("Bölüm 9 · Ürün Mimarisi ve Doğrulama Zinciri", "Aynı Doğrulanmış Veriden Beslenen İki Tamamlayıcı Karar Arayüzü")

    s10.add_rect(0.55, 1.25, 5.95, 3.25, border_color="D4D4D4")
    s10.add_textbox(
        0.75, 1.38, 5.55, 3.00,
        [
            {"text": "Web Observatory (web/)", "size": 14.0, "bold": True, "color": "111111", "space_after_pt": 6},
            {"text": "React 18 + Vite + Leaflet GIS + D3 Radar + Three.js WebGL (51×51 3B arazi)", "size": 10.5, "color": "525252", "space_after_pt": 8},
            {"text": "İstemci taraflı TypeScript motoru (scoring.ts) ile anlık ağırlık sürgüleri ve dinamik portföy eşiği", "size": 10.8, "bullet": True, "space_after_pt": 6},
            {"text": "V1 veri kapsama dürüstlüğü nedeniyle yalnızca 3 görev ön ayarı + özel ağırlık modu sunulur; ISRU ayrıştırılmıştır", "size": 10.8, "bullet": True, "space_after_pt": 6},
            {"text": "Sunum sırasında harita, radar ve topoğrafik kesit karşılaştırması canlı gösterilir", "size": 10.8, "bullet": True},
        ],
    )

    s10.add_rect(6.83, 1.25, 5.95, 3.25, border_color="D4D4D4")
    s10.add_textbox(
        7.03, 1.38, 5.55, 3.00,
        [
            {"text": "Araştırma Workbench'i (app/)", "size": 14.0, "bold": True, "color": "111111", "space_after_pt": 6},
            {"text": "Streamlit + PyDeck + Plotly (6 sekme, monokrom teknik inceleme)", "size": 10.5, "color": "525252", "space_after_pt": 8},
            {"text": "Doğrudan src/scoring/ Python referans çekirdeğini çalıştırır", "size": 10.8, "bullet": True, "space_after_pt": 6},
            {"text": "LRO LOLA 5 m hillshade & tehlike haritaları yanında 10 m Sentinel-2 L2A görsel bağlam atlasını inceler", "size": 10.8, "bullet": True, "space_after_pt": 6},
            {"text": "Kör Doğrulama ve tüm 4 MISSION_PRESETS ön ayarını kaynak kod referansı olarak taşır", "size": 10.8, "bullet": True},
        ],
    )

    s10.add_rect(0.55, 4.72, 12.23, 0.92, fill_color="F5F5F5", border_color="D4D4D4")
    s10.add_textbox(
        0.75, 4.80, 11.83, 0.78,
        [
            {"text": "python scripts/validate_all.py --fail-on-mock   ->   GECTI: 2 dosya, 0 hata, 0 uyari, 0/45 MOCK", "size": 10.5, "font": "Consolas", "color": "111111", "space_after_pt": 4},
            {"text": "pytest -q                                        ->   51 passed (skor, belirsizlik, portfoy, dogrulama, Earth/Moon boru hatlari)", "size": 10.5, "font": "Consolas", "color": "111111"},
        ],
    )

    s10.add_rect(0.55, 5.82, 12.23, 0.96, fill_color="FFFFFF", left_accent_pt=3.0)
    s10.add_textbox(
        0.75, 5.92, 11.85, 0.80,
        [{"runs": [
            {"text": "Sonuç: ", "size": 12.0, "bold": True, "color": "111111"},
            {"text": "Yeryüzünde tek bir mükemmel Ay analogu yoktur. Sistemimiz bunu gizlemek yerine ölçülebilir eksenlerle hangi sahanın hangi testi karşıladığını, belirsizliğini ve ne zaman testin Dünya sınırını aştığını gösterir", "size": 11.5, "color": "262626"},
        ]}],
    )
    s10.add_footer()
    slides.append(s10)

    return slides


def write_pptx(slides: list[SlideBuilder], out_path: Path) -> None:
    """Package slides and shared OOXML boilerplate into a standard valid .pptx zip."""
    n = len(slides)

    content_types_overrides = "".join(
        f'<Override PartName="/ppt/slides/slide{s.slide_num}.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        f'<Override PartName="/ppt/notesSlides/notesSlide{s.slide_num}.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/>'
        for s in slides
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Default Extension="png" ContentType="image/png"/>'
        '<Default Extension="jpg" ContentType="image/jpeg"/>'
        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
        '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>'
        '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>'
        '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
        '<Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>'
        '<Override PartName="/ppt/viewProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"/>'
        f'{content_types_overrides}'
        '</Types>'
    )

    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>'
        '</Relationships>'
    )

    sld_id_list = "".join(
        f'<p:sldId id="{256 + i}" r:id="rSld{i + 1}"/>' for i in range(n)
    )
    presentation_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" saveSubsetFonts="1">'
        '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rIdMaster1"/></p:sldMasterIdLst>'
        f'<p:sldIdLst>{sld_id_list}</p:sldIdLst>'
        f'<p:sldSz cx="{SLIDE_W}" cy="{SLIDE_H}" type="custom"/>'
        '<p:notesSz cx="6858000" cy="9144000"/>'
        '</p:presentation>'
    )

    pres_rels_items = [
        '<Relationship Id="rIdMaster1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>',
        '<Relationship Id="rIdTheme1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>',
        '<Relationship Id="rIdPresProps" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps" Target="presProps.xml"/>',
        '<Relationship Id="rIdViewProps" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps" Target="viewProps.xml"/>',
    ] + [
        f'<Relationship Id="rSld{i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i + 1}.xml"/>'
        for i in range(n)
    ]
    pres_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{"".join(pres_rels_items)}</Relationships>'
    )

    theme1 = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Monochrome Editorial">'
        '<a:themeElements>'
        '<a:clrScheme name="Graphite"><a:dk1><a:srgbClr val="111111"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>'
        '<a:dk2><a:srgbClr val="404040"/></a:dk2><a:lt2><a:srgbClr val="F5F5F5"/></a:lt2>'
        '<a:accent1><a:srgbClr val="171717"/></a:accent1><a:accent2><a:srgbClr val="9A3412"/></a:accent2>'
        '<a:accent3><a:srgbClr val="525252"/></a:accent3><a:accent4><a:srgbClr val="737373"/></a:accent4>'
        '<a:accent5><a:srgbClr val="A3A3A3"/></a:accent5><a:accent6><a:srgbClr val="D4D4D4"/></a:accent6>'
        '<a:hlink><a:srgbClr val="111111"/></a:hlink><a:folHlink><a:srgbClr val="525252"/></a:folHlink></a:clrScheme>'
        '<a:fontScheme name="Segoe UI">'
        '<a:majorFont><a:latin typeface="Segoe UI"/><a:ea typeface="Segoe UI"/><a:cs typeface="Segoe UI"/></a:majorFont>'
        '<a:minorFont><a:latin typeface="Segoe UI"/><a:ea typeface="Segoe UI"/><a:cs typeface="Segoe UI"/></a:minorFont>'
        '</a:fontScheme>'
        '<a:fmtScheme name="Basic"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
        '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>'
        '<a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>'
        '<a:ln w="19050"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>'
        '<a:ln w="25400"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>'
        '<a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle>'
        '<a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>'
        '<a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
        '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst>'
        '</a:fmtScheme></a:themeElements></a:theme>'
    )

    slide_master = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        '<p:cSld><p:bg><p:bgRef idx="1001"><a:schemeClr val="bg1"/></p:bgRef></p:bg>'
        '<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
        '</p:spTree></p:cSld>'
        '<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" '
        'accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>'
        '<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rIdLayout1"/></p:sldLayoutIdLst>'
        '</p:sldMaster>'
    )
    slide_master_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rIdLayout1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
        '<Relationship Id="rIdTheme1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>'
        '</Relationships>'
    )
    slide_layout = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">'
        '<p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
        '</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'
    )
    slide_layout_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rIdMaster1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>'
        '</Relationships>'
    )
    pres_props = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:presProps xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>'
    )
    view_props = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:viewProps xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>'
    )

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", root_rels)
        zf.writestr("ppt/presentation.xml", presentation_xml)
        zf.writestr("ppt/_rels/presentation.xml.rels", pres_rels)
        zf.writestr("ppt/presProps.xml", pres_props)
        zf.writestr("ppt/viewProps.xml", view_props)
        zf.writestr("ppt/theme/theme1.xml", theme1)
        zf.writestr("ppt/slideMasters/slideMaster1.xml", slide_master)
        zf.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", slide_master_rels)
        zf.writestr("ppt/slideLayouts/slideLayout1.xml", slide_layout)
        zf.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", slide_layout_rels)

        for s in slides:
            s.rels.append(
                (
                    "rIdNotes",
                    "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide",
                    f"../notesSlides/notesSlide{s.slide_num}.xml",
                )
            )
            zf.writestr(f"ppt/slides/slide{s.slide_num}.xml", s.to_slide_xml())
            zf.writestr(f"ppt/slides/_rels/slide{s.slide_num}.xml.rels", s.to_rels_xml())
            for media_name, blob in s.media_files:
                zf.writestr(f"ppt/media/{media_name}", blob)

            notes_xml = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<p:notes xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
                'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
                '<p:cSld><p:spTree>'
                '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
                '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
                '<p:sp><p:nvSpPr><p:cNvPr id="2" name="Notes"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr>'
                f'<p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr lang="tr-TR"/><a:t>{escape(s.notes_text)}</a:t></a:r></a:p></p:txBody></p:sp>'
                '</p:spTree></p:cSld></p:notes>'
            )
            notes_rels = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                f'<Relationship Id="rIdSlide" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="../slides/slide{s.slide_num}.xml"/>'
                '</Relationships>'
            )
            zf.writestr(f"ppt/notesSlides/notesSlide{s.slide_num}.xml", notes_xml)
            zf.writestr(f"ppt/notesSlides/_rels/notesSlide{s.slide_num}.xml.rels", notes_rels)


def render_and_verify_slides(expected_slides: int) -> None:
    """Convert PPTX via headless LibreOffice to PDF and rasterize all slides to scratch PNGs."""
    soffice = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")
    if not soffice.exists():
        raise FileNotFoundError(f"LibreOffice not found at {soffice}")

    scratch = Path(r"C:\Users\ASUS\.gemini\antigravity\brain\a87bc1f2-c8f4-46ac-9084-98d1166941ca\scratch\pptx_preview")
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir(parents=True, exist_ok=True)

    res = subprocess.run(
        [
            str(soffice),
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(scratch),
            str(PPTX_PATH),
        ],
        capture_output=True,
        check=True,
    )
    print("SOFFICE_OUT:", res.stdout.decode("utf-8", errors="replace").strip())

    pdf_file = scratch / f"{PPTX_PATH.stem}.pdf"
    import fitz

    doc = fitz.open(str(pdf_file))
    print("PPTX_RENDERED_PAGES:", len(doc))
    if len(doc) != expected_slides:
        raise RuntimeError(f"Expected {expected_slides} rendered slides, got {len(doc)}")
    for idx, page in enumerate(doc, start=1):
        pix = page.get_pixmap(dpi=150)
        pix.save(str(scratch / f"slide_{idx}.png"))
    doc.close()


def main() -> None:
    """Build slides from verified pipeline data, export PPTX, and rasterize previews."""
    data = compute_all_metrics()
    slides = build_slides(data)
    write_pptx(slides, PPTX_PATH)
    render_and_verify_slides(len(slides))
    print("PPTX_BUILD_OK:", PPTX_PATH, "SLIDES:", len(slides))


if __name__ == "__main__":
    main()
