"""Deterministic tests for the whole-sign house framework."""

from engine.houses import HouseChart, house_of


def test_house_of_basic():
    # Ascendant in Aries (sign 0): a planet in Aries is in house 1.
    assert house_of(5.0, 0) == 1
    assert house_of(35.0, 0) == 2     # Taurus -> 2nd
    assert house_of(345.0, 0) == 12   # Pisces -> 12th


def test_from_positions_lords_and_occupants():
    # Cancer ascendant (105° -> sign 3).
    hc = HouseChart.from_positions(
        {"Sun": 100.0, "Moon": 200.0, "Mars": 5.0}, ascendant=105.0,
    )
    assert hc.asc_sign == 3
    # House 1 = Cancer (lord Moon), house 10 = Aries (lord Mars).
    assert hc.house_lord[1] == "Moon"
    assert hc.house_lord[10] == "Mars"
    # Sun at 100° = Cancer -> house 1; Mars at 5° = Aries -> house 10.
    assert hc.house_of_planet["Sun"] == 1
    assert hc.house_of_planet["Mars"] == 10
    assert "Sun" in hc.occupants(1)


def test_houses_owned_by():
    # Aries ascendant: Mars owns 1 (Aries) and 8 (Scorpio).
    hc = HouseChart.from_positions({"Mars": 5.0}, ascendant=5.0)
    assert sorted(hc.houses_of("Mars")) == [1, 8]
    # Sun owns 5 (Leo) only.
    assert hc.houses_of("Sun") == [5]


def test_twelve_houses_partition_all_signs():
    hc = HouseChart.from_positions({"Sun": 0.0}, ascendant=200.0)
    signs = {hc.house_sign[h] for h in range(1, 13)}
    assert signs == set(range(12))
