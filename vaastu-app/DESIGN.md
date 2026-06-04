# Vaastu Plot Survey App — Design Document

**Status:** Design v1
**Target device:** Redmi Note 15 Pro (Android / HyperOS)
**Platform:** Native Android — Kotlin + Jetpack Compose
**Positioning:** Phone GNSS + walk-correction (architected to accept an external RTK/DGPS receiver later)
**Direction model:** 16 Vaastu zones + precise degrees
**North reference:** Magnetic north
**Vertex capture:** Walk the perimeter and record each corner

---

## 1. Purpose & Scope

A field tool for surveying a building plot for Vaastu analysis. The surveyor walks the
plot, records its corners, and the app produces:

1. The **exact center** of the plot (area centroid / Brahmasthan).
2. A set of **boundary points spaced every 0.5 m** along all sides, plus every corner.
3. For **each** of those points: the **direction from the center** expressed as a 16-zone
   Vaastu direction **and** a precise bearing in degrees (magnetic north).
4. A live **walked-distance** readout from one vertex to the next, to verify each side is
   mapped to its true length.
5. An **elevation profile** while walking the borders and the interior, with a one-tap
   **capture & record** of elevation at any chosen spot.
6. Clean **Android runtime-permission handling** for GPS, camera, media, notifications, and
   (future) Bluetooth.

### Non-goals (v1)
- iOS support (Android-only as requested).
- Centimeter-grade survey accuracy without external hardware (see §3 — honest limits).
- Cloud sync / multi-user (local-first; export instead).

---

## 2. The Accuracy Reality (read this first)

This is the single most important constraint and it shapes every feature.

| Source | Typical accuracy | Implication for this app |
|---|---|---|
| Phone GNSS (Redmi Note 15 Pro, dual-band L1+L5) | **~1–4 m** horizontal in open sky | Cannot *directly* resolve 0.5 m spacing from a single fix |
| GNSS altitude | **~±5–15 m** absolute, noisy | Absolute elevation unreliable; relative profiling is usable |
| Magnetometer (compass) | **±2–10°**, sensitive to interference | Raw heading is jittery; we stabilize it |

**How we still deliver 0.5 m spacing and "exact sides":**

- The 0.5 m points are **computed geometrically** by interpolating along the line between two
  recorded corners — they are *derived*, not individually GNSS-sampled. So once the corners
  are good, the 0.5 m grid is mathematically exact relative to those corners.
- Corner accuracy is improved by **multi-sample averaging** (stand at the corner, the app
  averages N fixes weighted by reported accuracy) instead of a single tap.
- Side lengths are checked two ways: (a) straight-line distance between averaged corners, and
  (b) the integrated **walked distance** (§7). Agreement between the two is the quality signal.
- The location layer is abstracted behind a `PositionProvider` interface so a **Bluetooth RTK
  receiver** (cm-grade, NMEA/NTRIP) can be dropped in later with **no change** to the survey,
  geometry, or UI code.

The app will **always display the current fix accuracy** and color-code it so the surveyor
knows when a corner reading is trustworthy.

---

## 3. Domain Model

```
Project
  └─ Plot (one active survey)
       ├─ vertices: List<Vertex>          # ordered corners, polygon ring
       ├─ center: GeoPoint                # computed area centroid
       ├─ boundaryPoints: List<BndPoint>  # corners + 0.5 m interpolated points
       ├─ sides: List<Side>               # vertex[i] -> vertex[i+1]
       ├─ elevationSamples: List<ElevSample>   # continuous track
       └─ elevationMarks: List<ElevMark>       # user-captured points
```

### Core types
```kotlin
data class GeoPoint(val lat: Double, val lon: Double, val altM: Double?, val accM: Float)

data class Vertex(
    val index: Int,
    val point: GeoPoint,          // accuracy-weighted average of samples
    val sampleCount: Int,
    val rmsAccM: Float,           // quality of the averaged fix
    val capturedAt: Long
)

data class BndPoint(
    val localXY: Vec2,            // ENU meters relative to center
    val geo: GeoPoint,
    val isCorner: Boolean,
    val sideIndex: Int,
    val distanceFromCenterM: Double,
    val bearingMagDeg: Double,    // 0..360, magnetic north
    val vaastuZone: VaastuZone    // one of 16
)

data class Side(
    val from: Int, val to: Int,
    val straightLenM: Double,     // geometry between averaged corners
    val walkedLenM: Double?,      // integrated GPS path (verification)
    val deltaM: Double?           // |walked - straight|, the quality flag
)

data class ElevSample(val ts: Long, val geo: GeoPoint, val relElevM: Double, val source: ElevSource)
data class ElevMark(val id: String, val label: String, val geo: GeoPoint,
                    val relElevM: Double, val source: ElevSource,
                    val photoUri: String?, val note: String?)

enum class ElevSource { GNSS, BAROMETER, FUSED }
```

---

## 4. Geometry & Algorithms

All plot math is done in a **local ENU (East-North-Up) plane** centered on the plot, because a
plot is small (tens of meters) and a flat-Earth approximation introduces sub-millimeter error
at this scale — far below GNSS noise. Lat/lon is converted to local meters via an
equirectangular projection about a reference latitude.

### 4.1 Lat/Lon ↔ local meters
```
metersPerDegLat = 111_132.0
metersPerDegLon = 111_320.0 * cos(refLatRad)
east  = (lon - refLon) * metersPerDegLon
north = (lat - refLat) * metersPerDegLat
```
(Inverse for converting computed points back to geo.)

### 4.2 Center = polygon area centroid (Brahmasthan)
Not the average of vertices — the **area centroid**, which is the correct geometric center for
an irregular plot:
```
A  = ½ Σ (x_i·y_{i+1} − x_{i+1}·y_i)
Cx = 1/(6A) Σ (x_i + x_{i+1})(x_i·y_{i+1} − x_{i+1}·y_i)
Cy = 1/(6A) Σ (y_i + y_{i+1})(x_i·y_{i+1} − x_{i+1}·y_i)
```
We also display the vertex-mean center for reference and let the user pick which to treat as
the Vaastu center.

### 4.3 Boundary point generation (0.5 m)
For each side `Vi → Vi+1`:
```
L = |Vi+1 − Vi|
n = round(L / 0.5)                 # nearest whole number of 0.5 m steps
for k in 0..n:
    t = (k / n)
    P = Vi + t * (Vi+1 − Vi)       # linear interpolation in ENU
    emit BndPoint(P, isCorner = (k==0))
```
Corners are always included; the last point of a side equals the first point of the next, so it
is emitted once. Spacing is exactly `L/n` (≈0.5 m, snapped so corners land perfectly).

### 4.4 Direction from center (16 Vaastu zones + degrees)
For each boundary point `P` relative to center `C`:
```
dx = P.east − C.east
dy = P.north − C.north
bearingTrue = (atan2(dx, dy) in degrees) normalized to [0,360)   # 0°=N, clockwise
bearingMag  = normalize(bearingTrue − declination)               # GeomagneticField gives declination
zoneIndex   = round(bearingMag / 22.5) mod 16
```

**The 16 zones** (each 22.5° wide, centered on the listed bearing):

| Idx | Abbr | Center° | Vaastu zone (Sanskrit) | Lord |
|----|------|--------|------------------------|------|
| 0  | N    | 0      | Uttara / Kubera        | Kubera |
| 1  | NNE  | 22.5   | —                      | between Kubera & Ishanya |
| 2  | NE   | 45     | Ishanya                | Ishana (Shiva) |
| 3  | ENE  | 67.5   | —                      | between Ishanya & Indra |
| 4  | E    | 90     | Purva / Indra          | Indra |
| 5  | ESE  | 112.5  | —                      | between Indra & Agni |
| 6  | SE   | 135    | Agneya                 | Agni |
| 7  | SSE  | 157.5  | —                      | between Agni & Yama |
| 8  | S    | 180    | Dakshina / Yama        | Yama |
| 9  | SSW  | 202.5  | —                      | between Yama & Nairutya |
| 10 | SW   | 225    | Nairutya               | Nirayti |
| 11 | WSW  | 247.5  | —                      | between Nairutya & Varuna |
| 12 | W    | 270    | Paschima / Varuna      | Varuna |
| 13 | WNW  | 292.5  | —                      | between Varuna & Vayavya |
| 14 | NW   | 315    | Vayavya                | Vayu |
| 15 | NNW  | 337.5  | —                      | between Vayavya & Kubera |

> Note: because directions are tied to magnetic north (your choice), the app stores the
> magnetic declination used so results are reproducible. A toggle can switch the whole display
> to true north without re-surveying (it just re-labels using the stored declination).

### 4.5 Magnetic heading stabilization
- Prefer the **rotation-vector** virtual sensor (`TYPE_ROTATION_VECTOR`) over raw magnetometer
  — it sensor-fuses gyro + accel + mag and is far steadier.
- Apply a low-pass filter and show a **calibration prompt** (figure-8) when accuracy is
  `SENSOR_STATUS_UNRELIABLE/LOW`.
- For computing point bearings we do **not** depend on live heading — those come from GNSS
  geometry + declination, which is stable. The live compass is only for the on-screen "which
  way am I facing" overlay.

---

## 5. Feature: Survey Workflow

1. **New Plot** → name it.
2. **Walk to corner 1**, stand still; tap **Capture Corner**. App collects samples for a few
   seconds, shows live accuracy, and stores the accuracy-weighted average. Repeat for each
   corner in order (CW or CCW; app detects winding).
3. App closes the ring, computes center, generates the 0.5 m boundary grid, and computes every
   point's distance + Vaastu direction.
4. **Plan view** renders the polygon, center, the 0.5 m points (color-coded by zone), and a
   table/list of points with `distance | bearing° | zone`.
5. **Export** (§9).

Editing: a corner can be re-captured; long-press a point to inspect; drag-free (no manual
nudging in v1 to keep data honest, but a "re-walk side" action exists).

---

## 6. Feature: Side Walk — live distance vertex→vertex

Goal: confirm each side's real length while walking it.

- After corners are set, choose a side; the app enters **Walk Mode** for `Vi → Vi+1`.
- A **foreground location service** streams fixes (~1 Hz, high accuracy).
- Walked distance integrates inter-fix Haversine segments with **noise gating**:
  ```
  if segAcc good AND segDist > max(0.3 m, 0.5*(acc_a+acc_b)):  add segDist
  else: ignore (prevents GPS jitter inflating the total while standing still)
  ```
- HUD shows: **walked distance**, straight-line target length, live **Δ (difference)**, and a
  progress bar toward the target. Color: green when Δ small, amber/red as it grows.
- On finish, `Side.walkedLenM` and `deltaM` are saved as the side's quality record.

This is the "ensure sides are exactly mapped" guarantee: you see, in real time, walked vs.
geometric length, and large disagreement flags a bad corner fix to re-capture.

---

## 7. Feature: Elevation (track + capture)

**Sources, auto-selected:**
- Detect `Sensor.TYPE_PRESSURE` at startup. *Redmi Note 15 Pro has no barometer*, so the app
  will fall back to **GNSS altitude**. If a future device has a barometer, it's used and fused.
- All elevation is reported as **relative** to a chosen **datum** (default: the plot center, or
  first captured point). Relative elevation cancels most of the absolute GNSS-altitude bias and
  is what matters for Vaastu slope analysis (e.g., NE should be lower, SW higher).

**Continuous track:** while any walk/survey mode runs, `ElevSample`s are logged with smoothing
(moving median + EMA) to tame GNSS-altitude noise. A live **elevation profile chart** plots
relative elevation vs. distance/position, both along borders and across interior walks.

**Capture & record:** a prominent **"Mark Elevation"** button stores an `ElevMark` at the
current location with:
- relative + absolute elevation, source, accuracy,
- optional **photo** (camera) and **text note**,
- auto Vaastu zone of that spot relative to center.

Marks are listed and shown as pins on the plan view, and included in export. A **slope summary**
(direction of overall fall, NE-vs-SW comparison) is generated from the marks + track.

> Honesty: GNSS relative elevation over a small plot is rough (decimeter-to-meter scatter).
> The chart shows a confidence band. For precise slope, the design keeps a hook for an external
> level/RTK-height source. This is surfaced in the UI, not hidden.

---

## 8. Permissions (Android runtime flow)

Declared in `AndroidManifest.xml`:

| Permission | Why | Notes |
|---|---|---|
| `ACCESS_FINE_LOCATION` | precise GNSS for survey | runtime prompt |
| `ACCESS_COARSE_LOCATION` | required alongside fine | runtime prompt |
| `FOREGROUND_SERVICE` + `FOREGROUND_SERVICE_LOCATION` | keep tracking while screen off / walking | Android 14 requires the typed FGS |
| `POST_NOTIFICATIONS` | foreground-service notification (Android 13+) | runtime prompt |
| `CAMERA` | photos on elevation marks | runtime prompt |
| `READ_MEDIA_IMAGES` | attach existing photos (Android 13+) | replaces legacy `READ_EXTERNAL_STORAGE` |
| `BLUETOOTH_CONNECT` / `BLUETOOTH_SCAN` | **future** RTK receiver | declared, requested only when RTK enabled |
| `ACCESS_BACKGROUND_LOCATION` | only if background tracking is ever needed | **not** requested in v1 (foreground only) |

**UX flow (best-practice, MIUI/HyperOS-friendly):**
1. First-run **onboarding** screen explains each permission *before* asking (rationale-first).
2. Request location → if "Approximate only" granted, prompt to upgrade to **Precise**.
3. Request notifications (for the FGS), then camera/media lazily when first marking elevation.
4. A central **Permission Status** screen shows green/red chips with a one-tap re-request and a
   deep-link to **App Settings** for any "Don't ask again" denials.
5. Also nudge the user to enable **High Accuracy / Google Location Accuracy** and disable MIUI
   battery optimization for the app (HyperOS aggressively kills background work) — with a
   deep-link to those settings, since they materially affect GNSS quality.

---

## 9. Persistence & Export

- **Room** database (local-first): Projects, Plots, Vertices, BndPoints, Sides, ElevSamples,
  ElevMarks. Photos stored in app-scoped storage; URIs referenced.
- **Export formats:**
  - **CSV** — one row per boundary point: `idx, isCorner, side, distanceM, bearingMagDeg, vaastuZone, lat, lon`.
  - **GeoJSON / KML** — polygon + points + elevation marks, openable in Google Earth / QGIS.
  - **PDF report** — plan diagram, point table, side-length table (walked vs straight),
    elevation profile, slope summary, and per-zone direction sheet for Vaastu analysis.
- Share via Android share-sheet; save to user-picked folder via Storage Access Framework
  (no broad storage permission needed for export).

---

## 10. Architecture

Clean architecture + MVVM, single-module to start, package-by-feature.

```
com.vaastu.survey
├─ core/
│   ├─ geo/         GeoMath, EnuProjection, Geodesy, PolygonCentroid, BoundaryInterpolator
│   ├─ vaastu/      VaastuZone, ZoneMapper (bearing -> 16 zones)
│   └─ util/        filters (LowPass, MovingMedian, EMA), DistanceIntegrator
├─ data/
│   ├─ db/          Room entities, DAOs, database
│   ├─ repo/        PlotRepository, ElevationRepository
│   └─ export/      CsvExporter, GeoJsonExporter, KmlExporter, PdfReporter
├─ location/
│   ├─ PositionProvider (interface)         # <-- RTK-ready seam
│   ├─ FusedPositionProvider                # phone GNSS (Play Services)
│   ├─ RtkBluetoothPositionProvider (stub)  # future NMEA/NTRIP
│   ├─ LocationForegroundService
│   └─ SampleAverager (corner capture)
├─ sensors/
│   ├─ HeadingProvider (rotation-vector)
│   └─ ElevationProvider (pressure-or-GNSS, auto-select)
├─ permissions/    PermissionController, rationale UI, settings deep-links
├─ ui/  (Compose)
│   ├─ survey/      capture corners, plan view, point table
│   ├─ walk/        side walk HUD
│   ├─ elevation/   profile chart, marks list, capture sheet
│   ├─ map/         plan rendering (Canvas) + optional OSM map
│   └─ permissions/ onboarding + status screen
└─ MainActivity, AppNav
```

**Key seams**
- `PositionProvider` emits `Flow<GeoPoint>` — swapping phone GNSS for RTK is one binding change.
- `ElevationProvider` auto-selects barometer vs GNSS behind one interface.
- All geometry is pure Kotlin (no Android deps) → unit-testable without a device.

### Tech stack
- **Kotlin**, **Jetpack Compose** (Material 3), **Coroutines/Flow**.
- **Play Services Location** (`FusedLocationProviderClient`) for fused GNSS; option to use raw
  `LocationManager` + `GnssStatus` to read satellite count / dual-band for a quality meter.
- **Room** for storage; **DataStore** for settings.
- **MPAndroidChart** (or Compose-canvas) for the elevation profile.
- **osmdroid** for an offline-capable map tile background (optional; plan view works without it).
- **Hilt** for DI. **WorkManager** not needed in v1.
- Min SDK 26, target latest stable; tested on HyperOS.

---

## 11. Screens (UX)

1. **Onboarding / Permissions** — rationale-first, status chips.
2. **Home / Projects** — list, new plot, open, export.
3. **Survey (Capture Corners)** — live map/plan, accuracy meter, satellite count, big
   *Capture Corner* button, corner list with quality.
4. **Plan View** — polygon + center + 0.5 m points colored by zone; tap a point → distance,
   bearing°, zone; toggle table view.
5. **Side Walk HUD** — target vs walked vs Δ, progress, big numbers.
6. **Elevation** — live profile chart, *Mark Elevation* button, marks list with photos/notes,
   slope summary.
7. **Export / Report** — choose format, preview, share.
8. **Settings** — center type (centroid/mean), north reference, datum, units, RTK toggle.

---

## 12. Quality, Edge Cases, Testing

- **Bad fix guard:** corners refuse to save if averaged RMS accuracy worse than a threshold
  (configurable, default 4 m) without an explicit "save anyway".
- **Self-intersecting / out-of-order corners:** detect via winding/area sign; warn.
- **< 3 corners:** geometry disabled until a valid ring exists.
- **Magnetometer interference:** detect via sensor accuracy callback; prompt calibration; warn
  near metal/rebar.
- **HyperOS battery kill:** foreground service + user nudge to whitelist app.
- **Unit tests** (pure Kotlin): centroid, interpolation spacing, ENU round-trip, zone mapping at
  boundaries (e.g., 11.25° edges), distance integrator with synthetic noisy tracks.
- **Field test protocol:** survey a known rectangle (tape-measured) and compare app side lengths
  and the walked vs straight Δ.

---

## 13. Roadmap / Milestones

- **M1 — Foundation:** project scaffold, permissions flow, location service, accuracy meter.
- **M2 — Survey core:** corner capture + averaging, centroid, 0.5 m interpolation, zone mapping,
  plan view + point table.
- **M3 — Side walk:** foreground tracking, distance integrator, HUD, walked-vs-straight Δ.
- **M4 — Elevation:** provider auto-select, profile chart, mark-capture with photo/note, slope
  summary.
- **M5 — Export:** CSV/GeoJSON/KML + PDF report.
- **M6 — Polish & field test:** calibration prompts, HyperOS tuning, accuracy validation.
- **M7 (future) — RTK:** implement `RtkBluetoothPositionProvider` (NMEA + NTRIP) for cm-grade.

---

## 14. Open Items to Confirm Before Build

1. **Export priority** — is the **PDF Vaastu report** the main deliverable, or CSV/GeoJSON for
   use in other tools? (affects M5 scope)
2. **Map background** — fine to render the plan on a plain canvas (works offline, no API key),
   or do you want **Google Maps / OSM satellite** tiles behind it (needs network / key)?
3. **Units** — meters only, or also feet for side lengths?
4. **Center choice** — default to **area centroid** for the Vaastu center (recommended), with
   vertex-mean as an option? Confirm.
5. **Elevation datum** — relative to **plot center** (recommended) vs first captured point?

Answer these and M1–M2 can start immediately.
