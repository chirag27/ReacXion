"""Engine tools exposed to the agent.

The consultation's :class:`BirthData` is bound **server-side** in the
:class:`ToolKit` — the model never supplies birth details or positions; it only
chooses *which* deterministic tool to call and passes non-birth arguments
(event type, house, varga code, date, query). Every tool returns a
JSON-serializable dict; failures are returned as ``{"error": ...}`` so the model
can abstain rather than guess.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

from .. import knowledge
from ..birth_data import BirthData
from ..rag import SYSTEMS, TextStore, get_embedder, ingest_corpus, search_texts


# --------------------------------------------------------------------------- #
# Tool schemas (names mirror the Phase-7 plan)
# --------------------------------------------------------------------------- #
def _obj(props=None, required=None):
    return {"type": "object", "properties": props or {},
            "required": required or []}


TOOL_SPECS: List[Dict] = [
    {"name": "compute_chart",
     "description": "Deterministic chart facts (planet longitudes, signs, "
                    "nakshatras, sub-lords, cusps, ascendant) for a system.",
     "input_schema": _obj({"system": {"type": "string", "enum": ["vedic", "kp"],
                                      "description": "vedic = Lahiri + whole-sign; "
                                      "kp = KP ayanamsa + Placidus"}},
                          ["system"])},
    {"name": "get_yogas",
     "description": "Detected Parashari yogas with the placements that trigger "
                    "each (Raja, Dhana, Pancha Mahapurusha, Gaja Kesari, etc.).",
     "input_schema": _obj()},
    {"name": "get_functional_nature",
     "description": "Functional benefic/malefic/yogakaraka nature of each graha "
                    "for this ascendant, with the houses it rules.",
     "input_schema": _obj()},
    {"name": "get_dignities",
     "description": "Dignity of each graha (exalted/debilitated/moolatrikona/"
                    "own/friend/neutral/enemy) by sign.",
     "input_schema": _obj()},
    {"name": "get_ashtakavarga",
     "description": "Sarvashtakavarga bindu totals by sign and by house.",
     "input_schema": _obj()},
    {"name": "get_divisional_chart",
     "description": "Sign placements in a divisional chart (varga), e.g. D9 "
                    "Navamsa, D10 Dasamsa.",
     "input_schema": _obj({"code": {"type": "string",
                                    "description": "varga code, e.g. 'D9', 'D10'"}},
                          ["code"])},
    {"name": "get_vimshottari_dasha",
     "description": "Vimshottari dasha tree (Maha -> Antar) with exact start/end "
                    "dates.",
     "input_schema": _obj({"depth": {"type": "integer", "minimum": 1, "maximum": 4,
                                     "description": "1=Maha, 2=+Antar (default 2)"}})},
    {"name": "dasha_at",
     "description": "The active dasha chain (Maha>Antar>Pratyantar>Sookshma) on a "
                    "given date.",
     "input_schema": _obj({"date": {"type": "string",
                                    "description": "ISO date, e.g. '2025-06-01'"}},
                          ["date"])},
    {"name": "get_kp_significators",
     "description": "KP 4-step significators of a house (ordered, strongest first).",
     "input_schema": _obj({"house": {"type": "integer", "minimum": 1, "maximum": 12}},
                          ["house"])},
    {"name": "get_cuspal_sublords",
     "description": "The KP cuspal sub-lord of each of the 12 cusps.",
     "input_schema": _obj()},
    {"name": "get_ruling_planets",
     "description": "KP Ruling Planets for the current moment at the birth place "
                    "(day lord + Moon's and Lagna's sign/star/sub lords).",
     "input_schema": _obj()},
    {"name": "judge_event_kp",
     "description": "KP judgment of an event: deciding-cusp sub-lord verdict, "
                    "significators, and Dasha-Bhukti timing windows.",
     "input_schema": _obj({"event": {"type": "string",
                                     "enum": ["marriage", "career", "childbirth",
                                              "education", "property",
                                              "foreign_travel", "wealth", "disease"]}},
                          ["event"])},
    {"name": "get_lal_kitab_chart",
     "description": "Lal Kitab (1941) fixed-grid chart: house placements, pakka "
                    "ghar, and awakened/asleep/blind states.",
     "input_schema": _obj()},
    {"name": "get_rinas",
     "description": "Lal Kitab rinas (ancestral debts) with the triggering "
                    "placement and affected life areas.",
     "input_schema": _obj()},
    {"name": "get_remedies",
     "description": "Lal Kitab remedies (totkay) keyed to detected rinas and "
                    "afflicted planets.",
     "input_schema": _obj()},
    {"name": "get_house_info",
     "description": "Karakas and significations of a bhava (reference data).",
     "input_schema": _obj({"house": {"type": "integer", "minimum": 1, "maximum": 12}},
                          ["house"])},
    {"name": "search_texts",
     "description": "Retrieve interpretive PROSE passages (not positional facts) "
                    "to support a reading, scoped to one system.",
     "input_schema": _obj({"query": {"type": "string"},
                           "system": {"type": "string",
                                      "enum": list(SYSTEMS)},
                           "k": {"type": "integer", "minimum": 1, "maximum": 8}},
                          ["query", "system"])},
]

TOOL_NAMES = {t["name"] for t in TOOL_SPECS}


class ToolKit:
    """Dispatches tool calls against a fixed birth and a lazily-built RAG store."""

    def __init__(self, birth: BirthData, store: Optional[TextStore] = None):
        self.birth = birth
        self._store = store

    # -- RAG store is built on first use so agent construction stays cheap --
    def _ensure_store(self) -> TextStore:
        if self._store is None:
            self._store = TextStore(embedder=get_embedder("hashing"))
            ingest_corpus(self._store)
        return self._store

    def _now_query(self) -> BirthData:
        tz = self.birth.local_datetime().tzinfo
        now = datetime.now(tz)
        return BirthData(now.year, now.month, now.day, now.hour, now.minute,
                         now.second, self.birth.latitude, self.birth.longitude,
                         self.birth.timezone, name="query-now")

    def dispatch(self, name: str, args: Dict) -> Dict:
        args = args or {}
        b = self.birth
        try:
            if name == "compute_chart":
                return knowledge.compute_chart_facts(b, args.get("system", "vedic"))
            if name == "get_yogas":
                return {"yogas": knowledge.get_yogas(b)}
            if name == "get_functional_nature":
                return knowledge.get_functional_nature(b)
            if name == "get_dignities":
                return knowledge.get_dignities(b)
            if name == "get_ashtakavarga":
                return knowledge.get_ashtakavarga(b)
            if name == "get_divisional_chart":
                return knowledge.get_divisional_chart(b, args["code"])
            if name == "get_vimshottari_dasha":
                return {"mahadashas": knowledge.get_vimshottari_dasha(
                    b, int(args.get("depth", 2)))}
            if name == "dasha_at":
                when = _parse_date(args["date"])
                return {"date": when.isoformat(), "chain": knowledge.dasha_on(b, when)}
            if name == "get_kp_significators":
                return {"house": args["house"],
                        "significators": knowledge.get_kp_significators(b, int(args["house"]))}
            if name == "get_cuspal_sublords":
                return {"cuspal_sub_lords": knowledge.get_cuspal_sublords(b)}
            if name == "get_ruling_planets":
                return knowledge.get_ruling_planets(self._now_query())
            if name == "judge_event_kp":
                return knowledge.judge_event_kp(b, args["event"])
            if name == "get_lal_kitab_chart":
                return knowledge.get_lal_kitab_chart(b)
            if name == "get_rinas":
                return {"rinas": knowledge.get_rinas(b)}
            if name == "get_remedies":
                return {"remedies": knowledge.get_remedies(b)}
            if name == "get_house_info":
                return knowledge.house_info(int(args["house"]))
            if name == "search_texts":
                hits = search_texts(self._ensure_store(), args["query"],
                                    args["system"], int(args.get("k", 3)))
                return {"passages": [{"text": h.text, "source": h.metadata.get("source"),
                                      "score": round(h.score, 4)} for h in hits]}
            return {"error": f"unknown tool {name!r}"}
        except KeyError as exc:
            return {"error": f"missing argument {exc} for tool {name!r}"}
        except Exception as exc:  # surface failure so the model abstains
            return {"error": f"{type(exc).__name__}: {exc}"}


def _parse_date(s: str) -> datetime:
    s = s.strip()
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        dt = datetime.strptime(s[:10], "%Y-%m-%d")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc, hour=dt.hour or 12)
    return dt
