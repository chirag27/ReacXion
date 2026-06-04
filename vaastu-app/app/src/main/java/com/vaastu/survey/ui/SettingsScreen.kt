package com.vaastu.survey.ui

import android.Manifest
import android.annotation.SuppressLint
import android.bluetooth.BluetoothManager
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.vaastu.survey.location.LocationSource

@Composable
fun SettingsScreen(vm: SurveyViewModel) {
    val state by vm.state.collectAsState()
    val context = LocalContext.current
    var devices by remember { mutableStateOf<List<Pair<String, String>>>(emptyList()) }

    val btPerm = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission(),
    ) { granted -> if (granted) devices = bondedDevices(context) }

    fun refreshDevices() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S &&
            ContextCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_CONNECT) !=
            PackageManager.PERMISSION_GRANTED
        ) {
            btPerm.launch(Manifest.permission.BLUETOOTH_CONNECT)
        } else {
            devices = bondedDevices(context)
        }
    }

    Column(
        modifier = Modifier.fillMaxWidth().padding(16.dp).verticalScroll(rememberScrollState()),
    ) {
        Text("Settings", style = MaterialTheme.typography.titleLarge)

        OutlinedTextField(
            value = state.plotName,
            onValueChange = { vm.setPlotName(it) },
            label = { Text("Plot name") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth().padding(top = 12.dp),
        )

        Text("Plot center", style = MaterialTheme.typography.titleMedium, modifier = Modifier.padding(top = 16.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            FilterChip(
                selected = state.centerMode == CenterMode.CENTROID,
                onClick = { vm.setCenterMode(CenterMode.CENTROID) },
                label = { Text("Area centroid") },
            )
            FilterChip(
                selected = state.centerMode == CenterMode.MEAN,
                onClick = { vm.setCenterMode(CenterMode.MEAN) },
                label = { Text("Vertex mean") },
            )
        }

        Text("Positioning source", style = MaterialTheme.typography.titleMedium, modifier = Modifier.padding(top = 16.dp))
        Text("Status: ${state.locationStatus}", style = MaterialTheme.typography.bodySmall)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(top = 4.dp)) {
            FilterChip(
                selected = state.locationSource == LocationSource.PHONE,
                onClick = { vm.setSource(LocationSource.PHONE) },
                label = { Text("Phone GNSS") },
            )
            FilterChip(
                selected = state.locationSource == LocationSource.RTK,
                onClick = {
                    vm.setSource(LocationSource.RTK)
                    refreshDevices()
                },
                label = { Text("External RTK (BT)") },
            )
        }

        if (state.locationSource == LocationSource.RTK) {
            Card(modifier = Modifier.fillMaxWidth().padding(top = 12.dp)) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Paired Bluetooth devices", style = MaterialTheme.typography.titleSmall)
                    Text(
                        "Pick your NMEA/RTK receiver (must already be paired in system Bluetooth " +
                            "settings). Experimental.",
                        style = MaterialTheme.typography.bodySmall,
                    )
                    Button(onClick = { refreshDevices() }, modifier = Modifier.padding(top = 8.dp)) {
                        Text("Scan paired devices")
                    }
                    devices.forEach { (name, mac) ->
                        Button(
                            onClick = { vm.setRtkMac(mac) },
                            modifier = Modifier.fillMaxWidth().padding(top = 6.dp),
                        ) { Text("$name\n$mac") }
                    }
                    if (devices.isEmpty()) {
                        Text(
                            "No paired devices found (grant Bluetooth permission and pair the receiver first).",
                            style = MaterialTheme.typography.bodySmall,
                            modifier = Modifier.padding(top = 8.dp),
                        )
                    }
                }
            }
        }

        Text(
            "Phone GNSS is ~1–4 m. RTK (with corrections) reaches centimeters. The 0.5 m grid is " +
                "derived from your corner fixes, so better corners ⇒ better grid.",
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.padding(top = 16.dp),
        )
    }
}

@SuppressLint("MissingPermission")
private fun bondedDevices(context: Context): List<Pair<String, String>> {
    val adapter = (context.getSystemService(Context.BLUETOOTH_SERVICE) as? BluetoothManager)?.adapter
        ?: return emptyList()
    return runCatching {
        adapter.bondedDevices.map { (it.name ?: "Unknown") to it.address }
    }.getOrDefault(emptyList())
}
