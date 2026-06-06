# Jyotish Consult — Android app

A Jetpack Compose front-end for the Jyotish engine. The phone is the **UI**; the
deterministic engine runs in the Python **backend** (`astro/service`). The app
sends birth details to the backend and renders the chart, current dasha, yogas,
Lal Kitab debts/remedies, a birth-time confidence indicator, and answers from
the tool-calling agent.

> Why a backend? The engine depends on Swiss Ephemeris (a C extension), Chroma,
> and the Anthropic SDK, which don't run inside an APK. The app talks to a local
> FastAPI server that hosts the engine.

## 1. Run the backend (on your PC, same LAN as the phone)

```bash
cd astro
pip install -r requirements.txt
# optional, for the "Ask the agent" feature:
export ANTHROPIC_API_KEY=sk-ant-...
uvicorn service.app:app --host 0.0.0.0 --port 8000
```

Find your PC's LAN IP (e.g. `192.168.1.20`). The calculation features work
without an API key; only **Ask the agent** needs `ANTHROPIC_API_KEY`.

## 2. Build & run the app

1. Open `astro/android/` in **Android Studio** (Giraffe/Koala or newer).
2. Let it sync Gradle. (If the Gradle wrapper jar is missing, run
   `gradle wrapper --gradle-version 8.7` in this folder, or let Android Studio
   generate it.)
3. Run on an emulator or a device.

**Backend URL** in the app:
- Android **emulator** → `http://10.0.2.2:8000` (host loopback; the default).
- Physical **device** → `http://<your-PC-LAN-IP>:8000` (e.g. `http://192.168.1.20:8000`).

Cleartext HTTP to the local server is allowed via
`res/xml/network_security_config.xml` (development convenience — tighten for a
production deployment).

## What it calls

| Screen action | Endpoint |
|---|---|
| Generate reading | `POST /report` (chart, dasha, yogas, rinas, remedies, confidence) |
| Ask the agent | `POST /ask` (tool-calling agent; needs `ANTHROPIC_API_KEY`) |
| (startup, optional) | `GET /health` |

## Stack

Kotlin · Jetpack Compose (Material 3) · Retrofit + kotlinx.serialization ·
Coroutines. Min SDK 26, target SDK 34.

## Notes / limitations

- Versions in the Gradle files are known-good but may need a sync/bump for your
  installed Android Studio + AGP; adjust if prompted.
- This project is source-only here — it was authored on a machine without the
  Android SDK, so it has **not** been compiled into an APK. Build it in Android
  Studio.
