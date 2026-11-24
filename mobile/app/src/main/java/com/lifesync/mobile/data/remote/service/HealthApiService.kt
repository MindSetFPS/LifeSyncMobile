package com.lifesync.mobile.data.remote.service

import com.lifesync.mobile.data.remote.dto.AllergyDto
import com.lifesync.mobile.data.remote.dto.AllergyRequest
import com.lifesync.mobile.data.remote.dto.EmergencyContactDto
import com.lifesync.mobile.data.remote.dto.EmergencyContactRequest
import com.lifesync.mobile.data.remote.dto.MedicalProfileDto
import com.lifesync.mobile.data.remote.dto.MedicalProfileRequest
import com.lifesync.mobile.data.remote.dto.MedicationDto
import com.lifesync.mobile.data.remote.dto.MedicationRequest
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path

/** Contrato HTTP de las entidades clínicas (Bearer inyectado por AuthInterceptor). */
interface HealthApiService {
    @GET("medical-profile")
    suspend fun getProfile(): MedicalProfileDto

    @PUT("medical-profile")
    suspend fun saveProfile(@Body request: MedicalProfileRequest): MedicalProfileDto

    @GET("allergies")
    suspend fun listAllergies(): List<AllergyDto>

    @POST("allergies")
    suspend fun createAllergy(@Body request: AllergyRequest): AllergyDto

    @DELETE("allergies/{id}")
    suspend fun deleteAllergy(@Path("id") id: String)

    @GET("medications")
    suspend fun listMedications(): List<MedicationDto>

    @POST("medications")
    suspend fun createMedication(@Body request: MedicationRequest): MedicationDto

    @DELETE("medications/{id}")
    suspend fun deleteMedication(@Path("id") id: String)

    @GET("emergency-contacts")
    suspend fun listContacts(): List<EmergencyContactDto>

    @POST("emergency-contacts")
    suspend fun createContact(
        @Body request: EmergencyContactRequest,
    ): EmergencyContactDto

    @DELETE("emergency-contacts/{id}")
    suspend fun deleteContact(@Path("id") id: String)
}
