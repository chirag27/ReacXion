"""Nakshatra and pada resolution.

Pure arithmetic on a sidereal longitude — deliberately free of any ephemeris
dependency so it can be unit-tested in isolation and reused by the KP module.
"""

from __future__ import annotations

from dataclasses import dataclass

from .constants import NAK_SPAN, PADA_SPAN, NAKSHATRA_NAMES, VIMSHOTTARI_ORDER


@dataclass(frozen=True)
class NakshatraInfo:
    """Where a longitude falls within the 27-fold nakshatra division."""

    index: int          # 0..26
    name: str
    lord: str           # star lord (Vimshottari lord of the nakshatra)
    pada: int           # 1..4
    degrees_in_nak: float  # offset from the start of the nakshatra (0..13°20')


def normalize(longitude: float) -> float:
    """Wrap a longitude into [0, 360)."""
    return longitude % 360.0


def nakshatra_of(longitude: float) -> NakshatraInfo:
    """Resolve the nakshatra, its lord, and the pada for a sidereal longitude.

    The nakshatra lord follows the Vimshottari order starting at Ketu for
    Ashwini, so it is simply ``VIMSHOTTARI_ORDER[index % 9]``.
    """
    lon = normalize(longitude)
    index = int(lon // NAK_SPAN)
    # Guard against floating point landing exactly on 360.0 -> index 27.
    if index >= 27:
        index = 26
    degrees_in_nak = lon - index * NAK_SPAN
    pada = int(degrees_in_nak // PADA_SPAN) + 1
    if pada > 4:
        pada = 4
    return NakshatraInfo(
        index=index,
        name=NAKSHATRA_NAMES[index],
        lord=VIMSHOTTARI_ORDER[index % 9],
        pada=pada,
        degrees_in_nak=degrees_in_nak,
    )
