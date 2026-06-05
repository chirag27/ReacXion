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
]
