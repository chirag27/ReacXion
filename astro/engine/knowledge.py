"""Knowledge query API — the codified rules (Phases 3-5) as serializable results.

This is the *clean query layer* the future agent calls. Every function returns
plain JSON-serializable dicts/lists (no engine dataclasses), so the Phase-7
tool-calling LLM can consume them directly. The function names mirror the
planned agent tools.

Crucially, this layer still **computes** — it does not interpret in prose. The
positional facts come from the deterministic engine; the prose comes from the
separate RAG layer. The agent grounds every claim in these results.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from .birth_data import BirthData
from .chart import compute_chart, compute_kp_chart, compute_vedic_chart
from .constants import PRESET_KP, PRESET_VEDIC
from . import bhava as _bhava
from .functional import classify_chart
from .dignity import chart_dignities
from .yogas import detect_yogas
from .ashtakavarga import sarvashtakavarga, by_house
from .dasha import chart_vimshottari, dasha_at
from .varga import divisional_chart
from .kp import KPAnalysis
from .kp_events import judge_event as _judge_event, event_dasha_periods
from .kp_ruling import ruling_planets as _ruling_planets
from .lalkitab import LalKitabChart
from .lalkitab_debts import detect_rinas
from .lalkitab_remedies import remedies_for


# --------------------------------------------------------------------------- #
# Serialization helpers
# --------------------------------------------------------------------------- #
def _planet_dict(p) -> Dict:
    return {
        "name": p.name, "longitude": round(p.longitude, 5), "sign": p.sign,
        "sign_lord": p.sign_lord, "nakshatra": p.nakshatra,
        "nakshatra_lord": p.nakshatra_lord, "pada": p.pada,
        "sub_lord": p.sub_lord, "retrograde": p.retrograde,
        "speed": round(p.speed, 6),
    }


def _cusp_dict(c) -> Dict:
    return {
        "house": c.house, "longitude": round(c.longitude, 5), "sign": c.sign,
        "sign_lord": c.sign_lord, "nakshatra_lord": c.nakshatra_lord,
        "sub_lord": c.sub_lord,
    }


def _chart_dict(chart) -> Dict:
    return {
        "ayanamsa": chart.ayanamsa, "house_system": chart.house_system,
        "jd_ut": round(chart.jd_ut, 6),
        "ascendant": round(chart.ascendant, 5),
        "planets": {n: _planet_dict(p) for n, p in chart.planets.items()},
        "cusps": [_cusp_dict(c) for c in chart.cusps],
    }


# --------------------------------------------------------------------------- #
# Chart + Vedic interpretation
# --------------------------------------------------------------------------- #
def compute_chart_facts(birth: BirthData, system: str = "vedic") -> Dict:
    """Deterministic chart facts for ``system`` ('vedic' or 'kp')."""
    preset = PRESET_KP if system == "kp" else PRESET_VEDIC
    return _chart_dict(compute_chart(birth, *preset))


def get_yogas(birth: BirthData) -> List[Dict]:
    chart = compute_vedic_chart(birth)
    return [{
        "name": y.name, "category": y.category, "planets": list(y.planets),
        "description": y.description, "triggers": list(y.triggers),
        "cancellation": y.cancellation,
    } for y in detect_yogas(chart)]


def get_functional_nature(birth: BirthData) -> Dict[str, Dict]:
    chart = compute_vedic_chart(birth)
    return {p: {"nature": fn.nature, "owned_houses": fn.owned_houses,
                "reason": fn.reason}
            for p, fn in classify_chart(chart).items()}


def get_dignities(birth: BirthData) -> Dict[str, Dict]:
    chart = compute_vedic_chart(birth)
    return {p: {"sign": d.sign, "sign_lord": d.sign_lord, "state": d.state}
            for p, d in chart_dignities(chart).items()}


def get_ashtakavarga(birth: BirthData) -> Dict:
    chart = compute_vedic_chart(birth)
    sav = sarvashtakavarga(chart)
    asc_sign = int(chart.ascendant // 30)
    return {"sarva_by_sign": sav, "sarva_by_house": by_house(sav, asc_sign),
            "total": sum(sav)}


def get_divisional_chart(birth: BirthData, code: str) -> Dict:
    chart = compute_vedic_chart(birth)
    vc = divisional_chart(chart, code)
    return {"code": vc.code, "name": vc.name, "ascendant_sign": vc.ascendant_sign,
            "planet_signs": vc.planet_signs}


def house_info(house: int) -> Dict:
    """Karakas + significations of a bhava (codified reference data)."""
    return {"house": house, "name": _bhava.BHAVA[house].name,
            "karakas": list(_bhava.karakas(house)),
            "significations": list(_bhava.significations(house))}


# --------------------------------------------------------------------------- #
# Dasha
# --------------------------------------------------------------------------- #
def get_vimshottari_dasha(birth: BirthData, depth: int = 2) -> List[Dict]:
    chart = compute_vedic_chart(birth)
    mahas = chart_vimshottari(chart, depth=depth)

    def ser(p):
        d = {"lord": p.lord, "level": p.level,
             "start": p.start.isoformat(), "end": p.end.isoformat()}
        if p.children:
            d["children"] = [ser(c) for c in p.children]
        return d

    return [ser(m) for m in mahas]


def dasha_on(birth: BirthData, when: datetime, depth: int = 4) -> List[Dict]:
    chart = compute_vedic_chart(birth)
    mahas = chart_vimshottari(chart, depth=depth)
    chain = dasha_at(mahas, when)
    return [{"lord": p.lord, "level": p.level, "level_name": p.level_name,
             "start": p.start.isoformat(), "end": p.end.isoformat()}
            for p in chain]


# --------------------------------------------------------------------------- #
# KP
# --------------------------------------------------------------------------- #
def _kp_analysis(birth: BirthData) -> KPAnalysis:
    return KPAnalysis.from_chart(compute_kp_chart(birth))


def get_kp_significators(birth: BirthData, house: int) -> List[Dict]:
    A = _kp_analysis(birth)
    return [{"planet": s.planet, "level": s.level, "reason": s.reason}
            for s in A.house_significators(house)]


def get_cuspal_sublords(birth: BirthData) -> Dict[int, str]:
    A = _kp_analysis(birth)
    return dict(A.cuspal_sub_lord)


def get_ruling_planets(query: BirthData) -> Dict:
    rp = _ruling_planets(query)
    return {"day_lord": rp.day_lord,
            "moon": {"sign": rp.moon_sign_lord, "star": rp.moon_star_lord,
                     "sub": rp.moon_sub_lord},
            "lagna": {"sign": rp.lagna_sign_lord, "star": rp.lagna_star_lord,
                      "sub": rp.lagna_sub_lord},
            "nodes": rp.nodes, "ordered": rp.ordered}


def judge_event_kp(birth: BirthData, event: str) -> Dict:
    A = _kp_analysis(birth)
    j = _judge_event(A, event)
    windows = event_dasha_periods(birth, A, event)
    return {
        "event": j.event, "houses": list(j.houses),
        "deciding_cusp": j.deciding_cusp, "cuspal_sub_lord": j.cuspal_sub_lord,
        "supports": j.supports, "negates": j.negates,
        "significators": j.significators,
        "final_significators": j.final_significators,
        "promised": j.promised, "verdict": j.verdict,
        "timing_windows": [
            {"maha": None, "lord": w.lord,
             "start": w.start.isoformat(), "end": w.end.isoformat()}
            for w in windows[:12]
        ],
    }


# --------------------------------------------------------------------------- #
# Lal Kitab
# --------------------------------------------------------------------------- #
def get_lal_kitab_chart(birth: BirthData) -> Dict:
    lk = LalKitabChart.from_chart(compute_vedic_chart(birth))
    return {
        "ascendant_house": lk.ascendant_house,
        "house_planets": {h: lk.house_planets[h] for h in range(1, 13)},
        "states": {g: {"house": s.house, "in_pakka_ghar": s.in_pakka_ghar,
                       "state": s.state, "companions": s.companions,
                       "aspected_by": s.aspected_by}
                   for g, s in lk.states.items()},
    }


def get_rinas(birth: BirthData) -> List[Dict]:
    lk = LalKitabChart.from_chart(compute_vedic_chart(birth))
    return [{"name": r.name, "sanskrit": r.sanskrit, "trigger": r.trigger,
             "effects": list(r.effects)} for r in detect_rinas(lk)]


def get_remedies(birth: BirthData) -> List[Dict]:
    lk = LalKitabChart.from_chart(compute_vedic_chart(birth))
    return [{"target": rem.target, "kind": rem.kind, "reason": rem.reason,
             "text": rem.text} for rem in remedies_for(lk)]
