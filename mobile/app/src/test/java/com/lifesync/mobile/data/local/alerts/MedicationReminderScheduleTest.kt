package com.lifesync.mobile.data.local.alerts

import com.google.common.truth.Truth.assertThat
import com.lifesync.mobile.domain.model.DoseUnit
import com.lifesync.mobile.domain.model.Medication
import com.lifesync.mobile.domain.model.MedicationRoute
import java.time.ZonedDateTime
import org.junit.Test

class MedicationReminderScheduleTest {

    private val from = ZonedDateTime.parse("2026-01-01T10:00:00Z")

    @Test
    fun `projects upcoming reminder times within horizon`() {
        val medication = medication(reminderTimes = listOf("08:00", "20:00"))

        val triggers = MedicationReminderSchedule.nextTriggers(medication, from)

        assertThat(triggers).isNotEmpty()
        assertThat(triggers.all { it.isAfter(from) }).isTrue()
        assertThat(triggers.first().toString()).isEqualTo("2026-01-01T20:00Z")
        // El día 0 sólo conserva las 20:00; los días restantes aportan ambas horas.
        assertThat(triggers).hasSize(MedicationReminderSchedule.HORIZON_DAYS * 2 - 1)
    }

    @Test
    fun `skips reminders before the current time`() {
        val medication = medication(reminderTimes = listOf("09:00"))

        val triggers = MedicationReminderSchedule.nextTriggers(medication, from)

        assertThat(triggers.first().toLocalDate().toString()).isEqualTo("2026-01-02")
    }

    @Test
    fun `inactive medication schedules nothing`() {
        val medication = medication(reminderTimes = listOf("08:00"), isActive = false)

        assertThat(MedicationReminderSchedule.nextTriggers(medication, from)).isEmpty()
    }

    @Test
    fun `falls back to interval hours when no explicit times`() {
        val medication = medication(reminderTimes = emptyList(), intervalHours = 6)

        val triggers = MedicationReminderSchedule.nextTriggers(medication, from)

        assertThat(triggers).hasSize(1)
        assertThat(triggers.first().toString()).isEqualTo("2026-01-01T16:00Z")
    }

    @Test
    fun `respects the medication end date`() {
        val medication = medication(
            reminderTimes = listOf("08:00"),
            endDate = "2026-01-03",
        )

        val triggers = MedicationReminderSchedule.nextTriggers(medication, from)

        assertThat(triggers).hasSize(2)
        assertThat(triggers.last().toLocalDate().toString()).isEqualTo("2026-01-03")
    }

    private fun medication(
        reminderTimes: List<String>,
        intervalHours: Int? = null,
        isActive: Boolean = true,
        endDate: String? = null,
    ): Medication = Medication(
        id = "med-1",
        userId = "user-1",
        name = "Tramadol",
        activeIngredient = null,
        dosage = "50",
        doseUnit = DoseUnit.MG,
        route = MedicationRoute.ORAL,
        frequencyText = "Cada 8 horas",
        intervalHours = intervalHours,
        reminderTimes = reminderTimes,
        isControlled = true,
        controlledSchedule = "II",
        prescriberName = null,
        prescriptionNumber = null,
        startDate = "2026-01-01",
        endDate = endDate,
        isActive = isActive,
        indication = null,
        showInEmergency = true,
        version = 1,
        createdAt = "2026-01-01T00:00:00Z",
        updatedAt = "2026-01-01T00:00:00Z",
    )
}
