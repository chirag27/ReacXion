package com.vaastu.survey.ui

import android.app.Application
import android.content.Intent
import android.hardware.GeomagneticField
import androidx.core.content.ContextCompat
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.vaastu.survey.core.geo.Bearing
import com.vaastu.survey.core.geo.BndPoint
import com.vaastu.survey.core.geo.Boundary
import com.vaastu.survey.core.geo.EnuProjection
import com.vaastu.survey.core.geo.Geo
import com.vaastu.survey.core.geo.GeoPoint
import com.vaastu.survey.core.geo.Polygon
import com.vaastu.survey.core.geo.VaastuZone
import com.vaastu.survey.core.geo.Vec2
import com.vaastu.survey.data.SavedPlot
import com.vaastu.survey.data.SurveyRepository
import com.vaastu.survey.location.LocationBus
import com.vaastu.survey.location.LocationForegroundService
import com.vaastu.survey.location.LocationSource
import com.vaastu.survey.sensors.HeadingProvider
import com.vaastu.survey.settings.AppSettings
import com.vaastu.survey.settings.SettingsStore
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.filterNotNull
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlin.math.abs
import kotlin.math.max
import kotlin.math.sqrt

data class VertexUi(
    val index: Int,
    val geo: GeoPoint,
    val sampleCount: Int,
    val rmsAccM: Float,
)

data class SideUi(
    val from: Int,
    val to: Int,
    val straightM: Double,
    val walkedM: Double?,
    val deltaM: Double?,
)

data class ElevMarkUi(
    val id: Long,
    val label: String,
    val geo: GeoPoint,
    val relElevM: Double,
    val zone: VaastuZone?,
    val note: String,
    val photoPath: String? = null,
)

enum class CenterMode { CENTROID, MEAN }

data class SurveyState(
    val plotName: String = "Plot 1",
    val location: GeoPoint? = null,
    val heading: Float = 0f,
    val hasBarometer: Boolean = false,
    val declinationDeg: Float = 0f,
    val centerMode: CenterMode = CenterMode.CENTROID,
    val locationSource: LocationSource = LocationSource.PHONE,
    val locationStatus: String = "Idle",
    val vertices: List<VertexUi> = emptyList(),
    val center: GeoPoint? = null,
    val boundary: List<BndPoint> = emptyList(),
    val sides: List<SideUi> = emptyList(),
    val areaM2: Double = 0.0,
    val perimeterM: Double = 0.0,
    val elevMarks: List<ElevMarkUi> = emptyList(),
    val elevDatumM: Double? = null,
    val currentRelElevM: Double? = null,
    val walkSideIndex: Int? = null,
    val walkWalkedM: Double = 0.0,
    val walkTargetM: Double = 0.0,
    val capturing: Boolean = false,
    val captureSamples: Int = 0,
)

class SurveyViewModel(app: Application) : AndroidViewModel(app) {

    private val appCtx: Application = app
    private val headingProvider = HeadingProvider(app)
    private val repo = SurveyRepository(app)
    private val settingsStore = SettingsStore(app)

    private val _state = MutableStateFlow(SurveyState())
    val state: StateFlow<SurveyState> = _state.asStateFlow()

    private val captureBuffer = mutableListOf<GeoPoint>()
    private var declinationSet = false
    private var walkLastPoint: GeoPoint? = null
    private var walkAccum = 0.0
    private var started = false
    private var settings = AppSettings()

    init {
        _state.update { it.copy(hasBarometer = headingProvider.hasPressureSensor()) }
        viewModelScope.launch {
            headingProvider.headingFlow().collect { h -> _state.update { it.copy(heading = h) } }
        }
        viewModelScope.launch {
            LocationBus.status.collect { s -> _state.update { it.copy(locationStatus = s) } }
        }
        viewModelScope.launch {
            settingsStore.settings.collect { s ->
                val changed = s != settings
                settings = s
                _state.update { it.copy(locationSource = s.source) }
                if (started && changed) startService()
            }
        }
        viewModelScope.launch {
            repo.load()?.let { restore(it) }
        }
    }

    /** Call once location permission is granted. Starts the FGS and observes fixes. */
    fun startLocation() {
        if (started) return
        started = true
        startService()
        viewModelScope.launch {
            LocationBus.positions.filterNotNull().collect { loc -> onLocation(loc) }
        }
    }

    private fun startService() {
        val intent = LocationForegroundService.intent(appCtx, settings.source, settings.rtkMac)
        ContextCompat.startForegroundService(appCtx, intent)
    }

    private fun restore(saved: SavedPlot) {
        if (_state.value.vertices.isNotEmpty()) return // don't clobber an in-progress survey
        if (saved.declinationDeg != 0f) declinationSet = true
        _state.update {
            it.copy(
                plotName = saved.name,
                centerMode = saved.centerMode,
                declinationDeg = saved.declinationDeg,
                vertices = saved.vertices,
                elevMarks = saved.marks,
            )
        }
        recompute()
        if (saved.sideWalks.isNotEmpty()) {
            _state.update { st ->
                st.copy(
                    sides = st.sides.map { s ->
                        saved.sideWalks[s.from]?.let { w -> s.copy(walkedM = w, deltaM = abs(w - s.straightM)) } ?: s
                    },
                )
            }
        }
    }

    private fun persist() {
        viewModelScope.launch { runCatching { repo.save(_state.value) } }
    }

    private fun onLocation(loc: GeoPoint) {
        _state.update { it.copy(location = loc) }
        if (!declinationSet) {
            val gf = GeomagneticField(
                loc.lat.toFloat(),
                loc.lon.toFloat(),
                (loc.altM ?: 0.0).toFloat(),
                if (loc.timestamp > 0) loc.timestamp else System.currentTimeMillis(),
            )
            declinationSet = true
            _state.update { it.copy(declinationDeg = gf.declination) }
        }
        if (_state.value.capturing) {
            captureBuffer.add(loc)
            _state.update { it.copy(captureSamples = captureBuffer.size) }
            if (captureBuffer.size >= TARGET_SAMPLES) finishCapture()
        }
        if (_state.value.walkSideIndex != null) integrateWalk(loc)
        updateElevation(loc)
    }

    // ---- Corner capture ----

    fun captureCorner() {
        if (_state.value.capturing || _state.value.location == null) return
        captureBuffer.clear()
        _state.update { it.copy(capturing = true, captureSamples = 0) }
    }

    fun cancelCapture() {
        captureBuffer.clear()
        _state.update { it.copy(capturing = false, captureSamples = 0) }
    }

    private fun finishCapture() {
        val samples = captureBuffer.toList()
        captureBuffer.clear()
        if (samples.isEmpty()) {
            _state.update { it.copy(capturing = false, captureSamples = 0) }
            return
        }
        var wsum = 0.0
        var lat = 0.0
        var lon = 0.0
        var alt = 0.0
        var altW = 0.0
        var accSq = 0.0
        for (s in samples) {
            val acc = max(1f, s.accM).toDouble()
            val w = 1.0 / (acc * acc)
            wsum += w
            lat += s.lat * w
            lon += s.lon * w
            s.altM?.let { alt += it * w; altW += w }
            accSq += (s.accM.toDouble() * s.accM.toDouble())
        }
        lat /= wsum
        lon /= wsum
        val avgAlt = if (altW > 0) alt / altW else null
        val rms = sqrt(accSq / samples.size).toFloat()
        val geo = GeoPoint(lat, lon, avgAlt, rms, System.currentTimeMillis())
        val idx = _state.value.vertices.size
        _state.update {
            it.copy(
                vertices = it.vertices + VertexUi(idx, geo, samples.size, rms),
                capturing = false,
                captureSamples = 0,
            )
        }
        recompute()
        persist()
    }

    fun undoLastVertex() {
        val verts = _state.value.vertices
        if (verts.isEmpty()) return
        _state.update {
            it.copy(vertices = verts.dropLast(1).mapIndexed { i, v -> v.copy(index = i) })
        }
        recompute()
        persist()
    }

    fun resetPlot() {
        captureBuffer.clear()
        walkLastPoint = null
        walkAccum = 0.0
        _state.update {
            SurveyState(
                hasBarometer = it.hasBarometer,
                declinationDeg = it.declinationDeg,
                location = it.location,
                heading = it.heading,
                centerMode = it.centerMode,
                locationSource = it.locationSource,
                locationStatus = it.locationStatus,
            )
        }
        persist()
    }

    fun setCenterMode(mode: CenterMode) {
        _state.update { it.copy(centerMode = mode) }
        recompute()
        persist()
    }

    fun setPlotName(name: String) {
        _state.update { it.copy(plotName = name) }
        persist()
    }

    // ---- Settings / source ----

    fun setSource(source: LocationSource) {
        viewModelScope.launch { settingsStore.setSource(source) }
    }

    fun setRtkMac(mac: String?) {
        viewModelScope.launch { settingsStore.setRtkMac(mac) }
    }

    // ---- Geometry recompute ----

    private fun recompute() {
        val verts = _state.value.vertices
        if (verts.isEmpty()) {
            _state.update {
                it.copy(
                    center = null, boundary = emptyList(), sides = emptyList(),
                    areaM2 = 0.0, perimeterM = 0.0, elevDatumM = null,
                )
            }
            return
        }
        val ref = verts.first().geo
        val proj = EnuProjection(ref.lat, ref.lon)
        val local = verts.map { proj.toLocal(it.geo) }
        val center = when {
            local.size >= 3 && _state.value.centerMode == CenterMode.CENTROID -> Polygon.areaCentroid(local)
            else -> Polygon.mean(local)
        }
        val centerGeo = proj.toGeo(center)
        val decl = _state.value.declinationDeg
        val boundary = if (local.size >= 2) Boundary.generate(local, center, proj, decl) else emptyList()
        val sides = buildSides(local)
        val area = Polygon.area(local)
        val perim = if (local.size >= 3) Polygon.perimeter(local) else 0.0
        val datum = verts.mapNotNull { it.geo.altM }.takeIf { it.isNotEmpty() }?.average()
        _state.update {
            it.copy(
                center = centerGeo, boundary = boundary, sides = sides,
                areaM2 = area, perimeterM = perim, elevDatumM = datum,
            )
        }
    }

    private fun buildSides(local: List<Vec2>): List<SideUi> {
        val n = local.size
        if (n < 2) return emptyList()
        val prev = _state.value.sides.associateBy { it.from }
        val count = if (n >= 3) n else n - 1
        val list = ArrayList<SideUi>()
        for (i in 0 until count) {
            val a = i
            val b = (i + 1) % n
            val straight = (local[b] - local[a]).length()
            val walked = prev[a]?.walkedM
            val delta = walked?.let { abs(it - straight) }
            list.add(SideUi(a, b, straight, walked, delta))
        }
        return list
    }

    // ---- Side walk ----

    fun startWalk(sideIndex: Int) {
        val side = _state.value.sides.getOrNull(sideIndex) ?: return
        walkLastPoint = null
        walkAccum = 0.0
        _state.update {
            it.copy(walkSideIndex = sideIndex, walkWalkedM = 0.0, walkTargetM = side.straightM)
        }
    }

    fun stopWalk(save: Boolean) {
        val si = _state.value.walkSideIndex ?: return
        if (save) {
            val walked = walkAccum
            val sides = _state.value.sides.toMutableList()
            val s = sides[si]
            sides[si] = s.copy(walkedM = walked, deltaM = abs(walked - s.straightM))
            _state.update { it.copy(sides = sides) }
            persist()
        }
        walkLastPoint = null
        _state.update { it.copy(walkSideIndex = null) }
    }

    private fun integrateWalk(loc: GeoPoint) {
        val lp = walkLastPoint
        if (lp == null) {
            walkLastPoint = loc
            return
        }
        val seg = Geo.haversine(lp, loc)
        val gate = max(0.3, 0.5 * (lp.accM + loc.accM).toDouble())
        if (seg > gate) {
            walkAccum += seg
            walkLastPoint = loc
            _state.update { it.copy(walkWalkedM = walkAccum) }
        }
    }

    // ---- Elevation ----

    private fun updateElevation(loc: GeoPoint) {
        val datum = _state.value.elevDatumM
        val alt = loc.altM
        if (datum != null && alt != null) {
            _state.update { it.copy(currentRelElevM = alt - datum) }
        }
    }

    fun markElevation(label: String, note: String, photoPath: String? = null) {
        val loc = _state.value.location ?: return
        val rel = _state.value.currentRelElevM ?: 0.0
        val center = _state.value.center
        val zone = if (center != null) {
            val proj = EnuProjection(center.lat, center.lon)
            val p = proj.toLocal(loc)
            val bTrue = Bearing.fromCenter(Vec2(0.0, 0.0), p)
            val bMag = ((bTrue - _state.value.declinationDeg) % 360 + 360) % 360
            VaastuZone.fromBearing(bMag)
        } else {
            null
        }
        val label2 = label.ifBlank { "Mark ${_state.value.elevMarks.size + 1}" }
        val mark = ElevMarkUi(System.currentTimeMillis(), label2, loc, rel, zone, note, photoPath)
        _state.update { it.copy(elevMarks = it.elevMarks + mark) }
        persist()
    }

    fun deleteMark(id: Long) {
        _state.update { it.copy(elevMarks = it.elevMarks.filterNot { m -> m.id == id }) }
        persist()
    }

    override fun onCleared() {
        appCtx.stopService(Intent(appCtx, LocationForegroundService::class.java))
        super.onCleared()
    }

    companion object {
        const val TARGET_SAMPLES = 8
    }
}
