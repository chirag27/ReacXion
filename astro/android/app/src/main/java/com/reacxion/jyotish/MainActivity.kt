package com.reacxion.jyotish

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.lifecycle.viewmodel.compose.viewModel
import com.reacxion.jyotish.ui.ConsultViewModel
import com.reacxion.jyotish.ui.JyotishApp
import com.reacxion.jyotish.ui.JyotishTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            JyotishTheme {
                val vm: ConsultViewModel = viewModel()
                JyotishApp(vm)
            }
        }
    }
}
