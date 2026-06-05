# Astrology Engine — Phase 1 (Calculation Core)

A deterministic astronomical calculation engine for Vedic, KP, and (later) Lal
Kitab astrology, built phase by phase per [`BUILD_PLAN.md`](BUILD_PLAN.md).
**Phases 1–2 are complete** (chart core + dasha/vargas/aspects/dignity); there
is still no LLM interpretation layer — everything here is deterministic
computation.

## The one rule: computation vs. interpretation

> **All astronomical computation is deterministic and lives in this engine.
> The LLM interpretation layer (a later phase) only interprets the engine's
> output and must never invent or recompute a position.**

The directory layout enforces that separation:

- `engine/` produces numbers (longitudes, cusps, nakshatras, sub-lords) from
  first principles via Swiss Ephemeris. Given the same `BirthData`, it always
  returns the same `Chart`.
- The future interpreter will consume an immutable `Chart` **read-only**. It
  never touches an ephemeris and never derives a position itself.

Only `engine/ephemeris.py` imports `swisseph`. Every other engine module is
pure Python arithmetic, so the astrology logic is independently testable and
the numerical surface is small and auditable.

## Stack

- Python 3.9+ (uses `zoneinfo`)
- [`pyswisseph`](https://pypi.org/project/pyswisseph/) — Swiss Ephemeris
- `pytest` — test harness
- Sidereal mode. **Lahiri** ayanamsa for Vedic, **KP (Krishnamurti)** ayanamsa
  for KP. **Whole-sign** (Parashari) and **Placidus** (KP) houses.

## Layout

```
astro/
├── BUILD_PLAN.md           # the full 8-phase plan (reference across sessions)
├── engine/                 # DETERMINISTIC core (no LLM, ever)
│   ├── constants.py        # signs, 27 nakshatras, Vimshottari lords/years, presets
│   ├── birth_data.py       # BirthData model + robust local-time -> UTC
│   ├── ephemeris.py        # the ONLY module that imports swisseph
│   ├── nakshatra.py        # pure math: longitude -> nakshatra + pada
│   ├── kp_sublord.py       # pure math: KP 249 sub-lord system
│   ├── chart.py            # compute_chart(): orchestrates into an immutable Chart
│   ├── dasha.py            # [P2] Vimshottari Maha->Antar->Pratyantar->Sookshma
│   ├── varga.py            # [P2] divisional charts (D1..D60), data-driven
│   ├── aspects.py          # [P2] graha drishti (Parashari aspects)
│   └── dignity.py          # [P2] exalt/debil/moolatrikona/own/friend/enemy
├── tests/
│   ├── golden_charts.py    # 3 golden charts; expected values are TODO placeholders
│   ├── test_birth_data.py  # timezone -> UTC (deterministic)
│   ├── test_kp_sublord.py  # 249-segment structure + known sub-lords
│   ├── test_chart.py       # structural smoke tests
│   ├── test_dasha.py       # [P2] dasha balance, ordering, nesting
│   ├── test_varga.py       # [P2] varga rules (D9 continuity, D30 bands, ...)
│   ├── test_aspects.py     # [P2] drishti (7th + special aspects)
│   ├── test_dignity.py     # [P2] dignity classification
│   └── test_golden.py      # arcminute match vs JHora (skips until filled)
└── data/
    └── ephe/               # optional Swiss *.se1 files (git-ignored)
```

## Install & run

```bash
cd astro
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q          # run from inside astro/
```

The engine runs on the built-in **Moshier** ephemeris with no data files
(accurate to within an arcminute). For maximum precision see `data/README.md`.
Positions are computed as **true geometric** longitudes (`FLG_TRUEPOS |
FLG_NOABERR | FLG_NOGDEFL`) to match Jagannatha Hora's convention — not the
apparent positions that are swisseph's default (the difference is the ~20″
annual-aberration term on the Sun).

## Usage

```python
from engine import BirthData, compute_vedic_chart, compute_kp_chart

birth = BirthData(
    year=1990, month=1, day=1, hour=12, minute=0, second=0,
    latitude=28.6139, longitude=77.2090,   # New Delhi
    timezone="Asia/Kolkata",               # IANA name, or a fixed offset like 5.5
)

vedic = compute_vedic_chart(birth)   # Lahiri  + whole-sign
kp    = compute_kp_chart(birth)      # KP      + Placidus

sun = vedic.planets["Sun"]
print(sun.longitude, sun.sign, sun.nakshatra, sun.pada, sun.sub_lord)
print("Ascendant:", kp.ascendant)
print("7th cusp sub-lord:", kp.cusps[6].sub_lord)
```

`compute_chart(birth, ayanamsa, house_system)` is the general entry point; the
two helpers above are presets.

## What the engine computes

For a given `(ayanamsa, house_system)`:

- **Nine grahas** — Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, and
  Rahu/Ketu as **mean nodes** (Ketu = Rahu + 180°). Each carries its sidereal
  longitude, sign + sign-lord, nakshatra + pada, KP sub-lord, speed, and a
  retrograde flag.
- **Twelve house cusps** + the **ascendant**, each cusp with its KP sub-lord.

### Timezone handling (the #1 bug source)

`BirthData` converts local civil time to UTC explicitly:

- IANA zone names resolve through `zoneinfo`, which knows **historical**
  offsets and DST transitions for the actual date — not just today's rule.
- A fixed numeric UTC offset (e.g. `5.5`) can be supplied instead — the safe
  choice for very old births.
- **Spring-forward gaps** (non-existent local times) are rejected loudly.
- **Fall-back ambiguity** (a repeated hour) is disambiguated by an explicit
  `fold` flag.

UTC is then converted to a UT Julian Day via `swe.utc_to_jd`, so leap seconds
and the UTC→UT1 reduction are handled by the library.

### The KP 249 sub-lord system

Each nakshatra (13°20′ = 800′) is divided into **9 subs** whose widths are
proportional to the Vimshottari dasha years, laid out in Vimshottari order
starting from the nakshatra's own (star) lord. For any longitude this yields:

```
sign lord  ->  star (nakshatra) lord  ->  sub lord
```

Across the zodiac the 9 × 27 = 243 subs, **additionally split wherever a sign
boundary falls inside a sub**, produce the canonical **249** distinct segments.
`engine.kp_sublord.build_kp_249_table()` materialises that table (the test
suite asserts it has exactly 249 segments); the engine itself uses the
per-longitude resolver `resolve()` for every planet and every cusp.

## Phase 2 — dasha, vargas, aspects, dignity

All Phase-2 modules are pure arithmetic layered on a Phase-1 `Chart` (no new
ephemeris calls), exposed as standalone functions ready to become agent tools.

```python
from engine import (compute_vedic_chart, chart_vimshottari, dasha_at,
                    divisional_chart, graha_drishti, chart_dignities)
from datetime import datetime, timezone

chart = compute_vedic_chart(birth)

# Vimshottari dasha (Maha > Antar > Pratyantar > Sookshma)
mahas = chart_vimshottari(chart, depth=4)
active = dasha_at(mahas, datetime(2025, 6, 1, tzinfo=timezone.utc))
print(" > ".join(p.lord for p in active))   # e.g. "Venus > Saturn > Mercury > Ketu"

# Divisional charts (D1..D60)
d9 = divisional_chart(chart, "D9")           # Navamsa
print(d9.planet_signs["Moon"], d9.ascendant_sign)

# Aspects and dignity
print(graha_drishti(chart)["Mars"].aspected_planets)
print(chart_dignities(chart)["Sun"].state)   # exalted/own/friend/...
```

- **Dasha** is computed from the Moon's nakshatra longitude with exact UTC
  start/end datetimes. The **year length** (`year_length_days`, default the
  **sidereal year** 365.256364 — JHora's default) is the key knob for matching
  a reference tool's long-range dates; the *balance-at-birth in years* is
  year-length-independent.
- **Vargas** are **data-driven**: each chart is one entry in `engine.varga.VARGAS`
  with a `(sign, part) -> sign` rule (or a special handler for the unequal D30
  Trimsamsa). Rules follow standard BPHS; several vargas have competing
  conventions, so the golden charts are the source of truth — adjust a single
  rule if your reference differs.
- **Drishti**: every graha aspects its 7th; Mars also 4th/8th, Jupiter 5th/9th,
  Saturn 3rd/10th. Node aspects default to the 7th only (configurable).
- **Dignity**: exaltation/debilitation points, moolatrikona ranges, own sign,
  and natural (naisargika) friendship. Temporary friendship is a later
  refinement; nodes report `neutral`.

## Validation status (Phases 1–2)

The golden charts are **filled and asserted** (no skips). Values were
cross-generated with **PyJHora** (`jhora` on PyPI — the Python port of Jagannatha
Hora), configured identically (Lahiri/KP ayanamsa, mean nodes, true positions).
Results across all 3 charts × both ayanamsas:

| Quantity | Agreement vs PyJHora |
|---|---|
| 9 planet longitudes | **< 0.3″** (0.005′) |
| Ascendant | **< 12″** (≤ 0.2′; from `utc_to_jd` vs plain `julday`) |
| Placidus / whole-sign cusps | within the arcminute |
| Nakshatra + pada | **exact** (0 mismatches over a full sweep) |
| KP sign/star/sub-lord | **exact** (0 mismatches over 27,693 samples) |
| Vimshottari lords + balance | lords exact; balance within 0.001 yr |
| D9 Navamsa | **exact** |

Two engine corrections came directly out of this validation: switching to
**true geometric positions** (the ~20″ aberration fix) and defaulting the dasha
year to the **sidereal year**.

**Still requiring confirmation in the JHora GUI:** the convention-dependent
divisional charts (D2, D3, D4, D10, D12, D24, D30, D40, D45, D60). This engine
uses classical Parashari rules; PyJHora's helper uses a uniform cyclic rule, so
they diverge. D9 and the cyclic-equivalent vargas (D7, D16, D20, D27) match
both. Check your JHora "varga calculation method" and tell the engine which
convention to use — each rule is a one-line entry in `engine.varga.VARGAS`.

## Re-validating / extending the golden set

The three golden charts in `tests/golden_charts.py` ship with expected values
left as `None` (TODO). To validate:

1. Cast each birth in **Jagannatha Hora** (free Vedic gold standard):
   - Vedic block → Lahiri ayanamsa + whole-sign houses.
   - KP block → KP ayanamsa + Placidus houses.
2. Transcribe planet longitudes and cusps into `golden_charts.py`.
3. Cross-check the **KP sub-lords** against a dedicated KP tool
   (e.g. KPStarOne / KPAstro) and fill those in too.
4. Run `pytest`. Filled charts assert agreement to the **arcminute**; unfilled
   ones are skipped, so the suite is green throughout.

For the tightest match to JHora, install the Swiss `*.se1` files
(`data/README.md`) and call `ephemeris.set_ephemeris_path("data/ephe")`.

**Phase 2 validation** (also TODO placeholders in `golden_charts.py`):

- `dasha_balance = ("<lord>", <years>)` — the Mahadasha balance-at-birth from
  JHora's Vimshottari table.
- `vargas = {"D9": {"Sun": "Leo", ...}, ...}` — key divisional placements from
  JHora's varga charts.

Filled values are asserted by `test_dasha_balance_at_birth` and
`test_varga_placements`.

## Scope

Phases 1–2 are complete: chart core, KP 249 sub-lords, Vimshottari dasha,
divisional charts, graha drishti, and dignity — all deterministic. Phase 3
(codified yogas/interpretation rules) onward, and the LLM interpretation layer,
follow per `BUILD_PLAN.md`.
