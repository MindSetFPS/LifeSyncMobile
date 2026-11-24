package com.lifesync.mobile.data.remote.dto

import com.lifesync.mobile.domain.model.AllergyCategory
import com.lifesync.mobile.domain.model.AllergyInput
import com.lifesync.mobile.domain.model.AllergySeverity
import com.lifesync.mobile.domain.model.AllergyStatus
import com.lifesync.mobile.domain.model.BloodType
import com.lifesync.mobile.domain.model.DoseUnit
import com.lifesync.mobile.domain.model.EmergencyContactInput
import com.lifesync.mobile.domain.model.MedicalProfileInput
import com.lifesync.mobile.domain.model.MedicationInput
import com.lifesync.mobile.domain.model.MedicationRoute
import com.lifesync.mobile.domain.model.RhFactor
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class MedicalProfileRequest(
    @SerialName("blood_type") val bloodType: BloodType? = null,
    @SerialName("rh_factor") val rhFactor: RhFactor? = null,
    @SerialName("date_of_birth") val dateOfBirth: String? = null,
    @SerialName("height_cm") val heightCm: Double? = null,
    @SerialName("weight_kg") val weightKg: Double? = null,
    @SerialName("organ_donor") val organDonor: Boolean? = null,
    @SerialName("chronic_conditions") val chronicConditions: String? = null,
)

@Serializable
data class AllergyRequest(
    @SerialName("allergen_name") val allergenName: String,
    val category: AllergyCategory,
    val severity: AllergySeverity,
    val status: AllergyStatus = AllergyStatus.ACTIVE,
    val reaction: String? = null,
    @SerialName("diagnosed_at") val diagnosedAt: String? = null,
    val notes: String? = null,
    @SerialName("is_emergency_relevant") val isEmergencyRelevant: Boolean = true,
)

@Serializable
data class MedicationRequest(
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
    @SerialName("is_active") val isActive: Boolean = true,
    val indication: String? = null,
    @SerialName("show_in_emergency") val showInEmergency: Boolean = true,
)

@Serializable
data class EmergencyContactRequest(
    @SerialName("full_name") val fullName: String,
    val relationship: String,
    @SerialName("phone_primary") val phonePrimary: String,
    @SerialName("phone_secondary") val phoneSecondary: String? = null,
    val email: String? = null,
    val priority: Int,
    @SerialName("notify_on_incident") val notifyOnIncident: Boolean = true,
    @SerialName("is_active") val isActive: Boolean = true,
    val notes: String? = null,
)

fun MedicalProfileInput.toRequest(): MedicalProfileRequest = MedicalProfileRequest(
    bloodType = bloodType,
    rhFactor = rhFactor,
    dateOfBirth = dateOfBirth,
    heightCm = heightCm,
    weightKg = weightKg,
    organDonor = organDonor,
    chronicConditions = chronicConditions,
)

fun AllergyInput.toRequest(): AllergyRequest = AllergyRequest(
    allergenName = allergenName,
    category = category,
    severity = severity,
    status = status,
    reaction = reaction,
    diagnosedAt = diagnosedAt,
    notes = notes,
    isEmergencyRelevant = isEmergencyRelevant,
)

fun MedicationInput.toRequest(): MedicationRequest = MedicationRequest(
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
)

fun EmergencyContactInput.toRequest(): EmergencyContactRequest = EmergencyContactRequest(
    fullName = fullName,
    relationship = relationship,
    phonePrimary = phonePrimary,
    phoneSecondary = phoneSecondary,
    email = email,
    priority = priority,
    notifyOnIncident = notifyOnIncident,
    isActive = isActive,
    notes = notes,
)
