"""Functional (lagna-based) benefic / malefic classification.

A planet's *functional* nature depends on the houses it rules from the
ascendant, independent of its natural (naisargika) benefic/malefic character.
This module encodes the classical Parashari logic, with every verdict traceable
to the houses the planet rules.

Precedence (highest first):
  1. **Yogakaraka** — rules both a kendra (4/7/10) and a trikona (5/9):
     strongly benefic.
  2. **Trikona lord** — rules the 5th or 9th (and the lagna lord, 1st):
     benefic.
  3. **Dusthana lord** — rules *only* dusthanas (6/8/12): malefic.
  4. **Trishadaya lord** — rules the 3rd/6th/11th without a trikona: malefic.
  5. Otherwise **neutral**, with a kendradhipati note (a natural benefic ruling
     only kendras loses sheen; a natural malefic ruling a kendra improves).

Schools differ (e.g. the Systems Approach uses fixed per-lagna lists); this is
the classical interpretation and is documented as such.

Pure arithmetic; no ephemeris dependency.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .constants import GRAHA_NAMES, SIGN_LORDS, SIGN_NAMES
from .houses import DUSTHANAS, KENDRAS, TRIKONAS

NATURAL_BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

BENEFIC = "benefic"
MALEFIC = "malefic"
YOGAKARAKA = "yogakaraka"
NEUTRAL = "neutral"


@dataclass(frozen=True)
class FunctionalNature:
    planet: str
    nature: str               # benefic / malefic / yogakaraka / neutral
    owned_houses: List[int]   # houses ruled from the lagna (empty for nodes)
    reason: str


def _houses_owned(planet: str, asc_sign: int) -> List[int]:
    """Houses (1..12) a planet rules for an ascendant; nodes rule none."""
    return [
        h for h in range(1, 13)
        if SIGN_LORDS[(asc_sign + h - 1) % 12] == planet
    ]


def functional_nature(planet: str, asc_sign: int) -> FunctionalNature:
    owned = _houses_owned(planet, asc_sign)

    if not owned:   # Rahu / Ketu have no sign rulership here
        return FunctionalNature(planet, NEUTRAL, owned,
                                "no house rulership (lunar node)")

    has_kendra = any(h in (4, 7, 10) for h in owned)   # 1 handled as trikona
    has_trikona = any(h in (5, 9) for h in owned)
    only_dusthana = all(h in DUSTHANAS for h in owned)

    if has_kendra and has_trikona:
        return FunctionalNature(
            planet, YOGAKARAKA, owned,
            f"rules a kendra and a trikona {sorted(owned)} (raja-yoga karaka)")

    if 1 in owned or has_trikona:
        trik = sorted(h for h in owned if h in TRIKONAS)
        return FunctionalNature(
            planet, BENEFIC, owned,
            f"trikona lord (rules {trik})")

    if only_dusthana:
        return FunctionalNature(
            planet, MALEFIC, owned,
            f"rules only dusthanas {sorted(owned)}")

    if any(h in (3, 6, 11) for h in owned):
        return FunctionalNature(
            planet, MALEFIC, owned,
            f"trishadaya/dusthana lord {sorted(owned)}")

    # Kendradhipati: pure kendra ownership (4/7/10) by a benefic dulls it.
    note = f"rules {sorted(owned)}"
    if has_kendra:
        if planet in NATURAL_BENEFICS:
            note += "; kendradhipati dosha (natural benefic owning a kendra)"
        elif planet in NATURAL_MALEFICS:
            note += "; natural malefic owning a kendra (capacity to do good)"
    return FunctionalNature(planet, NEUTRAL, owned, note)


def classify_all(asc_sign: int) -> Dict[str, FunctionalNature]:
    """Functional nature of all nine grahas for an ascendant sign (0..11)."""
    return {p: functional_nature(p, asc_sign) for p in GRAHA_NAMES}


def classify_chart(chart) -> Dict[str, FunctionalNature]:
    asc_sign = int(chart.ascendant % 360.0 // 30)
    return classify_all(asc_sign)


def yogakarakas_for(asc_sign: int) -> List[str]:
    return [p for p, fn in classify_all(asc_sign).items()
            if fn.nature == YOGAKARAKA]
