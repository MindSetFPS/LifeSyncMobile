package com.lifesync.mobile.presentation.profile

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.lifesync.mobile.core.result.Resource
import com.lifesync.mobile.domain.model.AllergyInput
import com.lifesync.mobile.domain.model.EmergencyContactInput
import com.lifesync.mobile.domain.model.MedicalProfile
import com.lifesync.mobile.domain.model.MedicalProfileInput
import com.lifesync.mobile.domain.model.MedicationInput
import com.lifesync.mobile.domain.repository.HealthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class PatientProfileViewModel @Inject constructor(
    private val repository: HealthRepository,
) : ViewModel() {
    private val _uiState = MutableStateFlow(ProfileUiState())
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    private val datePattern = Regex("""\d{4}-\d{2}-\d{2}""")
    private val phonePattern = Regex("""^\+[1-9]\d{1,14}$""")

    fun load() {
        viewModelScope.launch {
            _uiState.update {
                it.copy(isLoading = true, errorMessage = null, successMessage = null)
            }
            var next = _uiState.value.copy(isLoading = false)

            when (val result = repository.getProfile()) {
                is Resource.Success -> next = next.copy(
                    profile = result.data?.toForm() ?: ProfileForm(),
                )
                is Resource.Error -> next = next.copy(errorMessage = result.message)
                Resource.Loading -> Unit
            }

            when (val result = repository.listAllergies()) {
                is Resource.Success -> next = next.copy(allergies = result.data)
                is Resource.Error -> next = next.copy(
                    errorMessage = next.errorMessage ?: result.message,
                )
                Resource.Loading -> Unit
            }

            when (val result = repository.listMedications()) {
                is Resource.Success -> next = next.copy(medications = result.data)
                is Resource.Error -> next = next.copy(
                    errorMessage = next.errorMessage ?: result.message,
                )
                Resource.Loading -> Unit
            }

            when (val result = repository.listContacts()) {
                is Resource.Success -> next = next.copy(contacts = result.data)
                is Resource.Error -> next = next.copy(
                    errorMessage = next.errorMessage ?: result.message,
                )
                Resource.Loading -> Unit
            }

            _uiState.value = next
        }
    }

    fun updateProfileForm(form: ProfileForm) =
        update { it.copy(profile = form) }

    fun updateAllergyForm(form: AllergyForm) =
        update { it.copy(allergyForm = form) }

    fun updateMedicationForm(form: MedicationForm) =
        update { it.copy(medicationForm = form) }

    fun updateContactForm(form: ContactForm) =
        update { it.copy(contactForm = form) }

    fun saveProfile() {
        val form = _uiState.value.profile
        val height = parsePositive(form.heightCm)
        if (form.heightCm.isNotBlank() && height == null) {
            return fail("Estatura inválida")
        }
        val weight = parsePositive(form.weightKg)
        if (form.weightKg.isNotBlank() && weight == null) {
            return fail("Peso inválido")
        }
        val birthDate = form.dateOfBirth.trim()
        if (birthDate.isNotEmpty() && !datePattern.matches(birthDate)) {
            return fail("Fecha de nacimiento inválida (AAAA-MM-DD)")
        }

        viewModelScope.launch {
            save {
                repository.saveProfile(
                    MedicalProfileInput(
                        bloodType = form.bloodType,
                        rhFactor = form.rhFactor,
                        dateOfBirth = birthDate.nullIfBlank(),
                        heightCm = height,
                        weightKg = weight,
                        organDonor = form.organDonor,
                        chronicConditions = form.chronicConditions.nullIfBlank(),
                    ),
                )
            }?.let { profile ->
                _uiState.update {
                    it.copy(profile = profile.toForm(), successMessage = "Perfil clínico guardado")
                }
            }
        }
    }

    fun addAllergy() {
        val form = _uiState.value.allergyForm
        if (form.allergenName.isBlank()) {
            return fail("El alérgeno es obligatorio")
        }
        viewModelScope.launch {
            when (
                val result = save {
                    repository.createAllergy(
                        AllergyInput(
                            allergenName = form.allergenName.trim(),
                            category = form.category,
                            severity = form.severity,
                            reaction = form.reaction.nullIfBlank(),
                            notes = form.notes.nullIfBlank(),
                        ),
                    )
                }
            ) {
                null -> Unit
                else -> _uiState.update {
                    it.copy(
                        allergies = it.allergies + result,
                        allergyForm = AllergyForm(),
                        successMessage = "Alergia agregada",
                    )
                }
            }
        }
    }

    fun deleteAllergy(id: String) {
        viewModelScope.launch {
            if (delete { repository.deleteAllergy(id) }) {
                _uiState.update {
                    it.copy(
                        allergies = it.allergies.filterNot { record -> record.id == id },
                        successMessage = "Alergia eliminada",
                    )
                }
            }
        }
    }

    fun addMedication() {
        val form = _uiState.value.medicationForm
        if (form.name.isBlank() || form.dosage.isBlank() || form.frequencyText.isBlank()) {
            return fail("Completa nombre, dosis y frecuencia")
        }
        if (!datePattern.matches(form.startDate.trim())) {
            return fail("Fecha de inicio inválida (AAAA-MM-DD)")
        }
        if (form.endDate.isNotBlank() && !datePattern.matches(form.endDate.trim())) {
            return fail("Fecha de fin inválida (AAAA-MM-DD)")
        }
        if (form.isControlled && form.prescriberName.isBlank()) {
            return fail("Un medicamento controlado exige prescriptor")
        }

        viewModelScope.launch {
            when (
                val result = save {
                    repository.createMedication(
                        MedicationInput(
                            name = form.name.trim(),
                            activeIngredient = form.activeIngredient.nullIfBlank(),
                            dosage = form.dosage.trim(),
                            doseUnit = form.doseUnit,
                            route = form.route,
                            frequencyText = form.frequencyText.trim(),
                            isControlled = form.isControlled,
                            controlledSchedule = if (form.isControlled) {
                                form.controlledSchedule.nullIfBlank()
                            } else {
                                null
                            },
                            prescriberName = form.prescriberName.nullIfBlank(),
                            startDate = form.startDate.trim(),
                            endDate = form.endDate.nullIfBlank(),
                            indication = form.indication.nullIfBlank(),
                        ),
                    )
                }
            ) {
                null -> Unit
                else -> _uiState.update {
                    it.copy(
                        medications = it.medications + result,
                        medicationForm = MedicationForm(),
                        successMessage = "Medicamento agregado",
                    )
                }
            }
        }
    }

    fun deleteMedication(id: String) {
        viewModelScope.launch {
            if (delete { repository.deleteMedication(id) }) {
                _uiState.update {
                    it.copy(
                        medications = it.medications.filterNot { record -> record.id == id },
                        successMessage = "Medicamento eliminado",
                    )
                }
            }
        }
    }

    fun addContact() {
        val form = _uiState.value.contactForm
        if (form.fullName.isBlank() || form.relationship.isBlank() ||
            form.phonePrimary.isBlank()
        ) {
            return fail("Completa nombre, parentesco y teléfono")
        }
        if (!phonePattern.matches(form.phonePrimary.trim())) {
            return fail("Teléfono inválido: usa formato E.164 (ej. +5215555555555)")
        }
        val priority = form.priority.trim().toIntOrNull()
        if (priority == null || priority < 0) {
            return fail("Prioridad inválida (entero mayor o igual a 0)")
        }

        viewModelScope.launch {
            when (
                val result = save {
                    repository.createContact(
                        EmergencyContactInput(
                            fullName = form.fullName.trim(),
                            relationship = form.relationship.trim(),
                            phonePrimary = form.phonePrimary.trim(),
                            phoneSecondary = form.phoneSecondary.nullIfBlank(),
                            email = form.email.nullIfBlank(),
                            priority = priority,
                            notes = form.notes.nullIfBlank(),
                        ),
                    )
                }
            ) {
                null -> Unit
                else -> _uiState.update {
                    it.copy(
                        contacts = it.contacts + result,
                        contactForm = ContactForm(),
                        successMessage = "Contacto agregado",
                    )
                }
            }
        }
    }

    fun deleteContact(id: String) {
        viewModelScope.launch {
            if (delete { repository.deleteContact(id) }) {
                _uiState.update {
                    it.copy(
                        contacts = it.contacts.filterNot { record -> record.id == id },
                        successMessage = "Contacto eliminado",
                    )
                }
            }
        }
    }

    /** Ejecuta una operación de escritura y devuelve el resultado o null si falló. */
    private suspend fun <T> save(block: suspend () -> Resource<T>): T? {
        _uiState.update {
            it.copy(isSaving = true, errorMessage = null, successMessage = null)
        }
        return when (val result = block()) {
            is Resource.Success -> {
                _uiState.update { it.copy(isSaving = false) }
                result.data
            }
            is Resource.Error -> {
                _uiState.update { it.copy(isSaving = false, errorMessage = result.message) }
                null
            }
            Resource.Loading -> null
        }
    }

    private suspend fun delete(block: suspend () -> Resource<Unit>): Boolean {
        _uiState.update {
            it.copy(isSaving = true, errorMessage = null, successMessage = null)
        }
        return when (val result = block()) {
            is Resource.Success -> {
                _uiState.update { it.copy(isSaving = false) }
                true
            }
            is Resource.Error -> {
                _uiState.update { it.copy(isSaving = false, errorMessage = result.message) }
                false
            }
            Resource.Loading -> false
        }
    }

    private fun update(transform: (ProfileUiState) -> ProfileUiState) {
        _uiState.update { transform(it).copy(errorMessage = null, successMessage = null) }
    }

    private fun fail(message: String) {
        _uiState.update { it.copy(errorMessage = message, successMessage = null) }
    }

    private fun parsePositive(raw: String): Double? =
        raw.trim().replace(',', '.').takeIf { it.isNotEmpty() }
            ?.toDoubleOrNull()
            ?.takeIf { it > 0 }

    private fun String.nullIfBlank(): String? =
        trim().takeIf { it.isNotEmpty() }

    private fun MedicalProfile.toForm(): ProfileForm = ProfileForm(
        bloodType = bloodType,
        rhFactor = rhFactor,
        dateOfBirth = dateOfBirth.orEmpty(),
        heightCm = heightCm?.toString().orEmpty(),
        weightKg = weightKg?.toString().orEmpty(),
        organDonor = organDonor,
        chronicConditions = chronicConditions.orEmpty(),
    )
}
