"""Planetary dignity (avastha by sign) including Moolatrikona.

For a graha at a sidereal longitude this classifies its state as one of:
``exalted``, ``debilitated``, ``moolatrikona``, ``own``, ``friend``,
``neutral``, or ``enemy`` — using exaltation/debilitation points, moolatrikona
ranges, own-sign rulership, and the *natural* (naisargika) friendship table.

Temporary (tatkalika) friendship and the compound five-fold relationship are
later refinements; this module reports natural relationships only.

The lunar nodes have no universally agreed dignities, so by default they are
reported as ``neutral`` with no exaltation handling.

Pure arithmetic; no ephemeris dependency.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .constants import SIGN_LORDS, SIGN_NAMES, SIGN_SPAN

# Exaltation sign index and exact degree of deep exaltation. Debilitation is the
# opposite sign at the same degree.
EXALTATION: Dict[str, Tuple[int, float]] = {
    "Sun": (0, 10.0),       # Aries 10°
    "Moon": (1, 3.0),       # Taurus 3°
    "Mars": (9, 28.0),      # Capricorn 28°
    "Mercury": (5, 15.0),   # Virgo 15°
    "Jupiter": (3, 5.0),    # Cancer 5°
    "Venus": (11, 27.0),    # Pisces 27°
    "Saturn": (6, 20.0),    # Libra 20°
}

# Moolatrikona sign and degree range [low, high) within that sign.
MOOLATRIKONA: Dict[str, Tuple[int, float, float]] = {
    "Sun": (4, 0.0, 20.0),      # Leo 0-20°
    "Moon": (1, 3.0, 30.0),     # Taurus 3-30°
    "Mars": (0, 0.0, 12.0),     # Aries 0-12°
    "Mercury": (5, 15.0, 20.0), # Virgo 15-20°
    "Jupiter": (8, 0.0, 10.0),  # Sagittarius 0-10°
    "Venus": (6, 0.0, 15.0),    # Libra 0-15°
    "Saturn": (10, 0.0, 20.0),  # Aquarius 0-20°
}

# Natural friendships. Any planet not listed as friend/enemy is neutral.
FRIENDS: Dict[str, set] = {
    "Sun": {"Moon", "Mars", "Jupiter"},
    "Moon": {"Sun", "Mercury"},
    "Mars": {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus": {"Mercury", "Saturn"},
    "Saturn": {"Mercury", "Venus"},
}
ENEMIES: Dict[str, set] = {
    "Sun": {"Venus", "Saturn"},
    "Moon": set(),
    "Mars": {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"},
    "Venus": {"Sun", "Moon"},
    "Saturn": {"Sun", "Moon", "Mars"},
}

NODES = {"Rahu", "Ketu"}


def natural_relationship(planet: str, other: str) -> str:
    """``friend`` / ``enemy`` / ``neutral`` of ``other`` toward ``planet``."""
    if other in FRIENDS.get(planet, set()):
        return "friend"
    if other in ENEMIES.get(planet, set()):
        return "enemy"
    return "neutral"


@dataclass(frozen=True)
class DignityInfo:
    planet: str
    sign: str
    sign_lord: str          # dispositor
    state: str              # exalted/debilitated/moolatrikona/own/friend/neutral/enemy
    is_exalted: bool
    is_debilitated: bool


def planet_dignity(planet: str, longitude: float) -> DignityInfo:
    """Classify the dignity of ``planet`` at sidereal ``longitude``."""
    lon = longitude % 360.0
    sign = int(lon // SIGN_SPAN)
    degree_in_sign = lon - sign * SIGN_SPAN
    sign_lord = SIGN_LORDS[sign]

    if planet in NODES:
        # No standard exaltation; report relationship to the dispositor.
        state = ("own" if False else natural_relationship_for_node(planet, sign_lord))
        return DignityInfo(planet, SIGN_NAMES[sign], sign_lord, state, False, False)

    exalt_sign, _exalt_deg = EXALTATION[planet]
    debil_sign = (exalt_sign + 6) % 12

    if sign == exalt_sign:
        return DignityInfo(planet, SIGN_NAMES[sign], sign_lord, "exalted", True, False)
    if sign == debil_sign:
        return DignityInfo(planet, SIGN_NAMES[sign], sign_lord, "debilitated", False, True)

    mt_sign, mt_low, mt_high = MOOLATRIKONA[planet]
    if sign == mt_sign and mt_low <= degree_in_sign < mt_high:
        return DignityInfo(planet, SIGN_NAMES[sign], sign_lord, "moolatrikona", False, False)

    if sign_lord == planet:
        return DignityInfo(planet, SIGN_NAMES[sign], sign_lord, "own", False, False)

    return DignityInfo(
        planet, SIGN_NAMES[sign], sign_lord,
        natural_relationship(planet, sign_lord), False, False,
    )


def natural_relationship_for_node(node: str, sign_lord: str) -> str:
    """Nodes have no friendship table of their own; report ``neutral``."""
    return "neutral"


def chart_dignities(chart) -> Dict[str, DignityInfo]:
    """Dignity of every graha in a Phase-1 :class:`Chart`."""
    return {
        name: planet_dignity(name, p.longitude)
        for name, p in chart.planets.items()
    }
