package com.vaastu.survey.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val Teal = Color(0xFF0E5A4E)
private val TealLight = Color(0xFF3E8E7E)
private val Amber = Color(0xFFFFB300)

private val LightColors = lightColorScheme(
    primary = Teal,
    secondary = TealLight,
    tertiary = Amber,
)

private val DarkColors = darkColorScheme(
    primary = TealLight,
    secondary = Teal,
    tertiary = Amber,
)

@Composable
fun VaastuTheme(content: @Composable () -> Unit) {
    val colors = if (isSystemInDarkTheme()) DarkColors else LightColors
    MaterialTheme(colorScheme = colors, content = content)
}
