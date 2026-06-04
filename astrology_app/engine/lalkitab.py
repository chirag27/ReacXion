"""
Lal Kitab analysis layer.

Takes a Chart produced by ephemeris.build_chart() and returns:
  - the Lal Kitab reading for each planet (by house),
  - which planets are flagged malefic (need a remedy),
  - the matching remedies (general + house-specific).

Data lives in ../data/lalkitab/*.json so it can be edited without touching code
and reused directly by the Flutter app.
"""

from __future__ import annotations

import json
import os

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "lalkitab")


def _load(name):
    with open(os.path.join(_DATA_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)


REFERENCE = _load("reference.json")
PLANET_IN_HOUSE = _load("planet_in_house.json")
REMEDIES = _load("remedies.json")

_LAL_PLANETS = REFERENCE["planets"]  # excludes Ascendant


def _is_malefic(planet, chart):
    """
    Decide whether a planet is malefic in this chart (per reference.json rules).
    Returns (bool, reason).
    """
    p = chart.planets[planet]
    house = p.house

    # 1) Polarity from the planet-in-house table.
    entry = PLANET_IN_HOUSE.get(planet, {}).get(str(house))
    if entry and entry["polarity"] == "malefic":
        return True, f"{planet} in house {house} is malefic in Lal Kitab"

    # 2) Conjunction with an enemy planet (same house).
    enemies = set(REFERENCE["friendship"][planet]["enemies"])
    for other in _LAL_PLANETS:
        if other != planet and chart.planets[other].house == house and other in enemies:
            return True, f"{planet} sits with its enemy {other} in house {house}"

    # 3) Rahu / Ketu grahan-type combinations with luminaries.
    if planet in ("Sun", "Moon"):
        for node in ("Rahu", "Ketu"):
            if chart.planets[node].house == house:
                return True, f"{planet} with {node} (grahan) in house {house}"

    return False, ""


def analyse(chart):
    """Return a structured Lal Kitab report for a chart."""
    report = {
        "system": "Lal Kitab",
        "disclaimer": REMEDIES["_meta"]["disclaimer"],
        "global_rules": REMEDIES["_meta"]["global_rules"],
        "planets": [],
    }

    for planet in _LAL_PLANETS:
        p = chart.planets[planet]
        house = p.house
        reading = PLANET_IN_HOUSE.get(planet, {}).get(str(house), {})
        malefic, reason = _is_malefic(planet, chart)

        entry = {
            "planet": planet,
            "house": house,
            "sign": p.sign,
            "pakka_ghar": REFERENCE["pakka_ghar"][planet],
            "in_pakka_ghar": house == REFERENCE["pakka_ghar"][planet],
            "polarity": reading.get("polarity", "mixed"),
            "reading": reading.get("effect", ""),
            "malefic": malefic,
            "reason": reason,
            "remedies": _remedies_for(planet, house) if malefic else [],
        }
        report["planets"].append(entry)

    report["afflicted_planets"] = [e["planet"] for e in report["planets"] if e["malefic"]]
    return report


def _remedies_for(planet, house):
    block = REMEDIES["remedies"].get(planet, {})
    out = list(block.get("general", []))
    out += block.get("by_house", {}).get(str(house), [])
    return out


def remedies_for_problem(chart, planets):
    """
    Given a list of planets relevant to a stated problem (e.g. ['Venus','Mars']
    for marriage), return remedies for whichever of them are afflicted.
    """
    result = []
    for planet in planets:
        malefic, reason = _is_malefic(planet, chart)
        if malefic:
            result.append({
                "planet": planet,
                "reason": reason,
                "weekday": REMEDIES["weekdays"][planet],
                "remedies": _remedies_for(planet, chart.planets[planet].house),
            })
    return result


# Houses/planets commonly consulted per life area (for the problem->remedy layer).
PROBLEM_KARAKAS = {
    "marriage": ["Venus", "Mars", "Jupiter"],
    "career": ["Saturn", "Sun", "Mercury"],
    "finance": ["Jupiter", "Mercury", "Venus"],
    "health": ["Sun", "Moon", "Mars", "Saturn"],
    "children": ["Jupiter", "Ketu", "Sun"],
    "education": ["Mercury", "Jupiter", "Moon"],
    "litigation": ["Mars", "Saturn", "Rahu"],
}


if __name__ == "__main__":
    # Demo against the same Gandhi chart used in demo.py.
    import datetime as _dt
    import ephemeris as E

    when_utc = (_dt.datetime(1869, 10, 2, 7, 11)
                - _dt.timedelta(hours=4.5)).replace(tzinfo=_dt.timezone.utc)
    chart = E.build_chart(when_utc, 21.6417, 69.6293, system="vedic")

    rep = analyse(chart)
    print(f"=== {rep['system']} report ===")
    for e in rep["planets"]:
        flag = "  <-- MALEFIC" if e["malefic"] else ""
        print(f"\n{e['planet']} (house {e['house']}, {e['sign']}, "
              f"{e['polarity']}){flag}")
        print(f"  {e['reading']}")
        if e["malefic"]:
            print(f"  Reason: {e['reason']}")
            for r in e["remedies"][:3]:
                print(f"   * [{r['type']}] {r['instruction']}")

    print("\n--- Problem-based: MARRIAGE ---")
    for blk in remedies_for_problem(chart, PROBLEM_KARAKAS["marriage"]):
        print(f"{blk['planet']} ({blk['weekday']}): {blk['reason']}")
        for r in blk["remedies"][:2]:
            print(f"   * {r['instruction']}")
