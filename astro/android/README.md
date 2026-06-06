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

## Get the APK from GitHub (no Android Studio needed)

CI builds the APK on every push and **publishes it to a GitHub Release** with a
stable, non-expiring link:

- **Latest build:** repo → **Releases** → **Jyotish Consult — latest build**
  (tag `android-latest`) → download `app-debug.apk`.
  Direct: `https://github.com/chirag27/ReacXion/releases/download/android-latest/app-debug.apk`
- **Versioned release:** push a tag like `android-v1.0` to cut a permanent
  release with the same assets.

The build also uploads the APK(s) as a workflow **artifact** (expires after 90
days) — use the Release link for the durable one.

## Signed release APK (your keystore)

The debug APK is fine for sideloading. For a **signed release** APK (required to
publish on Play, and for stable update signing), configure these as GitHub
**repository secrets** (Settings → Secrets and variables → Actions):

| Secret | What it is |
|---|---|
| `ANDROID_KEYSTORE_BASE64` | your keystore file, base64-encoded |
| `ANDROID_KEYSTORE_PASSWORD` | keystore (store) password |
| `ANDROID_KEY_ALIAS` | key alias |
| `ANDROID_KEY_PASSWORD` | key password |

Generate a keystore once and keep it safe (losing it means you can't ship app
updates under the same identity):

```bash
keytool -genkeypair -v -keystore release.keystore \
  -alias jyotish -keyalg RSA -keysize 2048 -validity 10000

# base64 for the secret (Linux):  base64 -w0 release.keystore
# (macOS):                        base64 -i release.keystore | tr -d '\n'
```

Add the four secrets, then re-run the **Build Android APK** workflow. When the
secrets are present, CI builds `app-release.apk` (signed) and attaches it to the
Release alongside the debug APK; when they're absent, only the debug APK is
built and published. Nothing secret is committed to the repo — the keystore
lives only in your encrypted GitHub secrets and the ephemeral runner.

## Stack

Kotlin · Jetpack Compose (Material 3) · Retrofit + kotlinx.serialization ·
Coroutines. Min SDK 26, target SDK 34.

## Notes / limitations

- Versions in the Gradle files are known-good but may need a sync/bump for your
  installed Android Studio + AGP; adjust if prompted.
- This project is source-only here — it was authored on a machine without the
  Android SDK, so it has **not** been compiled into an APK. Build it in Android
  Studio.
