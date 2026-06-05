"""KP (Krishnamurti Paddhati) sub-lord system.

Each of the 27 nakshatras (13°20' = 800') is subdivided into 9 *subs* whose
widths are proportional to the Vimshottari dasha years, laid out in Vimshottari
order beginning with the nakshatra's own (star) lord. For any longitude this
yields the three-level KP signature::

    sign lord  ->  star (nakshatra) lord  ->  sub lord

The "249" of the title is the number of distinct segments the zodiac is cut
into once the 9x27 = 243 sub-divisions are *additionally* split wherever a sign
(rashi) boundary falls inside a sub. :func:`build_kp_249_table` materialises
that table; the engine itself only needs the per-longitude resolver
:func:`resolve`.

Pure arithmetic — no ephemeris dependency.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .constants import (
    CIRCLE,
    NAK_SPAN,
    SIGN_LORDS,
    SIGN_SPAN,
    VIMSHOTTARI_ORDER,
    VIMSHOTTARI_TOTAL,
    VIMSHOTTARI_YEARS,
)
from .nakshatra import normalize


# Width of each sub *within a nakshatra*, in degrees, keyed by the sub's lord.
# Proportional to that lord's Vimshottari years.
SUB_WIDTH = {
    lord: VIMSHOTTARI_YEARS[lord] / VIMSHOTTARI_TOTAL * NAK_SPAN
    for lord in VIMSHOTTARI_ORDER
}


@dataclass(frozen=True)
class KPLords:
    """The KP three-level lordship of a single point on the zodiac."""

    sign_lord: str
    star_lord: str   # nakshatra lord
    sub_lord: str


@dataclass(frozen=True)
class SubSegment:
    """One contiguous segment of the 249-fold KP table."""

    start: float          # inclusive, degrees [0, 360)
    end: float            # exclusive, degrees (0, 360]
    sign_lord: str
    star_lord: str
    sub_lord: str


def _sign_lord(longitude: float) -> str:
    return SIGN_LORDS[int(longitude // SIGN_SPAN) % 12]


def resolve(longitude: float) -> KPLords:
    """Return the sign / star / sub lords for a sidereal longitude.

    Boundary convention (KP standard): a point lying exactly on a sub boundary
    belongs to the *next* sub.
    """
    lon = normalize(longitude)
    nak_index = int(lon // NAK_SPAN)
    if nak_index >= 27:
        nak_index = 26

    star_lord = VIMSHOTTARI_ORDER[nak_index % 9]
    pos_in_nak = lon - nak_index * NAK_SPAN

    # Walk the 9 subs in Vimshottari order starting at the star lord.
    start_idx = nak_index % 9
    cumulative = 0.0
    sub_lord = VIMSHOTTARI_ORDER[(start_idx + 8) % 9]  # default: last sub
    for k in range(9):
        lord = VIMSHOTTARI_ORDER[(start_idx + k) % 9]
        cumulative += SUB_WIDTH[lord]
        # Tiny epsilon so floating-point round-off at a boundary does not push
        # a point that is *meant* to be at the boundary into the wrong sub.
        if pos_in_nak < cumulative - 1e-9:
            sub_lord = lord
            break

    return KPLords(
        sign_lord=_sign_lord(lon),
        star_lord=star_lord,
        sub_lord=sub_lord,
    )


def build_kp_249_table() -> List[SubSegment]:
    """Construct the full KP sub table, split at sign boundaries.

    Returns the 249 ordered segments spanning the whole zodiac. Verifying that
    ``len(build_kp_249_table()) == 249`` is a useful structural sanity check on
    the subdivision arithmetic.
    """
    # 1. Raw sub boundaries (243 of them) plus the 12 sign cusps, merged.
    raw_boundaries = {0.0, CIRCLE}
    for nak_index in range(27):
        nak_start = nak_index * NAK_SPAN
        start_idx = nak_index % 9
        cumulative = 0.0
        for k in range(9):
            lord = VIMSHOTTARI_ORDER[(start_idx + k) % 9]
            cumulative += SUB_WIDTH[lord]
            raw_boundaries.add(round(nak_start + cumulative, 9))
    for s in range(12):
        raw_boundaries.add(round(s * SIGN_SPAN, 9))

    ordered = sorted(b for b in raw_boundaries if 0.0 <= b < CIRCLE)

    segments: List[SubSegment] = []
    for i, start in enumerate(ordered):
        end = ordered[i + 1] if i + 1 < len(ordered) else CIRCLE
        # Sample the midpoint to label the segment unambiguously.
        mid = (start + end) / 2.0
        lords = resolve(mid)
        segments.append(
            SubSegment(
                start=start,
                end=end,
                sign_lord=lords.sign_lord,
                star_lord=lords.star_lord,
                sub_lord=lords.sub_lord,
            )
        )
    return segments
