"""Curated and literature-verified Earth validation and candidate sites (AGENTS.md §5, §6 & §7)."""

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
    # =========================================================================
    # 1. VALIDATION SITES (role="validation", 10 well-known planetary analogs)
    # =========================================================================
    {
        "site_id": "earth_etna_cisternazza",
        "name": "Mount Etna (Cisternazza / Piano del Lago)",
        "role": "validation",
        "lat": 37.7257,
        "lon": 15.0084,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Wedler et al. (2017) ROBEX & Schuster et al. (2020) ARCHES lunar analog "
            "rover campaigns, Cisternazza crater rim, Mt. Etna (OSM verified, ~2565 m, 37°43'33\"N, 15°00'30\"E)."
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
        "site_id": "earth_mauna_loa_hiseas",
        "name": "Mauna Loa North Flank (HI-SEAS Basalt Field, Hawaii)",
        "role": "validation",
        "lat": 19.6028,
        "lon": -155.4878,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Binsted et al. (2016) HI-SEAS lunar/Mars analog habitat & Bleacher et al. "
            "(2017, JVGR 342:1-10), Mauna Loa northern flank tholeiitic basalt (~2500 m, 19°36'10\"N, 155°29'16\"W)."
        ),
    },
    {
        "site_id": "earth_mcmurdo_wright_valley",
        "name": "McMurdo Dry Valleys (Wright Valley, Antarctica)",
        "role": "validation",
        "lat": -77.5180,
        "lon": 161.8500,
        "radius_m": 1000.0,
        "lithology_class": "regolith_permafrost",
        "citation": (
            "Marchant & Head (2007, Icarus 192:187-222) & Levy et al. (2009), "
            "Wright Valley cold hyperarid polar desert Mars/lunar ice analog (77°31'S, 161°51'E)."
        ),
    },
    {
        "site_id": "earth_lanzarote_timanfaya",
        "name": "Lanzarote Tinguatón / Timanfaya (ESA PANGAEA, Canary Islands)",
        "role": "validation",
        "lat": 29.0150,
        "lon": -13.7150,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Sauro et al. (2020, Earth-Science Reviews 208:103288) & Bessone et al. (2018), "
            "ESA PANGAEA astronaut geological training campaign, Lanzarote basaltic fissure field (29°00'54\"N, 13°42'54\"W)."
        ),
    },
    {
        "site_id": "earth_meteor_crater_arizona",
        "name": "Meteor Crater / Barringer Impact Crater (Arizona)",
        "role": "validation",
        "lat": 35.0272,
        "lon": -111.0225,
        "radius_m": 1000.0,
        "lithology_class": "impact_breccia",
        "citation": (
            "Kring (2007, LPI Contribution 1355) & Shoemaker (1963), Barringer Meteor Crater "
            "Apollo & Artemis astronaut training site (35°01'38\"N, 111°01'21\"W)."
        ),
    },
    {
        "site_id": "earth_craters_of_the_moon",
        "name": "Craters of the Moon Lava Field (Idaho)",
        "role": "validation",
        "lat": 43.4617,
        "lon": -113.5625,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Hughes et al. (2019, JVGR) & NASA FINESSE / BASALT planetary analog field campaigns, "
            "Craters of the Moon National Monument basalt flows (43°27'42\"N, 113°33'45\"W)."
        ),
    },
    {
        "site_id": "earth_svalbard_bockfjorden",
        "name": "Svalbard Bockfjorden (Sverrefjellet AMASE, Norway)",
        "role": "validation",
        "lat": 79.4280,
        "lon": 13.3850,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Steele et al. (2011, Astrobiology 11) & Amundsen et al. (2012), Arctic Mars Analog "
            "Svalbard Expedition (AMASE), Sverrefjellet Quaternary basalt volcano, Bockfjorden (79°25'41\"N, 13°23'06\"E)."
        ),
    },
    {
        "site_id": "earth_lunar_crater_nevada",
        "name": "Lunar Crater Volcanic Field (Black Rock Flow, Nevada)",
        "role": "validation",
        "lat": 38.3840,
        "lon": -116.0680,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Scott & Trask (1971, USGS Prof. Paper 599-I) & Valentine et al. (2017, Geosphere 13:391-438), "
            "Lunar Crater Volcanic Field maar and basaltic cone complex, Nevada (38°23'02\"N, 116°04'05\"W)."
        ),
    },
    # =========================================================================
    # 2. CANDIDATE SITES (role="candidate", 30 curated Turkish & global sites)
    # =========================================================================
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
            "Ekici et al. (2014), Karacadağ shield volcano summit plateau (37°40'12\"N, 39°49'48\"E)."
        ),
    },
    {
        "site_id": "earth_karacadag_ovabag",
        "name": "Karacadağ NE Flank (Ovabağ Low-Slope Basalt Flow, Diyarbakır)",
        "role": "candidate",
        "lat": 37.7850,
        "lon": 40.0250,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Ekici et al. (2014, Geodinamica Acta 26:3-4) & Lustrino et al. (2012), "
            "Quaternary Ovabağ plateau alkali-olivine basalt flows on NE Karacadağ shield (37°47'06\"N, 40°01'30\"E)."
        ),
    },
    {
        "site_id": "earth_kula_divlit",
        "name": "Kula Volcanic Geopark (Divlit Scoria Cone & ʻAʻā Basalt, Manisa)",
        "role": "candidate",
        "lat": 38.5660,
        "lon": 28.6360,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Ersoy et al. (2010, JVGR 190:291-306) & Aldanmaz et al. (2015), "
            "Kula Quaternary intraplate alkali basaltic cinder cones and blocky lava flows (38°33'58\"N, 28°38'10\"E)."
        ),
    },
    {
        "site_id": "earth_tendurek_shield",
        "name": "Tendürek Shield Volcano (Çaldıran Basalt Lava Apron, Ağrı-Van)",
        "role": "candidate",
        "lat": 39.3200,
        "lon": 43.9200,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Lebedev et al. (2016, Petrology 24:127-163) & Yılmaz et al. (1998, JVGR 85:173-210), "
            "Tendürek low-angle shield volcano Holocene basaltic-trachyandesitic lava flows (39°19'12\"N, 43°55'12\"E)."
        ),
    },
    {
        "site_id": "earth_erciyes_kojugedigi",
        "name": "Mount Erciyes (Koçdağ SE Flank Basalt-Andesite Plateau, Kayseri)",
        "role": "candidate",
        "lat": 38.5050,
        "lon": 35.5350,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Şen et al. (2003, JVGR 125:225-246) & Friedrichs et al. (2020), "
            "Erciyes stratovolcano southeastern flank monogenetic vents and lava domes (38°30'18\"N, 35°32'06\"E)."
        ),
    },
    {
        "site_id": "earth_hasandagi_kecekalecik",
        "name": "Mount Hasan / Hasandağı (NW Flank Basalt-Andesite Apron, Aksaray)",
        "role": "candidate",
        "lat": 38.1750,
        "lon": 34.1200,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Deniel et al. (1998, JVGR 87:275-302) & Aydar & Gourgaud (1998), "
            "Hasandağı Quaternary pyroclastic and basaltic-andesitic fan deposits (38°10'30\"N, 34°07'12\"E)."
        ),
    },
    {
        "site_id": "earth_acigol_guneydag",
        "name": "Acıgöl-Nevşehir Caldera (Güneydağ Maar & Tephra Ring, Nevşehir)",
        "role": "candidate",
        "lat": 38.5250,
        "lon": 34.5550,
        "radius_m": 1000.0,
        "lithology_class": "pyroclastic_tuff",
        "citation": (
            "Druitt et al. (1995, J. Geol. Soc. London 152:655-667) & Schmitt et al. (2011), "
            "Acıgöl-Nevşehir Pleistocene caldera maar craters and tephra ring plains (38°31'30\"N, 34°33'18\"E)."
        ),
    },
    {
        "site_id": "earth_cappadocia_kavakkoy",
        "name": "Cappadocia Ignimbrite Plateau (Kavak / Göreme Tuff Tableland, Nevşehir)",
        "role": "candidate",
        "lat": 38.6500,
        "lon": 34.8600,
        "radius_m": 1000.0,
        "lithology_class": "pyroclastic_tuff",
        "citation": (
            "Le Pennec et al. (1994, JVGR 63:59-87) & Aydar et al. (2012, Bull. Volcanol. 74:739-762), "
            "Neogene Cappadocian Ignimbrite Province welded tuff plateau (38°39'00\"N, 34°51'36\"E)."
        ),
    },
    {
        "site_id": "earth_tuz_golu_south",
        "name": "Tuz Gölü Basin (Southern Evaporite Marginal Flat, Aksaray)",
        "role": "candidate",
        "lat": 38.5500,
        "lon": 33.6200,
        "radius_m": 1000.0,
        "lithology_class": "evaporite",
        "citation": (
            "Çiner et al. (2021) & Kashima (2002, Catena 48:3-20), Tuz Gölü closed-basin "
            "subaerial halite/gypsum evaporite salt flat margin, Central Anatolia (38°33'00\"N, 33°37'12\"E)."
        ),
    },
    {
        "site_id": "earth_salda_terrace",
        "name": "Lake Salda Onshore Terrace (Hydromagnesite/Ultramafic Shore, Burdur)",
        "role": "candidate",
        "lat": 37.5150,
        "lon": 29.6350,
        "radius_m": 1000.0,
        "lithology_class": "evaporite",
        "citation": (
            "Horgan et al. (2020, Icarus 339:113526) & Russell et al. (1999, J. Geol. Soc. 156:869-888) — "
            "ALREADY ESTABLISHED IN LITERATURE as NASA Perseverance Jezero Crater carbonate/hydromagnesite Mars analog "
            "(not a newly proposed site; southwestern onshore ultramafic/hydromagnesite terrace, 37°30'54\"N, 29°38'06\"E)."
        ),
    },
    {
        "site_id": "earth_askja_holuhraun",
        "name": "Askja / Holuhraun Basalt Sand & Lava Plain (Dyngjusandur, Iceland)",
        "role": "candidate",
        "lat": 64.8800,
        "lon": -16.8200,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Pedersen et al. (2017, JVGR 340:155-170) & Greeley et al. (2000), "
            "Holuhraun / Dyngjusandur high-latitude glaciovolcanic basaltic lava and aeolian sand plain (64°52'48\"N, 16°49'12\"W)."
        ),
    },
    {
        "site_id": "earth_harrat_rahat_madinah",
        "name": "Harrat Rahat Volcanic Field (Northern Basalt Plateau, Saudi Arabia)",
        "role": "candidate",
        "lat": 24.3300,
        "lon": 39.7700,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Camp & Roobol (1989, GSA Bulletin 101:71-95) & Downs et al. (2018), "
            "Northern Harrat Rahat continental intraplate alkali basalt field (24°19'48\"N, 39°46'12\"E)."
        ),
    },
    {
        "site_id": "earth_pinacate_el_elegante",
        "name": "Sierra del Pinacate Volcanic Field (El Elegante Maar Rim, Sonora, Mexico)",
        "role": "candidate",
        "lat": 31.8403,
        "lon": -113.3951,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Gutmann (2002, GSA Special Paper 365) & Greeley et al. (1985), "
            "Pinacate arid basaltic maar crater south rim (Crater El Elegante, OSM verified, 31°50'25\"N, 113°23'42\"W)."
        ),
    },
    {
        "site_id": "earth_puna_campo_piedra_pomez",
        "name": "Puna de Atacama (Campo de Piedra Pómez Ignimbrite & Basalt, Argentina)",
        "role": "candidate",
        "lat": -26.5700,
        "lon": -67.4400,
        "radius_m": 1000.0,
        "lithology_class": "pyroclastic_tuff",
        "citation": (
            "de Silva et al. (2010, Geology 38:219-222) & Bridges et al. (2015, JGR Planets), "
            "Puna de Atacama hyperarid high-altitude (~3300 m) yardang ignimbrite and basalt field (26°34'12\"S, 67°26'24\"W)."
        ),
    },
    {
        "site_id": "earth_deccan_mahabaleshwar",
        "name": "Deccan Traps Flood Basalt Plateau (Panchgani Tableland, India)",
        "role": "candidate",
        "lat": 17.9240,
        "lon": 73.8050,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Self et al. (2006, EPSL 248:518-532) & Jay & Widdowson (2008), "
            "Deccan Traps Wai Subgroup tholeiitic flood basalt tableland (17°55'26\"N, 73°48'18\"E)."
        ),
    },
    {
        "site_id": "earth_harrat_ash_shaam",
        "name": "Harrat Ash Shaam Basalt Desert (Badia Black Basalt Plateau, Jordan)",
        "role": "candidate",
        "lat": 32.2200,
        "lon": 37.1500,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Ibrahim et al. (2006) & Shaw et al. (2003, J. Petrology 44:1657-1679), "
            "Harrat Ash Shaam arid intraplate basaltic boulder field (32°13'12\"N, 37°09'00\"E)."
        ),
    },
    {
        "site_id": "earth_kilbourne_hole_nm",
        "name": "Potrillo Volcanic Field (Kilbourne Hole Maar & Basalt Rim, New Mexico)",
        "role": "candidate",
        "lat": 31.9680,
        "lon": -106.9720,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Seeger et al. (2019) & Padovani & Carter (1977), Kilbourne Hole phreatomagmatic "
            "maar and Aden basalt field, Rio Grande Rift (31°58'05\"N, 106°58'19\"W)."
        ),
    },
    {
        "site_id": "earth_qaidam_dalangtan",
        "name": "Qaidam Basin (Dalangtan Hyperarid Evaporite Flat, China)",
        "role": "candidate",
        "lat": 38.4800,
        "lon": 91.4500,
        "radius_m": 1000.0,
        "lithology_class": "evaporite",
        "citation": (
            "Xiao et al. (2017, ESR 164:84-101) & Anglés & Li (2017, JGR Planets), "
            "Dalangtan high-altitude (~2700 m) hyperarid sulfate/halite evaporite flats, Qaidam Basin (38°28'48\"N, 91°27'00\"E)."
        ),
    },
    # Extended 12 verified candidates (Turkey + global) completing the 30-candidate pool (40 sites total)
    {
        "site_id": "earth_karapinar_meke",
        "name": "Karapınar Volcanic Field (Meke Maar & Scoria Apron, Konya)",
        "role": "candidate",
        "lat": 37.6750,
        "lon": 33.6650,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Keller (1974, Bull. Volcanol. 38:378-396) & Reid et al. (2017, JVGR 338:1-13), "
            "Karapınar Quaternary basaltic maar and scoria cone field, Konya Basin (37°40'30\"N, 33°39'54\"E)."
        ),
    },
    {
        "site_id": "earth_suphan_south_apron",
        "name": "Mount Süphan (Lower Adilcevaz Basalt-Andesite Lava Apron, Bitlis)",
        "role": "candidate",
        "lat": 38.8650,
        "lon": 42.8300,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Özdemir, Blundy & Güleç (2011, Contrib. Mineral. Petrol. 162:573-597), "
            "Özdemir & Güleç (2014, J. Petrol. 55:37-62) & Yılmaz et al. (1998, JVGR 85:173-210), "
            "Mount Süphan southern basaltic-trachyandesitic lower apron ~6.9 km S of summit (~2233 m, 38°51'54\"N, 42°49'48\"E)."
        ),
    },
    {
        "site_id": "earth_nemrut_caldera_flank",
        "name": "Nemrut Volcano (Tatvan Eastern Ignimbrite & Lava Flank, Bitlis)",
        "role": "candidate",
        "lat": 38.6100,
        "lon": 42.3100,
        "radius_m": 1000.0,
        "lithology_class": "pyroclastic_tuff",
        "citation": (
            "Çubukçu et al. (2012, JVGR 209-210:33-60) & Ulusoy et al. (2008), "
            "Nemrut Quaternary caldera eastern pyroclastic and pre-caldera lava apron (38°36'36\"N, 42°18'36\"E)."
        ),
    },
    {
        "site_id": "earth_agri_dogubayazit_flow",
        "name": "Mount Ararat / Ağrı Dağı (Western Basalt Lava Flank, Doğubayazıt)",
        "role": "candidate",
        "lat": 39.6800,
        "lon": 44.1400,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Yılmaz et al. (1998, JVGR 85:173-210) & Pearce et al. (1990, JVGR 44:189-229), "
            "Mount Ararat (Ağrı) lower western flank Quaternary basaltic lava flow above Doğubayazıt (~1764 m, 39°40'48\"N, 44°08'24\"E)."
        ),
    },
    {
        "site_id": "earth_payunia_pampa_negra",
        "name": "Payunia Volcanic Province (Pampa Negra Basalt & Lapilli Plain, Argentina)",
        "role": "candidate",
        "lat": -36.1800,
        "lon": -69.1800,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Søager et al. (2013, Chem. Geol. 349-350:36-53) & Hernando et al. (2014, JVGR 272:1-19), "
            "Payunia back-arc basaltic cinder cone and dark lapilli sheet, Mendoza (36°10'48\"S, 69°10'48\"W)."
        ),
    },
    {
        "site_id": "earth_chajnantor_plateau",
        "name": "Altiplano-Puna Complex (Chajnantor High-Altitude Ignimbrite Plateau, Chile)",
        "role": "candidate",
        "lat": -23.0230,
        "lon": -67.7540,
        "radius_m": 1000.0,
        "lithology_class": "pyroclastic_tuff",
        "citation": (
            "Salisbury et al. (2011, GSA Bull. 123:821-840) & de Silva (1989, Geology 17:1102-1106), "
            "Chajnantor hyperarid high-altitude (~5050 m) dacitic-rhyodacitic ignimbrite tableland (23°01'23\"S, 67°45'14\"W)."
        ),
    },
    {
        "site_id": "earth_waw_an_namus_apron",
        "name": "Waw an Namus Volcano (Dark Basaltic Tephra Apron, Fezzan, Libya)",
        "role": "candidate",
        "lat": 24.9500,
        "lon": 17.7600,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Bardintzeff et al. (2012, Chemie der Erde 72:135-145) & Busrewil & Wadsworth (1983), "
            "Waw an Namus Saharan intraplate maar dark basaltic tephra apron (24°57'00\"N, 17°45'36\"E)."
        ),
    },
    {
        "site_id": "earth_tibesti_tarso_voon",
        "name": "Tibesti Volcanic Massif (Tarso Voon Ignimbrite & Basalt Plateau, Chad)",
        "role": "candidate",
        "lat": 20.9200,
        "lon": 17.2800,
        "radius_m": 1000.0,
        "lithology_class": "pyroclastic_tuff",
        "citation": (
            "Permenter & Oppenheimer (2007, Bull. Volcanol. 69:609-626) & Gourgaud & Vincent (2004, JVGR 129:261-294), "
            "Tibesti intracontinental volcanic plateau, northern Chad (20°55'12\"N, 17°16'48\"E)."
        ),
    },
    {
        "site_id": "earth_paricutin_lava_field",
        "name": "Michoacán-Guanajuato Field (Parícutin Basaltic-Andesite Flow, Mexico)",
        "role": "candidate",
        "lat": 19.4930,
        "lon": -102.2510,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Luhr & Simkin (1993) & Erlund et al. (2010, Bull. Volcanol. 72:347-363), "
            "Parícutin 1943-1952 basaltic-andesite lava field, Michoacán (19°29'35\"N, 102°15'04\"W)."
        ),
    },
    {
        "site_id": "earth_tolbachik_apron",
        "name": "Tolbachik Volcanic Massif (Basalt Scoria & Lava Plain, Kamchatka)",
        "role": "candidate",
        "lat": 55.7550,
        "lon": 160.2950,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Belousov et al. (2015, JVGR 307:22-37) & Fedotov et al. (1991), "
            "Tolbachik fissure eruption basaltic scoria cones and lava apron, Kamchatka (55°45'18\"N, 160°17'42\"E)."
        ),
    },
    {
        "site_id": "earth_kilauea_kau_desert",
        "name": "Kīlauea SW Rift Zone (Kaʻū Desert Basalt & Tephra Plain, Hawaii)",
        "role": "candidate",
        "lat": 19.3650,
        "lon": -155.3350,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Craddock et al. (2012, JGR Planets 117:E08009) & Schiffman et al. (2006, Geology 34:921-924), "
            "Kaʻū Desert acid-sulfate altered tholeiitic basalt and ash plain, Kīlauea (19°21'54\"N, 155°20'06\"W)."
        ),
    },
    {
        "site_id": "earth_tongariro_rangipo",
        "name": "Tongariro Volcanic Centre (Rangipo Andesitic-Basaltic Tephra Plain, NZ)",
        "role": "candidate",
        "lat": -39.2850,
        "lon": 175.7200,
        "radius_m": 1000.0,
        "lithology_class": "basalt",
        "citation": (
            "Donoghue et al. (1995, Bull. Volcanol. 57:563-576) & Hobden et al. (1999, J. Petrology 40:1965-1990), "
            "Rangipo high-altitude volcaniclastic andesitic-basaltic ring plain, Ruapehu-Tongariro (39°17'06\"S, 175°43'12\"E)."
        ),
    },
]
