"""Graha drishti — Parashari planetary aspects.

Every graha aspects the 7th sign from itself. Mars additionally aspects the
4th and 8th, Jupiter the 5th and 9th, Saturn the 3rd and 10th (full special
aspects). The lunar nodes are given the 7th aspect only here (conventions vary;
some schools grant Rahu/Ketu Jupiter-like 5/9 aspects — adjust
:data:`SPECIAL_ASPECTS` if you follow that school).

Aspect "houses" are counted inclusively from the planet's own sign (the 1st),
so the Nth aspect lands on sign ``(planet_sign + N - 1) % 12``.

Pure arithmetic; no ephemeris dependency.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .constants import SIGN_NAMES, SIGN_SPAN

# Houses each planet aspects (the universal 7th plus any specials).
SPECIAL_ASPECTS: Dict[str, List[int]] = {
    "Mars": [4, 7, 8],
    "Jupiter": [5, 7, 9],
    "Saturn": [3, 7, 10],
}
DEFAULT_ASPECTS = [7]


def aspected_houses(planet: str) -> List[int]:
    """The house-numbers (counted from the planet) that ``planet`` aspects."""
    return SPECIAL_ASPECTS.get(planet, DEFAULT_ASPECTS)


def _sign_of(longitude: float) -> int:
    return int(longitude % 360.0 // SIGN_SPAN)


@dataclass(frozen=True)
class PlanetAspect:
    planet: str
    from_sign: str
    aspected_sign_indices: List[int]    # 0..11
    aspected_signs: List[str]
    aspected_planets: List[str]         # other grahas sitting in an aspected sign


def graha_drishti(chart) -> Dict[str, PlanetAspect]:
    """Compute every graha's sign aspects and which grahas it aspects.

    Returns a mapping ``graha name -> PlanetAspect``.
    """
    planet_signs = {name: _sign_of(p.longitude) for name, p in chart.planets.items()}

    result: Dict[str, PlanetAspect] = {}
    for name, sign in planet_signs.items():
        targets = sorted({(sign + h - 1) % 12 for h in aspected_houses(name)})
        aspected_planets = sorted(
            other for other, osign in planet_signs.items()
            if other != name and osign in targets
        )
        result[name] = PlanetAspect(
            planet=name,
            from_sign=SIGN_NAMES[sign],
            aspected_sign_indices=targets,
            aspected_signs=[SIGN_NAMES[i] for i in targets],
            aspected_planets=aspected_planets,
        )
    return result


def aspects_between(chart, a: str, b: str) -> bool:
    """True if graha ``a`` casts a Parashari aspect on graha ``b``."""
    return b in graha_drishti(chart)[a].aspected_planets
