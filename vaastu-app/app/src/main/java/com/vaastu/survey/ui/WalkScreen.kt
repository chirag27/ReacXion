package com.vaastu.survey.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import java.util.Locale
import kotlin.math.abs

@Composable
fun WalkScreen(vm: SurveyViewModel) {
    val state by vm.state.collectAsState()

    if (state.sides.isEmpty()) {
        Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
            Text("Walk a side", style = MaterialTheme.typography.titleLarge)
            Text(
                "Capture at least 3 corners first. Then walk each side to verify its length.",
                modifier = Modifier.padding(top = 16.dp),
            )
        }
        return
    }

    val walking = state.walkSideIndex
    if (walking != null) {
        WalkingView(vm, state, walking)
        return
    }

    Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
        Text("Walk a side", style = MaterialTheme.typography.titleLarge)
        Text(
            "Pick a side to walk. Compare the walked distance to the straight-line length to " +
                "confirm the side is mapped correctly.",
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.padding(top = 8.dp),
        )

        state.sides.forEachIndexed { i, s ->
            Card(modifier = Modifier.fillMaxWidth().padding(vertical = 6.dp)) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        "Side ${i + 1}: corner ${s.from + 1} → ${s.to + 1}",
                        style = MaterialTheme.typography.titleMedium,
                    )
                    Text("Straight-line: ${fmtMFt(s.straightM)}")
                    if (s.walkedM != null) {
                        Text(
                            "Walked: ${fmtM(s.walkedM)}   Δ ${String.format(Locale.US, "%.2f", s.deltaM ?: 0.0)} m",
                            color = deltaColor(s.deltaM ?: 0.0),
                        )
                    } else {
                        Text("Not walked yet", style = MaterialTheme.typography.bodySmall)
                    }
                    Button(
                        onClick = { vm.startWalk(i) },
                        modifier = Modifier.padding(top = 8.dp),
                    ) { Text("Walk this side") }
                }
            }
        }
    }
}

@Composable
private fun WalkingView(vm: SurveyViewModel, state: SurveyState, walking: Int) {
    val target = state.walkTargetM
    val walked = state.walkWalkedM
    val delta = walked - target
    val progress = if (target > 0) (walked / target).toFloat().coerceIn(0f, 1f) else 0f

    Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
        Text("Walk a side", style = MaterialTheme.typography.titleLarge)
        Card(modifier = Modifier.fillMaxWidth().padding(top = 16.dp)) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    "Walking side ${walking + 1}: corner ${walking + 1} → ${walking + 2}",
                    style = MaterialTheme.typography.titleMedium,
                )
                Text(
                    fmtM(walked),
                    style = MaterialTheme.typography.displaySmall,
                    fontWeight = FontWeight.Bold,
                )
                Text("Target (straight-line): ${fmtMFt(target)}")
                Text(
                    "Δ vs target: ${if (delta >= 0) "+" else ""}${String.format(Locale.US, "%.2f", delta)} m",
                    color = deltaColor(abs(delta)),
                    fontWeight = FontWeight.Bold,
                )
                LinearProgressIndicator(
                    progress = { progress },
                    modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                )
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(onClick = { vm.stopWalk(true) }, modifier = Modifier.weight(1f)) {
                        Text("Save")
                    }
                    OutlinedButton(onClick = { vm.stopWalk(false) }, modifier = Modifier.weight(1f)) {
                        Text("Discard")
                    }
                }
            }
        }
        Text(
            "Walk steadily from this corner to the next. Distance integrates your GPS path; " +
                "small jitter while standing is filtered out.",
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.padding(top = 12.dp),
        )
    }
}

private fun deltaColor(absDelta: Double): Color = when {
    absDelta <= 0.5 -> Color(0xFF2E7D32)
    absDelta <= 1.5 -> Color(0xFFF9A825)
    else -> Color(0xFFC62828)
}
