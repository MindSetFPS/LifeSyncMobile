package com.lifesync.mobile.presentation.alerts

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.lifesync.mobile.core.result.Resource
import com.lifesync.mobile.domain.model.AlertEvent
import com.lifesync.mobile.domain.observer.AlertEventPublisher
import com.lifesync.mobile.domain.usecase.ScheduleMedicationRemindersUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

/** Observador de eventos de alerta + motor de sincronización de la agenda. */
@HiltViewModel
class AlertsViewModel @Inject constructor(
    private val scheduleReminders: ScheduleMedicationRemindersUseCase,
    publisher: AlertEventPublisher,
) : ViewModel() {

    private val _uiState = MutableStateFlow(AlertsUiState())
    val uiState: StateFlow<AlertsUiState> = _uiState.asStateFlow()

    /** Flujo observable para que la UI reaccione a alertas disparadas. */
    val events: SharedFlow<AlertEvent> = publisher.events

    init {
        viewModelScope.launch {
            publisher.events.collect { event ->
                if (event is AlertEvent.Fired) {
                    _uiState.update { it.copy(lastFired = event) }
                }
            }
        }
    }

    fun syncSchedules() {
        viewModelScope.launch {
            _uiState.update { it.copy(isScheduling = true, errorMessage = null) }
            when (val result = scheduleReminders()) {
                is Resource.Success -> _uiState.update {
                    it.copy(isScheduling = false, scheduledCount = result.data)
                }
                is Resource.Error -> _uiState.update {
                    it.copy(isScheduling = false, errorMessage = result.message)
                }
                Resource.Loading -> Unit
            }
        }
    }
}
