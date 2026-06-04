package com.vaastu.survey.ui

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import java.util.Locale

@Composable
fun ElevationScreen(vm: SurveyViewModel) {
    val state by vm.state.collectAsState()
    var label by remember { mutableStateOf("") }
    var note by remember { mutableStateOf("") }

    Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
        Text("Elevation", style = MaterialTheme.typography.titleLarge)

        val src = if (state.hasBarometer) "barometer + GNSS" else "GNSS altitude"
        Text(
            "Source: $src. Elevation is shown relative to the plot center datum " +
                "(absolute GNSS altitude is noisy; relative change is what matters for slope).",
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.padding(top = 4.dp),
        )

        Card(modifier = Modifier.fillMaxWidth().padding(vertical = 12.dp)) {
            Column(modifier = Modifier.padding(16.dp)) {
                val rel = state.currentRelElevM
                if (state.elevDatumM == null) {
                    Text("Capture corners first to set the center datum.")
                } else if (rel == null) {
                    Text("Waiting for altitude…")
                } else {
                    Text("Current relative elevation", style = MaterialTheme.typography.labelMedium)
                    Text(
                        String.format(Locale.US, "%+.2f m", rel),
                        style = MaterialTheme.typography.displaySmall,
                        fontWeight = FontWeight.Bold,
                    )
                    state.location?.altM?.let {
                        Text(
                            String.format(Locale.US, "Absolute GNSS alt: %.1f m (±%.0f m)", it, state.location?.accM ?: 0f),
                            style = MaterialTheme.typography.bodySmall,
                        )
                    }
                }
            }
        }

        OutlinedTextField(
            value = label,
            onValueChange = { label = it },
            label = { Text("Label (optional)") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
        )
        OutlinedTextField(
            value = note,
            onValueChange = { note = it },
            label = { Text("Note (optional)") },
            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done),
            modifier = Modifier.fillMaxWidth().padding(top = 8.dp),
        )
        Button(
            onClick = {
                vm.markElevation(label, note)
                label = ""
                note = ""
            },
            enabled = state.location != null && state.elevDatumM != null,
            modifier = Modifier.fillMaxWidth().padding(top = 8.dp),
        ) { Text("Mark elevation here") }

        Text(
            "Marks (${state.elevMarks.size})",
            style = MaterialTheme.typography.titleMedium,
            modifier = Modifier.padding(top = 16.dp),
        )
        state.elevMarks.forEach { m ->
            Card(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Row(modifier = Modifier.fillMaxWidth()) {
                        Text(
                            m.label,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.weight(1f),
                        )
                        TextButton(onClick = { vm.deleteMark(m.id) }) { Text("Delete") }
                    }
                    Text(
                        String.format(
                            Locale.US,
                            "%+.2f m · zone %s",
                            m.relElevM, m.zone?.abbr ?: "-",
                        ),
                    )
                    if (m.note.isNotBlank()) {
                        Text(m.note, style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        }
    }
}
