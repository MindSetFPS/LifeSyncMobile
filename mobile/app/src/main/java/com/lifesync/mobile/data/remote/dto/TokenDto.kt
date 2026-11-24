package com.lifesync.mobile.data.remote.dto

import com.lifesync.mobile.domain.model.AuthToken
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class TokenDto(
    @SerialName("access_token") val accessToken: String,
    @SerialName("refresh_token") val refreshToken: String? = null,
    @SerialName("token_type") val tokenType: String,
    @SerialName("expires_in") val expiresIn: Int,
    val scope: String? = null,
) {
    fun toDomain(): AuthToken = AuthToken(
        accessToken = accessToken,
        refreshToken = refreshToken ?: "",
        tokenType = tokenType,
        expiresIn = expiresIn,
        scope = scope ?: "",
    )
}

@Serializable
data class RegisterRequest(
    val email: String,
    @SerialName("full_name") val fullName: String,
    val password: String,
)

@Serializable
data class RefreshRequest(@SerialName("refresh_token") val refreshToken: String)
