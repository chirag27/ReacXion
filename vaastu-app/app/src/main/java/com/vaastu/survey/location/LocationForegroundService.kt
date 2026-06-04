package com.vaastu.survey.location

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch

/**
 * Keeps positioning alive while walking the plot (screen off / pocket). Owns the
 * active PositionProvider (phone GNSS or RTK) and pushes every fix to LocationBus.
 */
class LocationForegroundService : Service() {

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
    private var streamJob: Job? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        createChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIF_ID, buildNotification())
        val source = intent?.getStringExtra(EXTRA_SOURCE) ?: LocationSource.PHONE.name
        val mac = intent?.getStringExtra(EXTRA_MAC)
        startStreaming(source, mac)
        return START_STICKY
    }

    private fun startStreaming(source: String, mac: String?) {
        streamJob?.cancel()
        val provider: PositionProvider = if (source == LocationSource.RTK.name) {
            RtkBluetoothPositionProvider(this, mac)
        } else {
            FusedPositionProvider(this)
        }
        LocationBus.status.value = provider.sourceName
        streamJob = scope.launch {
            provider.positions().collect { fix ->
                LocationBus.positions.value = fix
            }
        }
    }

    override fun onDestroy() {
        streamJob?.cancel()
        scope.cancel()
        LocationBus.status.value = "Idle"
        super.onDestroy()
    }

    private fun buildNotification(): Notification {
        val builder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            Notification.Builder(this, CHANNEL_ID)
        } else {
            @Suppress("DEPRECATION")
            Notification.Builder(this)
        }
        return builder
            .setContentTitle("Vaastu Survey")
            .setContentText("Tracking position for the plot survey")
            .setSmallIcon(android.R.drawable.ic_menu_mylocation)
            .setOngoing(true)
            .build()
    }

    private fun createChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val mgr = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Survey tracking",
                NotificationManager.IMPORTANCE_LOW,
            )
            mgr.createNotificationChannel(channel)
        }
    }

    companion object {
        const val EXTRA_SOURCE = "source"
        const val EXTRA_MAC = "mac"
        private const val CHANNEL_ID = "survey_tracking"
        private const val NOTIF_ID = 42

        fun intent(context: Context, source: LocationSource, mac: String?): Intent =
            Intent(context, LocationForegroundService::class.java).apply {
                putExtra(EXTRA_SOURCE, source.name)
                putExtra(EXTRA_MAC, mac)
            }
    }
}
