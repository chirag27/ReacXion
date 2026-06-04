package com.vaastu.survey.ui

import androidx.compose.ui.graphics.Color
import com.vaastu.survey.core.geo.VaastuZone
import java.util.Locale

/** Quality color for a GPS accuracy value (meters). */
fun accuracyColor(accM: Float): Color = when {
    accM <= 0f -> Color(0xFF9E9E9E)
    accM <= 4f -> Color(0xFF2E7D32) // good
    accM <= 8f -> Color(0xFFF9A825) // fair
    else -> Color(0xFFC62828) // poor
}

/** Distinct hue per Vaastu zone for the plan view. */
fun zoneColor(zone: VaastuZone): Color {
    val hue = (zone.ordinal * (360f / 16f))
    return Color.hsv(hue, 0.65f, 0.85f)
}

fun fmtM(m: Double): String = String.format(Locale.US, "%.2f m", m)

fun fmtMFt(m: Double): String =
    String.format(Locale.US, "%.2f m (%.2f ft)", m, m * 3.28084)

fun fmtDeg(d: Double): String = String.format(Locale.US, "%.1f°", d)
