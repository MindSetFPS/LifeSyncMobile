package com.lifesync.mobile.domain.model

data class EmergencyContact(
    val id: String,
    val userId: String,
    val fullName: String,
    val relationship: String,
    val phonePrimary: String,
    val phoneSecondary: String?,
    val email: String?,
    val priority: Int,
    val notifyOnIncident: Boolean,
    val isActive: Boolean,
    val notes: String?,
    val version: Int,
    val createdAt: String,
    val updatedAt: String,
    val deletedAt: String? = null,
)
