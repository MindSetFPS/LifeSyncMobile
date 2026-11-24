package com.lifesync.mobile.core.oauth

import android.net.Uri

/** Resultado del redirect de autorización (RFC 6749 §4.1.2). */
sealed interface AuthorizationResponse {
    data class Success(val code: String, val state: String?) : AuthorizationResponse
    data class Failure(val error: String, val description: String?, val state: String?) :
        AuthorizationResponse
    data object Invalid : AuthorizationResponse

    companion object {
        /** Parsea `com.lifesync.mobile://oauth2callback?code=...&state=...`. */
        fun parse(uri: Uri): AuthorizationResponse {
            if (uri.scheme != OAuthConfiguration.REDIRECT_SCHEME) return Invalid
            if (uri.host != OAuthConfiguration.REDIRECT_HOST) return Invalid

            val state = uri.getQueryParameter("state")
            val code = uri.getQueryParameter("code")
            val error = uri.getQueryParameter("error")

            return when {
                error != null -> Failure(
                    error = error,
                    description = uri.getQueryParameter("error_description"),
                    state = state,
                )
                !code.isNullOrBlank() -> Success(code, state)
                else -> Invalid
            }
        }
    }
}
