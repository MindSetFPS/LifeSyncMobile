package com.lifesync.mobile.data.remote

import com.lifesync.mobile.core.security.TokenStorage
import okhttp3.Interceptor
import okhttp3.Response

/** Inyecta el JWT del Keystore en todas las rutas excepto las públicas. */
class AuthInterceptor(private val tokenStorage: TokenStorage) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        val path = request.url.encodedPath
        val isPublic = PUBLIC_PATHS.any { path.endsWith(it) }
        if (isPublic) return chain.proceed(request)

        val token = tokenStorage.getAccessToken()
        val authorized = if (token.isNullOrBlank()) {
            request
        } else {
            request.newBuilder().header("Authorization", "Bearer $token").build()
        }
        return chain.proceed(authorized)
    }

    private companion object {
        val PUBLIC_PATHS = listOf("/auth/token", "/auth/register", "/auth/refresh")
    }
}
