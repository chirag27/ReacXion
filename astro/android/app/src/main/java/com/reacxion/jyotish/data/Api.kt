package com.reacxion.jyotish.data

import com.jakewharton.retrofit2.converter.kotlinx.serialization.asConverterFactory
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import java.util.concurrent.TimeUnit

/** The subset of backend endpoints the app uses. */
interface JyotishApi {
    @GET("/health")
    suspend fun health(): Health

    @POST("/report")
    suspend fun report(@Body body: BirthBody): Report

    @POST("/ask")
    suspend fun ask(@Body body: AskBody): AskResponse
}

/** Builds a [JyotishApi] for a given base URL (recreated when the URL changes). */
object ApiProvider {
    private val json = Json {
        ignoreUnknownKeys = true
        coerceInputValues = true
    }

    fun create(baseUrl: String): JyotishApi {
        val normalized = if (baseUrl.endsWith("/")) baseUrl else "$baseUrl/"
        val client = OkHttpClient.Builder()
            .connectTimeout(10, TimeUnit.SECONDS)
            .readTimeout(120, TimeUnit.SECONDS)   // /ask can run several tool turns
            .build()
        return Retrofit.Builder()
            .baseUrl(normalized)
            .client(client)
            .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
            .build()
            .create(JyotishApi::class.java)
    }
}
