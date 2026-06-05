"""KP event judgment: house groups, cuspal-sub-lord verdict, timing, and the
birth-time sensitivity flag.

For an event, KP asks whether the **sub lord of the deciding cusp** signifies
the houses that promote the matter (and not only the houses that negate it). The
significators of the event's house group give the agents, and the Vimshottari
dasha of those significators gives the timing.

Because KP cuspal sub lords shift within minutes, :func:`birth_time_sensitivity`
recasts the chart slightly earlier and later and reports any cusp whose sub lord
changes — a direct confidence signal when the birth time is uncertain.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Dict, List, Optional, Tuple

from .birth_data import BirthData
from .chart import compute_kp_chart
from .dasha import DashaPeriod, chart_vimshottari
from .kp import KPAnalysis


@dataclass(frozen=True)
class EventRule:
    name: str
    houses: Tuple[int, ...]       # supporting house group
    deciding_cusp: int            # cusp whose sub lord judges the matter
    negating: Tuple[int, ...] = ()  # houses that deny/obstruct the matter


# Standard KP house groupings.
EVENTS: Dict[str, EventRule] = {
    "marriage": EventRule("marriage", (2, 7, 11), 7, negating=(1, 6, 10)),
    "career": EventRule("career", (2, 6, 10, 11), 10),
    "childbirth": EventRule("childbirth", (2, 5, 11), 5, negating=(1, 4, 10)),
    "education": EventRule("education", (4, 9, 11), 4),
    "property": EventRule("property", (4, 11, 12), 4, negating=(3, 8, 12)),
    "foreign_travel": EventRule("foreign_travel", (3, 9, 12), 12),
    "wealth": EventRule("wealth", (2, 6, 10, 11), 2),
    "disease": EventRule("disease", (6, 8, 12), 6),
}


@dataclass
class EventJudgment:
    event: str
    houses: Tuple[int, ...]
    deciding_cusp: int
    cuspal_sub_lord: str
    csl_signifies: Dict[int, int]          # all houses the CSL signifies -> level
    supports: List[int]                    # event houses the CSL signifies
    negates: List[int]                     # negating houses the CSL signifies
    significators: List[str]               # raw 4-step significators of the group
    final_significators: List[str]         # pruned by the sub-lord concurrence rule
    promised: bool
    verdict: str


def judge_event(analysis: KPAnalysis, event: str) -> EventJudgment:
    """Judge an event from a KP chart's significators and deciding-cusp sub lord."""
    try:
        rule = EVENTS[event]
    except KeyError:
        raise ValueError(f"unknown event {event!r}; known: {sorted(EVENTS)}") from None

    csl = analysis.cuspal_sub_lord[rule.deciding_cusp]
    csl_sig = analysis.planet_significations(csl)
    supports = sorted(h for h in rule.houses if h in csl_sig)
    negates = sorted(h for h in rule.negating if h in csl_sig)
    significators = analysis.significators_of_houses(rule.houses)
    final = analysis.final_significators(rule.houses)

    promised = bool(supports)
    if promised and negates and not (set(rule.houses) & set(csl_sig) - set(negates)):
        # CSL touches supporting houses but is dominated by negating ones.
        verdict = "promised but obstructed"
    elif promised:
        verdict = "promised"
    else:
        verdict = "not promised (deciding sub lord does not signify the matter)"

    return EventJudgment(
        event=event, houses=rule.houses, deciding_cusp=rule.deciding_cusp,
        cuspal_sub_lord=csl, csl_signifies=csl_sig, supports=supports,
        negates=negates, significators=significators, final_significators=final,
        promised=promised, verdict=verdict,
    )


def event_dasha_periods(
    birth: BirthData,
    analysis: KPAnalysis,
    event: str,
) -> List[DashaPeriod]:
    """KP timing windows: Dasha-Bhukti spans whose *both* lords signify the event.

    Uses the pruned (final) significators and the standard KP rule that the
    matter fructifies when the Maha (dasha) lord and the Antar (bhukti) lord are
    both significators of the house group. Returns the qualifying Antardashas.
    """
    rule = EVENTS[event]
    significators = set(analysis.final_significators(rule.houses))

    chart = compute_kp_chart(birth)
    mahas = chart_vimshottari(chart, depth=2)

    windows: List[DashaPeriod] = []
    for maha in mahas:
        if maha.lord not in significators:
            continue
        for antar in maha.children:
            if antar.lord in significators:
                windows.append(antar)
    return windows


# --------------------------------------------------------------------------- #
# Birth-time sensitivity
# --------------------------------------------------------------------------- #
@dataclass
class CuspChange:
    house: int
    earlier: str
    at_birth: str
    later: str


@dataclass
class SensitivityReport:
    window_minutes: float
    unstable_cusps: List[CuspChange]
    confidence: str          # "high" | "low"

    @property
    def is_stable(self) -> bool:
        return not self.unstable_cusps


def _shift(birth: BirthData, delta: timedelta) -> BirthData:
    ld = birth.local_datetime() + delta
    return BirthData(
        ld.year, ld.month, ld.day, ld.hour, ld.minute, ld.second,
        birth.latitude, birth.longitude, birth.timezone,
        fold=birth.fold, name=birth.name,
    )


def birth_time_sensitivity(birth: BirthData, minutes: float = 4.0) -> SensitivityReport:
    """Flag cuspal sub lords that change within ±``minutes`` of the birth time.

    A change in any *cuspal* sub lord within the uncertainty window means KP
    judgments on that cusp are unreliable — the confidence drops to "low".
    """
    base = compute_kp_chart(birth)
    lo = compute_kp_chart(_shift(birth, timedelta(minutes=-minutes)))
    hi = compute_kp_chart(_shift(birth, timedelta(minutes=+minutes)))

    changes: List[CuspChange] = []
    for i in range(12):
        e, b, l = lo.cusps[i].sub_lord, base.cusps[i].sub_lord, hi.cusps[i].sub_lord
        if not (e == b == l):
            changes.append(CuspChange(i + 1, e, b, l))

    return SensitivityReport(
        window_minutes=minutes,
        unstable_cusps=changes,
        confidence="low" if changes else "high",
    )
