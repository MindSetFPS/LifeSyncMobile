package com.lifesync.mobile.data.remote.dto

import com.lifesync.mobile.domain.model.BloodType
import com.lifesync.mobile.domain.model.MedicalProfile
import com.lifesync.mobile.domain.model.RhFactor
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class MedicalProfileDto(
    val id: String,
    @SerialName("user_id") val userId: String,
    @SerialName("blood_type") val bloodType: BloodType? = null,
    @SerialName("rh_factor") val rhFactor: RhFactor? = null,
    @SerialName("date_of_birth") val dateOfBirth: String? = null,
    @SerialName("height_cm") val heightCm: Double? = null,
    @SerialName("weight_kg") val weightKg: Double? = null,
    @SerialName("organ_donor") val organDonor: Boolean? = null,
    @SerialName("chronic_conditions") val chronicConditions: String? = null,
    val version: Int,
    @SerialName("created_at") val createdAt: String,
    @SerialName("updated_at") val updatedAt: String,
    @SerialName("deleted_at") val deletedAt: String? = null,
) {
    fun toDomain(): MedicalProfile = MedicalProfile(
        id = id,
        userId = userId,
        bloodType = bloodType,
        rhFactor = rhFactor,
        dateOfBirth = dateOfBirth,
        heightCm = heightCm,
        weightKg = weightKg,
        organDonor = organDonor,
        chronicConditions = chronicConditions,
        version = version,
        createdAt = createdAt,
        updatedAt = updatedAt,
        deletedAt = deletedAt,
    )
}
