package com.vaastu.survey.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.runtime.collectAsState
import java.util.Locale

@Composable
fun SurveyScreen(vm: SurveyViewModel) {
    val state by vm.state.collectAsState()

    Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
        Text("Survey — capture corners", style = MaterialTheme.typography.titleLarge)

        // Live fix card
        Card(modifier = Modifier.fillMaxWidth().padding(vertical = 12.dp)) {
            Column(modifier = Modifier.padding(16.dp)) {
                val loc = state.location
                if (loc == null) {
                    Text("Acquiring GPS…", style = MaterialTheme.typography.bodyMedium)
                } else {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier.size(14.dp).clip(CircleShape)
                                .background(accuracyColor(loc.accM)),
                        )
                        Text(
                            "  Accuracy: ±${String.format(Locale.US, "%.1f", loc.accM)} m",
                            modifier = Modifier.padding(start = 4.dp),
                            style = MaterialTheme.typography.bodyMedium,
                        )
                    }
                    Text(
                        String.format(Locale.US, "Lat %.6f  Lon %.6f", loc.lat, loc.lon),
                        fontFamily = FontFamily.Monospace,
                        style = MaterialTheme.typography.bodySmall,
                        modifier = Modifier.padding(top = 4.dp),
                    )
                    loc.altM?.let {
                        Text(
                            String.format(Locale.US, "Alt %.1f m   Heading %.0f° (mag)", it, state.heading),
                            style = MaterialTheme.typography.bodySmall,
                        )
                    }
                    Text(
                        "Magnetic declination: ${String.format(Locale.US, "%.1f", state.declinationDeg)}°",
                        style = MaterialTheme.typography.bodySmall,
                    )
                }
            }
        }

        if (state.capturing) {
            Text(
                "Hold still — averaging ${state.captureSamples}/${SurveyViewModel.TARGET_SAMPLES} fixes…",
                color = MaterialTheme.colorScheme.tertiary,
                fontWeight = FontWeight.Bold,
            )
            OutlinedButton(
                onClick = { vm.cancelCapture() },
                modifier = Modifier.fillMaxWidth().padding(top = 8.dp),
            ) { Text("Cancel") }
        } else {
            Button(
                onClick = { vm.captureCorner() },
                enabled = state.location != null,
                modifier = Modifier.fillMaxWidth(),
            ) { Text("Capture corner ${state.vertices.size + 1}") }
        }

        Row(
            modifier = Modifier.fillMaxWidth().padding(top = 8.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            OutlinedButton(
                onClick = { vm.undoLastVertex() },
                enabled = state.vertices.isNotEmpty(),
                modifier = Modifier.weight(1f),
            ) { Text("Undo last") }
            OutlinedButton(
                onClick = { vm.resetPlot() },
                enabled = state.vertices.isNotEmpty(),
                modifier = Modifier.weight(1f),
            ) { Text("Reset plot") }
        }

        if (state.vertices.size >= 3) {
            Text(
                "Area: ${fmtM2(state.areaM2)}   Perimeter: ${fmtMFt(state.perimeterM)}",
                style = MaterialTheme.typography.bodyMedium,
                modifier = Modifier.padding(top = 12.dp),
            )
        } else {
            Text(
                "Capture at least 3 corners to form a plot.",
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(top = 12.dp),
            )
        }

        Text(
            "Corners (${state.vertices.size})",
            style = MaterialTheme.typography.titleMedium,
            modifier = Modifier.padding(top = 12.dp),
        )
        LazyColumn(modifier = Modifier.fillMaxWidth()) {
            items(state.vertices) { v ->
                Card(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Text("Corner ${v.index + 1}", fontWeight = FontWeight.Bold)
                        Text(
                            String.format(
                                Locale.US,
                                "±%.1f m · %d samples · %.6f, %.6f",
                                v.rmsAccM, v.sampleCount, v.geo.lat, v.geo.lon,
                            ),
                            style = MaterialTheme.typography.bodySmall,
                            fontFamily = FontFamily.Monospace,
                        )
                    }
                }
            }
        }
    }
}

private fun fmtM2(m2: Double): String =
    String.format(Locale.US, "%.1f m² (%.1f ft²)", m2, m2 * 10.7639)
