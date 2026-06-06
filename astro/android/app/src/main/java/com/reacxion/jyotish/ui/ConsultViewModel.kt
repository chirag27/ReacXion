package com.reacxion.jyotish.ui

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.reacxion.jyotish.data.ApiProvider
import com.reacxion.jyotish.data.AskBody
import com.reacxion.jyotish.data.AskResponse
import com.reacxion.jyotish.data.BirthBody
import com.reacxion.jyotish.data.Report
import kotlinx.coroutines.launch

/** Editable birth-form state. */
data class BirthForm(
    val name: String = "",
    val year: String = "1990",
    val month: String = "1",
    val day: String = "1",
    val hour: String = "12",
    val minute: String = "0",
    val latitude: String = "28.6139",
    val longitude: String = "77.2090",
    val timezone: String = "Asia/Kolkata",
)

class ConsultViewModel : ViewModel() {

    var backendUrl by mutableStateOf("http://10.0.2.2:8000")   // host loopback from emulator
        private set
    var form by mutableStateOf(BirthForm())
        private set

    var report by mutableStateOf<Report?>(null)
        private set
    var ask by mutableStateOf<AskResponse?>(null)
        private set
    var loading by mutableStateOf(false)
        private set
    var error by mutableStateOf<String?>(null)
        private set

    fun updateBackendUrl(v: String) { backendUrl = v }
    fun updateForm(f: BirthForm) { form = f }

    private fun birthBody() = BirthBody(
        year = form.year.toInt(), month = form.month.toInt(), day = form.day.toInt(),
        hour = form.hour.toInt(), minute = form.minute.toInt(),
        latitude = form.latitude.toDouble(), longitude = form.longitude.toDouble(),
        timezone = form.timezone.trim(), name = form.name.trim(),
    )

    fun fetchReport() {
        error = null
        val body = try { birthBody() } catch (e: Exception) {
            error = "Check the birth fields: ${e.message}"; return
        }
        loading = true
        viewModelScope.launch {
            try {
                report = ApiProvider.create(backendUrl).report(body)
            } catch (e: Exception) {
                error = "Could not reach the backend at $backendUrl — ${e.message}"
            } finally {
                loading = false
            }
        }
    }

    fun askQuestion(question: String) {
        if (question.isBlank()) return
        error = null
        val b = try { birthBody() } catch (e: Exception) {
            error = "Check the birth fields: ${e.message}"; return
        }
        val body = AskBody(
            b.year, b.month, b.day, b.hour, b.minute, b.second,
            b.latitude, b.longitude, b.timezone, b.name, question.trim())
        loading = true
        ask = null
        viewModelScope.launch {
            try {
                ask = ApiProvider.create(backendUrl).ask(body)
            } catch (e: Exception) {
                error = "Ask failed (is ANTHROPIC_API_KEY set on the backend?) — ${e.message}"
            } finally {
                loading = false
            }
        }
    }
}
