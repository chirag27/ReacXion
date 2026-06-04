package com.vaastu.survey.ui

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import java.io.File
import java.util.Locale

@Composable
fun ElevationScreen(vm: SurveyViewModel) {
    val state by vm.state.collectAsState()
    val context = LocalContext.current
    var label by remember { mutableStateOf("") }
    var note by remember { mutableStateOf("") }
    var pendingPhotoPath by remember { mutableStateOf<String?>(null) }
    var attachedPhotoPath by remember { mutableStateOf<String?>(null) }

    val takePicture = rememberLauncherForActivityResult(
        ActivityResultContracts.TakePicture(),
    ) { ok ->
        attachedPhotoPath = if (ok) pendingPhotoPath else null
    }

    fun startCapture() {
        val (path, uri) = createImageFile(context)
        pendingPhotoPath = path
        takePicture.launch(uri)
    }

    val cameraPerm = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission(),
    ) { granted -> if (granted) startCapture() }

    Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
        Text("Elevation", style = MaterialTheme.typography.titleLarge)

        val src = if (state.hasBarometer) "barometer + GNSS" else "GNSS altitude"
        Text(
            "Source: $src. Shown relative to the plot center datum (absolute GNSS altitude is " +
                "noisy; relative change is what matters for slope).",
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.padding(top = 4.dp),
        )

        Card(modifier = Modifier.fillMaxWidth().padding(vertical = 12.dp)) {
            Column(modifier = Modifier.padding(16.dp)) {
                val rel = state.currentRelElevM
                when {
                    state.elevDatumM == null -> Text("Capture corners first to set the center datum.")
                    rel == null -> Text("Waiting for altitude…")
                    else -> {
                        Text("Current relative elevation", style = MaterialTheme.typography.labelMedium)
                        Text(
                            String.format(Locale.US, "%+.2f m", rel),
                            style = MaterialTheme.typography.displaySmall,
                            fontWeight = FontWeight.Bold,
                        )
                        state.location?.altM?.let {
                            Text(
                                String.format(Locale.US, "Absolute GNSS alt: %.1f m", it),
                                style = MaterialTheme.typography.bodySmall,
                            )
                        }
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

        Row(modifier = Modifier.fillMaxWidth().padding(top = 8.dp)) {
            OutlinedButton(
                onClick = {
                    if (hasCameraPermission(context)) startCapture()
                    else cameraPerm.launch(Manifest.permission.CAMERA)
                },
                modifier = Modifier.weight(1f),
            ) { Text(if (attachedPhotoPath != null) "Photo ✓ (retake)" else "Add photo") }
        }

        Button(
            onClick = {
                vm.markElevation(label, note, attachedPhotoPath)
                label = ""
                note = ""
                attachedPhotoPath = null
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
                        Text(m.label, fontWeight = FontWeight.Bold, modifier = Modifier.weight(1f))
                        TextButton(onClick = { vm.deleteMark(m.id) }) { Text("Delete") }
                    }
                    Text(
                        String.format(Locale.US, "%+.2f m · zone %s", m.relElevM, m.zone?.abbr ?: "-"),
                    )
                    if (m.photoPath != null) {
                        Text("📷 photo attached", style = MaterialTheme.typography.bodySmall)
                    }
                    if (m.note.isNotBlank()) {
                        Text(m.note, style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        }
    }
}

private fun hasCameraPermission(context: Context): Boolean =
    ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) ==
        PackageManager.PERMISSION_GRANTED

/** Creates an app-private file under files/photos and returns (path, content-uri). */
private fun createImageFile(context: Context): Pair<String, Uri> {
    val dir = File(context.filesDir, "photos").apply { mkdirs() }
    val file = File(dir, "mark_${System.currentTimeMillis()}.jpg")
    val uri = FileProvider.getUriForFile(context, "${context.packageName}.fileprovider", file)
    return file.absolutePath to uri
}
