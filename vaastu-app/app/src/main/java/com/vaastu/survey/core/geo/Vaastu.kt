package com.vaastu.survey.core.geo

/**
 * The 16 Vaastu directions, each spanning 22.5 deg centered on [centerDeg].
 * Sanskrit / lord names are given for the eight principal zones.
 */
enum class VaastuZone(
    val abbr: String,
    val centerDeg: Double,
    val sanskrit: String,
    val lord: String,
) {
    N("N", 0.0, "Uttara", "Kubera"),
    NNE("NNE", 22.5, "Uttara-Ishanya", "Kubera–Ishana"),
    NE("NE", 45.0, "Ishanya", "Ishana"),
    ENE("ENE", 67.5, "Purva-Ishanya", "Ishana–Indra"),
    E("E", 90.0, "Purva", "Indra"),
    ESE("ESE", 112.5, "Purva-Agneya", "Indra–Agni"),
    SE("SE", 135.0, "Agneya", "Agni"),
    SSE("SSE", 157.5, "Dakshina-Agneya", "Agni–Yama"),
    S("S", 180.0, "Dakshina", "Yama"),
    SSW("SSW", 202.5, "Dakshina-Nairutya", "Yama–Nirayti"),
    SW("SW", 225.0, "Nairutya", "Nirayti"),
    WSW("WSW", 247.5, "Paschima-Nairutya", "Nirayti–Varuna"),
    W("W", 270.0, "Paschima", "Varuna"),
    WNW("WNW", 292.5, "Paschima-Vayavya", "Varuna–Vayu"),
    NW("NW", 315.0, "Vayavya", "Vayu"),
    NNW("NNW", 337.5, "Uttara-Vayavya", "Vayu–Kubera");

    companion object {
        /** Maps a compass bearing (deg) to one of the 16 zones. */
        fun fromBearing(deg: Double): VaastuZone {
            val d = ((deg % 360) + 360) % 360
            val idx = (Math.round(d / 22.5).toInt()) % 16
            return entries[idx]
        }
    }
}
