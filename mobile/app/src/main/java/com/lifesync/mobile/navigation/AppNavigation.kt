package com.lifesync.mobile.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.navigation
import androidx.navigation.compose.rememberNavController
import com.lifesync.mobile.presentation.alerts.AlertsViewModel
import com.lifesync.mobile.presentation.auth.AuthEvent
import com.lifesync.mobile.presentation.auth.AuthViewModel
import com.lifesync.mobile.presentation.auth.login.LoginScreen
import com.lifesync.mobile.presentation.auth.register.RegisterScreen
import com.lifesync.mobile.presentation.home.HomeScreen
import com.lifesync.mobile.presentation.home.HomeViewModel
import com.lifesync.mobile.presentation.profile.PatientProfileRoute

private const val AUTH_GRAPH = "auth_graph"
private const val MAIN_GRAPH = "main_graph"
private const val LOGIN = "login"
private const val REGISTER = "register"
private const val HOME = "home"
private const val PATIENT_PROFILE = "patient_profile"

/**
 * Navidad protegida: dos pilas independientes. El estado de autenticación
 * (observado desde el Keystore) decide qué grafo está activo y se aplica
 * `popUpTo(inclusive = true)` para impedir volver atrás con el botón Back.
 */
@Composable
fun AppNavigation(
    isAuthenticated: Boolean,
    authViewModel: AuthViewModel,
    homeViewModel: HomeViewModel,
    alertsViewModel: AlertsViewModel,
    onLaunchAuthorization: (String) -> Unit,
) {
    val navController: NavHostController = rememberNavController()
    val authState by authViewModel.uiState.collectAsStateWithLifecycle()
    val homeState by homeViewModel.uiState.collectAsStateWithLifecycle()

    LaunchedEffect(authViewModel.events) {
        authViewModel.events.collect { event ->
            when (event) {
                AuthEvent.NavigateToLogin -> navController.navigate(LOGIN)
                is AuthEvent.LaunchAuthorization -> onLaunchAuthorization(event.url)
            }
        }
    }

    LaunchedEffect(isAuthenticated) {
        val target = if (isAuthenticated) MAIN_GRAPH else AUTH_GRAPH
        val from = if (isAuthenticated) AUTH_GRAPH else MAIN_GRAPH
        navController.navigate(target) {
            popUpTo(from) { inclusive = true }
            launchSingleTop = true
        }
        if (isAuthenticated) alertsViewModel.syncSchedules()
    }

    NavHost(
        navController = navController,
        startDestination = if (isAuthenticated) MAIN_GRAPH else AUTH_GRAPH,
    ) {
        navigation(startDestination = LOGIN, route = AUTH_GRAPH) {
            composable(LOGIN) {
                LoginScreen(
                    uiState = authState,
                    onEmailChange = authViewModel::onEmailChange,
                    onPasswordChange = authViewModel::onPasswordChange,
                    onLogin = authViewModel::login,
                    onAuthorizeWithBrowser = authViewModel::startAuthorization,
                    onNavigateToRegister = { navController.navigate(REGISTER) },
                )
            }
            composable(REGISTER) {
                RegisterScreen(
                    uiState = authState,
                    onFullNameChange = authViewModel::onFullNameChange,
                    onEmailChange = authViewModel::onEmailChange,
                    onPasswordChange = authViewModel::onPasswordChange,
                    onRegister = authViewModel::register,
                    onNavigateToLogin = { navController.popBackStack() },
                )
            }
        }

        navigation(startDestination = HOME, route = MAIN_GRAPH) {
            composable(HOME) {
                LaunchedEffect(Unit) { homeViewModel.loadProfile() }
                HomeScreen(
                    uiState = homeState,
                    onOpenPatientProfile = { navController.navigate(PATIENT_PROFILE) },
                    onLogout = homeViewModel::logout,
                    onRetry = homeViewModel::loadProfile,
                )
            }
            composable(PATIENT_PROFILE) {
                PatientProfileRoute(onBack = { navController.popBackStack() })
            }
        }
    }
}
