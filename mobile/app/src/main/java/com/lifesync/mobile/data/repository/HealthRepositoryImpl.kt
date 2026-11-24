package com.lifesync.mobile.data.repository

import com.lifesync.mobile.core.result.Resource
import com.lifesync.mobile.data.remote.dto.toRequest
import com.lifesync.mobile.data.remote.service.HealthApiService
import com.lifesync.mobile.domain.model.Allergy
import com.lifesync.mobile.domain.model.AllergyInput
import com.lifesync.mobile.domain.model.EmergencyContact
import com.lifesync.mobile.domain.model.EmergencyContactInput
import com.lifesync.mobile.domain.model.MedicalProfile
import com.lifesync.mobile.domain.model.MedicalProfileInput
import com.lifesync.mobile.domain.model.Medication
import com.lifesync.mobile.domain.model.MedicationInput
import com.lifesync.mobile.domain.repository.HealthRepository
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject
import javax.inject.Singleton

/** Consumo asíncrono de las entidades clínicas con manejo tipado de errores. */
@Singleton
class HealthRepositoryImpl @Inject constructor(
    private val api: HealthApiService,
) : HealthRepository {
    override suspend fun getProfile(): Resource<MedicalProfile?> = try {
        Resource.Success(api.getProfile().toDomain())
    } catch (e: HttpException) {
        if (e.code() == 404) Resource.Success(null)
        else Resource.Error(mapHttpError(e.code()), e)
    } catch (e: IOException) {
        Resource.Error("Sin conexión con el servidor", e)
    } catch (e: Exception) {
        Resource.Error(e.message ?: "Error inesperado", e)
    }

    override suspend fun saveProfile(
        input: MedicalProfileInput,
    ): Resource<MedicalProfile> = safeCall {
        api.saveProfile(input.toRequest()).toDomain()
    }

    override suspend fun listAllergies(): Resource<List<Allergy>> = safeCall {
        api.listAllergies().map { it.toDomain() }
    }

    override suspend fun createAllergy(input: AllergyInput): Resource<Allergy> = safeCall {
        api.createAllergy(input.toRequest()).toDomain()
    }

    override suspend fun deleteAllergy(id: String): Resource<Unit> =
        safeCall { api.deleteAllergy(id) }

    override suspend fun listMedications(): Resource<List<Medication>> = safeCall {
        api.listMedications().map { it.toDomain() }
    }

    override suspend fun createMedication(input: MedicationInput): Resource<Medication> =
        safeCall { api.createMedication(input.toRequest()).toDomain() }

    override suspend fun deleteMedication(id: String): Resource<Unit> =
        safeCall { api.deleteMedication(id) }

    override suspend fun listContacts(): Resource<List<EmergencyContact>> = safeCall {
        api.listContacts().map { it.toDomain() }
    }

    override suspend fun createContact(
        input: EmergencyContactInput,
    ): Resource<EmergencyContact> = safeCall {
        api.createContact(input.toRequest()).toDomain()
    }

    override suspend fun deleteContact(id: String): Resource<Unit> =
        safeCall { api.deleteContact(id) }

    private suspend fun <T> safeCall(block: suspend () -> T): Resource<T> = try {
        Resource.Success(block())
    } catch (e: HttpException) {
        Resource.Error(mapHttpError(e.code()), e)
    } catch (e: IOException) {
        Resource.Error("Sin conexión con el servidor", e)
    } catch (e: Exception) {
        Resource.Error(e.message ?: "Error inesperado", e)
    }

    private fun mapHttpError(code: Int): String = when (code) {
        400, 401 -> "La sesión expiró o los datos no son válidos"
        403 -> "No tienes permiso para esta operación"
        404 -> "Registro no encontrado"
        409 -> "Conflicto: ya existe un registro con esos datos"
        422 -> "Revisa los datos ingresados"
        in 500..599 -> "Error del servidor, intenta más tarde"
        else -> "Error de la petición ($code)"
    }
}
