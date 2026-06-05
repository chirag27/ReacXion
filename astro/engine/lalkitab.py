"""Lal Kitab chart, pakka ghar, and planetary states.

A SEPARATE paradigm — this module deliberately does not reuse the Parashari
interpretation layer. Per the build plan it uses the classic Lal Kitab grid
where the houses (khanas) are fixed to signs: **Aries = 1st house, Taurus =
2nd, … Pisces = 12th**. A planet's Lal Kitab house is therefore its sign
number, independent of the ascendant. The ascendant's house is recorded
separately.

EDITION NOTE — these tables encode the **Lal Kitab 1941 edition** as commonly
reproduced. Lal Kitab has several conflicting editions (1939–1952) and even the
1941 tables are transcribed differently across sources. The values live in
plain data tables here so they are easy to audit and correct against a physical
copy of the chosen edition.

Pure arithmetic over a Phase-1 :class:`Chart`; no ephemeris dependency.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .constants import SIGN_NAMES, SIGN_SPAN

GRAHAS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
          "Rahu", "Ketu")

# Pakka ghar (permanent house) of each graha — Lal Kitab 1941 (as commonly
# reproduced). House numbers correspond to the fixed grid (1 = Aries khana).
PAKKA_GHAR: Dict[str, int] = {
    "Sun": 1, "Moon": 4, "Mars": 3, "Mercury": 7, "Jupiter": 9,
    "Venus": 7, "Saturn": 10, "Rahu": 12, "Ketu": 6,
}

# Lal Kitab drishti (nazar): the houses a graha sees, counted from itself.
LAL_KITAB_DRISHTI: Dict[str, List[int]] = {
    "Mars": [4, 7, 8],
    "Jupiter": [5, 7, 9],
    "Saturn": [3, 7, 10],
}
_DEFAULT_DRISHTI = [7]

# Planetary states.
IN_PAKKA_GHAR = "in_pakka_ghar"
AWAKENED = "awakened"
ASLEEP = "asleep"
BLIND = "blind"


def lal_kitab_house(longitude: float) -> int:
    """Fixed-grid Lal Kitab house (1..12) of a longitude (Aries=1)."""
    return int(longitude % 360.0 // SIGN_SPAN) + 1


def _aspect_houses(planet: str) -> List[int]:
    return LAL_KITAB_DRISHTI.get(planet, _DEFAULT_DRISHTI)


@dataclass(frozen=True)
class PlanetState:
    planet: str
    house: int
    in_pakka_ghar: bool
    state: str            # awakened / asleep / blind (or in_pakka_ghar emphasised)
    companions: List[str] # co-tenants in the same khana
    aspected_by: List[str]


@dataclass
class LalKitabChart:
    planet_house: Dict[str, int]          # graha -> fixed-grid house
    house_planets: Dict[int, List[str]]   # house -> grahas
    ascendant_house: int                  # the lagna's khana (its sign)
    states: Dict[str, PlanetState]

    @classmethod
    def from_chart(cls, chart) -> "LalKitabChart":
        planet_house = {
            name: lal_kitab_house(p.longitude)
            for name, p in chart.planets.items()
        }
        house_planets: Dict[int, List[str]] = {h: [] for h in range(1, 13)}
        for name, h in planet_house.items():
            house_planets[h].append(name)

        # Aspect map (who sees whom) in the fixed grid.
        aspected_by: Dict[str, List[str]] = {g: [] for g in planet_house}
        for seer, sh in planet_house.items():
            targets = {((sh - 1 + a - 1) % 12) + 1 for a in _aspect_houses(seer)}
            for other, oh in planet_house.items():
                if other != seer and oh in targets:
                    aspected_by[other].append(seer)

        states: Dict[str, PlanetState] = {}
        for name, h in planet_house.items():
            companions = [p for p in house_planets[h] if p != name]
            asp = sorted(aspected_by[name])
            in_pakka = (h == PAKKA_GHAR.get(name))
            # awakened if it has company; asleep if alone but aspected; else blind.
            if companions:
                state = AWAKENED
            elif asp:
                state = ASLEEP
            else:
                state = BLIND
            states[name] = PlanetState(
                planet=name, house=h, in_pakka_ghar=in_pakka, state=state,
                companions=sorted(companions), aspected_by=asp,
            )

        asc_house = lal_kitab_house(chart.ascendant)
        return cls(planet_house, house_planets, asc_house, states)

    def house_sign_name(self, house: int) -> str:
        """Fixed-grid sign for a house (Aries for 1, …)."""
        return SIGN_NAMES[(house - 1) % 12]

    def planets_in_pakka_ghar(self) -> List[str]:
        return [g for g, s in self.states.items() if s.in_pakka_ghar]
