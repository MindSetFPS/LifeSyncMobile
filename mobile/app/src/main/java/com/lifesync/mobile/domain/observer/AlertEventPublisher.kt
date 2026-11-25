package com.lifesync.mobile.domain.observer

import com.lifesync.mobile.domain.model.AlertEvent
import kotlinx.coroutines.flow.SharedFlow

/**
 * Sujeto observable del módulo de alertas médicas locales.
 *
 * Permite que cualquier componente (ViewModel, repositorio, UI) observe los
 * eventos de alerta sin que el emisor los conozca: patrón Observer.
 */
interface AlertEventPublisher {
    /** Flujo multicast: todos los observadores reciben cada evento. */
    val events: SharedFlow<AlertEvent>

    /** No bloqueante; pensado para `BroadcastReceiver.onReceive`. */
    fun publish(event: AlertEvent)
}
