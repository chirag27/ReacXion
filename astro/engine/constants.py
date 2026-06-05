"""Static astrological constants.

This module is pure data — no computation, no I/O, and crucially no
``swisseph`` import. Everything here is fixed by tradition (sign rulerships,
the 27 nakshatras, the Vimshottari dasha scheme) and is shared by the pure-math
modules (:mod:`engine.nakshatra`, :mod:`engine.kp_sublord`) and the ephemeris
wrapper.
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# Angular spans (degrees)
# --------------------------------------------------------------------------- #
CIRCLE = 360.0
SIGN_SPAN = 30.0                      # 12 signs
NAK_SPAN = CIRCLE / 27.0             # 13°20'  (exactly 800 arcminutes)
PADA_SPAN = NAK_SPAN / 4.0           # 3°20'   (exactly 200 arcminutes)

# --------------------------------------------------------------------------- #
# Signs (rashis) and their rulers
# --------------------------------------------------------------------------- #
SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Classical (Parashari / KP) seven-planet rulership — no outer planets.
SIGN_LORDS = [
    "Mars",     # Aries
    "Venus",    # Taurus
    "Mercury",  # Gemini
    "Moon",     # Cancer
    "Sun",      # Leo
    "Mercury",  # Virgo
    "Venus",    # Libra
    "Mars",     # Scorpio
    "Jupiter",  # Sagittarius
    "Saturn",   # Capricorn
    "Saturn",   # Aquarius
    "Jupiter",  # Pisces
]

# --------------------------------------------------------------------------- #
# 27 Nakshatras
# --------------------------------------------------------------------------- #
NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada",
    "Revati",
]
assert len(NAKSHATRA_NAMES) == 27

# --------------------------------------------------------------------------- #
# Vimshottari Dasha
#
# The nine dasha lords in their fixed cyclic order (starting from Ketu, the
# lord of Ashwini) together with their period lengths in years. The total is
# 120 years. This ordering drives BOTH the nakshatra (star) lord cycle and the
# KP sub-lord subdivision, so it is defined exactly once here.
# --------------------------------------------------------------------------- #
VIMSHOTTARI_ORDER = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
]

VIMSHOTTARI_YEARS = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17,
}
VIMSHOTTARI_TOTAL = 120
assert sum(VIMSHOTTARI_YEARS.values()) == VIMSHOTTARI_TOTAL

# --------------------------------------------------------------------------- #
# The nine grahas
#
# Rahu and Ketu are the MEAN lunar nodes (per the spec). Ketu is not queried
# from the ephemeris; it is derived as Rahu + 180°. The ``swe_id`` is resolved
# lazily inside engine.ephemeris to keep this module swisseph-free.
# --------------------------------------------------------------------------- #
GRAHA_NAMES = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
    "Rahu", "Ketu",
]

# --------------------------------------------------------------------------- #
# Ayanamsa and house-system configuration keys.
# The mapping to swisseph constants lives in engine.ephemeris.
# --------------------------------------------------------------------------- #
AYANAMSA_LAHIRI = "lahiri"          # Vedic / Parashari standard
AYANAMSA_KP = "kp"                  # Krishnamurti ayanamsa

HOUSE_WHOLE_SIGN = "whole_sign"     # Parashari
HOUSE_PLACIDUS = "placidus"         # KP

# Convenience presets: (ayanamsa, house_system)
PRESET_VEDIC = (AYANAMSA_LAHIRI, HOUSE_WHOLE_SIGN)
PRESET_KP = (AYANAMSA_KP, HOUSE_PLACIDUS)
