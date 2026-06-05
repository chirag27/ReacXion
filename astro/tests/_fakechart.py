"""Tiny helper to build a duck-typed chart for the pure-rule Phase-3 tests.

Only ``planets[name].longitude`` and ``ascendant`` are needed by the houses /
functional / yoga modules, so we avoid the ephemeris entirely and place grahas
at exact longitudes.
"""

from types import SimpleNamespace

from engine.constants import GRAHA_NAMES


def make_chart(ascendant: float, **longitudes) -> SimpleNamespace:
    """Build a chart with the given ascendant and graha longitudes.

    Unspecified grahas default to 0.0 (0° Aries). Specify every graha that
    matters for the rule under test to avoid spurious conjunctions.
    """
    longs = {name: 0.0 for name in GRAHA_NAMES}
    longs.update(longitudes)
    planets = {name: SimpleNamespace(longitude=lon) for name, lon in longs.items()}
    return SimpleNamespace(planets=planets, ascendant=ascendant)
