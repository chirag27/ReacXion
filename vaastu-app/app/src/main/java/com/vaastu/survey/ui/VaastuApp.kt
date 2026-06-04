package com.vaastu.survey.ui

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.provider.Settings
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Explore
import androidx.compose.material.icons.filled.Height
import androidx.compose.material.icons.filled.IosShare
import androidx.compose.material.icons.filled.Map
import androidx.compose.material.icons.filled.PinDrop
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.lifecycle.viewmodel.compose.viewModel

private enum class Tab(val label: String, val icon: ImageVector) {
    SURVEY("Survey", Icons.Filled.PinDrop),
    PLAN("Plan", Icons.Filled.Map),
    WALK("Walk", Icons.Filled.Explore),
    ELEVATION("Elevation", Icons.Filled.Height),
    EXPORT("Export", Icons.Filled.IosShare),
}

private fun hasPermission(ctx: Context, perm: String): Boolean =
    ContextCompat.checkSelfPermission(ctx, perm) == PackageManager.PERMISSION_GRANTED

@Composable
fun VaastuApp() {
    val context = LocalContext.current
    val vm: SurveyViewModel = viewModel()

    var locationGranted by remember {
        mutableStateOf(hasPermission(context, Manifest.permission.ACCESS_FINE_LOCATION))
    }

    val permLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions(),
    ) { result ->
        locationGranted = result[Manifest.permission.ACCESS_FINE_LOCATION] == true ||
            result[Manifest.permission.ACCESS_COARSE_LOCATION] == true
        if (locationGranted) vm.startLocation()
    }

    LaunchedEffect(Unit) {
        if (locationGranted) {
            vm.startLocation()
        } else {
            permLauncher.launch(initialPermissions())
        }
    }

    if (!locationGranted) {
        PermissionGate(
            onRequest = { permLauncher.launch(initialPermissions()) },
            onOpenSettings = { openAppSettings(context) },
        )
        return
    }

    var tab by remember { mutableStateOf(Tab.SURVEY) }

    Scaffold(
        bottomBar = {
            NavigationBar {
                Tab.entries.forEach { t ->
                    NavigationBarItem(
                        selected = tab == t,
                        onClick = { tab = t },
                        icon = { Icon(t.icon, contentDescription = t.label) },
                        label = { Text(t.label) },
                    )
                }
            }
        },
    ) { padding ->
        Column(modifier = Modifier.fillMaxSize().padding(padding)) {
            when (tab) {
                Tab.SURVEY -> SurveyScreen(vm)
                Tab.PLAN -> PlanScreen(vm)
                Tab.WALK -> WalkScreen(vm)
                Tab.ELEVATION -> ElevationScreen(vm)
                Tab.EXPORT -> ExportScreen(vm)
            }
        }
    }
}

private fun initialPermissions(): Array<String> {
    val list = mutableListOf(
        Manifest.permission.ACCESS_FINE_LOCATION,
        Manifest.permission.ACCESS_COARSE_LOCATION,
    )
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        list.add(Manifest.permission.POST_NOTIFICATIONS)
    }
    return list.toTypedArray()
}

private fun openAppSettings(context: Context) {
    val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
        data = Uri.fromParts("package", context.packageName, null)
        addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    }
    context.startActivity(intent)
}

@Composable
private fun PermissionGate(onRequest: () -> Unit, onOpenSettings: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().padding(32.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp, Alignment.CenterVertically),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text("Location needed", style = MaterialTheme.typography.headlineSmall)
        Text(
            "Vaastu Survey uses precise GPS to map your plot's corners, measure side " +
                "lengths, compute the center, and find each point's direction. Please grant " +
                "location (choose \"Precise\").",
            textAlign = TextAlign.Center,
            style = MaterialTheme.typography.bodyMedium,
        )
        Button(onClick = onRequest) { Text("Grant location") }
        Button(onClick = onOpenSettings) { Text("Open app settings") }
    }
}
