package com.lifesync.mobile.domain.model

/** Eventos que emite el módulo de alertas locales (patrón Observer). */
sealed interface AlertEvent {
    data class Fired(
        val alertId: String,
        val title: String,
        val message: String,
        val severity: AlertSeverity,
        val firedAtEpochMillis: Long,
    ) : AlertEvent

    data class Scheduled(
        val alertId: String,
        val nextFireAtEpochMillis: Long?,
    ) : AlertEvent

    data class Acknowledged(val alertId: String) : AlertEvent
}
