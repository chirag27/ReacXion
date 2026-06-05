"""Chart assembly — the deterministic public entry point.

``compute_chart`` ties the pieces together: it asks :mod:`engine.ephemeris`
for raw sidereal longitudes and house cusps, then layers on the pure-math
nakshatra and KP sub-lord resolution. The result is an immutable
:class:`Chart` snapshot.

Nothing here interprets the chart. Downstream layers (the LLM interpreter built
in a later phase) consume :class:`Chart` read-only and must never recompute or
invent a position.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from . import ephemeris
from .birth_data import BirthData
from .constants import (
    PRESET_KP,
    PRESET_VEDIC,
    SIGN_LORDS,
    SIGN_NAMES,
    SIGN_SPAN,
)
from .kp_sublord import resolve as kp_resolve
from .nakshatra import nakshatra_of


def _sign_index(longitude: float) -> int:
    return int((longitude % 360.0) // SIGN_SPAN)


@dataclass(frozen=True)
class PlanetPosition:
    name: str
    longitude: float            # sidereal, degrees [0, 360)
    sign: str
    sign_lord: str
    nakshatra: str
    nakshatra_lord: str         # KP "star lord"
    pada: int                   # 1..4
    sub_lord: str               # KP sub lord
    speed: float                # deg/day; negative => retrograde
    retrograde: bool

    @property
    def degrees_in_sign(self) -> float:
        return self.longitude % SIGN_SPAN


@dataclass(frozen=True)
class HouseCusp:
    house: int                  # 1..12
    longitude: float
    sign: str
    sign_lord: str
    nakshatra: str
    nakshatra_lord: str
    sub_lord: str

    @property
    def degrees_in_sign(self) -> float:
        return self.longitude % SIGN_SPAN


@dataclass(frozen=True)
class Chart:
    birth: BirthData
    ayanamsa: str
    house_system: str
    jd_ut: float
    ascendant: float
    planets: Dict[str, PlanetPosition]
    cusps: List[HouseCusp]


def _build_planet(name: str, longitude: float, speed: float) -> PlanetPosition:
    nak = nakshatra_of(longitude)
    lords = kp_resolve(longitude)
    sign_idx = _sign_index(longitude)
    # The lunar nodes are always retrograde in mean motion; rely on speed sign.
    return PlanetPosition(
        name=name,
        longitude=longitude,
        sign=SIGN_NAMES[sign_idx],
        sign_lord=SIGN_LORDS[sign_idx],
        nakshatra=nak.name,
        nakshatra_lord=nak.lord,
        pada=nak.pada,
        sub_lord=lords.sub_lord,
        speed=speed,
        retrograde=speed < 0.0,
    )


def _build_cusp(house: int, longitude: float) -> HouseCusp:
    nak = nakshatra_of(longitude)
    lords = kp_resolve(longitude)
    sign_idx = _sign_index(longitude)
    return HouseCusp(
        house=house,
        longitude=longitude,
        sign=SIGN_NAMES[sign_idx],
        sign_lord=SIGN_LORDS[sign_idx],
        nakshatra=nak.name,
        nakshatra_lord=nak.lord,
        sub_lord=lords.sub_lord,
    )


def compute_chart(
    birth: BirthData,
    ayanamsa: str = PRESET_VEDIC[0],
    house_system: str = PRESET_VEDIC[1],
) -> Chart:
    """Compute a full sidereal chart for ``birth``.

    Args:
        birth: the birth event.
        ayanamsa: ``"lahiri"`` (Vedic) or ``"kp"``.
        house_system: ``"whole_sign"`` (Parashari) or ``"placidus"`` (KP).

    Returns:
        An immutable :class:`Chart` with the nine grahas (each with nakshatra,
        pada and KP sub-lord), twelve house cusps (each with its KP sub-lord),
        and the ascendant.
    """
    jd_ut = ephemeris.julian_day_ut(birth.to_utc())

    raw_planets = ephemeris.planet_longitudes(jd_ut, ayanamsa)
    planets = {
        name: _build_planet(name, lon, speed)
        for name, (lon, speed) in raw_planets.items()
    }

    cusp_lons, ascendant = ephemeris.house_cusps(
        jd_ut, birth.latitude, birth.longitude, house_system, ayanamsa
    )
    cusps = [_build_cusp(i + 1, lon) for i, lon in enumerate(cusp_lons)]

    return Chart(
        birth=birth,
        ayanamsa=ayanamsa,
        house_system=house_system,
        jd_ut=jd_ut,
        ascendant=ascendant,
        planets=planets,
        cusps=cusps,
    )


def compute_vedic_chart(birth: BirthData) -> Chart:
    """Lahiri ayanamsa + whole-sign houses (Parashari preset)."""
    return compute_chart(birth, *PRESET_VEDIC)


def compute_kp_chart(birth: BirthData) -> Chart:
    """KP ayanamsa + Placidus houses (KP preset)."""
    return compute_chart(birth, *PRESET_KP)
