"""FastAPI backend: the engine + agent exposed over HTTP for the Android app.

Run locally:  uvicorn service.app:app --host 0.0.0.0 --port 8000
The Android app points its base URL at this server (e.g. http://<your-ip>:8000).

Calculation endpoints are deterministic and need no API key. ``/ask`` runs the
tool-calling agent and needs ANTHROPIC_API_KEY in the environment; without it,
it returns 503 (the rest of the app still works).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from engine import knowledge, rectify
from engine.kp_events import EVENTS
from engine.varga import VARGAS

from .models import (
    AskRequest,
    BirthInput,
    ChartRequest,
    DashaAtRequest,
    DashaRequest,
    EventRequest,
    HouseRequest,
    SensitivityRequest,
    VargaRequest,
)


def _parse_date(s: str) -> datetime:
    s = s.strip()
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        dt = datetime.strptime(s[:10], "%Y-%m-%d").replace(hour=12)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _birth(req: BirthInput):
    try:
        return req.to_birth()
    except Exception as exc:        # invalid date/tz/coords
        raise HTTPException(status_code=422, detail=str(exc))


def create_app(agent_llm=None) -> FastAPI:
    """Build the app. ``agent_llm`` injects an LLMClient for /ask (tests)."""
    app = FastAPI(title="Jyotish Engine API", version="1.0")
    app.add_middleware(CORSMiddleware, allow_origins=["*"],
                       allow_methods=["*"], allow_headers=["*"])
    app.state.agent_llm = agent_llm

    @app.get("/health")
    def health():
        return {"status": "ok", "events": sorted(EVENTS),
                "vargas": sorted(VARGAS), "agent_ready": _agent_available(app)}

    @app.post("/chart")
    def chart(req: ChartRequest):
        return knowledge.compute_chart_facts(_birth(req), req.system)

    @app.post("/yogas")
    def yogas(req: BirthInput):
        return {"yogas": knowledge.get_yogas(_birth(req))}

    @app.post("/functional")
    def functional(req: BirthInput):
        return knowledge.get_functional_nature(_birth(req))

    @app.post("/dignities")
    def dignities(req: BirthInput):
        return knowledge.get_dignities(_birth(req))

    @app.post("/ashtakavarga")
    def ashtakavarga(req: BirthInput):
        return knowledge.get_ashtakavarga(_birth(req))

    @app.post("/varga")
    def varga(req: VargaRequest):
        if req.code not in VARGAS:
            raise HTTPException(422, f"unknown varga {req.code!r}")
        return knowledge.get_divisional_chart(_birth(req), req.code)

    @app.post("/dasha")
    def dasha(req: DashaRequest):
        return {"mahadashas": knowledge.get_vimshottari_dasha(_birth(req), req.depth)}

    @app.post("/dasha_at")
    def dasha_at(req: DashaAtRequest):
        return {"chain": knowledge.dasha_on(_birth(req), _parse_date(req.date))}

    @app.post("/kp/significators")
    def kp_significators(req: HouseRequest):
        return {"house": req.house,
                "significators": knowledge.get_kp_significators(_birth(req), req.house)}

    @app.post("/kp/cusps")
    def kp_cusps(req: BirthInput):
        return {"cuspal_sub_lords": knowledge.get_cuspal_sublords(_birth(req))}

    @app.post("/kp/ruling_planets")
    def ruling_planets(req: BirthInput):
        # Ruling planets for the current moment at the birth place.
        from engine.knowledge import get_ruling_planets
        from engine.agent.tools import ToolKit
        return ToolKit(_birth(req)).dispatch("get_ruling_planets", {})

    @app.post("/kp/judge")
    def kp_judge(req: EventRequest):
        if req.event not in EVENTS:
            raise HTTPException(422, f"unknown event {req.event!r}")
        return knowledge.judge_event_kp(_birth(req), req.event)

    @app.post("/lalkitab")
    def lalkitab(req: BirthInput):
        return knowledge.get_lal_kitab_chart(_birth(req))

    @app.post("/rinas")
    def rinas(req: BirthInput):
        return {"rinas": knowledge.get_rinas(_birth(req))}

    @app.post("/remedies")
    def remedies(req: BirthInput):
        return {"remedies": knowledge.get_remedies(_birth(req))}

    @app.post("/sensitivity")
    def sensitivity(req: SensitivityRequest):
        from engine import birth_time_sensitivity
        sr = birth_time_sensitivity(_birth(req), minutes=req.minutes)
        return {"window_minutes": sr.window_minutes, "confidence": sr.confidence,
                "unstable_cusps": [{"house": c.house, "earlier": c.earlier,
                                    "at_birth": c.at_birth, "later": c.later}
                                   for c in sr.unstable_cusps]}

    @app.post("/confidence")
    def confidence(req: BirthInput):
        tc = rectify.time_confidence(_birth(req))
        s = rectify.suggest_rectification(_birth(req))
        return {"level": tc.level, "note": tc.note,
                "stable_width_seconds": round(tc.stable_width_seconds, 1),
                "stable_start": s.stable_start.isoformat(),
                "stable_end": s.stable_end.isoformat(),
                "suggested_center": s.suggested_center.isoformat()}

    @app.post("/report")
    def report(req: BirthInput):
        """One call returns everything the app renders for a reading."""
        b = _birth(req)
        tc = rectify.time_confidence(b)
        return {
            "name": req.name,
            "vedic_chart": knowledge.compute_chart_facts(b, "vedic"),
            "kp_chart": knowledge.compute_chart_facts(b, "kp"),
            "navamsa": knowledge.get_divisional_chart(b, "D9"),
            "dasamsa": knowledge.get_divisional_chart(b, "D10"),
            "dasha": knowledge.get_vimshottari_dasha(b, depth=2),
            "dasha_now": knowledge.dasha_on(b, datetime.now(timezone.utc)),
            "yogas": knowledge.get_yogas(b),
            "functional": knowledge.get_functional_nature(b),
            "dignities": knowledge.get_dignities(b),
            "ashtakavarga": knowledge.get_ashtakavarga(b),
            "cuspal_sub_lords": knowledge.get_cuspal_sublords(b),
            "lal_kitab": knowledge.get_lal_kitab_chart(b),
            "rinas": knowledge.get_rinas(b),
            "remedies": knowledge.get_remedies(b),
            "time_confidence": {"level": tc.level, "note": tc.note},
        }

    @app.post("/ask")
    def ask(req: AskRequest):
        from engine.agent import AstrologyAgent
        llm = app.state.agent_llm
        if llm is None and not _agent_available(app):
            raise HTTPException(
                503, "agent unavailable: set ANTHROPIC_API_KEY (or inject an LLM)")
        agent = AstrologyAgent(_birth(req), llm=llm)
        try:
            result = agent.ask(req.question)
        except Exception as exc:
            raise HTTPException(502, f"agent error: {type(exc).__name__}: {exc}")
        return {
            "answer": result.answer,
            "iterations": result.iterations,
            "stopped_early": result.stopped_early,
            "tool_calls": [{"tool": tc.tool, "input": tc.input} for tc in result.tool_calls],
        }

    return app


def _agent_available(app: FastAPI) -> bool:
    import os
    return app.state.agent_llm is not None or bool(os.environ.get("ANTHROPIC_API_KEY"))


# Module-level app for `uvicorn service.app:app`.
app = create_app()
