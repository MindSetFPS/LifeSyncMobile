package com.lifesync.mobile.domain.model

data class EmergencyExport(
    val id: String,
    val userId: String,
    val format: ExportFormat,
    val status: ExportStatus,
    val sections: List<ExportSection>,
    val strategy: String,
    val strategyVersion: String,
    val requestedAt: String,
    val generatedAt: String?,
    val expiresAt: String?,
    val contentSha256: String?,
    val sizeBytes: Int?,
    val recordCount: Int?,
    val errorCode: String?,
)
