package com.lifesync.mobile.presentation.alerts

import com.lifesync.mobile.domain.model.AlertEvent

data class AlertsUiState(
    val scheduledCount: Int = 0,
    val isScheduling: Boolean = false,
    val lastFired: AlertEvent.Fired? = null,
    val errorMessage: String? = null,
)
