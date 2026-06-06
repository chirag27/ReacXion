package com.reacxion.jyotish.ui

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val Indigo = Color(0xFF3F3D8C)
private val Amber = Color(0xFFC4862C)

private val LightColors = lightColorScheme(primary = Indigo, secondary = Amber)
private val DarkColors = darkColorScheme(primary = Color(0xFFB7B4FF), secondary = Amber)

@Composable
fun JyotishTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = if (isSystemInDarkTheme()) DarkColors else LightColors,
        content = content,
    )
}
