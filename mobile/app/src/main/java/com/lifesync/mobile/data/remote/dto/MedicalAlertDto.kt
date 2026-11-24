package com.lifesync.mobile.data.remote.dto

import com.lifesync.mobile.domain.model.AlertDelivery
import com.lifesync.mobile.domain.model.AlertRelatedType
import com.lifesync.mobile.domain.model.AlertSeverity
import com.lifesync.mobile.domain.model.AlertType
import com.lifesync.mobile.domain.model.MedicalAlert
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class MedicalAlertDto(
    val id: String,
    @SerialName("user_id") val userId: String,
    val type: AlertType,
    val severity: AlertSeverity,
    val title: String,
    val message: String,
    @SerialName("related_type") val relatedType: AlertRelatedType,
    @SerialName("related_id") val relatedId: String? = null,
    @SerialName("scheduled_at") val scheduledAt: String? = null,
    @SerialName("recurrence_rule") val recurrenceRule: String? = null,
    val timezone: String,
    @SerialName("is_enabled") val isEnabled: Boolean,
    @SerialName("next_fire_at") val nextFireAt: String? = null,
    @SerialName("last_fired_at") val lastFiredAt: String? = null,
    @SerialName("acknowledged_at") val acknowledgedAt: String? = null,
    @SerialName("snoozed_until") val snoozedUntil: String? = null,
    @SerialName("escalate_to_contact_id") val escalateToContactId: String? = null,
    val delivery: AlertDelivery,
    val version: Int,
    @SerialName("created_at") val createdAt: String,
    @SerialName("updated_at") val updatedAt: String,
    @SerialName("deleted_at") val deletedAt: String? = null,
) {
    fun toDomain(): MedicalAlert = MedicalAlert(
        id = id,
        userId = userId,
        type = type,
        severity = severity,
        title = title,
        message = message,
        relatedType = relatedType,
        relatedId = relatedId,
        scheduledAt = scheduledAt,
        recurrenceRule = recurrenceRule,
        timezone = timezone,
        isEnabled = isEnabled,
        nextFireAt = nextFireAt,
        lastFiredAt = lastFiredAt,
        acknowledgedAt = acknowledgedAt,
        snoozedUntil = snoozedUntil,
        escalateToContactId = escalateToContactId,
        delivery = delivery,
        version = version,
        createdAt = createdAt,
        updatedAt = updatedAt,
        deletedAt = deletedAt,
    )
}
