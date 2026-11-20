package com.lifesync.mobile.data.remote.dto

import com.lifesync.mobile.domain.model.User
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class UserDto(
    val id: String,
    val email: String,
    @SerialName("full_name") val fullName: String,
    @SerialName("is_active") val isActive: Boolean,
    @SerialName("created_at") val createdAt: String? = null,
) {
    fun toDomain(): User = User(id, email, fullName, isActive)
}
