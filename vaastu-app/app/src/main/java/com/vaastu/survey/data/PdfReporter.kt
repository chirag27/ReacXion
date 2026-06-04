package com.vaastu.survey.data

import android.graphics.Color
import android.graphics.Paint
import android.graphics.pdf.PdfDocument
import com.vaastu.survey.core.geo.BndPoint
import com.vaastu.survey.core.geo.EnuProjection
import com.vaastu.survey.core.geo.Vec2
import com.vaastu.survey.ui.SurveyState
import java.io.ByteArrayOutputStream
import java.util.Locale

private const val W = 595 // A4 @ 72dpi
private const val H = 842
private const val MARGIN = 40f
private const val LINE = 16f

/** Renders a multi-page PDF Vaastu report (plan diagram + tables). */
object PdfReporter {

    fun generate(state: SurveyState): ByteArray {
        val doc = PdfDocument()
        val ctx = RenderCtx(doc)

        ctx.newPage()
        ctx.heading("Vaastu Survey Report")
        ctx.text("Plot: ${state.plotName}")
        state.center?.let {
            ctx.text(String.format(Locale.US, "Center: %.7f, %.7f", it.lat, it.lon))
        }
        ctx.text(String.format(Locale.US, "Area: %.1f m²   Perimeter: %.2f m", state.areaM2, state.perimeterM))
        ctx.text(String.format(Locale.US, "Magnetic declination: %.1f°   Boundary points: %d", state.declinationDeg, state.boundary.size))
        ctx.gap()

        drawPlan(ctx, state)

        // Sides table
        ctx.newPage()
        ctx.heading("Sides (straight vs walked)")
        ctx.row("Side", "Straight (m)", "Walked (m)", "Δ (m)")
        state.sides.forEachIndexed { i, s ->
            ctx.row(
                "${i + 1}: ${s.from + 1}→${s.to + 1}",
                String.format(Locale.US, "%.2f", s.straightM),
                s.walkedM?.let { String.format(Locale.US, "%.2f", it) } ?: "-",
                s.deltaM?.let { String.format(Locale.US, "%.2f", it) } ?: "-",
            )
        }
        ctx.gap()

        // Boundary point table
        ctx.heading("Boundary points (direction from center)")
        ctx.row("#", "Dist (m)", "Bearing°", "Zone")
        state.boundary.forEachIndexed { i, p ->
            ctx.row(
                if (p.isCorner) "${i} *" else "$i",
                String.format(Locale.US, "%.2f", p.distanceFromCenterM),
                String.format(Locale.US, "%.1f", p.bearingMagDeg),
                "${p.zone.abbr} (${p.zone.sanskrit})",
            )
        }

        if (state.elevMarks.isNotEmpty()) {
            ctx.gap()
            ctx.heading("Elevation marks (relative to center)")
            ctx.row("Label", "Rel elev (m)", "Zone", "Note")
            state.elevMarks.forEach { m ->
                ctx.row(
                    m.label,
                    String.format(Locale.US, "%+.2f", m.relElevM),
                    m.zone?.abbr ?: "-",
                    m.note.take(28),
                )
            }
        }

        ctx.finish()
        val out = ByteArrayOutputStream()
        doc.writeTo(out)
        doc.close()
        return out.toByteArray()
    }

    private fun drawPlan(ctx: RenderCtx, state: SurveyState) {
        val boundary = state.boundary
        val center = state.center
        if (boundary.size < 2 || center == null || state.vertices.isEmpty()) {
            ctx.text("(Plan diagram needs at least 3 corners.)")
            return
        }
        ctx.heading("Plan")
        val proj = EnuProjection(state.vertices.first().geo.lat, state.vertices.first().geo.lon)
        val centerLocal = proj.toLocal(center)
        val top = ctx.y
        val areaH = 360f
        val es = boundary.map { it.local.east } + centerLocal.east
        val ns = boundary.map { it.local.north } + centerLocal.north
        val minE = es.min()
        val minN = ns.min()
        val spanE = (es.max() - minE).coerceAtLeast(1e-3)
        val spanN = (ns.max() - minN).coerceAtLeast(1e-3)
        val scale = minOf((W - 2 * MARGIN) / spanE, (areaH - 20) / spanN).coerceAtLeast(0.01)

        fun px(v: Vec2): Pair<Float, Float> {
            val x = MARGIN + ((v.east - minE) * scale).toFloat()
            val yy = top + areaH - ((v.north - minN) * scale).toFloat()
            return x to yy
        }

        val canvas = ctx.canvas
        val line = Paint().apply { color = Color.rgb(14, 90, 78); strokeWidth = 2f; style = Paint.Style.STROKE }
        val corners = boundary.filter { it.isCorner }
        for (i in corners.indices) {
            val (x1, y1) = px(corners[i].local)
            val (x2, y2) = px(corners[(i + 1) % corners.size].local)
            canvas.drawLine(x1, y1, x2, y2, line)
        }
        val dot = Paint().apply { color = Color.DKGRAY; style = Paint.Style.FILL }
        boundary.forEach { p ->
            val (x, yy) = px(p.local)
            canvas.drawCircle(x, yy, if (p.isCorner) 3.5f else 2f, dot)
        }
        val cPaint = Paint().apply { color = Color.RED; style = Paint.Style.FILL }
        val (cx, cy) = px(centerLocal)
        canvas.drawCircle(cx, cy, 4f, cPaint)
        ctx.y = top + areaH + LINE
    }

    private class RenderCtx(val doc: PdfDocument) {
        private var page: PdfDocument.Page? = null
        lateinit var canvas: android.graphics.Canvas
        var y = MARGIN
        private val textPaint = Paint().apply { color = Color.BLACK; textSize = 11f }
        private val headPaint = Paint().apply { color = Color.rgb(14, 90, 78); textSize = 15f; isFakeBoldText = true }

        fun newPage() {
            finish()
            val info = PdfDocument.PageInfo.Builder(W, H, doc.pages.size + 1).create()
            page = doc.startPage(info)
            canvas = page!!.canvas
            y = MARGIN
        }

        fun ensureSpace() {
            if (y > H - MARGIN) newPage()
        }

        fun heading(t: String) {
            ensureSpace()
            canvas.drawText(t, MARGIN, y, headPaint)
            y += LINE + 4
        }

        fun text(t: String) {
            ensureSpace()
            canvas.drawText(t, MARGIN, y, textPaint)
            y += LINE
        }

        fun row(a: String, b: String, c: String, d: String) {
            ensureSpace()
            canvas.drawText(a, MARGIN, y, textPaint)
            canvas.drawText(b, MARGIN + 150, y, textPaint)
            canvas.drawText(c, MARGIN + 280, y, textPaint)
            canvas.drawText(d, MARGIN + 380, y, textPaint)
            y += LINE
        }

        fun gap() { y += LINE }

        fun finish() {
            page?.let { doc.finishPage(it); page = null }
        }
    }
}
