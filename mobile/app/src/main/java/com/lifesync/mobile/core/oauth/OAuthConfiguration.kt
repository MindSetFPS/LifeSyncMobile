package com.lifesync.mobile.core.oauth

import com.lifesync.mobile.BuildConfig
import java.net.URLEncoder

/** Configuración del cliente OAuth y construcción de la URL de autorización. */
object OAuthConfiguration {
    const val CLIENT_ID = "lifesync-android"
    const val REDIRECT_SCHEME = "com.lifesync.mobile"
    const val REDIRECT_HOST = "oauth2callback"
    const val REDIRECT_URI = "$REDIRECT_SCHEME://$REDIRECT_HOST"
    const val SCOPE = "read write offline_access"

    /**
     * URL del endpoint `/oauth/authorize`. Se abre en un navegador externo
     * (RFC 8252 §8.12), nunca en un WebView, para que el usuario vea el
     * dominio real cuando introduce sus credenciales.
     */
    fun authorizationUrl(
        state: String,
        codeChallenge: String,
        baseUrl: String = BuildConfig.API_BASE_URL,
    ): String {
        val endpoint = baseUrl.trimEnd('/') + "/oauth/authorize"
        val params = listOf(
            "response_type" to "code",
            "client_id" to CLIENT_ID,
            "redirect_uri" to REDIRECT_URI,
            "scope" to SCOPE,
            "state" to state,
            "code_challenge" to codeChallenge,
            "code_challenge_method" to "S256",
        ).joinToString("&") { (key, value) ->
            "$key=${URLEncoder.encode(value, "UTF-8")}"
        }
        return "$endpoint?$params"
    }
}
