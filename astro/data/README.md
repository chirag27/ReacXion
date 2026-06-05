# data/

Runtime data for the engine.

## ephe/ — optional Swiss Ephemeris files

The engine runs out of the box on the built-in **Moshier** ephemeris (no files
needed), which is accurate to well within an arcminute.

For the highest precision — and the closest possible match to Jagannatha Hora
when filling the golden charts — drop the Swiss Ephemeris data files here and
point the engine at them:

```python
from engine import ephemeris
ephemeris.set_ephemeris_path("data/ephe")
```

Recommended files for the supported date range:

- `seas_18.se1`, `semo_18.se1`, `sepl_18.se1` (1800–2399), plus the matching
  `*_00.se1` / `*_24.se1` files if you cast charts outside that window.

Download from the Astrodienst ephemeris archive:
<https://www.astro.com/ftp/swisseph/ephe/>

These `*.se1` files are **git-ignored** (they are large binaries); only this
note and `.gitkeep` are tracked.
