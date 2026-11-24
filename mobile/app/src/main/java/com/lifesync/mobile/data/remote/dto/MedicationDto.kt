package com.lifesync.mobile.data.remote.dto

import com.lifesync.mobile.domain.model.DoseUnit
import com.lifesync.mobile.domain.model.Medication
import com.lifesync.mobile.domain.model.MedicationRoute
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class MedicationDto(
    val id: String,
    @SerialName("user_id") val userId: String,
    val name: String,
    @SerialName("active_ingredient") val activeIngredient: String? = null,
    val dosage: String,
    @SerialName("dose_unit") val doseUnit: DoseUnit,
    val route: MedicationRoute,
    @SerialName("frequency_text") val frequencyText: String,
    @SerialName("interval_hours") val intervalHours: Int? = null,
    @SerialName("reminder_times") val reminderTimes: List<String> = emptyList(),
    @SerialName("is_controlled") val isControlled: Boolean,
    @SerialName("controlled_schedule") val controlledSchedule: String? = null,
    @SerialName("prescriber_name") val prescriberName: String? = null,
    @SerialName("prescription_number") val prescriptionNumber: String? = null,
    @SerialName("start_date") val startDate: String,
    @SerialName("end_date") val endDate: String? = null,
    @SerialName("is_active") val isActive: Boolean,
    val indication: String? = null,
    @SerialName("show_in_emergency") val showInEmergency: Boolean,
    val version: Int,
    @SerialName("created_at") val createdAt: String,
    @SerialName("updated_at") val updatedAt: String,
    @SerialName("deleted_at") val deletedAt: String? = null,
) {
    fun toDomain(): Medication = Medication(
        id = id,
        userId = userId,
        name = name,
        activeIngredient = activeIngredient,
        dosage = dosage,
        doseUnit = doseUnit,
        route = route,
        frequencyText = frequencyText,
        intervalHours = intervalHours,
        reminderTimes = reminderTimes,
        isControlled = isControlled,
        controlledSchedule = controlledSchedule,
        prescriberName = prescriberName,
        prescriptionNumber = prescriptionNumber,
        startDate = startDate,
        endDate = endDate,
        isActive = isActive,
        indication = indication,
        showInEmergency = showInEmergency,
        version = version,
        createdAt = createdAt,
        updatedAt = updatedAt,
        deletedAt = deletedAt,
    )
}
