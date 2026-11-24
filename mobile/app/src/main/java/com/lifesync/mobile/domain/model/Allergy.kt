package com.lifesync.mobile.domain.model

data class Allergy(
    val id: String,
    val userId: String,
    val allergenName: String,
    val category: AllergyCategory,
    val severity: AllergySeverity,
    val status: AllergyStatus,
    val reaction: String?,
    val diagnosedAt: String?,
    val notes: String?,
    val isEmergencyRelevant: Boolean,
    val version: Int,
    val createdAt: String,
    val updatedAt: String,
    val deletedAt: String? = null,
)
