package com.reacxion.jyotish.data

import kotlinx.serialization.Serializable

/** Birth input sent to the backend (timezone as an IANA name, e.g. "Asia/Kolkata"). */
@Serializable
data class BirthBody(
    val year: Int,
    val month: Int,
    val day: Int,
    val hour: Int,
    val minute: Int,
    val second: Int = 0,
    val latitude: Double,
    val longitude: Double,
    val timezone: String,
    val name: String = "",
)

@Serializable
data class AskBody(
    val year: Int,
    val month: Int,
    val day: Int,
    val hour: Int,
    val minute: Int,
    val second: Int = 0,
    val latitude: Double,
    val longitude: Double,
    val timezone: String,
    val name: String = "",
    val question: String,
)

// ---- Response subsets (ignoreUnknownKeys is on, so we model only what we render) ----

@Serializable
data class Planet(
    val longitude: Double,
    val sign: String,
    val nakshatra: String,
    val nakshatra_lord: String,
    val pada: Int,
    val sub_lord: String,
    val retrograde: Boolean,
)

@Serializable
data class ChartFacts(
    val ascendant: Double,
    val planets: Map<String, Planet>,
)

@Serializable
data class DashaLink(
    val lord: String,
    val level_name: String = "",
    val start: String,
    val end: String,
)

@Serializable
data class Yoga(
    val name: String,
    val category: String,
    val description: String,
)

@Serializable
data class Remedy(
    val target: String,
    val kind: String,
    val reason: String,
    val text: String,
)

@Serializable
data class Rina(
    val name: String,
    val sanskrit: String,
    val trigger: String,
)

@Serializable
data class TimeConfidence(
    val level: String,
    val note: String,
)

@Serializable
data class Report(
    val name: String = "",
    val vedic_chart: ChartFacts,
    val dasha_now: List<DashaLink> = emptyList(),
    val yogas: List<Yoga> = emptyList(),
    val rinas: List<Rina> = emptyList(),
    val remedies: List<Remedy> = emptyList(),
    val time_confidence: TimeConfidence,
)

@Serializable
data class ToolCall(val tool: String)

@Serializable
data class AskResponse(
    val answer: String,
    val iterations: Int = 0,
    val tool_calls: List<ToolCall> = emptyList(),
)

@Serializable
data class Health(
    val status: String,
    val agent_ready: Boolean = false,
)
