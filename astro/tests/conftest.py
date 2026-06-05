"""Pytest configuration: make the ``engine`` package importable.

Tests import ``engine`` and ``golden_charts`` directly, so the ``astro/``
project root is placed on ``sys.path`` regardless of where pytest is invoked.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) in sys.path:
    sys.path.remove(str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT))
