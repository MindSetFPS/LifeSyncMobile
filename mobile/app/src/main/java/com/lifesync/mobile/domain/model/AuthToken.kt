package com.lifesync.mobile.domain.model

data class AuthToken(
    val accessToken: String,
    val refreshToken: String,
    val tokenType: String = "bearer",
    val expiresIn: Int,
    val scope: String = "",
)
