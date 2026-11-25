package com.lifesync.mobile.domain.scheduling

import com.lifesync.mobile.domain.model.Medication

/** Programa y cancela las notificaciones locales de recordatorios. */
interface MedicationReminderScheduler {
    fun schedule(medication: Medication)

    fun cancel(medicationId: String)

    fun cancelAll()
}
