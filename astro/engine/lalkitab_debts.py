"""Lal Kitab rinas (ancestral debts) — detection from the fixed-grid chart.

EDITION NOTE — the debt conditions below follow the **1941 edition** as commonly
reproduced. Rina conditions are stated differently across sources; they are kept
here as transparent, self-contained predicates so they can be checked against a
physical copy and corrected. Each detected rina cites the placement that
triggered it.

Pure logic over a :class:`LalKitabChart`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Tuple

from .lalkitab import LalKitabChart

# Planets treated as afflicters when they sit with / occupy a house.
AFFLICTERS = ("Saturn", "Rahu", "Ketu")
MALEFICS = ("Saturn", "Rahu", "Ketu", "Mars")


@dataclass(frozen=True)
class Rina:
    name: str
    sanskrit: str
    present: bool
    trigger: str
    effects: Tuple[str, ...]


def _in_house(lk: LalKitabChart, house: int) -> List[str]:
    return lk.house_planets.get(house, [])


def _malefics_in(lk: LalKitabChart, house: int) -> List[str]:
    return [p for p in _in_house(lk, house) if p in MALEFICS]


def _afflicters_with(lk: LalKitabChart, planet: str) -> List[str]:
    h = lk.planet_house[planet]
    return [p for p in lk.house_planets[h] if p != planet and p in AFFLICTERS]


# Each rule returns (present, trigger-text).
def _pitra_rin(lk):
    mal = _malefics_in(lk, 9)
    aff = _afflicters_with(lk, "Sun")
    if mal:
        return True, f"malefic(s) {mal} in the 9th house (ancestral/dharma)"
    if aff:
        return True, f"Sun afflicted by {aff}"
    return False, ""


def _matri_rin(lk):
    mal = _malefics_in(lk, 4)
    aff = _afflicters_with(lk, "Moon")
    if mal:
        return True, f"malefic(s) {mal} in the 4th house (mother/home)"
    if aff:
        return True, f"Moon afflicted by {aff}"
    return False, ""


def _stri_rin(lk):
    mal = _malefics_in(lk, 7)
    aff = _afflicters_with(lk, "Venus")
    if mal:
        return True, f"malefic(s) {mal} in the 7th house (spouse)"
    if aff:
        return True, f"Venus afflicted by {aff}"
    return False, ""


def _bahin_beti_rin(lk):
    mal = _malefics_in(lk, 6)
    aff = _afflicters_with(lk, "Mercury")
    if mal:
        return True, f"malefic(s) {mal} in the 6th house (sisters/daughters)"
    if aff:
        return True, f"Mercury afflicted by {aff}"
    return False, ""


def _santan_rin(lk):
    mal = _malefics_in(lk, 5)
    if mal:
        return True, f"malefic(s) {mal} in the 5th house (progeny)"
    return False, ""


def _atma_rin(lk):
    mal = _malefics_in(lk, 1)
    if mal:
        return True, f"malefic(s) {mal} in the 1st house (self)"
    return False, ""


_RIN_DEFINITIONS: List[Tuple[str, str, Tuple[str, ...], Callable]] = [
    ("Ancestral debt", "Pitra Rin",
     ("father", "ancestors", "lineage", "fortune", "dharma"), _pitra_rin),
    ("Maternal debt", "Matri Rin",
     ("mother", "mental peace", "property", "home"), _matri_rin),
    ("Debt of women / spouse", "Stri Rin",
     ("marriage", "spouse", "domestic comfort"), _stri_rin),
    ("Sisters / daughters debt", "Bahin-Beti Rin",
     ("sisters", "daughters", "in-laws"), _bahin_beti_rin),
    ("Progeny debt", "Santan Rin",
     ("children", "education", "creativity"), _santan_rin),
    ("Self debt", "Atma Rin",
     ("self", "health", "reputation"), _atma_rin),
]


def detect_rinas(lk: LalKitabChart) -> List[Rina]:
    """All rinas evaluated; only the *present* ones are returned."""
    out = []
    for name, sanskrit, effects, rule in _RIN_DEFINITIONS:
        present, trigger = rule(lk)
        if present:
            out.append(Rina(name, sanskrit, True, trigger, effects))
    return out


def rina_report(lk: LalKitabChart) -> List[Rina]:
    """Every rina with its present/absent status (for a full audit)."""
    out = []
    for name, sanskrit, effects, rule in _RIN_DEFINITIONS:
        present, trigger = rule(lk)
        out.append(Rina(name, sanskrit, present,
                        trigger or "condition not met", effects))
    return out
