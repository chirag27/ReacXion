"""KP significator engine — the 4-step theory.

Builds, from a KP chart (KP ayanamsa + Placidus cusps), the cuspal house
framework and the Krishnamurti Paddhati significators. House placement is
**cuspal** (a planet is in the bhava whose Placidus cusp span contains it), not
whole-sign — this is central to KP.

Significators of a house, strongest first (the 4-step theory):
  1. planets in the *star* (nakshatra) of an occupant of the house,
  2. occupants of the house,
  3. planets in the star of the *owner* (cuspal sign lord) of the house,
  4. the owner of the house.

The reverse — what a planet signifies — follows the same logic: a planet works
strongest through the houses its star-lord occupies/owns, then through the
houses it itself occupies/owns.

The lunar nodes are treated here as ordinary tenants (they signify by
occupancy and by being in some planet's star). Their additional KP agency —
representing a conjoined/aspected planet, their sign-lord and star-lord — is a
documented refinement layered on top, not yet folded into the base ordering.

Pure arithmetic over a Phase-1 KP :class:`Chart`; no ephemeris dependency.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

NODES = ("Rahu", "Ketu")


def _in_arc(longitude: float, start: float, end: float) -> bool:
    """True if ``longitude`` lies in the forward arc [start, end)."""
    span = (end - start) % 360.0
    if span == 0:
        span = 360.0
    offset = (longitude - start) % 360.0
    return offset < span


def kp_house_of(longitude: float, cusp_longitudes: List[float]) -> int:
    """Cuspal bhava (1..12) of a longitude given the 12 Placidus cusp starts."""
    lon = longitude % 360.0
    for h in range(12):
        start = cusp_longitudes[h]
        end = cusp_longitudes[(h + 1) % 12]
        if _in_arc(lon, start, end):
            return h + 1
    return 12  # unreachable for valid cusps


@dataclass(frozen=True)
class Significator:
    planet: str
    level: int          # 1 (strongest) .. 4
    reason: str


@dataclass
class KPAnalysis:
    planet_house: Dict[str, int]          # graha -> cuspal bhava
    occupants: Dict[int, List[str]]       # bhava -> grahas tenanting it
    owner: Dict[int, str]                 # bhava -> cuspal sign lord
    star_lord: Dict[str, str]             # graha -> its nakshatra (star) lord
    sub_lord: Dict[str, str]              # graha -> its KP sub lord
    houses_owned_by: Dict[str, List[int]] # graha -> bhavas it owns
    cuspal_sub_lord: Dict[int, str]       # bhava -> KP cuspal sub lord

    @classmethod
    def from_chart(cls, chart) -> "KPAnalysis":
        cusp_longs = [c.longitude for c in chart.cusps]

        planet_house, occupants = {}, {h: [] for h in range(1, 13)}
        star_lord, sub_lord = {}, {}
        for name, p in chart.planets.items():
            h = kp_house_of(p.longitude, cusp_longs)
            planet_house[name] = h
            occupants[h].append(name)
            star_lord[name] = p.nakshatra_lord
            sub_lord[name] = p.sub_lord

        owner = {c.house: c.sign_lord for c in chart.cusps}
        cuspal_sub_lord = {c.house: c.sub_lord for c in chart.cusps}

        houses_owned_by: Dict[str, List[int]] = {}
        for h, lord in owner.items():
            houses_owned_by.setdefault(lord, []).append(h)

        return cls(planet_house, occupants, owner, star_lord, sub_lord,
                   houses_owned_by, cuspal_sub_lord)

    # ------------------------------------------------------------------ #
    def house_significators(self, house: int) -> List[Significator]:
        """Ordered 4-step significators of ``house`` (strongest first, deduped)."""
        occ = self.occupants[house]
        own = self.owner[house]

        ranked: List[Significator] = []
        # Level 1: planets in the star of an occupant.
        for p, sl in self.star_lord.items():
            if sl in occ:
                ranked.append(Significator(p, 1, f"in star of occupant {sl}"))
        # Level 2: occupants.
        for p in occ:
            ranked.append(Significator(p, 2, "occupant"))
        # Level 3: planets in the star of the owner.
        for p, sl in self.star_lord.items():
            if sl == own:
                ranked.append(Significator(p, 3, f"in star of owner {own}"))
        # Level 4: the owner.
        ranked.append(Significator(own, 4, "house owner"))

        seen, out = set(), []
        for sig in ranked:
            if sig.planet not in seen:
                seen.add(sig.planet)
                out.append(sig)
        return out

    def planet_significations(self, planet: str) -> Dict[int, int]:
        """Houses a planet signifies -> strongest level (1..4) for each.

        1: house occupied by the planet's star-lord,
        2: house owned by the planet's star-lord,
        3: house occupied by the planet,
        4: house owned by the planet.
        """
        sl = self.star_lord[planet]
        levels: Dict[int, int] = {}

        def add(house: int, level: int):
            if house not in levels or level < levels[house]:
                levels[house] = level

        add(self.planet_house[sl], 1)
        for h in self.houses_owned_by.get(sl, []):
            add(h, 2)
        add(self.planet_house[planet], 3)
        for h in self.houses_owned_by.get(planet, []):
            add(h, 4)
        return levels

    def significators_of_houses(self, houses) -> List[str]:
        """Union of significator planets for several houses, strongest first.

        This is the raw 4-step candidate list (often long); narrow it with
        :meth:`final_significators`.
        """
        best: Dict[str, int] = {}
        for h in houses:
            for sig in self.house_significators(h):
                if sig.planet not in best or sig.level < best[sig.planet]:
                    best[sig.planet] = sig.level
        return [p for p, _ in sorted(best.items(), key=lambda kv: kv[1])]

    def final_significators(self, houses) -> List[str]:
        """Prune the raw significators by the KP sub-lord concurrence rule.

        A candidate survives only if its own *sub lord* also signifies the
        house group — the standard filter that turns the long 4-step list into
        the fruitful significators.
        """
        group = set(houses)
        out = []
        for p in self.significators_of_houses(houses):
            sub = self.sub_lord[p]
            if group & set(self.planet_significations(sub)):
                out.append(p)
        return out
