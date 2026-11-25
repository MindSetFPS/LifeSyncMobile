package com.lifesync.mobile.domain.usecase

import com.lifesync.mobile.core.result.Resource
import com.lifesync.mobile.domain.model.Medication
import com.lifesync.mobile.domain.repository.HealthRepository
import com.lifesync.mobile.domain.scheduling.MedicationReminderScheduler
import javax.inject.Inject

/**
 * Sincroniza la agenda local con los medicamentos activos del usuario.
 * Se recalcula cada vez que la app abre sesión para extender el horizonte.
 */
class ScheduleMedicationRemindersUseCase @Inject constructor(
    private val repository: HealthRepository,
    private val scheduler: MedicationReminderScheduler,
) {
    suspend operator fun invoke(): Resource<Int> = when (val result = repository.listMedications()) {
        is Resource.Success -> {
            val scheduled = result.data.count { medication ->
                scheduleIfNeeded(medication)
            }
            Resource.Success(scheduled)
        }
        is Resource.Error -> result
        Resource.Loading -> Resource.Loading
    }

    private fun scheduleIfNeeded(medication: Medication): Boolean {
        val hasReminders = medication.reminderTimes.isNotEmpty() ||
            (medication.intervalHours != null && medication.intervalHours > 0)
        if (!medication.isActive || !hasReminders) {
            scheduler.cancel(medication.id)
            return false
        }
        scheduler.schedule(medication)
        return true
    }
}
