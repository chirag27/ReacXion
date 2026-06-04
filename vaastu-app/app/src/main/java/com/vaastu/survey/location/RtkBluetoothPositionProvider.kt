package com.vaastu.survey.location

import android.annotation.SuppressLint
import android.bluetooth.BluetoothManager
import android.bluetooth.BluetoothSocket
import android.content.Context
import com.vaastu.survey.core.geo.GeoPoint
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import java.io.BufferedReader
import java.io.InputStreamReader
import java.util.UUID

/**
 * Experimental external-RTK source: reads NMEA over a classic Bluetooth (SPP)
 * serial link from a paired receiver and emits fixes. This is the concrete
 * realization of the PositionProvider seam (DESIGN.md M7). NTRIP correction
 * injection can be added on top of the same socket later.
 */
class RtkBluetoothPositionProvider(
    context: Context,
    private val mac: String?,
) : PositionProvider {
    override val sourceName = "RTK (Bluetooth)"

    private val adapter =
        (context.getSystemService(Context.BLUETOOTH_SERVICE) as? BluetoothManager)?.adapter
    private val sppUuid = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")

    @SuppressLint("MissingPermission")
    override fun positions(): Flow<GeoPoint> = callbackFlow {
        val a = adapter
        if (a == null || mac.isNullOrBlank()) {
            LocationBus.status.value = "RTK: no device selected"
            awaitClose { }
            return@callbackFlow
        }
        var socket: BluetoothSocket? = null
        val thread = Thread {
            try {
                LocationBus.status.value = "RTK: connecting…"
                val device = a.getRemoteDevice(mac)
                a.cancelDiscovery()
                socket = device.createRfcommSocketToServiceRecord(sppUuid)
                socket?.connect()
                LocationBus.status.value = "RTK: connected"
                val reader = BufferedReader(InputStreamReader(socket?.inputStream))
                while (!Thread.currentThread().isInterrupted) {
                    val line = reader.readLine() ?: break
                    NmeaParser.parse(line)?.let { trySend(it) }
                }
            } catch (e: Exception) {
                LocationBus.status.value = "RTK error: ${e.message}"
            }
        }
        thread.start()
        awaitClose {
            thread.interrupt()
            runCatching { socket?.close() }
        }
    }
}
