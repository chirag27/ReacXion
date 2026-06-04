package com.vaastu.survey.location

import com.vaastu.survey.core.geo.GeoPoint
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow

/**
 * Source-agnostic stream of fixes. The phone's fused provider and an external
 * RTK receiver both implement this, so the rest of the app never needs to know
 * where a position came from.
 */
interface PositionProvider {
    val sourceName: String
    fun positions(): Flow<GeoPoint>
}

enum class LocationSource { PHONE, RTK }

/**
 * Single place the UI observes for the current fix, regardless of which provider
 * (phone GNSS or RTK) the foreground service is currently feeding it.
 */
object LocationBus {
    val positions = MutableStateFlow<GeoPoint?>(null)
    /** Human-readable status of the active source, e.g. "Phone GNSS", "RTK: connecting…". */
    val status = MutableStateFlow("Idle")
}
