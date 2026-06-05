"""Vimshottari dasha — the 120-year nakshatra-based timeline.

Computed deterministically from the Moon's sidereal longitude. The starting
Mahadasha is the lord of the Moon's nakshatra; the *balance* of that first
period is the un-traversed fraction of the nakshatra times the lord's years.
Sub-periods nest by the same proportional rule (Antar within Maha, Pratyantar
within Antar, Sookshma within Pratyantar), each sequence beginning with its
parent's lord and proceeding in Vimshottari order.

Pure arithmetic on top of :mod:`engine.nakshatra`; no ephemeris dependency.

**Year length is the key tuning knob.** Different references use slightly
different "year" definitions for dasha (sidereal 365.2564, Julian 365.25,
Gregorian 365.2425, or a 360-day savana year), which shifts long-range dates by
days. The default here is the **sidereal year** (365.256364 days), matching
Jagannatha Hora; pass ``year_length_days`` to use another convention.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from .constants import (
    NAK_SPAN,
    VIMSHOTTARI_ORDER,
    VIMSHOTTARI_TOTAL,
    VIMSHOTTARI_YEARS,
)
from .nakshatra import nakshatra_of, normalize

# Default Vimshottari year length: the sidereal solar year, which is Jagannatha
# Hora's default (and the PyJHora port's `sidereal_year`). Override to use a
# Julian year (365.25), Gregorian (365.2425), or a 360-day savana year.
DEFAULT_YEAR_DAYS = 365.256364
SIDEREAL_YEAR_DAYS = 365.256364
JULIAN_YEAR_DAYS = 365.25

LEVEL_NAMES = {1: "Mahadasha", 2: "Antardasha", 3: "Pratyantardasha", 4: "Sookshma"}


@dataclass(frozen=True)
class DashaPeriod:
    """One dasha period at some nesting level, with exact UTC bounds."""

    lord: str
    level: int                  # 1=Maha, 2=Antar, 3=Pratyantar, 4=Sookshma
    start: datetime             # timezone-aware UTC, inclusive
    end: datetime               # timezone-aware UTC, exclusive
    children: Tuple["DashaPeriod", ...] = field(default_factory=tuple)

    @property
    def level_name(self) -> str:
        return LEVEL_NAMES.get(self.level, f"L{self.level}")

    @property
    def duration_days(self) -> float:
        return (self.end - self.start).total_seconds() / 86400.0


def balance_at_birth(
    moon_longitude: float,
    year_length_days: float = DEFAULT_YEAR_DAYS,
) -> Tuple[str, float, float]:
    """Return ``(lord, balance_years, balance_days)`` of the first Mahadasha.

    The balance is the portion of the starting nakshatra still to be traversed
    by the Moon, scaled to the lord's full dasha length.
    """
    nak = nakshatra_of(moon_longitude)
    lord = nak.lord
    fraction_remaining = 1.0 - (nak.degrees_in_nak / NAK_SPAN)
    balance_years = fraction_remaining * VIMSHOTTARI_YEARS[lord]
    return lord, balance_years, balance_years * year_length_days


def _build_period(
    lord: str,
    start: datetime,
    duration_days: float,
    level: int,
    max_level: int,
) -> DashaPeriod:
    """Recursively build a period and its sub-periods down to ``max_level``."""
    end = start + timedelta(days=duration_days)
    children: List[DashaPeriod] = []
    if level < max_level:
        start_idx = VIMSHOTTARI_ORDER.index(lord)
        cursor = start
        for k in range(9):
            sub_lord = VIMSHOTTARI_ORDER[(start_idx + k) % 9]
            sub_days = duration_days * VIMSHOTTARI_YEARS[sub_lord] / VIMSHOTTARI_TOTAL
            child = _build_period(sub_lord, cursor, sub_days, level + 1, max_level)
            children.append(child)
            cursor = child.end
    return DashaPeriod(lord, level, start, end, tuple(children))


def vimshottari_dasha(
    moon_longitude: float,
    birth_utc: datetime,
    depth: int = 4,
    year_length_days: float = DEFAULT_YEAR_DAYS,
) -> List[DashaPeriod]:
    """Full Vimshottari Mahadasha sequence nested to ``depth`` levels.

    Args:
        moon_longitude: sidereal Moon longitude (degrees) for the chart's
            ayanamsa.
        birth_utc: timezone-aware UTC birth instant (anchor for all dates).
        depth: 1=Maha, 2=+Antar, 3=+Pratyantar, 4=+Sookshma.
        year_length_days: days per dasha-year (see module docstring).

    Returns:
        Mahadashas covering at least 120 years from birth. The first Mahadasha
        begins *before* birth by its elapsed portion, so the tree is internally
        consistent; use :func:`dasha_at` to read the chain active at any date.
    """
    if birth_utc.tzinfo is None:
        raise ValueError("birth_utc must be timezone-aware (UTC)")
    if not 1 <= depth <= 4:
        raise ValueError("depth must be between 1 and 4")

    moon_longitude = normalize(moon_longitude)
    nak = nakshatra_of(moon_longitude)
    first_lord = nak.lord
    elapsed_years = (nak.degrees_in_nak / NAK_SPAN) * VIMSHOTTARI_YEARS[first_lord]
    first_start = birth_utc - timedelta(days=elapsed_years * year_length_days)

    horizon = birth_utc + timedelta(days=121 * year_length_days)
    mahas: List[DashaPeriod] = []
    start_idx = VIMSHOTTARI_ORDER.index(first_lord)
    cursor = first_start
    k = 0
    # Emit Mahadashas until the timeline comfortably covers a full lifetime.
    while cursor < horizon:
        lord = VIMSHOTTARI_ORDER[(start_idx + k) % 9]
        maha_days = VIMSHOTTARI_YEARS[lord] * year_length_days
        maha = _build_period(lord, cursor, maha_days, 1, depth)
        mahas.append(maha)
        cursor = maha.end
        k += 1
    return mahas


def chart_vimshottari(
    chart,
    depth: int = 4,
    year_length_days: float = DEFAULT_YEAR_DAYS,
) -> List[DashaPeriod]:
    """Convenience: Vimshottari dasha straight from a Phase-1 :class:`Chart`.

    Uses the chart's (ayanamsa-specific) Moon longitude and birth instant.
    """
    return vimshottari_dasha(
        chart.planets["Moon"].longitude,
        chart.birth.to_utc(),
        depth=depth,
        year_length_days=year_length_days,
    )


def dasha_at(periods: List[DashaPeriod], when: datetime) -> List[DashaPeriod]:
    """Return the active chain ``[Maha, Antar, Pratyantar, Sookshma]`` at ``when``.

    Descends only as deep as the tree was built. Returns ``[]`` if ``when`` is
    outside the generated span.
    """
    if when.tzinfo is None:
        raise ValueError("`when` must be timezone-aware")
    chain: List[DashaPeriod] = []
    level = periods
    while level:
        active: Optional[DashaPeriod] = next(
            (p for p in level if p.start <= when < p.end), None
        )
        if active is None:
            break
        chain.append(active)
        level = list(active.children)
    return chain
