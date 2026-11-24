package com.lifesync.mobile.data.remote.dto

import com.lifesync.mobile.domain.model.EmergencyContact
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class EmergencyContactDto(
    val id: String,
    @SerialName("user_id") val userId: String,
    @SerialName("full_name") val fullName: String,
    val relationship: String,
    @SerialName("phone_primary") val phonePrimary: String,
    @SerialName("phone_secondary") val phoneSecondary: String? = null,
    val email: String? = null,
    val priority: Int,
    @SerialName("notify_on_incident") val notifyOnIncident: Boolean,
    @SerialName("is_active") val isActive: Boolean,
    val notes: String? = null,
    val version: Int,
    @SerialName("created_at") val createdAt: String,
    @SerialName("updated_at") val updatedAt: String,
    @SerialName("deleted_at") val deletedAt: String? = null,
) {
    fun toDomain(): EmergencyContact = EmergencyContact(
        id = id,
        userId = userId,
        fullName = fullName,
        relationship = relationship,
        phonePrimary = phonePrimary,
        phoneSecondary = phoneSecondary,
        email = email,
        priority = priority,
        notifyOnIncident = notifyOnIncident,
        isActive = isActive,
        notes = notes,
        version = version,
        createdAt = createdAt,
        updatedAt = updatedAt,
        deletedAt = deletedAt,
    )
}
