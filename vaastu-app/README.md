# Vaastu Survey (Android)

A field tool to survey a building plot for Vaastu: walk the corners, get the
exact center, generate boundary points every **0.5 m** with their **16-zone Vaastu
direction + degrees**, verify each side by walking it, and record elevation.

Built for the **Redmi Note 15 Pro** (Android 14/15, HyperOS). Native Kotlin +
Jetpack Compose. See [`DESIGN.md`](DESIGN.md) for the full design.

## Features (v1)

- **Survey:** capture each corner by standing on it and tapping *Capture* — the app
  averages ~8 GPS fixes (accuracy-weighted) for a steadier corner than a single tap.
- **Center:** polygon **area centroid** (Brahmasthan).
- **0.5 m boundary points + corners**, each with distance from center, **magnetic
  bearing**, and **Vaastu zone** (Ishanya, Agneya, … with Sanskrit + lord names).
- **Plan view:** tap any point to see its direction/distance; points colored by zone.
- **Walk a side:** live walked-distance vs straight-line length, with Δ to confirm
  the side is mapped correctly (GPS jitter while standing is filtered out).
- **Elevation:** relative-to-center elevation profile + one-tap **Mark elevation**
  with label/note and the spot's Vaastu zone. (Uses GNSS altitude; auto-uses a
  barometer if the device has one — the Note 15 Pro does not.)
- **Export:** CSV (points + directions) and GeoJSON (open in Google Earth / QGIS).
- **Permissions:** rationale-first prompt for precise location + notifications;
  camera/media declared for future photo marks.

> **Accuracy note:** phone GPS is ~1–4 m, so the 0.5 m grid is *derived geometry*
> from your averaged corners, not individually sampled. The location layer is behind
> a `PositionProvider` seam so an external **RTK receiver** (cm-grade) can be added
> later without changing the app. See `DESIGN.md` §2.

## Get the APK (no Android Studio needed)

Every push to this branch runs the **"Build Vaastu Survey APK"** GitHub Action.

1. On GitHub → **Actions** tab → open the latest *Build Vaastu Survey APK* run.
2. Download the **`vaastu-survey-debug-apk`** artifact (a zip).
3. Unzip to get `app-debug.apk`, copy it to your phone.
4. On the phone, tap the APK → allow **Install unknown apps** for your file
   manager/browser when prompted → install.
5. Open the app, grant **Precise** location, and survey.

## Build locally (optional)

Requires Android SDK (platform 35, build-tools 35.0.0) + JDK 17.

```bash
cd vaastu-app
./gradlew assembleDebug
# APK at app/build/outputs/apk/debug/app-debug.apk
```

## Field tips (HyperOS)

- Grant **Precise** (not Approximate) location.
- Enable **Google Location Accuracy** / High accuracy mode for better GPS.
- Exempt the app from MIUI/HyperOS battery optimization so tracking isn't killed.
- Calibrate the compass (figure-8) and stay clear of rebar/metal for headings.
