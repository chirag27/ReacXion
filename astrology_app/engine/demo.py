"""
Quick verification / demo for the ephemeris engine.

Run:  python3 demo.py
"""

import datetime as _dt
import ephemeris as E


def show(birth_local, tz_offset_hours, lat, lon, place, system="vedic"):
    # Convert local birth time -> UTC.
    when_utc = (birth_local
                - _dt.timedelta(hours=tz_offset_hours)).replace(
                    tzinfo=_dt.timezone.utc)

    chart = E.build_chart(when_utc, lat, lon, system=system)

    print("=" * 64)
    print(f"{place}  |  system={system.upper()}")
    print(f"Local birth : {birth_local}  (UTC{tz_offset_hours:+})")
    print(f"Ayanamsa    : {chart.ayanamsa_name} = {chart.ayanamsa_value:.4f} deg")
    print(f"Ascendant   : {chart.ascendant.sign} "
          f"{chart.ascendant.degree_in_sign:.2f}  "
          f"({chart.ascendant.nakshatra}, sub={chart.ascendant.sub_lord})")
    print("-" * 64)
    print(f"{'Planet':10}{'Sign':12}{'Deg':>7}  {'House':>5}  "
          f"{'Nakshatra':16}{'Sub':8}{'R'}")
    order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter",
             "Venus", "Saturn", "Rahu", "Ketu"]
    for name in order:
        p = chart.planets[name]
        print(f"{p.name:10}{p.sign:12}{p.degree_in_sign:6.2f}  "
              f"{p.house:>5}  {p.nakshatra:16}{p.sub_lord:8}"
              f"{'R' if p.retrograde else ''}")
    print("-" * 64)
    b = chart.dasha_balance
    print(f"Dasha balance at birth: {b['starting_lord']} "
          f"({b['remaining_years']:.2f} of {b['total_years']} yrs remaining)")
    print("Mahadasha timeline:")
    for d in chart.vimshottari:
        print(f"   {d.lord:9} {d.start}  ->  {d.end}")
    print()


if __name__ == "__main__":
    # Mahatma Gandhi: 2 Oct 1869, 07:11 LMT, Porbandar (a widely-published chart).
    show(_dt.datetime(1869, 10, 2, 7, 11), 4.5 + 0.0,  # ~ +4:30 LMT approx
         21.6417, 69.6293, "M. Gandhi (Porbandar)", system="vedic")

    # Same birth, KP system, to show the ayanamsa/house difference.
    show(_dt.datetime(1869, 10, 2, 7, 11), 4.5,
         21.6417, 69.6293, "M. Gandhi (Porbandar)", system="kp")
