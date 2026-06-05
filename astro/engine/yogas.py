"""Yoga detection — codified, deterministic, fully traceable.

Each detector returns a :class:`Yoga` carrying the exact placements that
triggered it (and, where relevant, the cancellation that fired), so the agent
layer can cite *why* a yoga is present rather than asserting it. No LLM, no
vector store — pure structural rules over the rasi chart.

Covered: Pancha Mahapurusha (Ruchaka/Bhadra/Hamsa/Malavya/Sasa), Gaja Kesari,
Budha-Aditya, Chandra-Mangala, Neecha Bhanga Raja Yoga, Kemadruma, kendra-
trikona Raja Yogas, and Dhana Yogas.

Operates on any object exposing ``planets[name].longitude`` and ``ascendant``,
so it works on a full :class:`Chart` or a lightweight stand-in.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .aspects import graha_drishti
from .constants import SIGN_LORDS, SIGN_NAMES
from .dignity import EXALTATION, planet_dignity
from .houses import HouseChart, sign_index

# Planet exalted in each sign (inverse of the exaltation table).
_EXALTED_IN_SIGN = {sign: planet for planet, (sign, _deg) in EXALTATION.items()}

MAHAPURUSHA = {
    "Mars": "Ruchaka", "Mercury": "Bhadra", "Jupiter": "Hamsa",
    "Venus": "Malavya", "Saturn": "Sasa",
}


@dataclass(frozen=True)
class Yoga:
    name: str
    category: str                 # Pancha Mahapurusha / Raja / Dhana / Lunar / ...
    planets: Tuple[str, ...]
    description: str
    triggers: Tuple[str, ...]     # structured, human-readable trigger statements
    cancellation: str = ""        # populated for Neecha Bhanga etc.


# --------------------------------------------------------------------------- #
# Relationship helpers
# --------------------------------------------------------------------------- #
def _kendra_from(a_sign: int, b_sign: int) -> int:
    """House of sign ``a`` counted from sign ``b`` (1..12)."""
    return ((a_sign - b_sign) % 12) + 1


def _mutual_aspect(drishti, a: str, b: str) -> bool:
    return b in drishti[a].aspected_planets and a in drishti[b].aspected_planets


def _exchange(signs: Dict[str, int], a: str, b: str) -> bool:
    """Parivartana: each planet sits in a sign ruled by the other."""
    return (SIGN_LORDS[signs[a]] == b) and (SIGN_LORDS[signs[b]] == a)


def _association(signs, drishti, a: str, b: str) -> str:
    """Return the sambandha type between two planets, or '' if none."""
    if a == b:
        return ""
    if signs[a] == signs[b]:
        return "conjunction"
    if _mutual_aspect(drishti, a, b):
        return "mutual aspect"
    if _exchange(signs, a, b):
        return "exchange (parivartana)"
    return ""


# --------------------------------------------------------------------------- #
# Individual detectors
# --------------------------------------------------------------------------- #
def _pancha_mahapurusha(hc, dignities) -> List[Yoga]:
    out = []
    for planet, yoga_name in MAHAPURUSHA.items():
        dig = dignities[planet]
        house = hc.house_of_planet[planet]
        if dig.state in ("own", "moolatrikona", "exalted") and house in (1, 4, 7, 10):
            out.append(Yoga(
                name=f"{yoga_name} Yoga",
                category="Pancha Mahapurusha",
                planets=(planet,),
                description=(
                    f"{planet} {dig.state} in {dig.sign} occupies kendra "
                    f"house {house} from lagna"),
                triggers=(
                    f"{planet} is {dig.state} (in {dig.sign})",
                    f"{planet} is in kendra house {house}"),
            ))
    return out


def _gaja_kesari(signs) -> List[Yoga]:
    h = _kendra_from(signs["Jupiter"], signs["Moon"])
    if h in (1, 4, 7, 10):
        return [Yoga(
            name="Gaja Kesari Yoga",
            category="Lunar",
            planets=("Jupiter", "Moon"),
            description=f"Jupiter is in kendra (house {h}) from the Moon",
            triggers=(
                f"Jupiter in {SIGN_NAMES[signs['Jupiter']]}",
                f"Moon in {SIGN_NAMES[signs['Moon']]}",
                f"Jupiter is {h}th from the Moon"),
        )]
    return []


def _conjunction_yoga(signs, a, b, name, category, desc) -> List[Yoga]:
    if signs[a] == signs[b]:
        return [Yoga(
            name=name, category=category, planets=(a, b),
            description=desc.format(sign=SIGN_NAMES[signs[a]]),
            triggers=(f"{a} and {b} conjoin in {SIGN_NAMES[signs[a]]}",),
        )]
    return []


def _kendra_trikona_raja(hc, signs, drishti) -> List[Yoga]:
    out = []
    kendra_lords = {hc.house_lord[h]: h for h in (1, 4, 7, 10)}
    trikona_lords = {hc.house_lord[h]: h for h in (1, 5, 9)}
    seen = set()
    for kl, kh in kendra_lords.items():
        for tl, th in trikona_lords.items():
            if kl == tl:
                continue
            pair = frozenset((kl, tl))
            if pair in seen:
                continue
            link = _association(signs, drishti, kl, tl)
            if link:
                seen.add(pair)
                out.append(Yoga(
                    name="Raja Yoga",
                    category="Raja",
                    planets=tuple(sorted((kl, tl))),
                    description=(
                        f"kendra lord {kl} (house {kh}) and trikona lord {tl} "
                        f"(house {th}) linked by {link}"),
                    triggers=(
                        f"{kl} rules kendra {kh}",
                        f"{tl} rules trikona {th}",
                        f"link: {link}"),
                ))
    return out


def _dhana_yoga(hc, signs, drishti) -> List[Yoga]:
    out = []
    wealth_lords = {hc.house_lord[h]: h for h in (2, 11)}
    partner_lords = {h: hc.house_lord[h] for h in (1, 5, 9, 2, 11)}
    seen = set()
    for wl, wh in wealth_lords.items():
        for ph, pl in partner_lords.items():
            if wl == pl:
                continue
            pair = frozenset((wl, pl))
            if pair in seen:
                continue
            link = _association(signs, drishti, wl, pl)
            if link:
                seen.add(pair)
                out.append(Yoga(
                    name="Dhana Yoga",
                    category="Dhana",
                    planets=tuple(sorted((wl, pl))),
                    description=(
                        f"wealth lord {wl} (house {wh}) linked with house-{ph} "
                        f"lord {pl} by {link}"),
                    triggers=(
                        f"{wl} rules wealth house {wh}",
                        f"{pl} rules house {ph}",
                        f"link: {link}"),
                ))
    return out


# --------------------------------------------------------------------------- #
# Public entry point
# --------------------------------------------------------------------------- #
def detect_yogas(chart) -> List[Yoga]:
    """Detect all supported yogas in ``chart`` (use the Vedic/Lahiri chart)."""
    longs = {name: p.longitude for name, p in chart.planets.items()}
    signs = {name: sign_index(lon) for name, lon in longs.items()}
    hc = HouseChart.from_positions(longs, chart.ascendant)
    dignities = {name: planet_dignity(name, lon) for name, lon in longs.items()}
    drishti = graha_drishti(chart)

    yogas: List[Yoga] = []
    yogas += _pancha_mahapurusha(hc, dignities)
    yogas += _gaja_kesari(signs)
    yogas += _conjunction_yoga(
        signs, "Sun", "Mercury", "Budha-Aditya Yoga", "Solar",
        "Sun and Mercury conjoin in {sign} (intelligence)")
    yogas += _conjunction_yoga(
        signs, "Moon", "Mars", "Chandra-Mangala Yoga", "Dhana",
        "Moon and Mars conjoin in {sign} (wealth through enterprise)")
    yogas += neecha_bhanga(hc, signs, dignities, drishti)
    yogas += kemadruma(hc, signs)
    yogas += _kendra_trikona_raja(hc, signs, drishti)
    yogas += _dhana_yoga(hc, signs, drishti)
    return yogas


def neecha_bhanga(hc, signs, dignities, drishti) -> List[Yoga]:
    """Neecha Bhanga Raja Yoga: cancellation of a debilitation."""
    out = []
    moon_sign = signs["Moon"]
    asc_sign = hc.asc_sign
    for planet, dig in dignities.items():
        if not dig.is_debilitated:
            continue
        debil_sign = signs[planet]
        dispositor = SIGN_LORDS[debil_sign]
        exalted_planet = _EXALTED_IN_SIGN.get(debil_sign)

        reasons = []
        # (a) dispositor in a kendra from lagna or Moon
        if dispositor in signs:
            if _kendra_from(signs[dispositor], asc_sign) in (1, 4, 7, 10):
                reasons.append(f"dispositor {dispositor} is in a kendra from lagna")
            if _kendra_from(signs[dispositor], moon_sign) in (1, 4, 7, 10):
                reasons.append(f"dispositor {dispositor} is in a kendra from the Moon")
        # (b) the planet exalted in this sign sits in a kendra from lagna/Moon
        if exalted_planet and exalted_planet in signs:
            if _kendra_from(signs[exalted_planet], asc_sign) in (1, 4, 7, 10):
                reasons.append(
                    f"{exalted_planet} (exalted in {SIGN_NAMES[debil_sign]}) "
                    f"is in a kendra from lagna")
        # (c) dispositor or exaltation-lord conjoins/aspects the debilitated planet
        for other in filter(None, (dispositor, exalted_planet)):
            if other in signs and _association(signs, drishti, planet, other):
                reasons.append(
                    f"{other} is associated with debilitated {planet} "
                    f"({_association(signs, drishti, planet, other)})")

        if reasons:
            out.append(Yoga(
                name="Neecha Bhanga Raja Yoga",
                category="Raja",
                planets=(planet,),
                description=(
                    f"{planet} is debilitated in {dig.sign} but the "
                    f"debilitation is cancelled"),
                triggers=(f"{planet} debilitated in {dig.sign}",),
                cancellation="; ".join(dict.fromkeys(reasons)),
            ))
    return out


def kemadruma(hc, signs) -> List[Yoga]:
    """Kemadruma: the Moon is isolated — 2nd and 12th from it empty, no conjunction.

    Considers only the five non-luminary, non-nodal grahas (Mars, Mercury,
    Jupiter, Venus, Saturn) as 'company', per the common convention.
    """
    moon_sign = signs["Moon"]
    company = ("Mars", "Mercury", "Jupiter", "Venus", "Saturn")
    neighbours_and_conj = set()
    for p in company:
        rel = _kendra_from(signs[p], moon_sign)   # 1=conj, 2=2nd, 12=12th
        if rel in (1, 2, 12):
            neighbours_and_conj.add(p)
    if not neighbours_and_conj:
        return [Yoga(
            name="Kemadruma Yoga",
            category="Lunar",
            planets=("Moon",),
            description=(
                "the Moon has no graha in the 2nd or 12th from it and no "
                "conjunction (isolated Moon)"),
            triggers=(
                f"Moon in {SIGN_NAMES[moon_sign]}",
                "2nd and 12th houses from the Moon are empty of "
                "Mars/Mercury/Jupiter/Venus/Saturn"),
        )]
    return []
