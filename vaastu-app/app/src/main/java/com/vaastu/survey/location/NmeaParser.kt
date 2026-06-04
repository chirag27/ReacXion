package com.vaastu.survey.location

import com.vaastu.survey.core.geo.GeoPoint

/**
 * Minimal NMEA-0183 parser for GGA / RMC sentences (GP, GN, GL talkers), enough
 * to drive positioning from an external GNSS/RTK receiver over a serial stream.
 * Pure Kotlin so it is unit-testable without a device.
 */
object NmeaParser {

    /** Parses one sentence; returns a fix or null if the line is not a usable GGA/RMC. */
    fun parse(line: String): GeoPoint? {
        val s = line.trim()
        if (!s.startsWith("$")) return null
        val body = s.substringAfter('$').substringBefore('*')
        val f = body.split(',')
        if (f.isEmpty()) return null
        val type = f[0]
        return when {
            type.endsWith("GGA") -> parseGga(f)
            type.endsWith("RMC") -> parseRmc(f)
            else -> null
        }
    }

    private fun parseGga(f: List<String>): GeoPoint? {
        // type,time,lat,NS,lon,EW,fixQ,numSat,hdop,alt,M,...
        if (f.size < 11) return null
        val lat = coord(f[2], f[3]) ?: return null
        val lon = coord(f[4], f[5]) ?: return null
        val fixQ = f[6].toIntOrNull() ?: 0
        if (fixQ == 0) return null
        val hdop = f[8].toDoubleOrNull() ?: 1.0
        val alt = f[9].toDoubleOrNull()
        return GeoPoint(lat, lon, alt, accFor(fixQ, hdop), System.currentTimeMillis())
    }

    private fun parseRmc(f: List<String>): GeoPoint? {
        // type,time,status,lat,NS,lon,EW,...
        if (f.size < 7) return null
        if (f[2] != "A") return null // A = valid
        val lat = coord(f[3], f[4]) ?: return null
        val lon = coord(f[5], f[6]) ?: return null
        return GeoPoint(lat, lon, null, accFor(1, 1.0), System.currentTimeMillis())
    }

    /** NMEA ddmm.mmmm + hemisphere -> signed decimal degrees. */
    private fun coord(value: String, hemi: String): Double? {
        if (value.isBlank()) return null
        val dot = value.indexOf('.')
        if (dot < 3) return null
        val degLen = if (dot == 4) 2 else 3 // lat=2 deg digits, lon=3
        val deg = value.substring(0, degLen).toDoubleOrNull() ?: return null
        val min = value.substring(degLen).toDoubleOrNull() ?: return null
        var dec = deg + min / 60.0
        if (hemi == "S" || hemi == "W") dec = -dec
        return dec
    }

    /** Rough horizontal accuracy (m) from fix quality + HDOP. */
    private fun accFor(fixQuality: Int, hdop: Double): Float = when (fixQuality) {
        4 -> 0.05f // RTK fixed
        5 -> 0.5f // RTK float
        2 -> (hdop * 2.0).toFloat() // DGPS
        else -> (hdop * 5.0).toFloat() // autonomous
    }
}
