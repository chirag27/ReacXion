package com.reacxion.jyotish.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.reacxion.jyotish.data.Report

/** Single-screen consult flow: birth form -> report -> ask. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun JyotishApp(vm: ConsultViewModel) {
    Scaffold(topBar = { TopAppBar(title = { Text("Jyotish Consult") }) }) { pad ->
        Column(
            Modifier.padding(pad).padding(16.dp).verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            BackendField(vm)
            BirthFormCard(vm)

            Button(onClick = { vm.fetchReport() }, enabled = !vm.loading,
                   modifier = Modifier.fillMaxWidth()) {
                Text("Generate reading")
            }
            if (vm.loading) LinearProgressIndicator(Modifier.fillMaxWidth())
            vm.error?.let { ErrorCard(it) }

            vm.report?.let { ReportView(it) }
            if (vm.report != null) AskCard(vm)
        }
    }
}

@Composable
private fun BackendField(vm: ConsultViewModel) {
    OutlinedTextField(
        value = vm.backendUrl, onValueChange = vm::updateBackendUrl,
        label = { Text("Backend URL") }, singleLine = true,
        supportingText = { Text("Emulator: http://10.0.2.2:8000 · Device: your PC's LAN IP") },
        modifier = Modifier.fillMaxWidth())
}

@Composable
private fun BirthFormCard(vm: ConsultViewModel) {
    val f = vm.form
    Card(Modifier.fillMaxWidth()) {
        Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Birth details", style = MaterialTheme.typography.titleMedium)
            Field("Name", f.name) { vm.updateForm(f.copy(name = it)) }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                NumField("Year", f.year, Modifier.weight(1f)) { vm.updateForm(f.copy(year = it)) }
                NumField("Month", f.month, Modifier.weight(1f)) { vm.updateForm(f.copy(month = it)) }
                NumField("Day", f.day, Modifier.weight(1f)) { vm.updateForm(f.copy(day = it)) }
            }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                NumField("Hour", f.hour, Modifier.weight(1f)) { vm.updateForm(f.copy(hour = it)) }
                NumField("Minute", f.minute, Modifier.weight(1f)) { vm.updateForm(f.copy(minute = it)) }
            }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                NumField("Latitude", f.latitude, Modifier.weight(1f)) { vm.updateForm(f.copy(latitude = it)) }
                NumField("Longitude", f.longitude, Modifier.weight(1f)) { vm.updateForm(f.copy(longitude = it)) }
            }
            Field("Timezone (IANA)", f.timezone) { vm.updateForm(f.copy(timezone = it)) }
        }
    }
}

@Composable
private fun ReportView(r: Report) {
    val chart = r.vedic_chart
    SectionCard("Lagna & grahas (Vedic)") {
        Text("Ascendant ${fmtDeg(chart.ascendant)}",
             style = MaterialTheme.typography.bodyMedium)
        Spacer(Modifier.height(6.dp))
        chart.planets.forEach { (name, p) ->
            Text("$name — ${p.sign} ${degInSign(p.longitude)} · ${p.nakshatra} (pada ${p.pada})" +
                 (if (p.retrograde) " ℞" else ""),
                 style = MaterialTheme.typography.bodySmall)
        }
    }
    if (r.dasha_now.isNotEmpty()) SectionCard("Current dasha") {
        Text(r.dasha_now.joinToString(" › ") { it.lord })
        r.dasha_now.firstOrNull()?.let {
            Text("Maha ${it.lord}: ${it.start.take(10)} → ${it.end.take(10)}",
                 style = MaterialTheme.typography.bodySmall)
        }
    }
    if (r.yogas.isNotEmpty()) SectionCard("Yogas") {
        r.yogas.forEach { Text("• ${it.name} — ${it.description}",
                               style = MaterialTheme.typography.bodySmall) }
    }
    if (r.rinas.isNotEmpty()) SectionCard("Lal Kitab debts (rinas)") {
        r.rinas.forEach { Text("• ${it.sanskrit}: ${it.trigger}",
                               style = MaterialTheme.typography.bodySmall) }
    }
    if (r.remedies.isNotEmpty()) SectionCard("Remedies") {
        r.remedies.forEach { Text("• ${it.target}: ${it.text}",
                                  style = MaterialTheme.typography.bodySmall) }
    }
    SectionCard("Birth-time confidence") {
        Text(r.time_confidence.level.uppercase(), style = MaterialTheme.typography.titleSmall)
        Text(r.time_confidence.note, style = MaterialTheme.typography.bodySmall)
    }
}

@Composable
private fun AskCard(vm: ConsultViewModel) {
    var q by remember { mutableStateOf("") }
    SectionCard("Ask the agent") {
        OutlinedTextField(value = q, onValueChange = { q = it },
            label = { Text("e.g. When am I likely to marry?") },
            modifier = Modifier.fillMaxWidth())
        Spacer(Modifier.height(8.dp))
        Button(onClick = { vm.askQuestion(q) }, enabled = !vm.loading,
               modifier = Modifier.fillMaxWidth()) { Text("Ask") }
        vm.ask?.let { a ->
            Spacer(Modifier.height(8.dp))
            Text(a.answer, style = MaterialTheme.typography.bodyMedium)
            if (a.tool_calls.isNotEmpty()) {
                Spacer(Modifier.height(6.dp))
                Text("Grounded in: " + a.tool_calls.joinToString { it.tool },
                     style = MaterialTheme.typography.labelSmall,
                     overflow = TextOverflow.Ellipsis)
            }
        }
    }
}

// ---- small helpers ----
@Composable
private fun SectionCard(title: String, body: @Composable ColumnScope.() -> Unit) {
    Card(Modifier.fillMaxWidth()) {
        Column(Modifier.padding(12.dp)) {
            Text(title, style = MaterialTheme.typography.titleMedium)
            Spacer(Modifier.height(6.dp))
            body()
        }
    }
}

@Composable
private fun ErrorCard(msg: String) {
    Card(colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.errorContainer)) {
        Text(msg, Modifier.padding(12.dp),
             color = MaterialTheme.colorScheme.onErrorContainer)
    }
}

@Composable
private fun Field(label: String, value: String, onChange: (String) -> Unit) =
    OutlinedTextField(value, onChange, label = { Text(label) }, singleLine = true,
        modifier = Modifier.fillMaxWidth())

@Composable
private fun NumField(label: String, value: String, modifier: Modifier, onChange: (String) -> Unit) =
    OutlinedTextField(value, onChange, label = { Text(label) }, singleLine = true,
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
        modifier = modifier)

private fun fmtDeg(d: Double) = String.format("%.2f°", d)
private fun degInSign(lon: Double): String {
    val x = lon % 30.0
    val deg = x.toInt()
    val min = ((x - deg) * 60).toInt()
    return String.format("%02d°%02d'", deg, min)
}
