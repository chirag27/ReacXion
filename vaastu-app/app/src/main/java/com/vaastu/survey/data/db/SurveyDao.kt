package com.vaastu.survey.data.db

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Transaction

@Dao
interface SurveyDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertPlot(plot: PlotEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertVertices(vertices: List<VertexEntity>)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertSideWalks(walks: List<SideWalkEntity>)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertMarks(marks: List<ElevMarkEntity>)

    @Query("DELETE FROM vertices WHERE plotId = :plotId")
    suspend fun clearVertices(plotId: Long)

    @Query("DELETE FROM side_walks WHERE plotId = :plotId")
    suspend fun clearSideWalks(plotId: Long)

    @Query("DELETE FROM elev_marks WHERE plotId = :plotId")
    suspend fun clearMarks(plotId: Long)

    @Query("SELECT * FROM plots ORDER BY updatedAt DESC LIMIT 1")
    suspend fun latestPlot(): PlotEntity?

    @Query("SELECT * FROM vertices WHERE plotId = :plotId ORDER BY idx ASC")
    suspend fun verticesFor(plotId: Long): List<VertexEntity>

    @Query("SELECT * FROM side_walks WHERE plotId = :plotId")
    suspend fun sideWalksFor(plotId: Long): List<SideWalkEntity>

    @Query("SELECT * FROM elev_marks WHERE plotId = :plotId ORDER BY id ASC")
    suspend fun marksFor(plotId: Long): List<ElevMarkEntity>

    @Transaction
    suspend fun savePlot(
        plot: PlotEntity,
        vertices: List<VertexEntity>,
        walks: List<SideWalkEntity>,
        marks: List<ElevMarkEntity>,
    ) {
        upsertPlot(plot)
        clearVertices(plot.id)
        clearSideWalks(plot.id)
        clearMarks(plot.id)
        insertVertices(vertices)
        insertSideWalks(walks)
        insertMarks(marks)
    }
}
