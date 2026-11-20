package com.lifesync.mobile.presentation.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.lifesync.mobile.core.result.Resource
import com.lifesync.mobile.domain.repository.AuthRepository
import com.lifesync.mobile.domain.usecase.LoginUseCase
import com.lifesync.mobile.domain.usecase.RegisterUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val loginUseCase: LoginUseCase,
    private val registerUseCase: RegisterUseCase,
    authRepository: AuthRepository,
) : ViewModel() {
    val isAuthenticated = authRepository.isAuthenticated

    private val _uiState = MutableStateFlow(AuthUiState())
    val uiState: StateFlow<AuthUiState> = _uiState.asStateFlow()

    private val _events = MutableSharedFlow<AuthEvent>(extraBufferCapacity = 1)
    val events: SharedFlow<AuthEvent> = _events.asSharedFlow()

    fun onEmailChange(value: String) = _uiState.update { it.copy(email = value, errorMessage = null) }
    fun onPasswordChange(value: String) = _uiState.update { it.copy(password = value, errorMessage = null) }
    fun onFullNameChange(value: String) = _uiState.update { it.copy(fullName = value, errorMessage = null) }

    fun login() = submit(register = false)
    fun register() = submit(register = true)

    private fun submit(register: Boolean) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            val state = _uiState.value
            val result = if (register) {
                registerUseCase(state.email, state.fullName, state.password)
            } else {
                loginUseCase(state.email, state.password)
            }

            _uiState.update {
                when (result) {
                    is Resource.Success -> it.copy(isLoading = false, errorMessage = null)
                    is Resource.Error -> it.copy(isLoading = false, errorMessage = result.message)
                    Resource.Loading -> it.copy(isLoading = true)
                }
            }

            if (register && result is Resource.Success) {
                _events.tryEmit(AuthEvent.NavigateToLogin)
            }
        }
    }
}
