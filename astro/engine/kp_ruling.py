"""KP Ruling Planets (RP) at a query moment.

The ruling planets for a query cast for a time and place are:
  * the **day lord** (lord of the weekday),
  * the **Moon's** sign lord, star lord and sub lord,
  * the **Lagna's** (ascendant at query time) sign lord, star lord and sub lord.

A KP chart is cast for the query instant (KP ayanamsa, Placidus) and the lords
are read off the Moon and the ascendant. The weekday is taken from the query's
local civil date; strictly the Hindu day runs from sunrise, so a pre-sunrise
query belongs to the previous weekday — a documented refinement.

The lunar nodes are added when they tenant the star of a ruling planet (a
common KP rule); fuller node agency is left as a refinement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .birth_data import BirthData
from .chart import compute_kp_chart
from .kp_sublord import resolve as kp_resolve

# Python date.weekday(): Monday=0 .. Sunday=6
_WEEKDAY_LORD = {
    0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter",
    4: "Venus", 5: "Saturn", 6: "Sun",
}

NODES = ("Rahu", "Ketu")


@dataclass
class RulingPlanets:
    day_lord: str
    moon_sign_lord: str
    moon_star_lord: str
    moon_sub_lord: str
    lagna_sign_lord: str
    lagna_star_lord: str
    lagna_sub_lord: str
    nodes: List[str] = field(default_factory=list)

    @property
    def ordered(self) -> List[str]:
        """Deduped RP set, Lagna sub/star/sign, then Moon, then day lord, + nodes."""
        seq = [
            self.lagna_sub_lord, self.lagna_star_lord, self.lagna_sign_lord,
            self.moon_sub_lord, self.moon_star_lord, self.moon_sign_lord,
            self.day_lord, *self.nodes,
        ]
        seen, out = set(), []
        for p in seq:
            if p not in seen:
                seen.add(p)
                out.append(p)
        return out


def ruling_planets(query: BirthData) -> RulingPlanets:
    """Compute the ruling planets for a query cast at ``query`` (time + place)."""
    chart = compute_kp_chart(query)

    moon = chart.planets["Moon"]
    lagna = kp_resolve(chart.ascendant)

    # Weekday from the local civil date of the query.
    weekday = query.local_datetime().weekday()
    day_lord = _WEEKDAY_LORD[weekday]

    rp = RulingPlanets(
        day_lord=day_lord,
        moon_sign_lord=moon.sign_lord,
        moon_star_lord=moon.nakshatra_lord,
        moon_sub_lord=moon.sub_lord,
        lagna_sign_lord=lagna.sign_lord,
        lagna_star_lord=lagna.star_lord,
        lagna_sub_lord=lagna.sub_lord,
    )

    # Add a node if its star-lord is already among the ruling planets.
    base = set(rp.ordered)
    nodes = [n for n in NODES if chart.planets[n].nakshatra_lord in base]
    rp.nodes = nodes
    return rp
