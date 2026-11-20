package com.lifesync.mobile.domain.model

data class User(
    val id: String,
    val email: String,
    val fullName: String,
    val isActive: Boolean,
)
