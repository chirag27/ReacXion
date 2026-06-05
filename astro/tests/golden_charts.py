"""Golden charts for cross-validation against Jagannatha Hora.

Each entry pins a fully-specified birth event. The ``expected_*`` fields are
left as ``None`` (TODO) on purpose: fill them by casting the *same* birth data
in Jagannatha Hora (the free Vedic gold standard) for the planet longitudes and
cusps, and in a dedicated KP tool for the sub-lords, then transcribe the values
here. ``test_golden.py`` will skip any chart whose expectations are still
``None`` and, once filled, assert agreement to the arcminute.

How to fill, per chart:
  1. Vedic block  -> JHora with Lahiri ayanamsa + whole-sign houses.
  2. KP block     -> JHora (or a KP tool) with KP ayanamsa + Placidus houses.
  3. Sub-lords    -> a dedicated KP tool (e.g. KPStarOne / KPAstro) for the KP
                     planetary + cuspal sub-lords.

Longitudes are stored as decimal degrees in [0, 360). A handy converter:
    deg = d + m/60 + s/3600
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from engine.birth_data import BirthData


@dataclass
class ExpectedChart:
    """Expected values for one (ayanamsa, house-system) casting of a birth.

    All values are decimal-degree sidereal longitudes unless noted. Leave a
    field ``None`` to skip its assertion until you have the reference value.
    """

    # Map graha name -> expected sidereal longitude (deg). e.g.
    #   {"Sun": 256.1234, "Moon": 12.0050, ...}
    planet_longitudes: Optional[Dict[str, float]] = None

    # Map graha name -> expected (nakshatra, pada). e.g.
    #   {"Moon": ("Ashwini", 2)}
    planet_nakshatra_pada: Optional[Dict[str, tuple]] = None

    # Map graha name -> expected KP sub-lord. e.g. {"Sun": "Venus"}
    planet_sublords: Optional[Dict[str, str]] = None

    # Expected ascendant longitude (deg).
    ascendant: Optional[float] = None

    # House cusp longitudes, 1-indexed dict {1: deg, ..., 12: deg}.
    cusps: Optional[Dict[int, float]] = None

    # Expected KP cuspal sub-lords {1: "Mercury", ...}.
    cusp_sublords: Optional[Dict[int, str]] = None


@dataclass
class GoldenChart:
    label: str
    birth: BirthData
    notes: str = ""
    vedic: ExpectedChart = field(default_factory=ExpectedChart)   # Lahiri + whole-sign
    kp: ExpectedChart = field(default_factory=ExpectedChart)      # KP + Placidus

    # ---- Phase 2 expectations (computed on the Vedic / Lahiri chart) ----
    # Balance-of-dasha at birth as (lord, years), e.g. ("Venus", 12.345).
    # The years value is fraction-based and independent of the dasha year-length.
    dasha_balance: Optional[tuple] = None

    # Key divisional placements: {"D9": {"Sun": "Leo", ...}, "D10": {...}}.
    # Fill only the planets/vargas you want asserted.
    vargas: Optional[Dict[str, Dict[str, str]]] = None


# --------------------------------------------------------------------------- #
# Three golden charts chosen to exercise distinct timezone regimes.
# --------------------------------------------------------------------------- #
GOLDEN_CHARTS: List[GoldenChart] = [
    # 1) India, no DST, clean +5:30 offset — the simplest baseline.
    GoldenChart(
        label="delhi_1990_noon",
        birth=BirthData(
            year=1990, month=1, day=1,
            hour=12, minute=0, second=0,
            latitude=28.6139, longitude=77.2090,   # New Delhi
            timezone="Asia/Kolkata",
            name="Delhi 1990 noon",
        ),
        notes="No DST in India; fixed +5:30. Baseline sanity chart.",
        vedic=ExpectedChart(
            # TODO: fill from JHora (Lahiri + whole-sign)
            planet_longitudes=None,
            planet_nakshatra_pada=None,
            ascendant=None,
            cusps=None,
        ),
        kp=ExpectedChart(
            # TODO: fill from JHora/KP tool (KP ayanamsa + Placidus)
            planet_longitudes=None,
            planet_sublords=None,
            ascendant=None,
            cusps=None,
            cusp_sublords=None,
        ),
    ),

    # 2) New York during Eastern Daylight Time — exercises a DST offset.
    GoldenChart(
        label="nyc_1985_edt",
        birth=BirthData(
            year=1985, month=7, day=13,
            hour=21, minute=30, second=0,
            latitude=40.7128, longitude=-74.0060,   # New York City
            timezone="America/New_York",
            name="NYC 1985 EDT",
        ),
        notes="EDT in effect (UTC-4). Verifies DST-aware conversion.",
        vedic=ExpectedChart(
            # TODO: fill from JHora (Lahiri + whole-sign)
            planet_longitudes=None,
            planet_nakshatra_pada=None,
            ascendant=None,
            cusps=None,
        ),
        kp=ExpectedChart(
            # TODO: fill from JHora/KP tool (KP ayanamsa + Placidus)
            planet_longitudes=None,
            planet_sublords=None,
            ascendant=None,
            cusps=None,
            cusp_sublords=None,
        ),
    ),

    # 3) Pre-DB-era India via an EXPLICIT fixed offset — robustness for old
    #    births where IANA history may be uncertain. (Indian independence.)
    GoldenChart(
        label="midnight_1947_fixed_offset",
        birth=BirthData(
            year=1947, month=8, day=15,
            hour=0, minute=0, second=0,
            latitude=28.6139, longitude=77.2090,    # New Delhi
            timezone=5.5,                            # explicit +5:30, not IANA
            name="1947-08-15 00:00 +5:30",
        ),
        notes="Fixed numeric offset path; no reliance on IANA historical data.",
        vedic=ExpectedChart(
            # TODO: fill from JHora (Lahiri + whole-sign)
            planet_longitudes=None,
            planet_nakshatra_pada=None,
            ascendant=None,
            cusps=None,
        ),
        kp=ExpectedChart(
            # TODO: fill from JHora/KP tool (KP ayanamsa + Placidus)
            planet_longitudes=None,
            planet_sublords=None,
            ascendant=None,
            cusps=None,
            cusp_sublords=None,
        ),
    ),
]
