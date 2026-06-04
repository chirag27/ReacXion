package com.vaastu.survey

import android.os.Bundle
import android.view.WindowManager
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.vaastu.survey.ui.VaastuApp
import com.vaastu.survey.ui.theme.VaastuTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Keep the screen on while surveying / walking the plot.
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        setContent {
            VaastuTheme {
                VaastuApp()
            }
        }
    }
}
