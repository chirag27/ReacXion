package com.vaastu.survey.data

import com.vaastu.survey.ui.SurveyState
import java.util.Locale

/** Serializes a survey to CSV and GeoJSON for use in Vaastu analysis or GIS tools. */
object Exporters {

    fun csv(state: SurveyState): String {
        val sb = StringBuilder()
        sb.append("# Vaastu Survey: ").append(state.plotName).append('\n')
        state.center?.let {
            sb.append(
                String.format(
                    Locale.US,
                    "# Center,%.7f,%.7f,area_m2=%.2f,perimeter_m=%.2f,declination_deg=%.2f\n",
                    it.lat, it.lon, state.areaM2, state.perimeterM, state.declinationDeg,
                ),
            )
        }
        sb.append("idx,isCorner,side,distanceM,bearingMagDeg,zone,zoneSanskrit,lat,lon\n")
        state.boundary.forEachIndexed { i, p ->
            sb.append(
                String.format(
                    Locale.US,
                    "%d,%b,%d,%.3f,%.1f,%s,%s,%.7f,%.7f\n",
                    i, p.isCorner, p.sideIndex, p.distanceFromCenterM,
                    p.bearingMagDeg, p.zone.abbr, p.zone.sanskrit, p.geo.lat, p.geo.lon,
                ),
            )
        }
        if (state.elevMarks.isNotEmpty()) {
            sb.append("\n# Elevation marks\n")
            sb.append("label,relElevM,zone,lat,lon,note\n")
            state.elevMarks.forEach { m ->
                sb.append(
                    String.format(
                        Locale.US,
                        "%s,%.2f,%s,%.7f,%.7f,%s\n",
                        m.label, m.relElevM, m.zone?.abbr ?: "-", m.geo.lat, m.geo.lon,
                        m.note.replace(",", ";"),
                    ),
                )
            }
        }
        return sb.toString()
    }

    fun geoJson(state: SurveyState): String {
        val features = StringBuilder()

        // Polygon ring
        if (state.vertices.size >= 3) {
            val ring = StringBuilder("[")
            state.vertices.forEach { v ->
                ring.append(String.format(Locale.US, "[%.7f,%.7f],", v.geo.lon, v.geo.lat))
            }
            val first = state.vertices.first().geo
            ring.append(String.format(Locale.US, "[%.7f,%.7f]", first.lon, first.lat))
            ring.append("]")
            features.append(
                """{"type":"Feature","properties":{"name":"plot","area_m2":${"%.2f".format(Locale.US, state.areaM2)}},"geometry":{"type":"Polygon","coordinates":[$ring]}},""",
            )
        }

        // Center
        state.center?.let {
            features.append(
                """{"type":"Feature","properties":{"name":"center"},"geometry":{"type":"Point","coordinates":[${"%.7f".format(Locale.US, it.lon)},${"%.7f".format(Locale.US, it.lat)}]}},""",
            )
        }

        // Boundary points
        state.boundary.forEach { p ->
            features.append(
                """{"type":"Feature","properties":{"corner":${p.isCorner},"distance_m":${"%.3f".format(Locale.US, p.distanceFromCenterM)},"bearing_mag_deg":${"%.1f".format(Locale.US, p.bearingMagDeg)},"zone":"${p.zone.abbr}"},"geometry":{"type":"Point","coordinates":[${"%.7f".format(Locale.US, p.geo.lon)},${"%.7f".format(Locale.US, p.geo.lat)}]}},""",
            )
        }

        // Elevation marks
        state.elevMarks.forEach { m ->
            features.append(
                """{"type":"Feature","properties":{"name":"${escape(m.label)}","rel_elev_m":${"%.2f".format(Locale.US, m.relElevM)},"zone":"${m.zone?.abbr ?: ""}","note":"${escape(m.note)}"},"geometry":{"type":"Point","coordinates":[${"%.7f".format(Locale.US, m.geo.lon)},${"%.7f".format(Locale.US, m.geo.lat)}]}},""",
            )
        }

        val body = features.toString().trimEnd(',')
        return """{"type":"FeatureCollection","name":"${escape(state.plotName)}","features":[$body]}"""
    }

    private fun escape(s: String): String =
        s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", " ")
}
