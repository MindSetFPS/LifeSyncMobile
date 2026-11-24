package com.lifesync.mobile.domain.model

enum class BloodType { A, B, AB, O }

enum class RhFactor { POSITIVE, NEGATIVE }

enum class AllergyCategory { MEDICATION, FOOD, ENVIRONMENTAL, INSECT, OTHER }

enum class AllergySeverity { MILD, MODERATE, SEVERE, ANAPHYLAXIS, UNKNOWN }

enum class AllergyStatus { ACTIVE, RESOLVED, SUSPECTED }

enum class DoseUnit { MG, ML, MCG, G, IU, DROPS, PUFFS, TABLET, CAPSULE, OTHER }

enum class MedicationRoute { ORAL, IV, IM, TOPICAL, INHALED, SUBLINGUAL, RECTAL, OTHER }

enum class ExportFormat { JSON, CSV }

enum class ExportStatus { PENDING, READY, FAILED, EXPIRED, REVOKED }

enum class ExportSection { PROFILE, ALLERGIES, MEDICATIONS, CONTACTS, ALERTS }

enum class AlertType {
    MEDICATION_REMINDER,
    APPOINTMENT,
    ALLERGY_WARNING,
    VITAL_ANOMALY,
    EMERGENCY,
}

enum class AlertSeverity { LOW, MEDIUM, HIGH, CRITICAL }

enum class AlertRelatedType { ALLERGY, MEDICATION, CONTACT, EXPORT, NONE }

enum class AlertDelivery { LOCAL_NOTIFICATION }
