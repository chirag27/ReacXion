package com.vaastu.survey.core.geo

import kotlin.math.max

/** A single boundary point with its direction from the plot center. */
data class BndPoint(
    val local: Vec2,
    val geo: GeoPoint,
    val isCorner: Boolean,
    val sideIndex: Int,
    val distanceFromCenterM: Double,
    val bearingMagDeg: Double,
    val zone: VaastuZone,
)

object Boundary {
    /**
     * Generates boundary points along the polygon ring, spaced ~[spacingM] apart,
     * with every corner included. Spacing on each side is snapped so corners land
     * exactly (each side gets a whole number of equal steps closest to [spacingM]).
     *
     * Directions are computed from [center]; [declinationDeg] converts the
     * geometry's true bearing to a magnetic bearing for display.
     */
    fun generate(
        verticesLocal: List<Vec2>,
        center: Vec2,
        proj: EnuProjection,
        declinationDeg: Float,
        spacingM: Double = 0.5,
    ): List<BndPoint> {
        val out = ArrayList<BndPoint>()
        val n = verticesLocal.size
        if (n < 2) return out
        for (i in 0 until n) {
            val a = verticesLocal[i]
            val b = verticesLocal[(i + 1) % n]
            val len = (b - a).length()
            val steps = max(1, Math.round(len / spacingM).toInt())
            // Emit start corner + interior points; the end corner is emitted by the next side.
            for (k in 0 until steps) {
                val t = k.toDouble() / steps
                val p = a + (b - a) * t
                out.add(makePoint(p, center, proj, declinationDeg, i, k == 0))
            }
        }
        return out
    }

    fun makePoint(
        p: Vec2,
        center: Vec2,
        proj: EnuProjection,
        declinationDeg: Float,
        sideIndex: Int,
        isCorner: Boolean,
    ): BndPoint {
        val bTrue = Bearing.fromCenter(center, p)
        val bMag = ((bTrue - declinationDeg) % 360 + 360) % 360
        val dist = (p - center).length()
        return BndPoint(p, proj.toGeo(p), isCorner, sideIndex, dist, bMag, VaastuZone.fromBearing(bMag))
    }
}
