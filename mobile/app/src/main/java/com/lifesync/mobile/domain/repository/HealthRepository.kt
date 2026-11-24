package com.lifesync.mobile.domain.repository

import com.lifesync.mobile.core.result.Resource
import com.lifesync.mobile.domain.model.Allergy
import com.lifesync.mobile.domain.model.AllergyInput
import com.lifesync.mobile.domain.model.EmergencyContact
import com.lifesync.mobile.domain.model.EmergencyContactInput
import com.lifesync.mobile.domain.model.MedicalProfile
import com.lifesync.mobile.domain.model.MedicalProfileInput
import com.lifesync.mobile.domain.model.Medication
import com.lifesync.mobile.domain.model.MedicationInput

/** Contrato de dominio para el perfil clínico del paciente. */
interface HealthRepository {
    suspend fun getProfile(): Resource<MedicalProfile?>
    suspend fun saveProfile(input: MedicalProfileInput): Resource<MedicalProfile>

    suspend fun listAllergies(): Resource<List<Allergy>>
    suspend fun createAllergy(input: AllergyInput): Resource<Allergy>
    suspend fun deleteAllergy(id: String): Resource<Unit>

    suspend fun listMedications(): Resource<List<Medication>>
    suspend fun createMedication(input: MedicationInput): Resource<Medication>
    suspend fun deleteMedication(id: String): Resource<Unit>

    suspend fun listContacts(): Resource<List<EmergencyContact>>
    suspend fun createContact(input: EmergencyContactInput): Resource<EmergencyContact>
    suspend fun deleteContact(id: String): Resource<Unit>
}
