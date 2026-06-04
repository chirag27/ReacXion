"""
Core astrology calculation engine (reference implementation).

This module is the single source of truth for all chart math. The mobile
(Flutter) app mirrors this logic using the Dart `sweph` package; the JSON it
produces is validated against the output of this engine.

Everything here is deterministic given (datetime, latitude, longitude, tz).
No interpretation/remedy text lives here -- only positions, signs, nakshatras,
dashas and KP sub-lords.

Dependencies: pyswisseph  (pip install pyswisseph)
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from typing import Optional

import swisseph as swe

# --------------------------------------------------------------------------
# Static reference tables
# --------------------------------------------------------------------------

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Sign lord (rashi adhipati) used across Vedic / KP / Lal Kitab.
SIGN_LORD = [
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter",
]

# 27 Nakshatras with their ruling planet (Vimshottari lord). Order matters:
# index i spans [i * 13.333..., (i+1) * 13.333...] degrees of the sidereal zodiac.
NAKSHATRAS = [
    ("Ashwini", "Ketu"), ("Bharani", "Venus"), ("Krittika", "Sun"),
    ("Rohini", "Moon"), ("Mrigashira", "Mars"), ("Ardra", "Rahu"),
    ("Punarvasu", "Jupiter"), ("Pushya", "Saturn"), ("Ashlesha", "Mercury"),
    ("Magha", "Ketu"), ("Purva Phalguni", "Venus"), ("Uttara Phalguni", "Sun"),
    ("Hasta", "Moon"), ("Chitra", "Mars"), ("Swati", "Rahu"),
    ("Vishakha", "Jupiter"), ("Anuradha", "Saturn"), ("Jyeshtha", "Mercury"),
    ("Mula", "Ketu"), ("Purva Ashadha", "Venus"), ("Uttara Ashadha", "Sun"),
    ("Shravana", "Moon"), ("Dhanishta", "Mars"), ("Shatabhisha", "Rahu"),
    ("Purva Bhadrapada", "Jupiter"), ("Uttara Bhadrapada", "Saturn"), ("Revati", "Mercury"),
]

# Vimshottari dasha: planet order (starting reference) and total years.
# This same 120-year cycle drives both Vedic dasha periods and KP sub-divisions.
VIMSHOTTARI_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars",
                     "Rahu", "Jupiter", "Saturn", "Mercury"]
VIMSHOTTARI_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17,
}
TOTAL_DASHA_YEARS = 120  # sum of the above

NAKSHATRA_SPAN = 360.0 / 27.0       # 13.3333... degrees
PADA_SPAN = NAKSHATRA_SPAN / 4.0    # 3.3333... degrees

# Swiss Ephemeris planet handles.
PLANET_IDS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
    "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    # Rahu = Moon's north node. We use the MEAN node (standard for KP/Vedic).
    "Rahu": swe.MEAN_NODE,
}

# Ayanamsa modes.
AYANAMSA_LAHIRI = swe.SIDM_LAHIRI       # Vedic default (Chitrapaksha)
AYANAMSA_KP = swe.SIDM_KRISHNAMURTI     # KP system


# --------------------------------------------------------------------------
# Data structures
# --------------------------------------------------------------------------

@dataclass
class PlanetPosition:
    name: str
    longitude: float          # sidereal longitude 0-360
    sign: str
    sign_index: int           # 0-11
    degree_in_sign: float
    nakshatra: str
    nakshatra_index: int      # 0-26
    nakshatra_lord: str
    pada: int                 # 1-4
    sub_lord: str             # KP sub-lord
    retrograde: bool
    house: Optional[int] = None  # filled in once houses are known


@dataclass
class DashaPeriod:
    lord: str
    start: _dt.date
    end: _dt.date
    sub_periods: list = field(default_factory=list)


@dataclass
class Chart:
    when_utc: _dt.datetime
    latitude: float
    longitude: float
    ayanamsa_name: str
    ayanamsa_value: float
    ascendant: PlanetPosition
    planets: dict          # name -> PlanetPosition
    house_cusps: list      # 12 sidereal cusp longitudes
    dasha_balance: dict    # starting dasha lord + remaining years
    vimshottari: list      # list[DashaPeriod]


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _norm360(x: float) -> float:
    return x % 360.0


def to_julian_day_ut(when_utc: _dt.datetime) -> float:
    """Convert a timezone-aware UTC datetime to Julian Day (UT)."""
    if when_utc.tzinfo is not None:
        when_utc = when_utc.astimezone(_dt.timezone.utc).replace(tzinfo=None)
    frac_hour = (when_utc.hour
                 + when_utc.minute / 60.0
                 + when_utc.second / 3600.0)
    return swe.julday(when_utc.year, when_utc.month, when_utc.day,
                      frac_hour, swe.GREG_CAL)


def nakshatra_of(longitude: float):
    """Return (index, name, lord, pada) for a sidereal longitude."""
    lon = _norm360(longitude)
    idx = int(lon // NAKSHATRA_SPAN)
    name, lord = NAKSHATRAS[idx]
    pada = int((lon - idx * NAKSHATRA_SPAN) // PADA_SPAN) + 1
    return idx, name, lord, pada


def sub_lord_of(longitude: float) -> str:
    """
    KP sub-lord for a sidereal longitude.

    The 13.333-degree nakshatra is subdivided into 9 'subs' in Vimshottari
    proportion, starting from the nakshatra lord. This is the heart of KP and
    yields the famous 249-sub table when applied across all 27 nakshatras.
    """
    lon = _norm360(longitude)
    nidx = int(lon // NAKSHATRA_SPAN)
    star_lord = NAKSHATRAS[nidx][1]
    pos_in_nak = lon - nidx * NAKSHATRA_SPAN

    # Walk the Vimshottari order starting from the star lord, allocating each
    # sub a width proportional to its dasha years.
    start = VIMSHOTTARI_ORDER.index(star_lord)
    cursor = 0.0
    for k in range(9):
        lord = VIMSHOTTARI_ORDER[(start + k) % 9]
        width = NAKSHATRA_SPAN * VIMSHOTTARI_YEARS[lord] / TOTAL_DASHA_YEARS
        if pos_in_nak < cursor + width or k == 8:
            return lord
        cursor += width
    return star_lord  # unreachable


def _make_position(name: str, lon: float, retro: bool) -> PlanetPosition:
    lon = _norm360(lon)
    sidx = int(lon // 30)
    nidx, nname, nlord, pada = nakshatra_of(lon)
    return PlanetPosition(
        name=name,
        longitude=lon,
        sign=SIGNS[sidx],
        sign_index=sidx,
        degree_in_sign=lon - sidx * 30,
        nakshatra=nname,
        nakshatra_index=nidx,
        nakshatra_lord=nlord,
        pada=pada,
        sub_lord=sub_lord_of(lon),
        retrograde=retro,
    )


# --------------------------------------------------------------------------
# Vimshottari Dasha
# --------------------------------------------------------------------------

def _add_years(d: _dt.date, years: float) -> _dt.date:
    # Astrological year approximated as 365.25 days (standard for dasha calc).
    return d + _dt.timedelta(days=years * 365.25)


def compute_vimshottari(moon_longitude: float, birth_date: _dt.date,
                        levels: int = 2) -> tuple:
    """
    Build the Vimshottari mahadasha timeline from the Moon's nakshatra.
    Returns (balance_info, list_of_DashaPeriod).
    """
    nidx, _, star_lord, _ = nakshatra_of(moon_longitude)
    pos_in_nak = _norm360(moon_longitude) - nidx * NAKSHATRA_SPAN
    fraction_elapsed = pos_in_nak / NAKSHATRA_SPAN

    full_years = VIMSHOTTARI_YEARS[star_lord]
    remaining_years = full_years * (1 - fraction_elapsed)

    balance = {
        "starting_lord": star_lord,
        "remaining_years": round(remaining_years, 4),
        "total_years": full_years,
    }

    start_idx = VIMSHOTTARI_ORDER.index(star_lord)
    periods = []
    # First (partial) mahadasha starts at birth.
    cursor = birth_date
    for i in range(9):
        lord = VIMSHOTTARI_ORDER[(start_idx + i) % 9]
        years = remaining_years if i == 0 else VIMSHOTTARI_YEARS[lord]
        end = _add_years(cursor, years)
        period = DashaPeriod(lord=lord, start=cursor, end=end)
        if levels >= 2:
            period.sub_periods = _compute_antardasha(lord, cursor, years)
        periods.append(period)
        cursor = end
    return balance, periods


def _compute_antardasha(maha_lord: str, start: _dt.date, maha_years: float):
    """Sub-periods (bhukti) within a mahadasha, proportional to dasha years."""
    subs = []
    start_idx = VIMSHOTTARI_ORDER.index(maha_lord)
    cursor = start
    for i in range(9):
        lord = VIMSHOTTARI_ORDER[(start_idx + i) % 9]
        years = maha_years * VIMSHOTTARI_YEARS[lord] / TOTAL_DASHA_YEARS
        end = _add_years(cursor, years)
        subs.append(DashaPeriod(lord=lord, start=cursor, end=end))
        cursor = end
    return subs


# --------------------------------------------------------------------------
# Top-level chart builder
# --------------------------------------------------------------------------

def build_chart(when_utc: _dt.datetime, latitude: float, longitude: float,
                system: str = "vedic") -> Chart:
    """
    Compute a full chart.

    system:
      "vedic" -> Lahiri ayanamsa, whole-sign houses (Parashari).
      "kp"    -> Krishnamurti ayanamsa, Placidus houses (KP).

    `when_utc` must be in UTC (convert local birth time first).
    """
    system = system.lower()
    if system == "kp":
        ayan_mode, ayan_name, house_sys = AYANAMSA_KP, "Krishnamurti (KP)", b"P"
    else:
        ayan_mode, ayan_name, house_sys = AYANAMSA_LAHIRI, "Lahiri", b"W"

    swe.set_sid_mode(ayan_mode)
    jd = to_julian_day_ut(when_utc)
    ayan_value = swe.get_ayanamsa_ut(jd)

    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    planets = {}
    for name, pid in PLANET_IDS.items():
        res = swe.calc_ut(jd, pid, flags)
        lon = res[0][0]
        speed = res[0][3]
        retro = speed < 0
        planets[name] = _make_position(name, lon, retro)

    # Ketu is always exactly opposite Rahu.
    rahu_lon = planets["Rahu"].longitude
    planets["Ketu"] = _make_position("Ketu", rahu_lon + 180.0,
                                     planets["Rahu"].retrograde)

    # Houses & ascendant (sidereal).
    cusps, ascmc = swe.houses_ex(jd, latitude, longitude, house_sys,
                                 swe.FLG_SIDEREAL)
    asc_lon = ascmc[0]
    ascendant = _make_position("Ascendant", asc_lon, False)

    house_cusps = [_norm360(c) for c in cusps[:12]]
    _assign_houses(planets, ascendant, house_cusps, system)

    moon_lon = planets["Moon"].longitude
    balance, vim = compute_vimshottari(moon_lon, when_utc.date())

    return Chart(
        when_utc=when_utc,
        latitude=latitude,
        longitude=longitude,
        ayanamsa_name=ayan_name,
        ayanamsa_value=ayan_value,
        ascendant=ascendant,
        planets=planets,
        house_cusps=house_cusps,
        dasha_balance=balance,
        vimshottari=vim,
    )


def _assign_houses(planets, ascendant, house_cusps, system):
    """Tag each planet with its house number."""
    if system == "kp":
        # Placidus: a planet is in house i if its longitude lies between cusp i
        # and cusp i+1 (wrapping at 360).
        for p in planets.values():
            p.house = _house_from_cusps(p.longitude, house_cusps)
        ascendant.house = 1
    else:
        # Whole-sign: house = sign distance from the ascendant's sign + 1.
        asc_sign = ascendant.sign_index
        for p in planets.values():
            p.house = ((p.sign_index - asc_sign) % 12) + 1
        ascendant.house = 1


def _house_from_cusps(lon, cusps):
    lon = _norm360(lon)
    for i in range(12):
        a = cusps[i]
        b = cusps[(i + 1) % 12]
        if a < b:
            if a <= lon < b:
                return i + 1
        else:  # wraps past 360
            if lon >= a or lon < b:
                return i + 1
    return 12
