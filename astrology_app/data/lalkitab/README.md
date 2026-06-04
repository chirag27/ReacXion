# Lal Kitab dataset

Data and logic for the Lal Kitab system, plus its remedies (upay/totke).

## Files

| File | What it holds |
|------|---------------|
| `reference.json` | Pakka ghar (permanent houses), planetary friendship/enemy table, significations, planet states, and the rules that decide if a planet is malefic. |
| `planet_in_house.json` | A Lal Kitab reading for every planet in every house (9 × 12 = 108 entries), each tagged `benefic` / `mixed` / `malefic`. |
| `remedies.json` | The remedy database: per-planet **general** remedies + **house-specific** remedies, with type, instruction, timing, what it addresses, and weekday. |
| `../../engine/lalkitab.py` | Loads the JSON, flags afflicted planets in a chart, and returns matching remedies (incl. a problem-based lookup, e.g. marriage → Venus/Mars/Jupiter). |

## How a remedy gets surfaced

1. `ephemeris.build_chart()` computes planet houses for the birth chart.
2. `lalkitab.analyse(chart)` checks each planet against the malefic rules
   (malefic house placement, conjunction with an enemy, Sun/Moon + node grahan).
3. For each afflicted planet it returns the general + house-specific remedies.

## Important

These remedies are **traditional/cultural**, not medical, legal, financial or
psychological advice. The `disclaimer` field in `remedies.json` must be shown to
the user with every remedy. Variants exist across Lal Kitab editions; the values
here follow the most commonly cited tradition and are meant to be edited to taste.

## Try it

```bash
cd ../../engine
pip install pyswisseph
python3 lalkitab.py
```
