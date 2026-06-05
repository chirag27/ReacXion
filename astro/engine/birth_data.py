"""The :class:`BirthData` model and robust local-time -> UTC conversion.

Timezone handling is the single biggest source of wrong charts, so it is
isolated here and handled explicitly:

* IANA zone names (e.g. ``"Asia/Kolkata"``, ``"America/New_York"``) are
  resolved through :mod:`zoneinfo`, which knows the *historical* offsets and
  daylight-saving transitions for a given date — not just today's rule.
* A fixed numeric UTC offset in hours may be supplied instead, which is the
  safe choice for very old births or places where the IANA history is
  uncertain.
* Ambiguous wall-clock times (the hour repeated when clocks fall back) are
  disambiguated by the explicit ``fold`` flag.
* Non-existent wall-clock times (the hour skipped when clocks spring forward)
  are detected and rejected loudly rather than silently producing a wrong UTC
  instant.

The model carries no ephemeris logic; it only knows how to produce a precise,
timezone-aware UTC :class:`~datetime.datetime`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, tzinfo
from typing import Optional, Union
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class TimezoneError(ValueError):
    """Raised when a local time cannot be unambiguously converted to UTC."""


@dataclass(frozen=True)
class BirthData:
    """A birth event: exact local civil time + place.

    Args:
        year, month, day: civil calendar date (proleptic Gregorian).
        hour, minute, second: exact local time of birth (24h clock).
        latitude: degrees, North positive (-90..90).
        longitude: degrees, East positive (-180..180).
        timezone: either an IANA zone name (``str``) or a fixed UTC offset in
            hours (``float``/``int``, e.g. ``5.5`` for IST).
        fold: 0 or 1, selecting the earlier/later instant for an ambiguous
            local time (clocks-fall-back hour). Ignored for fixed offsets.
        name: optional label for charts/tests.
    """

    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int
    latitude: float
    longitude: float
    timezone: Union[str, float]
    fold: int = 0
    name: str = ""

    # Cached resolved tzinfo (excluded from equality/repr noise).
    _tzinfo: tzinfo = field(default=None, init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not -90.0 <= self.latitude <= 90.0:
            raise ValueError(f"latitude out of range: {self.latitude}")
        if not -180.0 <= self.longitude <= 180.0:
            raise ValueError(f"longitude out of range: {self.longitude}")
        if self.fold not in (0, 1):
            raise ValueError(f"fold must be 0 or 1, got {self.fold}")
        # Validate the date/time components eagerly.
        try:
            datetime(self.year, self.month, self.day,
                     self.hour, self.minute, self.second)
        except ValueError as exc:
            raise ValueError(f"invalid date/time: {exc}") from exc

        object.__setattr__(self, "_tzinfo", self._resolve_tzinfo())

    # ------------------------------------------------------------------ #
    # Timezone resolution
    # ------------------------------------------------------------------ #
    def _resolve_tzinfo(self) -> tzinfo:
        tz = self.timezone
        if isinstance(tz, (int, float)):
            return timezone(timedelta(hours=float(tz)))
        if isinstance(tz, str):
            try:
                return ZoneInfo(tz)
            except ZoneInfoNotFoundError as exc:
                raise TimezoneError(
                    f"unknown IANA timezone {tz!r}; install 'tzdata' or pass a "
                    f"fixed offset in hours instead"
                ) from exc
        raise TimezoneError(
            f"timezone must be an IANA name or a numeric offset, got {tz!r}"
        )

    # ------------------------------------------------------------------ #
    # Conversion
    # ------------------------------------------------------------------ #
    def local_datetime(self) -> datetime:
        """The naive wall-clock time as an aware datetime in its own zone."""
        return datetime(
            self.year, self.month, self.day,
            self.hour, self.minute, self.second,
            tzinfo=self._tzinfo, fold=self.fold,
        )

    def to_utc(self) -> datetime:
        """Convert the local birth time to a timezone-aware UTC datetime.

        Raises:
            TimezoneError: if the wall-clock time does not exist in the given
                zone (a spring-forward gap).
        """
        local = self.local_datetime()

        # Detect a non-existent (skipped) local time. For such an instant the
        # round-trip local -> UTC -> local does not reproduce the original
        # wall-clock fields. Fixed offsets never have gaps, so this only fires
        # for IANA zones.
        if isinstance(self._tzinfo, ZoneInfo):
            roundtrip = local.astimezone(timezone.utc).astimezone(self._tzinfo)
            if (roundtrip.hour, roundtrip.minute, roundtrip.second) != (
                self.hour, self.minute, self.second
            ):
                raise TimezoneError(
                    f"local time {self.hour:02d}:{self.minute:02d}:"
                    f"{self.second:02d} on {self.year:04d}-{self.month:02d}-"
                    f"{self.day:02d} does not exist in {self.timezone!r} "
                    f"(daylight-saving spring-forward gap)"
                )

        return local.astimezone(timezone.utc)

    def utc_offset_hours(self) -> float:
        """The effective UTC offset (hours) actually applied to this birth."""
        offset = self.local_datetime().utcoffset() or timedelta(0)
        return offset.total_seconds() / 3600.0
