package com.vaastu.survey.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import com.vaastu.survey.core.geo.BndPoint
import com.vaastu.survey.core.geo.EnuProjection
import com.vaastu.survey.core.geo.Vec2
import java.util.Locale
import kotlin.math.hypot

@Composable
fun PlanScreen(vm: SurveyViewModel) {
    val state by vm.state.collectAsState()
    var selected by remember { mutableStateOf<Int?>(null) }

    val boundary = state.boundary
    val center = state.center
    if (boundary.size < 2 || center == null || state.vertices.isEmpty()) {
        Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
            Text("Plan view", style = MaterialTheme.typography.titleLarge)
            Text(
                "Capture at least 3 corners on the Survey tab to see the plan.",
                modifier = Modifier.padding(top = 16.dp),
            )
        }
        return
    }

    // Center in the same local frame as the boundary points (ref = first vertex).
    val ref = state.vertices.first().geo
    val proj = EnuProjection(ref.lat, ref.lon)
    val centerLocal = proj.toLocal(center)

    Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
        Text("Plan view", style = MaterialTheme.typography.titleLarge)

        Canvas(
            modifier = Modifier
                .fillMaxWidth()
                .height(360.dp)
                .pointerInput(boundary.size) {
                    detectTapGestures { tap ->
                        val t = transform(boundary, centerLocal, size.width.toFloat(), size.height.toFloat())
                        var best = -1
                        var bestD = Float.MAX_VALUE
                        boundary.forEachIndexed { i, p ->
                            val o = t.project(p.local)
                            val d = hypot(o.x - tap.x, o.y - tap.y)
                            if (d < bestD) { bestD = d; best = i }
                        }
                        selected = if (bestD < 48f) best else null
                    }
                },
        ) {
            val t = transform(boundary, centerLocal, size.width, size.height)

            // Plot outline (corners only, in order)
            val corners = boundary.filter { it.isCorner }
            if (corners.size >= 2) {
                val path = Path()
                corners.forEachIndexed { i, p ->
                    val o = t.project(p.local)
                    if (i == 0) path.moveTo(o.x, o.y) else path.lineTo(o.x, o.y)
                }
                path.close()
                drawPath(path, color = Color(0x220E5A4E))
                drawPath(path, color = Color(0xFF0E5A4E), style = Stroke(width = 3f))
            }

            // Boundary points colored by zone
            boundary.forEachIndexed { i, p ->
                val o = t.project(p.local)
                val r = if (p.isCorner) 7f else 4f
                drawCircle(zoneColor(p.zone), radius = r, center = o)
                if (selected == i) {
                    drawCircle(Color.Black, radius = r + 4f, center = o, style = Stroke(width = 2f))
                }
            }

            // Center marker + north arrow (up = local north)
            drawCircle(Color(0xFFC62828), radius = 8f, center = t.project(centerLocal))
            drawLine(Color.Black, Offset(24f, size.height - 24f), Offset(24f, size.height - 64f), strokeWidth = 3f)
            drawCircle(Color.Black, radius = 3f, center = Offset(24f, size.height - 64f))
        }

        Text(
            "Corners + 0.5 m points colored by 16 Vaastu zones; red = center. Up = true north. Tap a point.",
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.padding(top = 8.dp),
        )

        selected?.let { idx ->
            boundary.getOrNull(idx)?.let { p ->
                Card(modifier = Modifier.fillMaxWidth().padding(top = 12.dp)) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            if (p.isCorner) "Corner (side ${p.sideIndex + 1})" else "Point on side ${p.sideIndex + 1}",
                            style = MaterialTheme.typography.titleMedium,
                        )
                        Text("Direction: ${p.zone.abbr} — ${p.zone.sanskrit} (${p.zone.lord})")
                        Text("Bearing (magnetic): ${fmtDeg(p.bearingMagDeg)}")
                        Text("Distance from center: ${fmtMFt(p.distanceFromCenterM)}")
                        Text(
                            String.format(Locale.US, "Lat %.7f  Lon %.7f", p.geo.lat, p.geo.lon),
                            fontFamily = FontFamily.Monospace,
                            style = MaterialTheme.typography.bodySmall,
                        )
                    }
                }
            }
        }

        Text(
            "Total boundary points: ${boundary.size}",
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.padding(top = 12.dp),
        )
    }
}

private class PlanTransform(
    private val minE: Double,
    private val minN: Double,
    private val scale: Float,
    private val pad: Float,
    private val height: Float,
) {
    fun project(v: Vec2): Offset {
        val x = pad + ((v.east - minE) * scale).toFloat()
        val y = height - pad - ((v.north - minN) * scale).toFloat()
        return Offset(x, y)
    }
}

private fun transform(
    boundary: List<BndPoint>,
    center: Vec2,
    width: Float,
    height: Float,
): PlanTransform {
    val pad = 40f
    val es = boundary.map { it.local.east } + center.east
    val ns = boundary.map { it.local.north } + center.north
    val minE = es.min()
    val minN = ns.min()
    val spanE = (es.max() - minE).coerceAtLeast(1e-3)
    val spanN = (ns.max() - minN).coerceAtLeast(1e-3)
    val scale = minOf(
        ((width - 2 * pad) / spanE).toFloat(),
        ((height - 2 * pad) / spanN).toFloat(),
    ).coerceAtLeast(0.01f)
    return PlanTransform(minE, minN, scale, pad, height)
}
