package com.vaastu.survey.data.db

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "plots")
data class PlotEntity(
    @PrimaryKey val id: Long,
    val name: String,
    val centerMode: String,
    val declinationDeg: Float,
    val updatedAt: Long,
)

@Entity(tableName = "vertices")
data class VertexEntity(
    @PrimaryKey(autoGenerate = true) val rowId: Long = 0,
    val plotId: Long,
    val idx: Int,
    val lat: Double,
    val lon: Double,
    val alt: Double?,
    val accM: Float,
    val sampleCount: Int,
    val rmsAccM: Float,
)

@Entity(tableName = "side_walks")
data class SideWalkEntity(
    @PrimaryKey(autoGenerate = true) val rowId: Long = 0,
    val plotId: Long,
    val fromIdx: Int,
    val walkedM: Double,
)

@Entity(tableName = "elev_marks")
data class ElevMarkEntity(
    @PrimaryKey val id: Long,
    val plotId: Long,
    val label: String,
    val lat: Double,
    val lon: Double,
    val alt: Double?,
    val relElevM: Double,
    val zoneOrdinal: Int, // -1 if unknown
    val note: String,
    val photoPath: String?,
)
