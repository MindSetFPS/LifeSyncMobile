package com.lifesync.mobile.data.remote

import com.lifesync.mobile.core.security.TokenStorage
import com.lifesync.mobile.data.remote.dto.RefreshRequest
import com.lifesync.mobile.data.remote.service.AuthApiService
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import okhttp3.Authenticator
import okhttp3.Request
import okhttp3.Response
import okhttp3.Route
import javax.inject.Inject
import javax.inject.Named

/**
 * Ante un 401 renueva el access token usando el refresh token almacenado.
 * El mutex evita la "tormenta de refresh" cuando varias peticiones fallan
 * simultáneamente; usa un cliente HTTP sin interceptor para no recursar.
 */
class AuthAuthenticator @Inject constructor(
    private val tokenStorage: TokenStorage,
    @Named("refresh") private val refreshApi: AuthApiService,
) : Authenticator {
    private val mutex = Mutex()

    override fun authenticate(route: Route?, response: Response): Request? {
        if (response.code != 401) return null
        return runBlocking(Dispatchers.IO) {
            mutex.withLock {
                val sentToken = response.request.header("Authorization")?.removePrefix("Bearer ")
                val storedToken = tokenStorage.getAccessToken()
                if (!storedToken.isNullOrBlank() && storedToken != sentToken) {
                    return@withLock response.request.newBuilder()
                        .header("Authorization", "Bearer $storedToken")
                        .build()
                }

                val refreshToken = tokenStorage.getRefreshToken() ?: return@withLock null
                val refreshed = try {
                    withContext(Dispatchers.IO) {
                        refreshApi.refresh(RefreshRequest(refreshToken))
                    }
                } catch (_: Exception) {
                    return@withLock null
                }
                tokenStorage.save(refreshed.toDomain())
                response.request.newBuilder()
                    .header("Authorization", "Bearer ${refreshed.accessToken}")
                    .build()
            }
        }
    }
}
