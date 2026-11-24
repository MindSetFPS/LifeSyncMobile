package com.lifesync.mobile

import android.content.ActivityNotFoundException
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.runtime.getValue
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.lifesync.mobile.core.oauth.AuthorizationResponse
import com.lifesync.mobile.navigation.AppNavigation
import com.lifesync.mobile.presentation.LifeSyncTheme
import com.lifesync.mobile.presentation.auth.AuthViewModel
import com.lifesync.mobile.presentation.home.HomeViewModel
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    private val authViewModel: AuthViewModel by viewModels()
    private val homeViewModel: HomeViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            LifeSyncTheme {
                val isAuthenticated by authViewModel.isAuthenticated
                    .collectAsStateWithLifecycle(initialValue = false)
                AppNavigation(
                    isAuthenticated = isAuthenticated,
                    authViewModel = authViewModel,
                    homeViewModel = homeViewModel,
                    onLaunchAuthorization = ::openAuthorizationUrl,
                )
            }
        }

        handleAuthorizationRedirect(intent)
    }

    /** El navegador vuelve por el deep link; no se reutiliza la tarea existente. */
    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        handleAuthorizationRedirect(intent)
    }

    /**
     * Abre el endpoint de autorización en el navegador externo (RFC 8252 §8.12).
     * Un WebView ocultaría la barra de direcciones y permitiría phishing.
     */
    private fun openAuthorizationUrl(url: String) {
        val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
        try {
            startActivity(intent)
        } catch (_: ActivityNotFoundException) {
            authViewModel.onAuthorizationFailed(
                "No hay un navegador disponible para completar la autorización",
            )
        }
    }

    private fun handleAuthorizationRedirect(intent: Intent?) {
        val data = intent?.data ?: return
        when (val response = AuthorizationResponse.parse(data)) {
            is AuthorizationResponse.Success -> authViewModel.onAuthorizationRedirect(
                code = response.code,
                state = response.state,
            )
            is AuthorizationResponse.Failure -> authViewModel.onAuthorizationFailed(
                response.description ?: response.error,
            )
            AuthorizationResponse.Invalid -> authViewModel.onAuthorizationFailed(
                "Respuesta de autorización inválida",
            )
        }
    }
}
