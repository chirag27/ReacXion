package com.vaastu.survey.settings

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.vaastu.survey.location.LocationSource
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.dataStore by preferencesDataStore("vaastu_settings")

data class AppSettings(
    val source: LocationSource = LocationSource.PHONE,
    val rtkMac: String? = null,
)

class SettingsStore(private val context: Context) {
    private val keySource = stringPreferencesKey("source")
    private val keyMac = stringPreferencesKey("rtk_mac")

    val settings: Flow<AppSettings> = context.dataStore.data.map { p ->
        AppSettings(
            source = runCatching { LocationSource.valueOf(p[keySource] ?: "PHONE") }
                .getOrDefault(LocationSource.PHONE),
            rtkMac = p[keyMac],
        )
    }

    suspend fun setSource(source: LocationSource) {
        context.dataStore.edit { it[keySource] = source.name }
    }

    suspend fun setRtkMac(mac: String?) {
        context.dataStore.edit { p ->
            if (mac == null) p.remove(keyMac) else p[keyMac] = mac
        }
    }
}
