"""Deterministic astrological calculation engine (Phase 1).

This package computes — it never interprets. Sidereal longitudes, nakshatras,
house cusps and KP sub-lords are produced here from first principles via Swiss
Ephemeris. The future LLM interpretation layer will consume :class:`Chart`
objects strictly read-only and must never invent or recompute a position.
"""

from .birth_data import BirthData, TimezoneError
from .chart import (
    Chart,
    HouseCusp,
    PlanetPosition,
    compute_chart,
    compute_kp_chart,
    compute_vedic_chart,
)
from .constants import (
    AYANAMSA_KP,
    AYANAMSA_LAHIRI,
    HOUSE_PLACIDUS,
    HOUSE_WHOLE_SIGN,
    PRESET_KP,
    PRESET_VEDIC,
)
from .kp_sublord import KPLords, build_kp_249_table, resolve as kp_resolve
from .nakshatra import NakshatraInfo, nakshatra_of
from .dasha import (
    DashaPeriod,
    balance_at_birth,
    chart_vimshottari,
    dasha_at,
    vimshottari_dasha,
)
from .varga import (
    VARGAS,
    Varga,
    VargaChart,
    divisional_chart,
    varga_sign,
    varga_sign_index,
)
from .aspects import PlanetAspect, aspects_between, graha_drishti
from .dignity import DignityInfo, chart_dignities, planet_dignity
from .houses import HouseChart, house_of
from .bhava import BHAVA, Bhava, karakas, significations
from .functional import (
    FunctionalNature,
    classify_chart,
    functional_nature,
    yogakarakas_for,
)
from .yogas import Yoga, detect_yogas
from .ashtakavarga import bhinnashtakavarga, sarvashtakavarga, by_house
from .kp import KPAnalysis, Significator, kp_house_of
from .kp_ruling import RulingPlanets, ruling_planets
from .kp_events import (
    EVENTS,
    EventJudgment,
    EventRule,
    SensitivityReport,
    birth_time_sensitivity,
    event_dasha_periods,
    judge_event,
)

__all__ = [
    "BirthData",
    "TimezoneError",
    "Chart",
    "HouseCusp",
    "PlanetPosition",
    "compute_chart",
    "compute_vedic_chart",
    "compute_kp_chart",
    "AYANAMSA_LAHIRI",
    "AYANAMSA_KP",
    "HOUSE_WHOLE_SIGN",
    "HOUSE_PLACIDUS",
    "PRESET_VEDIC",
    "PRESET_KP",
    "KPLords",
    "kp_resolve",
    "build_kp_249_table",
    "NakshatraInfo",
    "nakshatra_of",
    # Phase 2 — dasha
    "DashaPeriod",
    "vimshottari_dasha",
    "chart_vimshottari",
    "dasha_at",
    "balance_at_birth",
    # Phase 2 — vargas
    "Varga",
    "VargaChart",
    "VARGAS",
    "divisional_chart",
    "varga_sign",
    "varga_sign_index",
    # Phase 2 — aspects
    "PlanetAspect",
    "graha_drishti",
    "aspects_between",
    # Phase 2 — dignity
    "DignityInfo",
    "planet_dignity",
    "chart_dignities",
    # Phase 3 — houses & significations
    "HouseChart",
    "house_of",
    "BHAVA",
    "Bhava",
    "karakas",
    "significations",
    # Phase 3 — functional nature
    "FunctionalNature",
    "functional_nature",
    "classify_chart",
    "yogakarakas_for",
    # Phase 3 — yogas
    "Yoga",
    "detect_yogas",
    # Phase 3 — ashtakavarga
    "bhinnashtakavarga",
    "sarvashtakavarga",
    "by_house",
    # Phase 4 — KP judgment
    "KPAnalysis",
    "Significator",
    "kp_house_of",
    "RulingPlanets",
    "ruling_planets",
    "EVENTS",
    "EventRule",
    "EventJudgment",
    "judge_event",
    "event_dasha_periods",
    "SensitivityReport",
    "birth_time_sensitivity",
]
