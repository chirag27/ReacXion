package com.vaastu.survey.core.geo

import kotlin.math.abs
import kotlin.math.asin
import kotlin.math.atan2
import kotlin.math.cos
import kotlin.math.hypot
import kotlin.math.min
import kotlin.math.pow
import kotlin.math.sin
import kotlin.math.sqrt

/** A geographic fix. accM is the reported horizontal accuracy (meters, 68% conf). */
data class GeoPoint(
    val lat: Double,
    val lon: Double,
    val altM: Double? = null,
    val accM: Float = 0f,
    val timestamp: Long = 0L,
)

/** A point in the local East-North plane, meters. */
data class Vec2(val east: Double, val north: Double) {
    operator fun minus(o: Vec2) = Vec2(east - o.east, north - o.north)
    operator fun plus(o: Vec2) = Vec2(east + o.east, north + o.north)
    operator fun times(s: Double) = Vec2(east * s, north * s)
    fun length() = hypot(east, north)
}

/**
 * Equirectangular projection about a reference point. Valid for small areas
 * (a plot of tens of meters) where curvature error is far below GNSS noise.
 */
class EnuProjection(private val refLat: Double, private val refLon: Double) {
    private val mPerDegLat = 111_132.0
    private val mPerDegLon = 111_320.0 * cos(Math.toRadians(refLat))

    fun toLocal(p: GeoPoint): Vec2 = Vec2(
        east = (p.lon - refLon) * mPerDegLon,
        north = (p.lat - refLat) * mPerDegLat,
    )

    fun toGeo(v: Vec2): GeoPoint = GeoPoint(
        lat = refLat + v.north / mPerDegLat,
        lon = refLon + v.east / mPerDegLon,
    )
}

object Geo {
    private const val R = 6_371_000.0

    /** Great-circle distance in meters between two fixes. */
    fun haversine(a: GeoPoint, b: GeoPoint): Double {
        val dLat = Math.toRadians(b.lat - a.lat)
        val dLon = Math.toRadians(b.lon - a.lon)
        val la1 = Math.toRadians(a.lat)
        val la2 = Math.toRadians(b.lat)
        val h = sin(dLat / 2).pow(2) + cos(la1) * cos(la2) * sin(dLon / 2).pow(2)
        return 2 * R * asin(min(1.0, sqrt(h)))
    }
}

object Bearing {
    /** Bearing (deg, 0=N, clockwise) from [center] to [p] in the local plane. */
    fun fromCenter(center: Vec2, p: Vec2): Double {
        val dx = p.east - center.east
        val dy = p.north - center.north
        val deg = Math.toDegrees(atan2(dx, dy))
        return (deg % 360 + 360) % 360
    }
}

object Polygon {
    /** Mean of vertices (a simple "center of vertices"). */
    fun mean(pts: List<Vec2>): Vec2 =
        Vec2(pts.map { it.east }.average(), pts.map { it.north }.average())

    /** Signed-area centroid — the true geometric center used as the Vaastu Brahmasthan. */
    fun areaCentroid(pts: List<Vec2>): Vec2 {
        if (pts.size < 3) return mean(pts)
        var a = 0.0
        var cx = 0.0
        var cy = 0.0
        for (i in pts.indices) {
            val p0 = pts[i]
            val p1 = pts[(i + 1) % pts.size]
            val cross = p0.east * p1.north - p1.east * p0.north
            a += cross
            cx += (p0.east + p1.east) * cross
            cy += (p0.north + p1.north) * cross
        }
        a *= 0.5
        if (abs(a) < 1e-9) return mean(pts)
        return Vec2(cx / (6 * a), cy / (6 * a))
    }

    /** Absolute polygon area in m^2. */
    fun area(pts: List<Vec2>): Double {
        if (pts.size < 3) return 0.0
        var a = 0.0
        for (i in pts.indices) {
            val p0 = pts[i]
            val p1 = pts[(i + 1) % pts.size]
            a += p0.east * p1.north - p1.east * p0.north
        }
        return abs(a * 0.5)
    }

    /** Closed-ring perimeter in meters. */
    fun perimeter(pts: List<Vec2>): Double {
        if (pts.size < 2) return 0.0
        var s = 0.0
        for (i in pts.indices) s += (pts[(i + 1) % pts.size] - pts[i]).length()
        return s
    }
}
