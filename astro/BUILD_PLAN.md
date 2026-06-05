# Jyotish Agent — Phase-by-Phase Build Plan

A multi-system astrology agent covering Vedic (Parashari), KP, and Lal Kitab.
Each phase below is written to be pasted directly into Claude Code as a single
message. **Do not start a phase until the previous one validates.**

## The one rule that governs everything

All astronomical computation is deterministic and lives in a calculation
engine. The LLM layer only interprets — it must never invent a planetary
position, dasha, sub-lord, or cusp. Every positional claim in a reading must
trace back to a tool call. This separation is what makes the agent credible
instead of a confident fabricator.

**Stack:** Python · `pyswisseph` (ephemeris) · `pytest` (validation) · a vector
DB for retrieval (Chroma/Qdrant/pgvector) · a tool-calling LLM for
orchestration. Sidereal mode throughout. Lahiri (Chitrapaksha) ayanamsa for
Vedic; KP (Krishnamurti) ayanamsa for KP. Support both Placidus (KP) and
whole-sign (Parashari) house systems.

## Phase 1 — Chart engine + validation harness

1. Project setup: `requirements.txt`, folders (`engine/`, `tests/`, `data/`), a
   README documenting the architecture, `.gitignore`, and `git init`.
2. A `BirthData` model: date, exact time, timezone, lat/long, with robust
   timezone→UTC conversion (the #1 bug source — handle carefully).
3. A core function returning, per ayanamsa + house system: sidereal longitudes
   for all 9 grahas (Rahu/Ketu as mean nodes), each planet's nakshatra + pada,
   the 12 house cusps, and the ascendant.
4. The KP 249 sub-lord system: divide each nakshatra into 9 subs proportional
   to Vimshottari periods; resolve sign-lord → star-lord → sub-lord for every
   planet and every cusp.
5. A pytest harness with 3 golden charts, expected values left as TODO
   placeholders (fill from Jagannatha Hora).

Validate: fill golden-chart expected values from Jagannatha Hora and confirm
planet longitudes + cusps match to the arcminute. Cross-check KP sub-lords
against a dedicated KP tool.

## Phase 2 — Vimshottari dasha + divisional charts

1. Vimshottari dasha: full Maha → Antar → Pratyantar → Sookshma, computed from
   the Moon's nakshatra longitude, with exact start/end datetimes. Add a
   `dasha_at(date)` helper returning the active chain on any date.
2. Divisional charts (vargas) from the D1 longitudes: D9 (Navamsa), D10
   (Dasamsa), D7 (Saptamsa), D2, D3, D4, D12, D16, D20, D24, D27, D30, D40,
   D45, D60. Make the divisor logic data-driven so adding a varga is trivial.
3. Graha drishti (Parashari aspects, incl. special aspects of
   Mars/Jupiter/Saturn) and dignity state per planet
   (exalt/debilitate/own/friend/enemy/neutral) with Moolatrikona.
4. Extend the pytest harness: validate dasha balance-at-birth and key varga
   placements against Jagannatha Hora.

## Phase 3 — Vedic interpretation rules (codified, not LLM)

Deterministic rules in code/structured data, not a vector store.

1. Yoga detection: Raj, Dhana, Pancha Mahapurusha, Gaja Kesari, Neecha Bhanga,
   Kemadruma, etc. Each yoga returns name, triggering placements, and a
   structured strength/cancellation note.
2. Functional benefic/malefic classification per ascendant (Lagna-based).
3. House-significations (bhava karakas + what each house signifies) as
   structured data.
4. Optional: basic Ashtakavarga (Bhinna + Sarva totals).
5. Tests for yoga detection on charts with known yogas.

## Phase 4 — KP module

1. Significator theory: 4-step significators for any house (planets in star of
   occupants, occupants, planets in star of owner, owner), ordered.
2. Cuspal Sub Lords (CSL) for all 12 cusps, with the significations each CSL
   must permit for an event (e.g. marriage needs cusps 2/7/11).
3. Ruling Planets at a query timestamp (day lord, Moon's sign/star/sub lords,
   Lagna sign/star/sub lords).
4. Event-judgment helper: given an event type, return the house combination,
   CSL verdict, significators, plus a dasha-period correlation for timing.
5. Flag birth-time sensitivity (KP sub-lords shift within minutes).
6. Tests validating significators and CSLs against a dedicated KP tool.

## Phase 5 — Lal Kitab module (separate paradigm)

1. Lal Kitab chart from D1 house placements (fixed Aries=1st grid).
2. Pakka ghar (permanent house) per planet and blind/sleeping/awakened states.
3. Rinas (ancestral debts) detection and life-area effects.
4. Remedies / totkay engine keyed to afflicted placements.
5. Pick ONE canonical edition (1939–1952), document it in the README, encode
   only that variant.
6. Tests on charts with known pakka ghar / rina outcomes.

## Phase 6 — Knowledge layer (codified rules + RAG)

1. Codified rules (Phases 3–5) exposed through a clean query API.
2. RAG for interpretive prose: vector DB (Chroma to start), chunk + embed
   source material, `search_texts(query, system)` retriever scoped by system.

Copyright: build the corpus only from public-domain editions, licensed
material, or own rewritten summaries — not scraped book text. Add a
`sources.md` documenting provenance.

## Phase 7 — Agent orchestration (tool-calling loop)

Expose the engine as tools: `compute_chart`, `get_vimshottari_dasha`,
`dasha_at`, `get_divisional_chart`, `get_yogas`, `get_kp_significators`,
`get_cuspal_sublords`, `get_ruling_planets`, `judge_event_kp`,
`get_lal_kitab_chart`, `get_remedies`, `search_texts`.

Loop: classify question → call calculation tools to ground every claim →
retrieve codified rules + passages → synthesize citing what drove each
conclusion. Guardrail: the model may never state a position/dasha/sub-lord/cusp
that did not come from a tool call. Default to separate-then-synthesize across
systems.

## Phase 8 — Validation, reports, and frontend

1. Regression suite of golden charts on every change.
2. Interpretation-quality eval set.
3. Optional birth-time rectification, or at minimum a confidence indicator.
4. Web frontend: chart (D1 + key vargas), dasha timeline, structured reading as
   an HTML report.

## Validation checklist (return to this constantly)

- [ ] D1 longitudes + cusps match Jagannatha Hora to the arcminute
- [ ] KP sub-lords match a dedicated KP tool
- [ ] Vimshottari balance-at-birth correct
- [ ] Navamsa + key vargas match
- [ ] Yoga detection correct on known charts
- [ ] KP significators + CSLs match reference
- [ ] Lal Kitab pakka ghar / rinas match the chosen canonical edition
- [ ] Agent never emits a position without a tool call
- [ ] Corpus provenance documented; no copyrighted text ingested

Tip: feed one phase per message; validate; then proceed.
