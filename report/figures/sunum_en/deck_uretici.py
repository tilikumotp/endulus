# 7-slide English submission deck for NASA Space Apps global judging.
# MAX 7 slides (cover + team included) - the jury rule. All content English,
# every number from the verified app_data.json tables (no recomputation).
import pathlib

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

ROOT = pathlib.Path(r"T:\Endülüs")
FIG = ROOT / "report/figures/sunum_en"
OUT = ROOT / "report/nasa_submission_7slides.pptx"

PAPER = RGBColor(0xFA, 0xF9, 0xF6)
INK = RGBColor(0x22, 0x25, 0x2A)
INK2 = RGBColor(0x56, 0x5B, 0x64)
INK3 = RGBColor(0x8A, 0x8F, 0x98)
ACCENT = RGBColor(0x2B, 0x5A, 0xA6)
SURFACE = RGBColor(0xF1, 0xEF, 0xEA)
HAIR = RGBColor(0xE4, 0xE2, 0xDD)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
SW, SH = 13.333, 7.5


def slide():
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = PAPER
    return s


def txt(s, x, y, w, h, lines, align=PP_ALIGN.LEFT, space_after=6):
    """lines: list of (text, size, color, bold, font, italic)"""
    box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    for i, (t, size, color, bold, font) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space_after)
        r = p.add_run()
        r.text = t
        r.font.size = Pt(size)
        r.font.color.rgb = color
        r.font.bold = bold
        r.font.name = font
    return box


def kicker(s, text):
    txt(s, 0.5, 0.32, 12.3, 0.4, [(text, 11, INK3, False, "Consolas")])


def title(s, text):
    txt(s, 0.5, 0.62, 12.3, 0.85, [(text, 27, INK, True, "Georgia")])


def hairline(s, y=1.42):
    ln = s.shapes.add_shape(1, Inches(0.5), Inches(y), Inches(12.33), Emu(9525))  # 1px line
    ln.fill.solid()
    ln.fill.fore_color.rgb = HAIR
    ln.line.fill.background()


def pageno(s, n):
    txt(s, 12.35, 7.05, 0.7, 0.35, [(f"{n}/7", 10, INK3, False, "Consolas")], align=PP_ALIGN.RIGHT)


def bullets(s, x, y, w, h, items, size=13, gap=7, color=INK2):
    lines = [(("• " + t) if t else "", size, color, False, "Segoe UI") for t in items]
    txt(s, x, y, w, h, lines, space_after=gap)


def img(s, path, x, y, w, aspect):
    return s.shapes.add_picture(str(path), Inches(x), Inches(y), width=Inches(w), height=Inches(w / aspect))


# ============================== SLIDE 1 · COVER =====================================
s = slide()
txt(s, 0.9, 1.55, 11.5, 0.4, [("NASA SPACE APPS CHALLENGE 2026 · TEAM ENDÜLÜS · GLOBAL JUDGING SUBMISSION", 12, INK3, False, "Consolas")])
txt(s, 0.9, 2.05, 11.5, 1.5, [("Moon Analogue Scorer", 54, INK, True, "Georgia")])
txt(s, 0.9, 3.45, 11.0, 0.5, [("Challenge: Permanent Moon Base Locations and Mars", 18, ACCENT, False, "Segoe UI")])
txt(s, 0.9, 4.15, 10.6, 1.2, [(
    "A per-axis, uncertainty-aware Earth analogue scorer for lunar south pole hardware testing - "
    "built entirely from open satellite data (LOLA, Copernicus GLO-30, MODIS).",
    15.5, INK2, False, "Segoe UI")])
bar = s.shapes.add_shape(1, Inches(0.9), Inches(5.45), Inches(3.2), Emu(28575))
bar.fill.solid(); bar.fill.fore_color.rgb = ACCENT; bar.line.fill.background()
txt(s, 0.9, 6.55, 11.5, 0.4, [("github.com/tilikumotp/endulus (public) · Team of 4 · November 15, 2026", 12, INK3, False, "Consolas")])

# ============================== SLIDE 2 · WHY AND HOW ===============================
s = slide()
kicker(s, "PROBLEM AND METHOD")
title(s, "Which Earth site can test which subsystem - and where must a lab step in?")
hairline(s)
txt(s, 0.5, 1.62, 5.9, 0.4, [("THE PROBLEM", 13, ACCENT, True, "Consolas")])
bullets(s, 0.5, 2.05, 5.9, 4.6, [
    "Hardware must be tested on Earth before flight; the classic analogue sites (Atacama, Etna, Mauna Loa, Haughton) are abroad and expensive.",
    'A "generic analogue" label can fail the real subsystem: a flat desert cannot test wheel climbing; a very dark lava flow does not match polar regolith brightness for camera exposure.',
    "Türkiye has no quantitative, evidence-based national test-bed inventory - our two gaps to fill.",
], size=13.5, gap=9)
txt(s, 6.95, 1.62, 5.9, 0.4, [("THE METHOD", 13, ACCENT, True, "Consolas")])
bullets(s, 6.95, 2.05, 5.9, 4.6, [
    "40 Earth sites (14 in Türkiye) vs 5 Moon south-pole reference regions; identical 1 km-radius aggregation on both bodies.",
    "Same features everywhere: mean slope, p90 slope, roughness, relief (Mobility axis) and broadband albedo (Surface axis).",
    "z-scored distance D against the 40-site pool, score = exp(-D); Monte Carlo error bands (n=200, fixed seed).",
    "Three mission profiles reweight the axes: Balanced 50/50, Climbing 67/33, Optical 33/67.",
    "Thermal axis suspended (NaN): Diviner lunar local-time and MODIS 24-h definitions differ - we do not invent numbers.",
], size=13, gap=7)
pageno(s, 2)

# ============================== SLIDE 3 · RESULTS ===================================
s = slide()
kicker(s, "RESULTS · SHACKLETON CRATER RIM (STEEP REFERENCE)")
title(s, "Top 10 Earth sites - and an honest read of the #1")
hairline(s)
img(s, FIG / "figA_top10_shackleton_en.png", 0.5, 1.7, 7.6, 9 / 5.4)
txt(s, 8.45, 1.75, 4.4, 0.4, [("WHAT TO READ", 13, ACCENT, True, "Consolas")])
bullets(s, 8.45, 2.2, 4.4, 4.4, [
    "#1 Karapinar Meke 0.528 [0.41-0.57] - carried by surface-brightness similarity; it ranks #11 on mobility.",
    "The score is a ranking index, not a guarantee - the app and the report state this openly.",
    "#2 McMurdo's very wide interval [0.09-0.51] shows how measurement uncertainty splits sites.",
    "Max score is 0.53: no Earth site imitates the Moon in every axis. The index depends on the 40-site pool.",
], size=13, gap=9)
pageno(s, 3)

# ============================== SLIDE 4 · MISSION PROFILES ==========================
s = slide()
kicker(s, "MISSION PROFILES")
title(s, "Which subsystem to test where - rankings change with the task")
hairline(s)
img(s, FIG / "figC_mission_profiles_en.png", 0.5, 1.7, 7.6, 9 / 5.4)
txt(s, 8.45, 1.75, 4.4, 0.4, [("TASK-BASED SELECTION", 13, ACCENT, True, "Consolas")])
bullets(s, 8.45, 2.2, 4.4, 4.4, [
    "Climbing and wheel-grip tests: Hasandagi Keçikalecik #1 (0.446) - slope 15.6°, mobility #1 under the steep reference.",
    "Optical camera / solar panel tests: Karapinar Meke #1 (0.653) - albedo 0.141 vs lunar 0.147.",
    "Same data, same sites - only the axis weights change (67/33 vs 33/67). Hasandagi walks #3 -> #1 -> #6.",
    "So the deliverable is not one site: it is a per-subsystem test-bed inventory.",
], size=13, gap=9)
pageno(s, 4)

# ============================== SLIDE 5 · REFERENCE GEOMETRY ========================
s = slide()
kicker(s, "STRONGEST EVIDENCE")
title(s, "The method is sensitive to reference geometry - by design")
hairline(s)
img(s, FIG / "figD_faustini_flip_en.png", 0.7, 1.85, 8.6, 9 / 4.9)
txt(s, 9.6, 1.85, 3.3, 0.4, [("FAUSTINI FLIP", 13, ACCENT, True, "Consolas")])
bullets(s, 9.6, 2.3, 3.3, 4.2, [
    "Known analogues sit #22-#28 in mobility under the steep rim.",
    "Switch to the flat Faustini rim (5.2°): Svalbard #3, Mauna Loa #5, Haughton #6, Atacama #8.",
    "We therefore do not claim 'we recover known analogues' - we report the geometry sensitivity, and we frame known analogues as a descriptive rank diagnostic.",
], size=12.5, gap=8)
pageno(s, 5)

# ============================== SLIDE 6 · BIG PICTURE + ROBUSTNESS ==================
s = slide()
kicker(s, "PHYSICAL SPACE AND ROBUSTNESS")
title(s, "40 sites in one physical space - and stable under the scaling factor")
hairline(s)
img(s, FIG / "figE_physical_space_en.png", 0.5, 1.75, 6.15, 9 / 5.6)
img(s, FIG / "figF_albedo_sensitivity_en.png", 7.0, 1.75, 6.15, 9 / 5.4)
txt(s, 0.5, 5.95, 6.15, 1.1, [(
    "Moon reference regions (blue diamonds) cluster at dark albedo; most candidates are brighter and gentler. "
    "Etna matches Shackleton in slope but not in brightness - exactly why the axes stay separate.",
    11.5, INK2, False, "Segoe UI")])
txt(s, 7.0, 5.95, 6.15, 1.1, [(
    "LOLA 1064 nm is scaled to broadband by x0.38. Within +/-10% of that factor the ranking survives "
    "(Spearman rho >= 0.87 in all 5 Moon regions); the #1 site changes at the extremes - we report it.",
    11.5, INK2, False, "Segoe UI")])
pageno(s, 6)

# ============================== SLIDE 7 · TEAM + LIMITS =============================
s = slide()
kicker(s, "TEAM AND LIMITS")
title(s, "Four people, four open data streams - and the limits we state out loud")
hairline(s)
txt(s, 0.5, 1.62, 6.0, 0.4, [("TEAM ENDÜLÜS", 13, ACCENT, True, "Consolas")])
members = [
    ("Serdar Otlutepe", "Lead / Approver - methodology, scoring, integration"),
    ("Berathan Menek", "Web design and testing - interactive map app"),
    ("Eray Seylan", "Earth satellite data - GLO-30, MODIS, Sentinel-2"),
    ("Emirjan Aksoy", "Moon data - LOLA DEM, reflectivity, Diviner"),
]
y = 2.08
for name, role in members:
    txt(s, 0.5, y, 6.0, 0.55, [
        (name, 14.5, INK, True, "Segoe UI"),
        (role, 11.5, INK2, False, "Segoe UI"),
    ], space_after=0)
    y += 0.78
txt(s, 0.5, 5.35, 6.0, 1.6, [
    ("WHERE THE ANALOGY BREAKS DOWN", 11.5, ACCENT, True, "Consolas"),
    ("Earth cannot reproduce 1/6 gravity, vacuum, radiation or the 29.5-day lunar day - those tests belong to a lab or a simulation.", 12, INK2, False, "Segoe UI"),
    ("40 curated sites is a pre-screen; a global grid scan is our v2 roadmap.", 12, INK2, False, "Segoe UI"),
], space_after=4)
txt(s, 7.0, 1.62, 5.85, 0.4, [("ONE-PARAGRAPH SUMMARY", 13, ACCENT, True, "Consolas")])
txt(s, 7.0, 2.08, 5.85, 3.2, [(
    "A decision-support system that scores 40 Earth sites - 14 of them Turkish candidates - against 5 Moon "
    "south-pole reference regions on slope, roughness, relief and albedo, in two axes with Monte Carlo error "
    "bands, and re-ranks by mission profile and reference geometry. The goal is not one perfect analogue: it is "
    "knowing which subsystem to test in which national site, and which answers only a lab can give.",
    14, INK, False, "Segoe UI")])
bar = s.shapes.add_shape(1, Inches(7.0), Inches(5.45), Inches(2.4), Emu(28575))
bar.fill.solid(); bar.fill.fore_color.rgb = ACCENT; bar.line.fill.background()
txt(s, 7.0, 5.7, 5.85, 1.2, [
    ("github.com/tilikumotp/endulus (public repository)", 12.5, ACCENT, False, "Consolas"),
    ("Interactive app, method report and verified data tables live in the repo.", 11.5, INK2, False, "Segoe UI"),
], space_after=3)
pageno(s, 7)

prs.save(str(OUT))
print("SAVED:", OUT, "slides:", len(prs.slides.__iter__.__self__._sldIdLst))
