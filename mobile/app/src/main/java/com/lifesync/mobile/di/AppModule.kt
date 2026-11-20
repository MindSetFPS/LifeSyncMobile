package com.lifesync.mobile.di

import android.content.Context
import com.jakewharton.retrofit2.converter.kotlinx.serialization.asConverterFactory
import com.lifesync.mobile.BuildConfig
import com.lifesync.mobile.core.security.TokenStorage
import com.lifesync.mobile.data.local.SecureTokenStorage
import com.lifesync.mobile.data.remote.AuthAuthenticator
import com.lifesync.mobile.data.remote.AuthInterceptor
import com.lifesync.mobile.data.remote.service.AuthApiService
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import javax.inject.Named
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton
    fun provideJson(): Json = Json { ignoreUnknownKeys = true }

    @Provides
    @Singleton
    fun provideTokenStorage(@ApplicationContext context: Context): TokenStorage =
        SecureTokenStorage(context)

    /** Cliente sin autenticación: evita recursión al refrescar el token. */
    @Provides
    @Singleton
    @Named("refresh")
    fun provideRefreshApi(json: Json): AuthApiService =
        createApi(json, OkHttpClient.Builder().build())

    @Provides
    @Singleton
    fun provideAuthenticator(
        tokenStorage: TokenStorage,
        @Named("refresh") refreshApi: AuthApiService,
    ): AuthAuthenticator = AuthAuthenticator(tokenStorage, refreshApi)

    @Provides
    @Singleton
    @Named("auth")
    fun provideAuthApi(
        json: Json,
        tokenStorage: TokenStorage,
        authenticator: AuthAuthenticator,
    ): AuthApiService {
        val logging = HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BASIC
            else HttpLoggingInterceptor.Level.NONE
        }
        val client = OkHttpClient.Builder()
            .addInterceptor(AuthInterceptor(tokenStorage))
            .authenticator(authenticator)
            .addInterceptor(logging)
            .build()
        return createApi(json, client)
    }

    private fun createApi(json: Json, client: OkHttpClient): AuthApiService =
        Retrofit.Builder()
            .baseUrl(BuildConfig.API_BASE_URL)
            .client(client)
            .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
            .build()
            .create(AuthApiService::class.java)
}
