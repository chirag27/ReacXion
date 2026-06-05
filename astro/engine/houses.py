"""Bhava (house) structural analysis for the Parashari rasi chart.

Turns a Phase-1 :class:`Chart` (or a bare longitudes + ascendant pair) into the
whole-sign house framework the interpretation rules need: which planet sits in
which bhava, the sign and lord of each bhava, and the houses each planet rules.

Whole-sign convention: house 1 is the whole sign of the ascendant, so the bhava
of a body is ``((its_sign - asc_sign) mod 12) + 1``.

Pure arithmetic; no ephemeris dependency.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping

from .constants import SIGN_LORDS, SIGN_NAMES, SIGN_SPAN

KENDRAS = (1, 4, 7, 10)
TRIKONAS = (1, 5, 9)
DUSTHANAS = (6, 8, 12)
UPACHAYAS = (3, 6, 10, 11)
MARAKAS = (2, 7)
TRISHADAYA = (3, 6, 11)


def sign_index(longitude: float) -> int:
    return int(longitude % 360.0 // SIGN_SPAN)


def house_of(longitude: float, asc_sign: int) -> int:
    """Whole-sign bhava (1..12) of a longitude given the ascendant's sign."""
    return ((sign_index(longitude) - asc_sign) % 12) + 1


@dataclass(frozen=True)
class HouseChart:
    asc_sign: int                          # 0..11
    house_of_planet: Dict[str, int]        # graha -> bhava 1..12
    planets_in_house: Dict[int, List[str]] # bhava -> grahas
    house_sign: Dict[int, int]             # bhava -> sign index 0..11
    house_lord: Dict[int, str]             # bhava -> ruling graha
    houses_owned_by: Dict[str, List[int]]  # graha -> bhavas it rules

    def sign_name_of_house(self, house: int) -> str:
        return SIGN_NAMES[self.house_sign[house]]

    @classmethod
    def from_positions(
        cls, planet_longitudes: Mapping[str, float], ascendant: float
    ) -> "HouseChart":
        asc_sign = sign_index(ascendant)

        house_sign = {h: (asc_sign + h - 1) % 12 for h in range(1, 13)}
        house_lord = {h: SIGN_LORDS[house_sign[h]] for h in range(1, 13)}

        house_of_planet: Dict[str, int] = {}
        planets_in_house: Dict[int, List[str]] = {h: [] for h in range(1, 13)}
        for name, lon in planet_longitudes.items():
            h = house_of(lon, asc_sign)
            house_of_planet[name] = h
            planets_in_house[h].append(name)

        houses_owned_by: Dict[str, List[int]] = {}
        for h in range(1, 13):
            houses_owned_by.setdefault(house_lord[h], []).append(h)

        return cls(
            asc_sign=asc_sign,
            house_of_planet=house_of_planet,
            planets_in_house=planets_in_house,
            house_sign=house_sign,
            house_lord=house_lord,
            houses_owned_by=houses_owned_by,
        )

    @classmethod
    def from_chart(cls, chart) -> "HouseChart":
        longs = {name: p.longitude for name, p in chart.planets.items()}
        return cls.from_positions(longs, chart.ascendant)

    # -- convenience queries used by the rule modules --
    def lord_of(self, house: int) -> str:
        return self.house_lord[house]

    def houses_of(self, planet: str) -> List[int]:
        return self.houses_owned_by.get(planet, [])

    def occupants(self, house: int) -> List[str]:
        return self.planets_in_house[house]
