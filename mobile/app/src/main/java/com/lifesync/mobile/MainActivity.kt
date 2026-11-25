package com.lifesync.mobile

import android.Manifest
import android.content.ActivityNotFoundException
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.core.content.ContextCompat
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.lifesync.mobile.core.oauth.AuthorizationResponse
import com.lifesync.mobile.domain.model.AlertEvent
import com.lifesync.mobile.navigation.AppNavigation
import com.lifesync.mobile.presentation.LifeSyncTheme
import com.lifesync.mobile.presentation.alerts.AlertsViewModel
import com.lifesync.mobile.presentation.auth.AuthViewModel
import com.lifesync.mobile.presentation.home.HomeViewModel
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    private val authViewModel: AuthViewModel by viewModels()
    private val homeViewModel: HomeViewModel by viewModels()
    private val alertsViewModel: AlertsViewModel by viewModels()

    private val notificationPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission(),
    ) { }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        requestNotificationPermissionIfNeeded()

        setContent {
            LifeSyncTheme {
                val isAuthenticated by authViewModel.isAuthenticated
                    .collectAsStateWithLifecycle(initialValue = false)

                LaunchedEffect(Unit) {
                    alertsViewModel.events.collect { event ->
                        if (event is AlertEvent.Fired) {
                            Toast.makeText(
                                this@MainActivity,
                                "${event.title}: ${event.message}",
                                Toast.LENGTH_LONG,
                            ).show()
                        }
                    }
                }

                AppNavigation(
                    isAuthenticated = isAuthenticated,
                    authViewModel = authViewModel,
                    homeViewModel = homeViewModel,
                    alertsViewModel = alertsViewModel,
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

    private fun requestNotificationPermissionIfNeeded() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
            ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.POST_NOTIFICATIONS,
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            notificationPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
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
