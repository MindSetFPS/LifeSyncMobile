package com.lifesync.mobile.di

import android.content.Context
import com.jakewharton.retrofit2.converter.kotlinx.serialization.asConverterFactory
import com.lifesync.mobile.BuildConfig
import com.lifesync.mobile.core.security.TokenStorage
import com.lifesync.mobile.data.local.SecureTokenStorage
import com.lifesync.mobile.data.remote.AuthAuthenticator
import com.lifesync.mobile.data.remote.AuthInterceptor
import com.lifesync.mobile.data.remote.service.AuthApiService
import com.lifesync.mobile.data.remote.service.HealthApiService
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
        createRetrofit(json, OkHttpClient.Builder().build())
            .create(AuthApiService::class.java)

    @Provides
    @Singleton
    fun provideAuthenticator(
        tokenStorage: TokenStorage,
        @Named("refresh") refreshApi: AuthApiService,
    ): AuthAuthenticator = AuthAuthenticator(tokenStorage, refreshApi)

    @Provides
    @Singleton
    @Named("authenticated")
    fun provideAuthenticatedClient(
        tokenStorage: TokenStorage,
        authenticator: AuthAuthenticator,
    ): OkHttpClient {
        val logging = HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BASIC
            else HttpLoggingInterceptor.Level.NONE
        }
        return OkHttpClient.Builder()
            .addInterceptor(AuthInterceptor(tokenStorage))
            .authenticator(authenticator)
            .addInterceptor(logging)
            .build()
    }

    @Provides
    @Singleton
    fun provideAuthenticatedRetrofit(
        json: Json,
        @Named("authenticated") client: OkHttpClient,
    ): Retrofit = createRetrofit(json, client)

    @Provides
    @Singleton
    fun provideAuthApi(retrofit: Retrofit): AuthApiService =
        retrofit.create(AuthApiService::class.java)

    @Provides
    @Singleton
    fun provideHealthApi(retrofit: Retrofit): HealthApiService =
        retrofit.create(HealthApiService::class.java)

    private fun createRetrofit(json: Json, client: OkHttpClient): Retrofit =
        Retrofit.Builder()
            .baseUrl(BuildConfig.API_BASE_URL)
            .client(client)
            .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
            .build()
}
