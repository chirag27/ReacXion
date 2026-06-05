"""House (bhava) significations and karakas as structured, queryable data.

This is reference data the agent layer can retrieve — deliberately codified
rather than left to an LLM. ``BHAVA`` holds, per house, its Sanskrit name, the
chara/sthira karaka-style significator planet(s), and the life areas it governs.

Bhava karakas follow the classical Parashari assignment. Several houses have
more than one karaka; the primary is listed first.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class Bhava:
    number: int
    name: str                     # Sanskrit bhava name
    karakas: Tuple[str, ...]      # significator graha(s), primary first
    significations: Tuple[str, ...]


BHAVA: Dict[int, Bhava] = {
    1: Bhava(1, "Tanu", ("Sun",),
             ("self", "body", "appearance", "vitality", "personality", "head")),
    2: Bhava(2, "Dhana", ("Jupiter",),
             ("wealth", "family", "speech", "food", "face", "accumulated assets")),
    3: Bhava(3, "Sahaja", ("Mars",),
             ("siblings", "courage", "effort", "communication", "short journeys",
              "skills")),
    4: Bhava(4, "Sukha", ("Moon", "Mars"),
             ("mother", "home", "property", "vehicles", "happiness",
              "education", "heart")),
    5: Bhava(5, "Putra", ("Jupiter",),
             ("children", "intellect", "purva-punya (merit)", "romance",
              "speculation", "mantra")),
    6: Bhava(6, "Ari", ("Mars", "Saturn"),
             ("enemies", "disease", "debts", "obstacles", "service",
              "competition")),
    7: Bhava(7, "Yuvati", ("Venus",),
             ("spouse", "marriage", "partnerships", "business", "trade")),
    8: Bhava(8, "Randhra", ("Saturn",),
             ("longevity", "death", "transformation", "inheritance", "occult",
              "sudden events")),
    9: Bhava(9, "Dharma", ("Jupiter", "Sun"),
             ("father", "fortune", "dharma", "guru", "higher learning",
              "long journeys", "luck")),
    10: Bhava(10, "Karma", ("Mercury", "Jupiter", "Sun", "Saturn"),
              ("career", "status", "authority", "action", "fame", "profession")),
    11: Bhava(11, "Labha", ("Jupiter",),
              ("gains", "income", "elder siblings", "friends", "aspirations",
               "fulfilment of desires")),
    12: Bhava(12, "Vyaya", ("Saturn",),
              ("loss", "expenditure", "moksha", "foreign lands", "isolation",
               "bed pleasures", "sleep")),
}


def significations(house: int) -> Tuple[str, ...]:
    """Life areas governed by ``house`` (1..12)."""
    return BHAVA[house].significations


def karakas(house: int) -> Tuple[str, ...]:
    """Significator graha(s) of ``house``, primary first."""
    return BHAVA[house].karakas


def houses_signifying(keyword: str) -> List[int]:
    """Houses whose significations contain ``keyword`` (case-insensitive substring)."""
    k = keyword.lower()
    return [h for h, b in BHAVA.items()
            if any(k in s.lower() for s in b.significations)]
