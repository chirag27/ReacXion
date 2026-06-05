# Astrology Engine — Phase 1 (Calculation Core)

A deterministic astronomical calculation engine for Vedic, KP, and (later) Lal
Kitab astrology. This is **Phase 1**: the calculation core only. There is no
interpretation layer yet.

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
├── engine/                 # DETERMINISTIC core (no LLM, ever)
│   ├── constants.py        # signs, 27 nakshatras, Vimshottari lords/years, presets
│   ├── birth_data.py       # BirthData model + robust local-time -> UTC
│   ├── ephemeris.py        # the ONLY module that imports swisseph
│   ├── nakshatra.py        # pure math: longitude -> nakshatra + pada
│   ├── kp_sublord.py       # pure math: KP 249 sub-lord system
│   └── chart.py            # compute_chart(): orchestrates into an immutable Chart
├── tests/
│   ├── golden_charts.py    # 3 golden charts; expected values are TODO placeholders
│   ├── test_birth_data.py  # timezone -> UTC (deterministic)
│   ├── test_kp_sublord.py  # 249-segment structure + known sub-lords
│   ├── test_chart.py       # structural smoke tests
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

## Validation workflow

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

## Scope

Phase 1 stops here: calculation only. Dasha timelines, yogas, Lal Kitab
specifics, and the LLM interpretation layer are later phases.
