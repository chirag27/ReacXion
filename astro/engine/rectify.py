"""Birth-time confidence and (coarse) rectification via KP cuspal stability.

A KP chart is only valid for the span over which its 12 cuspal sub-lords stay
fixed — they shift within minutes. This module measures that stable span around
a recorded birth time, turns it into a confidence indicator, and suggests the
most robust time (the centre of the stable span) for an uncertain birth time.

This is a *coarse* aid: true rectification also weighs life events against
dasha/transits. Here we only quantify how birth-time-sensitive the KP chart is.

Pure engine logic (deterministic); no LLM.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from .birth_data import BirthData
from .chart import compute_kp_chart


def cuspal_signature(birth: BirthData) -> Tuple[str, ...]:
    """The 12 KP cuspal sub-lords — the identity that must hold for the chart."""
    return tuple(c.sub_lord for c in compute_kp_chart(birth).cusps)


def _shift(birth: BirthData, seconds: float) -> BirthData:
    ld = birth.local_datetime() + timedelta(seconds=seconds)
    return BirthData(ld.year, ld.month, ld.day, ld.hour, ld.minute, ld.second,
                     birth.latitude, birth.longitude, birth.timezone,
                     fold=birth.fold, name=birth.name)


@dataclass
class StableInterval:
    before_seconds: float        # how far back the signature holds (>= 0)
    after_seconds: float         # how far forward it holds
    start: datetime              # earliest UTC instant with the same signature
    end: datetime                # latest UTC instant with the same signature
    width_seconds: float
    center: datetime             # midpoint — the most robust time


def stable_interval(
    birth: BirthData,
    max_minutes: float = 12.0,
    step_seconds: float = 10.0,
) -> StableInterval:
    """Scan ± ``max_minutes`` for the span where the cuspal signature is unchanged."""
    base = cuspal_signature(birth)
    limit = max_minutes * 60.0

    def hold(direction: int) -> float:
        held = 0.0
        t = step_seconds
        while t <= limit:
            if cuspal_signature(_shift(birth, direction * t)) != base:
                break
            held = t
            t += step_seconds
        return held

    before = hold(-1)
    after = hold(+1)
    birth_utc = birth.to_utc()
    start = birth_utc - timedelta(seconds=before)
    end = birth_utc + timedelta(seconds=after)
    return StableInterval(
        before_seconds=before, after_seconds=after, start=start, end=end,
        width_seconds=before + after, center=start + (end - start) / 2)


@dataclass
class TimeConfidence:
    level: str                   # "high" | "medium" | "low"
    stable_width_seconds: float
    interval: StableInterval
    note: str


def time_confidence(birth: BirthData, max_minutes: float = 12.0) -> TimeConfidence:
    """Confidence in KP judgments given how wide the stable cuspal span is."""
    iv = stable_interval(birth, max_minutes=max_minutes)
    w = iv.width_seconds
    if w >= 240:           # cuspal signature stable across at least ~4 minutes
        level, note = "high", "cuspal sub-lords are stable for several minutes"
    elif w >= 90:
        level, note = "medium", "cuspal sub-lords stable for a minute or two — KP results fairly robust"
    else:
        level, note = "low", "a cuspal sub-lord changes within ~a minute — verify the birth time before fine KP judgments"
    return TimeConfidence(level=level, stable_width_seconds=w, interval=iv, note=note)


@dataclass
class RectificationSuggestion:
    recorded: datetime           # the recorded birth instant (UTC)
    confidence: str
    stable_start: datetime
    stable_end: datetime
    suggested_center: datetime   # most robust time within the stable span
    candidates: List[datetime]   # boundary instants where the signature flips


def suggest_rectification(
    birth: BirthData,
    max_minutes: float = 12.0,
) -> RectificationSuggestion:
    """Suggest a robust time and the nearby instants where the KP chart changes."""
    conf = time_confidence(birth, max_minutes=max_minutes)
    iv = conf.interval
    return RectificationSuggestion(
        recorded=birth.to_utc(),
        confidence=conf.level,
        stable_start=iv.start,
        stable_end=iv.end,
        suggested_center=iv.center,
        candidates=[iv.start, iv.end],
    )
