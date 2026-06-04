package com.vaastu.survey.ui

import android.net.Uri
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
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
import com.vaastu.survey.data.Exporters
import com.vaastu.survey.data.PdfReporter

@Composable
fun ExportScreen(vm: SurveyViewModel) {
    val state by vm.state.collectAsState()
    val context = LocalContext.current
    var pendingText by remember { mutableStateOf("") }
    var pendingBytes by remember { mutableStateOf(ByteArray(0)) }

    fun writeText(uri: Uri?) {
        if (uri == null) return
        runCatching {
            context.contentResolver.openOutputStream(uri)?.use { it.write(pendingText.toByteArray()) }
        }.onSuccess { Toast.makeText(context, "Saved", Toast.LENGTH_SHORT).show() }
            .onFailure { Toast.makeText(context, "Save failed: ${it.message}", Toast.LENGTH_LONG).show() }
    }

    fun writeBytes(uri: Uri?) {
        if (uri == null) return
        runCatching {
            context.contentResolver.openOutputStream(uri)?.use { it.write(pendingBytes) }
        }.onSuccess { Toast.makeText(context, "Saved", Toast.LENGTH_SHORT).show() }
            .onFailure { Toast.makeText(context, "Save failed: ${it.message}", Toast.LENGTH_LONG).show() }
    }

    val csvLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.CreateDocument("text/csv"),
    ) { writeText(it) }
    val jsonLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.CreateDocument("application/geo+json"),
    ) { writeText(it) }
    val pdfLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.CreateDocument("application/pdf"),
    ) { writeBytes(it) }

    Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
        Text("Export", style = MaterialTheme.typography.titleLarge)

        Card(modifier = Modifier.fillMaxWidth().padding(vertical = 12.dp)) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Plot: ${state.plotName}")
                Text("Corners: ${state.vertices.size}")
                Text("Boundary points (0.5 m): ${state.boundary.size}")
                Text("Elevation marks: ${state.elevMarks.size}")
            }
        }

        val ready = state.boundary.isNotEmpty()
        Button(
            onClick = {
                pendingText = Exporters.csv(state)
                csvLauncher.launch("${safeName(state.plotName)}.csv")
            },
            enabled = ready,
            modifier = Modifier.fillMaxWidth(),
        ) { Text("Export CSV (points + directions)") }

        Button(
            onClick = {
                pendingText = Exporters.geoJson(state)
                jsonLauncher.launch("${safeName(state.plotName)}.geojson")
            },
            enabled = ready,
            modifier = Modifier.fillMaxWidth().padding(top = 8.dp),
        ) { Text("Export GeoJSON (Google Earth / QGIS)") }

        Button(
            onClick = {
                pendingBytes = PdfReporter.generate(state)
                pdfLauncher.launch("${safeName(state.plotName)}.pdf")
            },
            enabled = ready,
            modifier = Modifier.fillMaxWidth().padding(top = 8.dp),
        ) { Text("Export PDF report") }

        if (!ready) {
            Text(
                "Capture at least 3 corners to enable export.",
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(top = 8.dp),
            )
        }

        Text(
            "CSV columns: idx, isCorner, side, distanceM, bearingMagDeg, zone, zoneSanskrit, " +
                "lat, lon. Bearings are magnetic (declination noted in the file header).",
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.padding(top = 16.dp),
        )
    }
}

private fun safeName(name: String): String =
    name.replace(Regex("[^A-Za-z0-9_-]"), "_").ifBlank { "vaastu_plot" }
