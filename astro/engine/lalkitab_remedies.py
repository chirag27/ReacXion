"""Lal Kitab remedies (upay / totkay), keyed to afflicted placements and rinas.

EDITION NOTE — the remedy texts follow the **1941 edition** as commonly
reproduced and are paraphrased canonical upay. They are reference data, not
prescriptions; many Lal Kitab remedies carry timing/quantity conditions in the
original that are not modelled here. Verify against a physical copy before use.

Pure logic over a :class:`LalKitabChart`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .lalkitab import LalKitabChart
from .lalkitab_debts import AFFLICTERS, Rina, detect_rinas

# Canonical per-planet remedies (paraphrased).
PLANET_REMEDIES: Dict[str, str] = {
    "Sun": "Offer water to the rising Sun; respect your father and elders; "
           "donate wheat and jaggery.",
    "Moon": "Keep a silver vessel; serve your mother; offer milk or water at a "
            "temple; do not accept milk as a gift.",
    "Mars": "Keep good relations with brothers; keep conduct and teeth clean; "
            "donate sweets.",
    "Mercury": "Keep cordial relations with sisters, daughters and aunts; feed "
               "green fodder to cows; donate green moong.",
    "Jupiter": "Apply a saffron/turmeric tilak; respect your guru and elders; "
               "donate gram dal and turmeric; water a peepal tree.",
    "Venus": "Honour your wife and women; keep a cow; offer curd and perfume; "
             "donate to young girls.",
    "Saturn": "Serve labourers and the needy; offer mustard oil; feed crows and "
              "fish; keep iron; light a lamp in the evening.",
    "Rahu": "Keep barley or a silver square; float a coconut in flowing water; "
            "feed dogs; avoid ivory items.",
    "Ketu": "Feed and care for dogs; donate a black-and-white blanket; keep "
            "good relations with sons; bathe with sesame.",
}

# Canonical per-rina remedies, keyed by the rina's Sanskrit name.
RINA_REMEDIES: Dict[str, str] = {
    "Pitra Rin": "Honour and remember ancestors; on Amavasya donate food/clothes "
                 "on their behalf; offer water to forefathers.",
    "Matri Rin": "Serve your mother and elderly women; donate milk and rice; "
                 "keep silver.",
    "Stri Rin": "Respect your wife and women; donate to married women; keep "
                "domestic harmony.",
    "Bahin-Beti Rin": "Maintain good relations with and gift sisters and "
                      "daughters; feed cows green fodder.",
    "Santan Rin": "Donate to and feed children; water a peepal tree.",
    "Atma Rin": "Maintain personal charity and conduct; also do the remedy of "
                "the afflicting planet.",
}


@dataclass(frozen=True)
class Remedy:
    target: str        # planet name or rina sanskrit name
    kind: str          # "planet" | "rina"
    reason: str
    text: str


def _afflicted_planets(lk: LalKitabChart) -> List[str]:
    """Planets sharing a khana with an afflicter, or in the 'blind' state."""
    out = []
    for name, st in lk.states.items():
        with_aff = [p for p in st.companions if p in AFFLICTERS]
        if with_aff or st.state == "blind":
            out.append(name)
    return out


def remedies_for(
    lk: LalKitabChart,
    rinas: Optional[List[Rina]] = None,
) -> List[Remedy]:
    """Remedies keyed to detected rinas and afflicted/blind planets."""
    if rinas is None:
        rinas = detect_rinas(lk)

    out: List[Remedy] = []

    for rina in rinas:
        text = RINA_REMEDIES.get(rina.sanskrit)
        if text:
            out.append(Remedy(rina.sanskrit, "rina", rina.trigger, text))

    for planet in _afflicted_planets(lk):
        st = lk.states[planet]
        reason = (f"{planet} is {st.state}"
                  + (f" with {', '.join(p for p in st.companions if p in AFFLICTERS)}"
                     if any(p in AFFLICTERS for p in st.companions) else ""))
        out.append(Remedy(planet, "planet", reason, PLANET_REMEDIES[planet]))

    return out
