"""Ashtakavarga — Bhinnashtakavarga and Sarvashtakavarga (bindu totals).

Uses the canonical Brihat Parashara Hora Shastra benefic-point tables. For each
of the seven grahas, the table lists — per contributor (the seven grahas plus
the Lagna) — the houses, counted from that contributor, in which the graha
earns a bindu. The per-graha totals are the well-known 48/49/39/54/56/52/39
(Sun..Saturn), summing to 337 across the Sarvashtakavarga.

Pure arithmetic; no ephemeris dependency.
"""

from __future__ import annotations

from typing import Dict, List

from .constants import SIGN_NAMES, SIGN_SPAN

CONTRIBUTORS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Lagna")
AV_PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")

# Benefic houses (counted from contributor, 1 = contributor's own sign).
# Transcribed to match Jagannatha Hora / PyJHora's tables exactly (a few rows —
# e.g. Moon-from-Moon, Moon-from-Mars, Venus-from-Mars — have textual variants
# across editions; these follow the JHora convention).
BENEFIC_HOUSES: Dict[str, Dict[str, tuple]] = {
    "Sun": {
        "Sun": (1, 2, 4, 7, 8, 9, 10, 11), "Moon": (3, 6, 10, 11), "Mars": (1, 2, 4, 7, 8, 9, 10, 11), "Mercury": (3, 5, 6, 9, 10, 11, 12),
        "Jupiter": (5, 6, 9, 11), "Venus": (6, 7, 12), "Saturn": (1, 2, 4, 7, 8, 9, 10, 11), "Lagna": (3, 4, 6, 10, 11, 12),
    },
    "Moon": {
        "Sun": (3, 6, 7, 8, 10, 11), "Moon": (1, 3, 6, 7, 9, 10, 11), "Mars": (2, 3, 5, 6, 10, 11), "Mercury": (1, 3, 4, 5, 7, 8, 10, 11),
        "Jupiter": (1, 2, 4, 7, 8, 10, 11), "Venus": (3, 4, 5, 7, 9, 10, 11), "Saturn": (3, 5, 6, 11), "Lagna": (3, 6, 10, 11),
    },
    "Mars": {
        "Sun": (3, 5, 6, 10, 11), "Moon": (3, 6, 11), "Mars": (1, 2, 4, 7, 8, 10, 11), "Mercury": (3, 5, 6, 11),
        "Jupiter": (6, 10, 11, 12), "Venus": (6, 8, 11, 12), "Saturn": (1, 4, 7, 8, 9, 10, 11), "Lagna": (1, 3, 6, 10, 11),
    },
    "Mercury": {
        "Sun": (5, 6, 9, 11, 12), "Moon": (2, 4, 6, 8, 10, 11), "Mars": (1, 2, 4, 7, 8, 9, 10, 11), "Mercury": (1, 3, 5, 6, 9, 10, 11, 12),
        "Jupiter": (6, 8, 11, 12), "Venus": (1, 2, 3, 4, 5, 8, 9, 11), "Saturn": (1, 2, 4, 7, 8, 9, 10, 11), "Lagna": (1, 2, 4, 6, 8, 10, 11),
    },
    "Jupiter": {
        "Sun": (1, 2, 3, 4, 7, 8, 9, 10, 11), "Moon": (2, 5, 7, 9, 11), "Mars": (1, 2, 4, 7, 8, 10, 11), "Mercury": (1, 2, 4, 5, 6, 9, 10, 11),
        "Jupiter": (1, 2, 3, 4, 7, 8, 10, 11), "Venus": (2, 5, 6, 9, 10, 11), "Saturn": (3, 5, 6, 12), "Lagna": (1, 2, 4, 5, 6, 7, 9, 10, 11),
    },
    "Venus": {
        "Sun": (8, 11, 12), "Moon": (1, 2, 3, 4, 5, 8, 9, 11, 12), "Mars": (3, 4, 6, 9, 11, 12), "Mercury": (3, 5, 6, 9, 11),
        "Jupiter": (5, 8, 9, 10, 11), "Venus": (1, 2, 3, 4, 5, 8, 9, 10, 11), "Saturn": (3, 4, 5, 8, 9, 10, 11), "Lagna": (1, 2, 3, 4, 5, 8, 9, 11),
    },
    "Saturn": {
        "Sun": (1, 2, 4, 7, 8, 10, 11), "Moon": (3, 6, 11), "Mars": (3, 5, 6, 10, 11, 12), "Mercury": (6, 8, 9, 10, 11, 12),
        "Jupiter": (5, 6, 11, 12), "Venus": (6, 11, 12), "Saturn": (3, 5, 6, 11), "Lagna": (1, 3, 4, 6, 10, 11),
    },
}


def _sign(longitude: float) -> int:
    return int(longitude % 360.0 // SIGN_SPAN)


def _contributor_signs(chart) -> Dict[str, int]:
    signs = {p: _sign(chart.planets[p].longitude) for p in AV_PLANETS}
    signs["Lagna"] = _sign(chart.ascendant)
    return signs


def bhinnashtakavarga(chart) -> Dict[str, List[int]]:
    """Per-graha bindus by sign index (0..11). Each list sums to the graha total."""
    csigns = _contributor_signs(chart)
    result: Dict[str, List[int]] = {}
    for planet in AV_PLANETS:
        bindus = [0] * 12
        for contributor, houses in BENEFIC_HOUSES[planet].items():
            base = csigns[contributor]
            for h in houses:
                bindus[(base + h - 1) % 12] += 1
        result[planet] = bindus
    return result


def sarvashtakavarga(chart) -> List[int]:
    """Total bindus per sign index (0..11) across the seven grahas (sum = 337)."""
    bav = bhinnashtakavarga(chart)
    total = [0] * 12
    for planet in AV_PLANETS:
        for s in range(12):
            total[s] += bav[planet][s]
    return total


def by_house(values_by_sign: List[int], asc_sign: int) -> Dict[int, int]:
    """Re-key a by-sign bindu list into houses 1..12 from the ascendant."""
    return {((s - asc_sign) % 12) + 1: values_by_sign[s] for s in range(12)}
