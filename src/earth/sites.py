"""Curated and literature-verified Earth validation and candidate sites (AGENTS.md §5 & §6)."""

from __future__ import annotations

from typing import TypedDict


class SiteSpec(TypedDict):
    """Specification of a verified Earth analog or candidate site."""

    site_id: str
    name: str
    role: str
    lat: float
    lon: float
    radius_m: float
    lithology_class: str
    citation: str


VERIFIED_EARTH_SITES: list[SiteSpec] = [
    {
        "site_id": "earth_etna_cisternazza",
        "name": "Mount Etna (Cisternazza / Piano del Lago)",
        "role": "validation",
        "lat": 37.7450,
        "lon": 15.0060,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Wedler et al. (2017) ROBEX & Schuster et al. (2020) ARCHES lunar analog "
            "rover campaigns, Cisternazza / Piano del Lago, Mt. Etna (~2600 m)."
        ),
    },
    {
        "site_id": "earth_atacama_yungay",
        "name": "Atacama Desert (Yungay Station)",
        "role": "validation",
        "lat": -24.1052,
        "lon": -70.0321,
        "radius_m": 1000.0,
        "lithology_class": "evaporite",
        "citation": (
            "Navarro-González et al. (2003, Science 302:1018-1021) & Warren-Rhodes "
            "et al. (2006), Yungay hyperarid core (24°06'18.6\"S, 70°01'55.6\"W)."
        ),
    },
    {
        "site_id": "earth_haughton_crater",
        "name": "Haughton Impact Crater (Devon Island)",
        "role": "validation",
        "lat": 75.3700,
        "lon": -89.6800,
        "radius_m": 1000.0,
        "lithology_class": "impact_breccia",
        "citation": (
            "Osinski et al. (2005, Meteoritics & Planetary Science 40:1759-1776) & "
            "Lee (Haughton-Mars Project), Devon Island (75°22'N, 89°41'W)."
        ),
    },
    {
        "site_id": "earth_karacadag_summit",
        "name": "Karacadağ Shield Volcano (Kollubaba / Lav Platosu)",
        "role": "candidate",
        "lat": 37.6700,
        "lon": 39.8300,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Lustrino et al. (2010, Lithos 117:135-151), Keskin et al. (2012) & "
            "Ekici et al. (2014), Karacadağ shield volcano (37°40'12\"N, 39°49'48\"E)."
        ),
    },
]
