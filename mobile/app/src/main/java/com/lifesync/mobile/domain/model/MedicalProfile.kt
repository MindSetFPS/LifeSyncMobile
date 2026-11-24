package com.lifesync.mobile.domain.model

data class MedicalProfile(
    val id: String,
    val userId: String,
    val bloodType: BloodType?,
    val rhFactor: RhFactor?,
    val dateOfBirth: String?,
    val heightCm: Double?,
    val weightKg: Double?,
    val organDonor: Boolean?,
    val chronicConditions: String?,
    val version: Int,
    val createdAt: String,
    val updatedAt: String,
    val deletedAt: String? = null,
)
