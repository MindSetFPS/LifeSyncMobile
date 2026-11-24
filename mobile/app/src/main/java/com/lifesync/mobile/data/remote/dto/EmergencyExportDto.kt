package com.lifesync.mobile.data.remote.dto

import com.lifesync.mobile.domain.model.EmergencyExport
import com.lifesync.mobile.domain.model.ExportFormat
import com.lifesync.mobile.domain.model.ExportSection
import com.lifesync.mobile.domain.model.ExportStatus
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class EmergencyExportDto(
    val id: String,
    @SerialName("user_id") val userId: String,
    val format: ExportFormat,
    val status: ExportStatus,
    val sections: List<ExportSection> = emptyList(),
    val strategy: String,
    @SerialName("strategy_version") val strategyVersion: String,
    @SerialName("requested_at") val requestedAt: String,
    @SerialName("generated_at") val generatedAt: String? = null,
    @SerialName("expires_at") val expiresAt: String? = null,
    @SerialName("content_sha256") val contentSha256: String? = null,
    @SerialName("size_bytes") val sizeBytes: Int? = null,
    @SerialName("record_count") val recordCount: Int? = null,
    @SerialName("error_code") val errorCode: String? = null,
) {
    fun toDomain(): EmergencyExport = EmergencyExport(
        id = id,
        userId = userId,
        format = format,
        status = status,
        sections = sections,
        strategy = strategy,
        strategyVersion = strategyVersion,
        requestedAt = requestedAt,
        generatedAt = generatedAt,
        expiresAt = expiresAt,
        contentSha256 = contentSha256,
        sizeBytes = sizeBytes,
        recordCount = recordCount,
        errorCode = errorCode,
    )
}
