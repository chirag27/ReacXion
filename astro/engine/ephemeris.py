"""The sole bridge to Swiss Ephemeris (``pyswisseph``).

Every call into the astronomical library happens here. Nothing else in the
engine imports ``swisseph``. This keeps the deterministic numerical core in one
auditable place and makes the rest of the engine pure Python arithmetic.

By default the analytical **Moshier** ephemeris is used, which needs no data
files and is accurate to well within an arcminute. If you drop the Swiss
``*.se1`` files into ``data/ephe`` and call :func:`set_ephemeris_path`, the
higher-precision Swiss ephemeris is used instead — the closest possible match
to Jagannatha Hora for golden-chart validation.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple

import swisseph as swe

from .constants import (
    AYANAMSA_KP,
    AYANAMSA_LAHIRI,
    GRAHA_NAMES,
    HOUSE_PLACIDUS,
    HOUSE_WHOLE_SIGN,
)

# --------------------------------------------------------------------------- #
# Configuration maps (string keys -> swisseph constants)
# --------------------------------------------------------------------------- #
_AYANAMSA_MODE = {
    AYANAMSA_LAHIRI: swe.SIDM_LAHIRI,
    AYANAMSA_KP: swe.SIDM_KRISHNAMURTI,
}

_HOUSE_HSYS = {
    HOUSE_WHOLE_SIGN: b"W",
    HOUSE_PLACIDUS: b"P",
}

# Grahas queried directly from the ephemeris. Ketu is derived (Rahu + 180),
# and Rahu is the MEAN node per the spec.
_GRAHA_SWE_ID = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
}

# Whether Swiss data files have been registered. Falls back to Moshier if not.
_EPHE_PATH_SET = False


def set_ephemeris_path(path: str) -> None:
    """Register a directory of Swiss ``*.se1`` files for higher precision."""
    global _EPHE_PATH_SET
    swe.set_ephe_path(path)
    _EPHE_PATH_SET = True


def _base_flags() -> int:
    """Sidereal, with speed; Swiss if data files are present, else Moshier."""
    eph = swe.FLG_SWIEPH if _EPHE_PATH_SET else swe.FLG_MOSEPH
    return eph | swe.FLG_SIDEREAL | swe.FLG_SPEED


def _set_ayanamsa(ayanamsa: str) -> None:
    try:
        mode = _AYANAMSA_MODE[ayanamsa]
    except KeyError:
        raise ValueError(
            f"unknown ayanamsa {ayanamsa!r}; expected one of "
            f"{sorted(_AYANAMSA_MODE)}"
        ) from None
    swe.set_sid_mode(mode, 0, 0)


# --------------------------------------------------------------------------- #
# Time
# --------------------------------------------------------------------------- #
def julian_day_ut(utc_dt: datetime) -> float:
    """Universal-Time Julian Day for a timezone-aware UTC datetime.

    Uses ``swe.utc_to_jd`` so leap seconds and the UTC->UT1 reduction are
    handled by the library rather than approximated.
    """
    if utc_dt.tzinfo is None:
        raise ValueError("julian_day_ut expects a timezone-aware UTC datetime")
    # Normalize to true UTC before extracting components (no-op if already UTC).
    utc_dt = utc_dt.astimezone(timezone.utc)
    seconds = utc_dt.second + utc_dt.microsecond / 1_000_000.0
    _jd_et, jd_ut = swe.utc_to_jd(
        utc_dt.year, utc_dt.month, utc_dt.day,
        utc_dt.hour, utc_dt.minute, seconds,
        swe.GREG_CAL,
    )
    return jd_ut


# --------------------------------------------------------------------------- #
# Planets
# --------------------------------------------------------------------------- #
def planet_longitudes(jd_ut: float, ayanamsa: str) -> Dict[str, Tuple[float, float]]:
    """Sidereal longitude and longitudinal speed (deg, deg/day) per graha.

    Returns a dict keyed by the nine graha names. Ketu is Rahu + 180° with the
    same speed; the nodes are mean nodes.
    """
    _set_ayanamsa(ayanamsa)
    flags = _base_flags()

    out: Dict[str, Tuple[float, float]] = {}
    for name, swe_id in _GRAHA_SWE_ID.items():
        values, ret_flag = swe.calc_ut(jd_ut, swe_id, flags)
        if ret_flag < 0:
            raise RuntimeError(f"swisseph failed for {name}: flag {ret_flag}")
        longitude, _lat, _dist, speed_long = values[0], values[1], values[2], values[3]
        out[name] = (longitude % 360.0, speed_long)

    rahu_lon, rahu_speed = out["Rahu"]
    out["Ketu"] = ((rahu_lon + 180.0) % 360.0, rahu_speed)

    # Preserve the canonical graha ordering.
    return {name: out[name] for name in GRAHA_NAMES}


# --------------------------------------------------------------------------- #
# Houses
# --------------------------------------------------------------------------- #
def house_cusps(
    jd_ut: float,
    latitude: float,
    longitude: float,
    house_system: str,
    ayanamsa: str,
) -> Tuple[list[float], float]:
    """Return ``(cusps, ascendant)`` — 12 sidereal cusp longitudes + the asc.

    ``cusps[i]`` is the cusp of house ``i + 1``. For whole-sign houses each
    cusp snaps to 0° of its sign; the ascendant remains the precise degree.
    """
    _set_ayanamsa(ayanamsa)
    try:
        hsys = _HOUSE_HSYS[house_system]
    except KeyError:
        raise ValueError(
            f"unknown house system {house_system!r}; expected one of "
            f"{sorted(_HOUSE_HSYS)}"
        ) from None

    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, hsys, swe.FLG_SIDEREAL)
    # pyswisseph returns 12 cusps (house 1..12) for these systems.
    cusp_list = [c % 360.0 for c in cusps[:12]]
    ascendant = ascmc[0] % 360.0
    return cusp_list, ascendant
