package com.lifesync.mobile.data.local.alerts

import com.lifesync.mobile.domain.model.AlertEvent
import com.lifesync.mobile.domain.observer.AlertEventPublisher
import kotlinx.coroutines.channels.BufferOverflow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import javax.inject.Inject
import javax.inject.Singleton

/** Implementación en memoria del sujeto observable (Observer). */
@Singleton
class InMemoryAlertEventPublisher @Inject constructor() : AlertEventPublisher {
    private val _events = MutableSharedFlow<AlertEvent>(
        replay = 0,
        extraBufferCapacity = 32,
        onBufferOverflow = BufferOverflow.DROP_OLDEST,
    )

    override val events: SharedFlow<AlertEvent> = _events.asSharedFlow()

    override fun publish(event: AlertEvent) {
        _events.tryEmit(event)
    }
}
