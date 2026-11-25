package com.lifesync.mobile.data.local.alerts

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.lifesync.mobile.domain.model.AlertEvent
import com.lifesync.mobile.domain.model.AlertSeverity
import com.lifesync.mobile.domain.observer.AlertEventPublisher
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

/**
 * Punto de entrada del sistema operativo cuando vence un recordatorio.
 * Notifica al usuario y publica el evento a los observadores (Observer).
 */
@AndroidEntryPoint
class MedicationReminderReceiver : BroadcastReceiver() {

    @Inject
    lateinit var notificationFactory: AlertNotificationFactory

    @Inject
    lateinit var publisher: AlertEventPublisher

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != ACTION_REMIND) return

        val medicationId = intent.getStringExtra(EXTRA_MEDICATION_ID) ?: return
        val title = intent.getStringExtra(EXTRA_TITLE) ?: return
        val message = intent.getStringExtra(EXTRA_MESSAGE) ?: return
        val severity = runCatching {
            AlertSeverity.valueOf(intent.getStringExtra(EXTRA_SEVERITY) ?: "")
        }.getOrDefault(AlertSeverity.MEDIUM)

        val event = AlertEvent.Fired(
            alertId = medicationId,
            title = title,
            message = message,
            severity = severity,
            firedAtEpochMillis = System.currentTimeMillis(),
        )

        notificationFactory.notifyFired(event)
        publisher.publish(event)
    }

    companion object {
        const val ACTION_REMIND = "com.lifesync.mobile.action.MEDICATION_REMINDER"
        const val EXTRA_MEDICATION_ID = "extra_medication_id"
        const val EXTRA_TITLE = "extra_title"
        const val EXTRA_MESSAGE = "extra_message"
        const val EXTRA_SEVERITY = "extra_severity"
    }
}
