package com.lifesync.mobile.domain.model

/** Entradas del formulario clínico, independientes de la capa HTTP. */

data class MedicalProfileInput(
    val bloodType: BloodType? = null,
    val rhFactor: RhFactor? = null,
    val dateOfBirth: String? = null,
    val heightCm: Double? = null,
    val weightKg: Double? = null,
    val organDonor: Boolean? = null,
    val chronicConditions: String? = null,
)

data class AllergyInput(
    val allergenName: String,
    val category: AllergyCategory,
    val severity: AllergySeverity,
    val status: AllergyStatus = AllergyStatus.ACTIVE,
    val reaction: String? = null,
    val diagnosedAt: String? = null,
    val notes: String? = null,
    val isEmergencyRelevant: Boolean = true,
)

data class MedicationInput(
    val name: String,
    val activeIngredient: String? = null,
    val dosage: String,
    val doseUnit: DoseUnit,
    val route: MedicationRoute,
    val frequencyText: String,
    val intervalHours: Int? = null,
    val reminderTimes: List<String> = emptyList(),
    val isControlled: Boolean = false,
    val controlledSchedule: String? = null,
    val prescriberName: String? = null,
    val prescriptionNumber: String? = null,
    val startDate: String,
    val endDate: String? = null,
    val isActive: Boolean = true,
    val indication: String? = null,
    val showInEmergency: Boolean = true,
)

data class EmergencyContactInput(
    val fullName: String,
    val relationship: String,
    val phonePrimary: String,
    val phoneSecondary: String? = null,
    val email: String? = null,
    val priority: Int,
    val notifyOnIncident: Boolean = true,
    val isActive: Boolean = true,
    val notes: String? = null,
)
