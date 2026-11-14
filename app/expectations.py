"""Verified E1 expectation matrix & E8 ice/permafrost metadata for the UI.

All entries are sourced verbatim from ``docs/validation_expectations.md``
(pre-registered prior to inspection of ranking outputs). Under Karar #30,
v1 numeric scoring uses Mobility and Surface only while Thermal is suspended.
"""
from __future__ import annotations

VALIDATION_EXPECTATIONS: dict[str, dict[str, str]] = {
    "earth_etna_cisternazza": {
        "expected_v1": "mobility",
        "ice_e8": "kısmi",
        "ice_e8_en": "partial",
        "rationale_tr": (
            "ARCHES/ROBEX kampanyaları Cisternazza yamacını doğrudan Ay rover "
            "otonom mobilite sahası olarak doğrulamıştır."
        ),
        "rationale_en": (
            "ARCHES and ROBEX field campaigns directly validate Mt. Etna as a "
            "lunar autonomous rover mobility testbed."
        ),
        "source_label": "Schuster et al. (2020), IEEE RA-L",
        "source_url": "https://doi.org/10.1109/LRA.2020.3007468",
    },
    "earth_atacama_yungay": {
        "expected_v1": "mobility",
        "ice_e8": "yok",
        "ice_e8_en": "none",
        "rationale_tr": (
            "Zoë otonom sürüş testleri düz hiperkurak zemin mobilitesini doğrular; "
            "dik krater duvarı eğimlerini temsil etmez."
        ),
        "rationale_en": (
            "Zoë rover autonomous traverse validates flat hyperarid mobility "
            "but does not represent steep crater-wall slopes."
        ),
        "source_label": "Wettergreen et al. (2005), IEEE ICRA",
        "source_url": "https://doi.org/10.1109/ROBOT.2005.1570227",
    },
    "earth_haughton_crater": {
        "expected_v1": "mobility",
        "ice_e8": "var",
        "ice_e8_en": "present",
        "rationale_tr": (
            "Haughton-Mars Projesi çarpma krateri içinde doğrudan rover, "
            "sondaj ve EVA mobilite operasyonlarını yürütmüştür."
        ),
        "rationale_en": (
            "The Haughton-Mars Project conducts rover, drilling and EVA "
            "mobility tests directly inside an Arctic impact crater."
        ),
        "source_label": "Lee & Osinski (2005), MAPS",
        "source_url": "https://doi.org/10.1111/j.1945-5100.2005.tb00144.x",
    },
    "earth_mauna_loa_hiseas": {
        "expected_v1": "mobility",
        "ice_e8": "veri yok",
        "ice_e8_en": "no data",
        "rationale_tr": (
            "HI-SEAS görevleri toleyitik bazalt lav akıntıları üzerinde "
            "doğrudan jeolojik yürüyüş ve saha operasyonlarını doğrular."
        ),
        "rationale_en": (
            "HI-SEAS missions validate astronaut EVA and geological field "
            "operations on tholeiitic basalt lava flows."
        ),
        "source_label": "Shiro et al. (2022), Planet. Space Sci.",
        "source_url": "https://doi.org/10.1016/j.pss.2021.105409",
    },
    "earth_mcmurdo_wright_valley": {
        "expected_v1": "thermal_only",
        "ice_e8": "var",
        "ice_e8_en": "present",
        "rationale_tr": (
            "Birincil literatürde soğuk-çöl permafrost/termal rejim analoğudur "
            "(termal v1'de askıda); v1 aktif eksenlerde kesin beklenti yoktur."
        ),
        "rationale_en": (
            "Primary analogue for cold-desert permafrost/thermal regimes "
            "(suspended in v1); no confirmed mobility/surface claim."
        ),
        "source_label": "Marchant & Head (2007), Icarus",
        "source_url": "https://doi.org/10.1016/j.icarus.2007.06.018",
    },
    "earth_lanzarote_timanfaya": {
        "expected_v1": "mobility",
        "ice_e8": "veri yok",
        "ice_e8_en": "no data",
        "rationale_tr": (
            "ESA PANGAEA astronot eğitimi taze bazaltik lav/skorya arazisini "
            "saha mobilite ve operasyon analoğu olarak kullanır."
        ),
        "rationale_en": (
            "ESA PANGAEA astronaut training uses fresh basaltic lava fields "
            "as a planetary surface mobility and operations analogue."
        ),
        "source_label": "Sauro et al. (2023), Acta Astronautica",
        "source_url": "https://doi.org/10.1016/j.actaastro.2022.12.034",
    },
    "earth_meteor_crater_arizona": {
        "expected_v1": "mobility",
        "ice_e8": "veri yok",
        "ice_e8_en": "no data",
        "rationale_tr": (
            "Kring rehberi ve Shoemaker (1959) basit krater duvar eğimi ve "
            "Apollo eğitimi için Meteor Crater'ı standart referans kurar."
        ),
        "rationale_en": (
            "Kring guidebook and Shoemaker (1959) establish simple crater wall "
            "slopes and Apollo field training at Meteor Crater."
        ),
        "source_label": "Shoemaker (1959) / Kring (2017), LPI",
        "source_url": "https://doi.org/10.3133/ofr59108",
    },
    "earth_craters_of_the_moon": {
        "expected_v1": "mobility",
        "ice_e8": "veri yok",
        "ice_e8_en": "no data",
        "rationale_tr": (
            "NASA BASALT ve FINESSE programları lav akıntısı pürüzlülüğü "
            "üzerinde insan/robotik yürüyüş operasyonlarını doğrulamıştır."
        ),
        "rationale_en": (
            "NASA BASALT and FINESSE select Craters of the Moon lava flows "
            "for human and robotic planetary field mobility."
        ),
        "source_label": "Hughes et al. (2019), Astrobiology",
        "source_url": "https://doi.org/10.1089/ast.2018.1847",
    },
    "earth_svalbard_bockfjorden": {
        "expected_v1": "none",
        "ice_e8": "var",
        "ice_e8_en": "present",
        "rationale_tr": (
            "Arktik permafrost belgelenmiştir; ancak rover mobilite veya "
            "broadband albedo kalibrasyonu için birincil yayın doğrulanamadı."
        ),
        "rationale_en": (
            "Arctic permafrost is documented, but no primary rover mobility "
            "or broadband albedo calibration study is verified."
        ),
        "source_label": "Humlum et al. (2003), Polar Research",
        "source_url": "https://doi.org/10.3402/polar.v22i2.6455",
    },
    "earth_lunar_crater_nevada": {
        "expected_v1": "mobility",
        "ice_e8": "veri yok",
        "ice_e8_en": "no data",
        "rationale_tr": (
            "AIRSAR radar deneylerinde yüzey pürüzlülüğü (roughness) "
            "kestirimi için birincil yer-gerçeği kalibrasyon sahasıdır."
        ),
        "rationale_en": (
            "Primary ground-truth site for AIRSAR surface roughness estimation "
            "across maar craters and volcanic basalt flows."
        ),
        "source_label": "Evans et al. (1992), IEEE TGARS",
        "source_url": "https://doi.org/10.1109/36.134087",
    },
}
