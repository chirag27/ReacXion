# Corpus Provenance

Every document ingested into the RAG corpus must be listed here with its origin
and license. **Do not ingest scraped or copyrighted book text.** Build the
corpus only from public-domain editions, properly licensed material, or original
rule summaries written for this project.

## Current corpus

| File | System | Origin | License |
|---|---|---|---|
| `vedic/raja_dhana_yogas.md` | Vedic | Original summary written for this project | Project-owned |
| `vedic/pancha_mahapurusha_lunar_yogas.md` | Vedic | Original summary written for this project | Project-owned |
| `vedic/houses_and_dignity.md` | Vedic | Original summary written for this project | Project-owned |
| `kp/significators_and_csl.md` | KP | Original summary written for this project | Project-owned |
| `kp/ruling_planets.md` | KP | Original summary written for this project | Project-owned |
| `lalkitab/pakka_ghar_states_rinas.md` | Lal Kitab | Original summary written for this project (1941-edition concepts, paraphrased) | Project-owned |

All current entries are **original prose written for this repository**, summarising
widely-known classical concepts in our own words. No third-party text has been
copied.

## Adding a source

1. Confirm the licence permits ingestion (public domain, an explicit licence
   that allows it, or your own writing).
2. Place the file under `data/corpus/<system>/` as Markdown.
3. Add a row above recording the file, system, origin, and licence.
4. Re-run ingestion (`engine.rag.ingest_corpus`).

Never add scraped website text or copyrighted book passages, even if they are
freely accessible online.
