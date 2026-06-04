package com.vaastu.survey.data

import android.content.Context
import com.vaastu.survey.core.geo.GeoPoint
import com.vaastu.survey.core.geo.VaastuZone
import com.vaastu.survey.data.db.AppDatabase
import com.vaastu.survey.data.db.ElevMarkEntity
import com.vaastu.survey.data.db.PlotEntity
import com.vaastu.survey.data.db.SideWalkEntity
import com.vaastu.survey.data.db.VertexEntity
import com.vaastu.survey.ui.CenterMode
import com.vaastu.survey.ui.ElevMarkUi
import com.vaastu.survey.ui.SurveyState
import com.vaastu.survey.ui.VertexUi

/** Snapshot loaded from the database to restore a survey on launch. */
data class SavedPlot(
    val name: String,
    val centerMode: CenterMode,
    val declinationDeg: Float,
    val vertices: List<VertexUi>,
    val sideWalks: Map<Int, Double>,
    val marks: List<ElevMarkUi>,
)

/** Persists the single current plot so a survey survives app restarts. */
class SurveyRepository(context: Context) {
    private val dao = AppDatabase.get(context).surveyDao()
    private val plotId = 1L

    suspend fun save(state: SurveyState) {
        val plot = PlotEntity(
            id = plotId,
            name = state.plotName,
            centerMode = state.centerMode.name,
            declinationDeg = state.declinationDeg,
            updatedAt = System.currentTimeMillis(),
        )
        val vertices = state.vertices.map { v ->
            VertexEntity(
                plotId = plotId,
                idx = v.index,
                lat = v.geo.lat,
                lon = v.geo.lon,
                alt = v.geo.altM,
                accM = v.geo.accM,
                sampleCount = v.sampleCount,
                rmsAccM = v.rmsAccM,
            )
        }
        val walks = state.sides.mapNotNull { s ->
            s.walkedM?.let { SideWalkEntity(plotId = plotId, fromIdx = s.from, walkedM = it) }
        }
        val marks = state.elevMarks.map { m ->
            ElevMarkEntity(
                id = m.id,
                plotId = plotId,
                label = m.label,
                lat = m.geo.lat,
                lon = m.geo.lon,
                alt = m.geo.altM,
                relElevM = m.relElevM,
                zoneOrdinal = m.zone?.ordinal ?: -1,
                note = m.note,
                photoPath = m.photoPath,
            )
        }
        dao.savePlot(plot, vertices, walks, marks)
    }

    suspend fun load(): SavedPlot? {
        val plot = dao.latestPlot() ?: return null
        val vertices = dao.verticesFor(plot.id).map { v ->
            VertexUi(
                index = v.idx,
                geo = GeoPoint(v.lat, v.lon, v.alt, v.accM),
                sampleCount = v.sampleCount,
                rmsAccM = v.rmsAccM,
            )
        }
        val walks = dao.sideWalksFor(plot.id).associate { it.fromIdx to it.walkedM }
        val marks = dao.marksFor(plot.id).map { m ->
            ElevMarkUi(
                id = m.id,
                label = m.label,
                geo = GeoPoint(m.lat, m.lon, m.alt),
                relElevM = m.relElevM,
                zone = m.zoneOrdinal.takeIf { it in 0..15 }?.let { VaastuZone.entries[it] },
                note = m.note,
                photoPath = m.photoPath,
            )
        }
        val centerMode = runCatching { CenterMode.valueOf(plot.centerMode) }
            .getOrDefault(CenterMode.CENTROID)
        return SavedPlot(plot.name, centerMode, plot.declinationDeg, vertices, walks, marks)
    }
}
