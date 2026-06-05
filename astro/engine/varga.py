"""Divisional charts (vargas), data-driven.

Each varga Dn divides a 30° sign into ``n`` equal parts (except D30, which uses
the classical unequal Trimsamsa bands) and maps each part to a result sign via
a per-varga rule. Adding a new varga is a one-line entry in :data:`VARGAS`.

The rules below follow the standard Brihat Parashara Hora Shastra (BPHS)
definitions. Several vargas (notably D16, D20, D24, D27, D40, D45, D60) have
competing conventions across authors; this module encodes the common BPHS
variant. Treat the golden charts as the source of truth and adjust a rule here
if your reference tool (Jagannatha Hora) uses a different convention — the
data-driven design makes that a localized change.

Pure arithmetic; no ephemeris dependency. Result is the *sign placement* of
each body in the divisional chart (what JHora's varga charts display).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from .constants import SIGN_LORDS, SIGN_NAMES, SIGN_SPAN
from .nakshatra import normalize

# Modality of a sign: 0 = movable (chara), 1 = fixed (sthira), 2 = dual.
def _modality(sign: int) -> int:
    return sign % 3


# Element of a sign: 0 = fire, 1 = earth, 2 = air, 3 = water.
def _element(sign: int) -> int:
    return sign % 4


def _is_odd_sign(sign: int) -> bool:
    """Aries, Gemini, ... are 'odd' signs (1-based odd => 0-based even)."""
    return sign % 2 == 0


# --------------------------------------------------------------------------- #
# Per-varga rules: (sign 0..11, part 0..n-1) -> result sign 0..11
# --------------------------------------------------------------------------- #
def _d1(sign: int, part: int) -> int:
    return sign


def _d2_hora(sign: int, part: int) -> int:
    # Parashari Hora: only Leo (Sun) or Cancer (Moon).
    leo, cancer = 4, 3
    if _is_odd_sign(sign):
        return leo if part == 0 else cancer
    return cancer if part == 0 else leo


def _d3_drekkana(sign: int, part: int) -> int:
    # Same sign, 5th, or 9th (the trine).
    return (sign + 4 * part) % 12


def _d4(sign: int, part: int) -> int:
    # 1st, 4th, 7th, 10th (the kendras).
    return (sign + 3 * part) % 12


def _d7_saptamsa(sign: int, part: int) -> int:
    start = sign if _is_odd_sign(sign) else sign + 6
    return (start + part) % 12


def _d9_navamsa(sign: int, part: int) -> int:
    # Movable from itself, fixed from the 9th, dual from the 5th.
    start = sign + (0, 8, 4)[_modality(sign)]
    return (start + part) % 12


def _d10_dasamsa(sign: int, part: int) -> int:
    start = sign if _is_odd_sign(sign) else sign + 8
    return (start + part) % 12


def _d12_dwadasamsa(sign: int, part: int) -> int:
    return (sign + part) % 12


def _d16(sign: int, part: int) -> int:
    # Movable from Aries, fixed from Leo, dual from Sagittarius.
    start = (0, 4, 8)[_modality(sign)]
    return (start + part) % 12


def _d20(sign: int, part: int) -> int:
    # Movable from Aries, fixed from Sagittarius, dual from Leo.
    start = (0, 8, 4)[_modality(sign)]
    return (start + part) % 12


def _d24(sign: int, part: int) -> int:
    # Odd signs from Leo, even signs from Cancer.
    start = 4 if _is_odd_sign(sign) else 3
    return (start + part) % 12


def _d27(sign: int, part: int) -> int:
    # By element: fire from Aries, earth from Cancer, air from Libra, water Cap.
    start = _element(sign) * 3
    return (start + part) % 12


def _d40(sign: int, part: int) -> int:
    # Odd signs from Aries, even signs from Libra.
    start = 0 if _is_odd_sign(sign) else 6
    return (start + part) % 12


def _d45(sign: int, part: int) -> int:
    # Movable from Aries, fixed from Leo, dual from Sagittarius (like D16).
    start = (0, 4, 8)[_modality(sign)]
    return (start + part) % 12


def _d60(sign: int, part: int) -> int:
    return (sign + part) % 12


# D30 Trimsamsa: 5 unequal lordship bands per sign. Each band maps to a fixed
# result sign (the lord's relevant rashi), and the assignment differs between
# odd and even signs. Bands are (upper_degree_exclusive, result_sign_index).
_D30_ODD = [(5, 0), (10, 10), (18, 8), (25, 2), (30, 6)]
#            Mars→Aries  Sat→Aqu  Jup→Sag  Merc→Gem  Ven→Libra
_D30_EVEN = [(5, 1), (12, 5), (20, 11), (25, 9), (30, 7)]
#            Ven→Taurus Merc→Virgo Jup→Pisces Sat→Cap Mars→Scorpio


def _d30_trimsamsa(degree_in_sign: float, sign: int) -> int:
    """Classical Trimsamsa: 5 unequal lordship bands; even signs differ."""
    bands = _D30_ODD if _is_odd_sign(sign) else _D30_EVEN
    for upper, result_sign in bands:
        if degree_in_sign < upper:
            return result_sign
    return bands[-1][1]


@dataclass(frozen=True)
class Varga:
    code: str
    name: str
    divisions: int
    rule: Optional[Callable[[int, int], int]] = None       # equal-part rule
    special: Optional[Callable[[float, int], int]] = None  # (deg_in_sign, sign)


VARGAS: Dict[str, Varga] = {v.code: v for v in [
    Varga("D1", "Rashi", 1, _d1),
    Varga("D2", "Hora", 2, _d2_hora),
    Varga("D3", "Drekkana", 3, _d3_drekkana),
    Varga("D4", "Chaturthamsa", 4, _d4),
    Varga("D7", "Saptamsa", 7, _d7_saptamsa),
    Varga("D9", "Navamsa", 9, _d9_navamsa),
    Varga("D10", "Dasamsa", 10, _d10_dasamsa),
    Varga("D12", "Dwadasamsa", 12, _d12_dwadasamsa),
    Varga("D16", "Shodasamsa", 16, _d16),
    Varga("D20", "Vimsamsa", 20, _d20),
    Varga("D24", "Chaturvimsamsa", 24, _d24),
    Varga("D27", "Bhamsa", 27, _d27),
    Varga("D30", "Trimsamsa", 30, special=_d30_trimsamsa),
    Varga("D40", "Khavedamsa", 40, _d40),
    Varga("D45", "Akshavedamsa", 45, _d45),
    Varga("D60", "Shashtiamsa", 60, _d60),
]}


def varga_sign_index(longitude: float, code: str) -> int:
    """Return the 0..11 sign index of ``longitude`` in divisional chart ``code``."""
    try:
        varga = VARGAS[code]
    except KeyError:
        raise ValueError(
            f"unknown varga {code!r}; known: {sorted(VARGAS)}"
        ) from None

    lon = normalize(longitude)
    sign = int(lon // SIGN_SPAN)
    degree_in_sign = lon - sign * SIGN_SPAN

    if varga.special is not None:
        return varga.special(degree_in_sign, sign) % 12

    part = int(degree_in_sign // (SIGN_SPAN / varga.divisions))
    if part >= varga.divisions:        # guard floating edge at 30.0
        part = varga.divisions - 1
    return varga.rule(sign, part) % 12


def varga_sign(longitude: float, code: str) -> str:
    return SIGN_NAMES[varga_sign_index(longitude, code)]


@dataclass(frozen=True)
class VargaChart:
    code: str
    name: str
    ascendant_sign: str
    planet_signs: Dict[str, str]       # graha name -> sign name
    planet_sign_lords: Dict[str, str]  # graha name -> lord of its varga sign


def divisional_chart(chart, code: str) -> VargaChart:
    """Build the divisional chart ``code`` from a Phase-1 :class:`Chart`.

    Uses the D1 sidereal longitudes already computed (and thus the chart's
    ayanamsa). Returns sign placements for every graha and the ascendant.
    """
    varga = VARGAS[code]
    planet_signs: Dict[str, str] = {}
    planet_lords: Dict[str, str] = {}
    for name, p in chart.planets.items():
        idx = varga_sign_index(p.longitude, code)
        planet_signs[name] = SIGN_NAMES[idx]
        planet_lords[name] = SIGN_LORDS[idx]
    asc_idx = varga_sign_index(chart.ascendant, code)
    return VargaChart(
        code=code,
        name=varga.name,
        ascendant_sign=SIGN_NAMES[asc_idx],
        planet_signs=planet_signs,
        planet_sign_lords=planet_lords,
    )
