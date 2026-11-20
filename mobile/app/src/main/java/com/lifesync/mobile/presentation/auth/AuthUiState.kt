package com.lifesync.mobile.presentation.auth

import com.lifesync.mobile.domain.model.User

data class AuthUiState(
    val email: String = "",
    val password: String = "",
    val fullName: String = "",
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
)

sealed interface AuthEvent {
    data object NavigateToLogin : AuthEvent
}

data class HomeUiState(
    val user: User? = null,
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
)
