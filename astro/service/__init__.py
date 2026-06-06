"""HTTP service exposing the deterministic engine + agent to clients (e.g. the
Android app). The app is the UI; this backend runs the engine."""

from .app import app, create_app

__all__ = ["app", "create_app"]
