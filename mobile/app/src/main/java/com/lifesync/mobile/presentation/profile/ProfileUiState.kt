package com.lifesync.mobile.presentation.profile

import com.lifesync.mobile.domain.model.Allergy
import com.lifesync.mobile.domain.model.AllergyCategory
import com.lifesync.mobile.domain.model.AllergySeverity
import com.lifesync.mobile.domain.model.BloodType
import com.lifesync.mobile.domain.model.DoseUnit
import com.lifesync.mobile.domain.model.EmergencyContact
import com.lifesync.mobile.domain.model.Medication
import com.lifesync.mobile.domain.model.MedicationRoute
import com.lifesync.mobile.domain.model.RhFactor

data class ProfileForm(
    val bloodType: BloodType? = null,
    val rhFactor: RhFactor? = null,
    val dateOfBirth: String = "",
    val heightCm: String = "",
    val weightKg: String = "",
    val organDonor: Boolean? = null,
    val chronicConditions: String = "",
)

data class AllergyForm(
    val allergenName: String = "",
    val category: AllergyCategory = AllergyCategory.OTHER,
    val severity: AllergySeverity = AllergySeverity.UNKNOWN,
    val reaction: String = "",
    val notes: String = "",
)

data class MedicationForm(
    val name: String = "",
    val activeIngredient: String = "",
    val dosage: String = "",
    val doseUnit: DoseUnit = DoseUnit.MG,
    val route: MedicationRoute = MedicationRoute.ORAL,
    val frequencyText: String = "",
    val startDate: String = "",
    val endDate: String = "",
    val isControlled: Boolean = false,
    val controlledSchedule: String = "",
    val prescriberName: String = "",
    val indication: String = "",
)

data class ContactForm(
    val fullName: String = "",
    val relationship: String = "",
    val phonePrimary: String = "",
    val phoneSecondary: String = "",
    val email: String = "",
    val priority: String = "",
    val notes: String = "",
)

data class ProfileUiState(
    val isLoading: Boolean = false,
    val isSaving: Boolean = false,
    val profile: ProfileForm = ProfileForm(),
    val allergies: List<Allergy> = emptyList(),
    val medications: List<Medication> = emptyList(),
    val contacts: List<EmergencyContact> = emptyList(),
    val allergyForm: AllergyForm = AllergyForm(),
    val medicationForm: MedicationForm = MedicationForm(),
    val contactForm: ContactForm = ContactForm(),
    val errorMessage: String? = null,
    val successMessage: String? = null,
)
