package com.vaastu.survey.location

import android.annotation.SuppressLint
import android.content.Context
import android.os.Looper
import com.google.android.gms.location.LocationCallback
import com.google.android.gms.location.LocationRequest
import com.google.android.gms.location.LocationResult
import com.google.android.gms.location.LocationServices
import com.google.android.gms.location.Priority
import com.vaastu.survey.core.geo.GeoPoint
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow

/**
 * Thin wrapper over the fused location provider. This is the seam where a
 * Bluetooth RTK provider can later be swapped in: anything emitting Flow<GeoPoint>.
 */
class LocationRepository(context: Context) {
    private val appContext = context.applicationContext
    private val client = LocationServices.getFusedLocationProviderClient(appContext)

    @SuppressLint("MissingPermission")
    fun locationFlow(intervalMs: Long = 1000L): Flow<GeoPoint> = callbackFlow {
        val request = LocationRequest.Builder(Priority.PRIORITY_HIGH_ACCURACY, intervalMs)
            .setMinUpdateIntervalMillis(500L)
            .setWaitForAccurateLocation(true)
            .build()

        val callback = object : LocationCallback() {
            override fun onLocationResult(result: LocationResult) {
                val loc = result.lastLocation ?: return
                trySend(
                    GeoPoint(
                        lat = loc.latitude,
                        lon = loc.longitude,
                        altM = if (loc.hasAltitude()) loc.altitude else null,
                        accM = if (loc.hasAccuracy()) loc.accuracy else 0f,
                        timestamp = loc.time,
                    ),
                )
            }
        }

        client.requestLocationUpdates(request, callback, Looper.getMainLooper())
        awaitClose { client.removeLocationUpdates(callback) }
    }
}
