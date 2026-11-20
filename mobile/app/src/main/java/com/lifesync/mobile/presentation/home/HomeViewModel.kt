package com.lifesync.mobile.presentation.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.lifesync.mobile.core.result.Resource
import com.lifesync.mobile.domain.usecase.GetProfileUseCase
import com.lifesync.mobile.domain.usecase.LogoutUseCase
import com.lifesync.mobile.presentation.auth.HomeUiState
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val getProfileUseCase: GetProfileUseCase,
    private val logoutUseCase: LogoutUseCase,
) : ViewModel() {
    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    fun loadProfile() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            when (val result = getProfileUseCase()) {
                is Resource.Success -> _uiState.update {
                    it.copy(user = result.data, isLoading = false, errorMessage = null)
                }
                is Resource.Error -> _uiState.update {
                    it.copy(isLoading = false, errorMessage = result.message)
                }
                Resource.Loading -> Unit
            }
        }
    }

    fun logout() {
        viewModelScope.launch { logoutUseCase() }
    }
}
