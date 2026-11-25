package com.lifesync.mobile.data.local.alerts

import com.lifesync.mobile.domain.model.Medication
import java.time.LocalDate
import java.time.LocalTime
import java.time.ZonedDateTime

/**
 * Cálculo puro de los próximos disparos de un medicamento.
 *
 * A partir de `reminderTimes` (formato HH:MM) proyecta las ocurrencias de los
 * próximos [HORIZON_DAYS] días; si no hay horas explícitas usa `intervalHours`.
 * Se recalcula al abrir la app para extender el horizonte.
 */
object MedicationReminderSchedule {
    const val HORIZON_DAYS = 7
    const val MAX_TRIGGERS = 64

    fun nextTriggers(
        medication: Medication,
        from: ZonedDateTime = ZonedDateTime.now(),
    ): List<ZonedDateTime> {
        if (!medication.isActive) return emptyList()

        val startDate = parseDate(medication.startDate)
        val endDate = parseDate(medication.endDate)
        val times = medication.reminderTimes.mapNotNull { parseTime(it) }

        if (times.isEmpty()) {
            val interval = medication.intervalHours ?: return emptyList()
            if (interval <= 0) return emptyList()
            val next = from.plusHours(interval.toLong())
            return listOf(next).filterInRange(startDate, endDate)
        }

        val today = from.toLocalDate()
        val triggers = mutableListOf<ZonedDateTime>()
        for (dayOffset in 0 until HORIZON_DAYS) {
            val date = today.plusDays(dayOffset.toLong())
            for (time in times) {
                val candidate = date.atTime(time).atZone(from.zone)
                if (candidate.isAfter(from)) triggers.add(candidate)
            }
        }
        return triggers
            .filterInRange(startDate, endDate)
            .sorted()
            .take(MAX_TRIGGERS)
    }

    private fun List<ZonedDateTime>.filterInRange(
        startDate: LocalDate?,
        endDate: LocalDate?,
    ): List<ZonedDateTime> = filter { trigger ->
        val date = trigger.toLocalDate()
        (startDate == null || !date.isBefore(startDate)) &&
            (endDate == null || !date.isAfter(endDate))
    }

    private fun parseDate(value: String?): LocalDate? =
        value?.let { runCatching { LocalDate.parse(it) }.getOrNull() }

    private fun parseTime(value: String): LocalTime? =
        runCatching { LocalTime.parse(value) }.getOrNull()
}
