package com.vaastu.survey.sensors

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow

/**
 * Magnetic heading from the fused rotation-vector sensor (steadier than raw
 * magnetometer). Also reports whether the device has a pressure sensor.
 */
class HeadingProvider(context: Context) {
    private val sm = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private val rotation: Sensor? = sm.getDefaultSensor(Sensor.TYPE_ROTATION_VECTOR)

    fun hasPressureSensor(): Boolean = sm.getDefaultSensor(Sensor.TYPE_PRESSURE) != null

    /** Emits magnetic azimuth in degrees [0,360). */
    fun headingFlow(): Flow<Float> = callbackFlow {
        if (rotation == null) {
            trySend(0f)
            awaitClose { }
            return@callbackFlow
        }
        val matrix = FloatArray(9)
        val orientation = FloatArray(3)
        val listener = object : SensorEventListener {
            override fun onSensorChanged(event: SensorEvent) {
                SensorManager.getRotationMatrixFromVector(matrix, event.values)
                SensorManager.getOrientation(matrix, orientation)
                val az = (Math.toDegrees(orientation[0].toDouble()).toFloat() + 360f) % 360f
                trySend(az)
            }

            override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}
        }
        sm.registerListener(listener, rotation, SensorManager.SENSOR_DELAY_UI)
        awaitClose { sm.unregisterListener(listener) }
    }
}
