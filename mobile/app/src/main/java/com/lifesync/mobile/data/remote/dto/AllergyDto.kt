package com.lifesync.mobile.data.remote.dto

import com.lifesync.mobile.domain.model.Allergy
import com.lifesync.mobile.domain.model.AllergyCategory
import com.lifesync.mobile.domain.model.AllergySeverity
import com.lifesync.mobile.domain.model.AllergyStatus
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class AllergyDto(
    val id: String,
    @SerialName("user_id") val userId: String,
    @SerialName("allergen_name") val allergenName: String,
    val category: AllergyCategory,
    val severity: AllergySeverity,
    val status: AllergyStatus,
    val reaction: String? = null,
    @SerialName("diagnosed_at") val diagnosedAt: String? = null,
    val notes: String? = null,
    @SerialName("is_emergency_relevant") val isEmergencyRelevant: Boolean,
    val version: Int,
    @SerialName("created_at") val createdAt: String,
    @SerialName("updated_at") val updatedAt: String,
    @SerialName("deleted_at") val deletedAt: String? = null,
) {
    fun toDomain(): Allergy = Allergy(
        id = id,
        userId = userId,
        allergenName = allergenName,
        category = category,
        severity = severity,
        status = status,
        reaction = reaction,
        diagnosedAt = diagnosedAt,
        notes = notes,
        isEmergencyRelevant = isEmergencyRelevant,
        version = version,
        createdAt = createdAt,
        updatedAt = updatedAt,
        deletedAt = deletedAt,
    )
}
