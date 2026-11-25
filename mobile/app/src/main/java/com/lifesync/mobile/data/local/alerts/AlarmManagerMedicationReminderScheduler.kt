package com.lifesync.mobile.data.local.alerts

import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import com.lifesync.mobile.domain.model.Medication
import com.lifesync.mobile.domain.scheduling.MedicationReminderScheduler
import dagger.hilt.android.qualifiers.ApplicationContext
import java.time.ZonedDateTime
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Agenda recordatorios con `AlarmManager`. No hay proceso vivo cuando la app
 * está cerrada, por eso el disparo es del sistema operativo y el Observer
 * reacciona dentro de la app.
 */
@Singleton
class AlarmManagerMedicationReminderScheduler @Inject constructor(
    @ApplicationContext private val context: Context,
) : MedicationReminderScheduler {

    private val alarmManager: AlarmManager =
        context.getSystemService(AlarmManager::class.java)

    override fun schedule(medication: Medication) {
        cancel(medication.id)
        val triggers = MedicationReminderSchedule.nextTriggers(medication, ZonedDateTime.now())
        triggers.forEachIndexed { index, trigger ->
            val pendingIntent = reminderPendingIntent(
                medicationId = medication.id,
                title = medication.name,
                message = buildMessage(medication),
                severity = if (medication.isControlled) HIGH else MEDIUM,
                index = index,
            )
            val millis = trigger.toInstant().toEpochMilli()
            if (canScheduleExact()) {
                alarmManager.setExactAndAllowWhileIdle(
                    AlarmManager.RTC_WAKEUP,
                    millis,
                    pendingIntent,
                )
            } else {
                alarmManager.setWindow(
                    AlarmManager.RTC_WAKEUP,
                    millis,
                    WINDOW_MILLIS,
                    pendingIntent,
                )
            }
        }
    }

    override fun cancel(medicationId: String) {
        for (index in 0 until MedicationReminderSchedule.MAX_TRIGGERS) {
            alarmManager.cancel(
                reminderPendingIntent(
                    medicationId = medicationId,
                    title = "",
                    message = "",
                    severity = MEDIUM,
                    index = index,
                ),
            )
        }
    }

    override fun cancelAll() {
        // La app sólo cancela medicamentos conocidos; cancel() es idempotente.
    }

    private fun reminderPendingIntent(
        medicationId: String,
        title: String,
        message: String,
        severity: String,
        index: Int,
    ): PendingIntent {
        val intent = Intent(context, MedicationReminderReceiver::class.java).apply {
            action = MedicationReminderReceiver.ACTION_REMIND
            putExtra(MedicationReminderReceiver.EXTRA_MEDICATION_ID, medicationId)
            putExtra(MedicationReminderReceiver.EXTRA_TITLE, title)
            putExtra(MedicationReminderReceiver.EXTRA_MESSAGE, message)
            putExtra(MedicationReminderReceiver.EXTRA_SEVERITY, severity)
        }
        return PendingIntent.getBroadcast(
            context,
            requestCode(medicationId, index),
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
    }

    private fun canScheduleExact(): Boolean =
        Build.VERSION.SDK_INT < Build.VERSION_CODES.S ||
            alarmManager.canScheduleExactAlarms()

    private fun buildMessage(medication: Medication): String =
        "${medication.dosage} ${medication.doseUnit.name.lowercase()} · ${medication.frequencyText}"

    private fun requestCode(medicationId: String, index: Int): Int =
        medicationId.hashCode() * 31 + index

    private companion object {
        const val HIGH = "HIGH"
        const val MEDIUM = "MEDIUM"
        const val WINDOW_MILLIS = 15 * 60 * 1000L
    }
}
