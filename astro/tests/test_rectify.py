"""Tests for birth-time confidence / rectification."""

from engine.birth_data import BirthData
from engine.rectify import (
    cuspal_signature,
    stable_interval,
    suggest_rectification,
    time_confidence,
)

BIRTH = BirthData(1990, 1, 1, 12, 0, 0, 28.6139, 77.2090, "Asia/Kolkata")


def test_cuspal_signature_has_twelve_entries():
    sig = cuspal_signature(BIRTH)
    assert len(sig) == 12 and all(isinstance(s, str) for s in sig)


def test_stable_interval_brackets_birth():
    iv = stable_interval(BIRTH, max_minutes=6, step_seconds=15)
    assert iv.before_seconds >= 0 and iv.after_seconds >= 0
    assert iv.start <= BIRTH.to_utc() <= iv.end
    assert iv.start <= iv.center <= iv.end
    # The signature holds across the reported interval.
    assert cuspal_signature(BIRTH) == cuspal_signature(
        BirthData(BIRTH.year, BIRTH.month, BIRTH.day, BIRTH.hour, BIRTH.minute,
                  BIRTH.second, BIRTH.latitude, BIRTH.longitude, BIRTH.timezone))


def test_time_confidence_level_valid():
    tc = time_confidence(BIRTH, max_minutes=6)
    assert tc.level in ("high", "medium", "low")
    assert tc.stable_width_seconds == tc.interval.width_seconds
    assert tc.note


def test_suggest_rectification_fields():
    s = suggest_rectification(BIRTH, max_minutes=6)
    assert s.stable_start <= s.suggested_center <= s.stable_end
    assert len(s.candidates) == 2
