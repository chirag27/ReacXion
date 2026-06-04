package com.vaastu.survey.ui

import android.app.Application
import android.hardware.GeomagneticField
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
import com.vaastu.survey.location.LocationRepository
import com.vaastu.survey.sensors.HeadingProvider
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
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
)

enum class CenterMode { CENTROID, MEAN }

data class SurveyState(
    val plotName: String = "Plot 1",
    val location: GeoPoint? = null,
    val heading: Float = 0f,
    val hasBarometer: Boolean = false,
    val declinationDeg: Float = 0f,
    val centerMode: CenterMode = CenterMode.CENTROID,
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

    private val locationRepo = LocationRepository(app)
    private val headingProvider = HeadingProvider(app)

    private val _state = MutableStateFlow(SurveyState())
    val state: StateFlow<SurveyState> = _state.asStateFlow()

    private val captureBuffer = mutableListOf<GeoPoint>()
    private var declinationSet = false
    private var walkLastPoint: GeoPoint? = null
    private var walkAccum = 0.0
    private var collecting = false

    init {
        _state.update { it.copy(hasBarometer = headingProvider.hasPressureSensor()) }
        viewModelScope.launch {
            headingProvider.headingFlow().collect { h ->
                _state.update { it.copy(heading = h) }
            }
        }
    }

    /** Call once location permission is granted. Safe to call again (no-op). */
    fun startLocation() {
        if (collecting) return
        collecting = true
        viewModelScope.launch {
            locationRepo.locationFlow().collect { loc -> onLocation(loc) }
        }
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
    }

    fun undoLastVertex() {
        val verts = _state.value.vertices
        if (verts.isEmpty()) return
        _state.update {
            it.copy(vertices = verts.dropLast(1).mapIndexed { i, v -> v.copy(index = i) })
        }
        recompute()
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
            )
        }
    }

    fun setCenterMode(mode: CenterMode) {
        _state.update { it.copy(centerMode = mode) }
        recompute()
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
        val count = if (n >= 3) n else n - 1 // only close the ring for a polygon
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

    fun markElevation(label: String, note: String) {
        val loc = _state.value.location ?: return
        val rel = _state.value.currentRelElevM ?: 0.0
        val center = _state.value.center
        val zone = if (center != null) {
            val proj = EnuProjection(center.lat, center.lon)
            val p = proj.toLocal(loc) // offset from center
            val bTrue = Bearing.fromCenter(Vec2(0.0, 0.0), p)
            val bMag = ((bTrue - _state.value.declinationDeg) % 360 + 360) % 360
            VaastuZone.fromBearing(bMag)
        } else {
            null
        }
        val label2 = label.ifBlank { "Mark ${_state.value.elevMarks.size + 1}" }
        val mark = ElevMarkUi(System.currentTimeMillis(), label2, loc, rel, zone, note)
        _state.update { it.copy(elevMarks = it.elevMarks + mark) }
    }

    fun deleteMark(id: Long) {
        _state.update { it.copy(elevMarks = it.elevMarks.filterNot { m -> m.id == id }) }
    }

    fun setPlotName(name: String) {
        _state.update { it.copy(plotName = name) }
    }

    companion object {
        const val TARGET_SAMPLES = 8 // ~8 fixes (~8 s) averaged per corner
    }
}
