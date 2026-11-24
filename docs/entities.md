# Entidades del dominio clínico — LifeSync Mobile

Definición de las entidades de datos sensibles de salud (Sprints 2 y 3). Este
documento es **solo de modelado**: no define endpoints ni implementación.

Alcance tomado del README:

- Alergias.
- Tipo de sangre.
- Medicamentos controlados.
- Contactos de emergencia.
- Exportación del historial clínico de emergencia (JSON / CSV).
- Módulo de alertas médicas locales.

## Supuestos

- El **tipo de sangre** vive en un perfil clínico 1:1 (`MedicalProfile`), no
  como registro N:1: solo puede existir un tipo de sangre vigente por usuario.
- La **exportación** es un *snapshot/job* inmutable generado en el servidor
  (patrón Strategy), no una fuente de verdad.
- Las **alertas** son local-first (Room + notificación), con sincronización
  opcional solo para respaldo.
- Fuera de alcance por ahora: recetas escaneadas (cámara) y ubicación del
  incidente (GPS). Se anotan como entidades futuras.

## Convenciones

- Backend: SQLAlchemy 2.0 (`Mapped` / `mapped_column`), PK `String(36)` UUID,
  tablas en plural snake_case, timestamps en UTC.
- Backend: Pydantic v2 con `ConfigDict(extra="forbid")` en todos los schemas.
- Móvil: `data class` de dominio en camelCase, DTO con `@SerialName` para
  snake_case, entidad Room para persistencia offline.
- Todo dato clínico es **PHI**: cifrado en reposo, nunca en logs ni en
  mensajes de error.

## Modelo relacional

```
User 1───1 MedicalProfile          (tipo de sangre, RH, datos base)
User 1───N Allergy                 (alergias)
User 1───N Medication              (medicamentos, marca is_controlled)
User 1───N EmergencyContact        (contactos, con prioridad)
User 1───N MedicalAlert ──?──1 EmergencyContact   (escalamiento opcional)
                 └────?── Allergy | Medication    (origen polimórfico)
User 1───N EmergencyExport         (snapshots generados bajo demanda)
```

## Campos comunes

Aplican a todas las tablas clínicas.

| Campo | Tipo | Regla |
|---|---|---|
| `id` | `String(36)` UUID | Generado en el móvil para permitir creación offline; el servidor lo valida y **nunca confía en él para autorizar**. |
| `user_id` | `String(36)` FK `users.id` | Dueño derivado del JWT (`sub`), nunca del body; índice obligatorio. |
| `created_at` | `DateTime(tz=UTC)` | Servidor. |
| `updated_at` | `DateTime(tz=UTC)` | Servidor. |
| `deleted_at` | `DateTime(tz=UTC)` nullable | Borrado lógico → tombstone de sincronización. |
| `version` | `Integer` | Bloqueo optimista; el update exige la versión esperada o responde `409`. |

Campos **solo del cliente** (Room, no viajan al backend):

- `sync_state`: `PENDING_CREATE | PENDING_UPDATE | PENDING_DELETE | SYNCED | CONFLICT`.
- `client_updated_at`.
- `server_version`.
- `last_sync_error`.

## Entidades

### 1. `MedicalProfile` → `medical_profiles` (1:1 con User)

| Campo | Tipo | Restricción |
|---|---|---|
| `user_id` | String(36) | `UNIQUE`, FK `users.id` |
| `blood_type` | Enum `A, B, AB, O` | nullable = desconocido |
| `rh_factor` | Enum `POSITIVE, NEGATIVE` | nullable |
| `date_of_birth` | Date | nullable; se omite del export si no es necesario |
| `height_cm` | Numeric | nullable, > 0 |
| `weight_kg` | Numeric | nullable, > 0 |
| `organ_donor` | Boolean | nullable |
| `chronic_conditions` | String(1000) | texto plano saneado |

Sanitización: `blood_type` y `rh_factor` se validan por enum; no se aceptan
strings libres.

### 2. `Allergy` → `allergies`

| Campo | Tipo | Restricción |
|---|---|---|
| `allergen_name` | String(120) | obligatorio, trim, sin HTML |
| `category` | Enum `MEDICATION, FOOD, ENVIRONMENTAL, INSECT, OTHER` | obligatorio |
| `severity` | Enum `MILD, MODERATE, SEVERE, ANAPHYLAXIS, UNKNOWN` | obligatorio |
| `status` | Enum `ACTIVE, RESOLVED, SUSPECTED` | default `ACTIVE` |
| `reaction` | String(255) | nullable |
| `diagnosed_at` | Date | nullable |
| `notes` | String(500) | nullable |
| `is_emergency_relevant` | Boolean | default `true` → entra al export |

### 3. `Medication` → `medications`

| Campo | Tipo | Restricción |
|---|---|---|
| `name` | String(120) | obligatorio |
| `active_ingredient` | String(120) | nullable |
| `dosage` | String(60) | obligatorio (dosis numérica o texto corto) |
| `dose_unit` | Enum `MG, ML, MCG, G, IU, DROPS, PUFFS, TABLET, CAPSULE, OTHER` | obligatorio |
| `route` | Enum `ORAL, IV, IM, TOPICAL, INHALED, SUBLINGUAL, RECTAL, OTHER` | obligatorio |
| `frequency_text` | String(120) | texto para mostrar |
| `interval_hours` | Integer | nullable, 1–168 (base para recordatorios) |
| `reminder_times` | JSON `["HH:MM"]` | nullable, máx. 12 entradas, TZ del dispositivo |
| `is_controlled` | Boolean | default `false` → marca de medicamento controlado |
| `controlled_schedule` | String(20) | nullable, allowlist configurable (ej. `II`, `III`, `IV`) |
| `prescriber_name` | String(120) | nullable |
| `prescription_number` | String(60) | nullable; se enmascara en export por defecto |
| `start_date` | Date | obligatorio |
| `end_date` | Date | nullable; `end_date >= start_date` |
| `is_active` | Boolean | default `true` |
| `indication` | String(255) | nullable |
| `show_in_emergency` | Boolean | default `true` |

Sanitización y reglas:

- `controlled_schedule` solo se acepta si `is_controlled = true`.
- Un medicamento controlado exige `prescriber_name` (regla de negocio, no
  constraint de BD).

### 4. `EmergencyContact` → `emergency_contacts`

| Campo | Tipo | Restricción |
|---|---|---|
| `full_name` | String(120) | obligatorio |
| `relationship` | String(60) | obligatorio ("madre", "cónyuge", ...) |
| `phone_primary` | String(20) | E.164 `^\+[1-9]\d{1,14}$`, normalizado |
| `phone_secondary` | String(20) | nullable, mismo formato |
| `email` | String(320) | nullable, `EmailStr` |
| `priority` | Integer | ≥ 0; `UNIQUE(user_id, priority)`; `0` = principal |
| `notify_on_incident` | Boolean | default `true` |
| `is_active` | Boolean | default `true` |
| `notes` | String(255) | nullable |

Regla: al menos un contacto debe tener `priority = 0`; el borrado lógico del
principal se rechaza hasta reasignar prioridad.

### 5. `EmergencyExport` → `emergency_exports` (snapshot inmutable)

| Campo | Tipo | Restricción |
|---|---|---|
| `format` | Enum `JSON, CSV` | obligatorio (Strategy: JSON médicos / CSV aseguradoras) |
| `status` | Enum `PENDING, READY, FAILED, EXPIRED, REVOKED` | default `PENDING` |
| `sections` | JSON enum[] | subconjunto de `PROFILE, ALLERGIES, MEDICATIONS, CONTACTS, ALERTS` |
| `strategy` | String(40) | ej. `json_medical`, `csv_insurer` |
| `strategy_version` | String(10) | permite reproducir el formato |
| `requested_at` | DateTime UTC | obligatorio |
| `generated_at` | DateTime UTC | nullable |
| `expires_at` | DateTime UTC | TTL corto (ej. 15 min–24 h) |
| `content_sha256` | String(64) | integridad del archivo |
| `size_bytes` | Integer | metadato, sin PHI |
| `record_count` | Integer | metadato, sin PHI |
| `storage_key` | String(255) | referencia al blob cifrado, nullable |
| `download_token_hash` | String(64) | solo hash del token de un solo uso |
| `error_code` | String(40) | nullable, sin datos sensibles |

Reglas:

- No se versiona ni se borra lógicamente: estado terminal `EXPIRED` / `REVOKED`.
- El contenido del archivo jamás se registra en logs.

### 6. `MedicalAlert` → `medical_alerts` (local-first)

| Campo | Tipo | Restricción |
|---|---|---|
| `type` | Enum `MEDICATION_REMINDER, APPOINTMENT, ALLERGY_WARNING, VITAL_ANOMALY, EMERGENCY` | obligatorio |
| `severity` | Enum `LOW, MEDIUM, HIGH, CRITICAL` | obligatorio |
| `title` | String(120) | obligatorio |
| `message` | String(500) | saneado |
| `related_type` | Enum `ALLERGY, MEDICATION, CONTACT, EXPORT, NONE` | default `NONE` |
| `related_id` | String(36) | nullable; coherente con `related_type` |
| `scheduled_at` | DateTime UTC | nullable (alerta única) |
| `recurrence_rule` | String(255) | nullable; subconjunto RFC 5545 (`FREQ=DAILY;...`) |
| `timezone` | String(64) | IANA; default del dispositivo |
| `is_enabled` | Boolean | default `true` |
| `next_fire_at` | DateTime UTC | nullable; base del patrón Observer |
| `last_fired_at` | DateTime UTC | nullable |
| `acknowledged_at` | DateTime UTC | nullable |
| `snoozed_until` | DateTime UTC | nullable |
| `escalate_to_contact_id` | String(36) FK `emergency_contacts.id` | nullable |
| `delivery` | Enum `LOCAL_NOTIFICATION` | solo local por ahora |

Regla: `scheduled_at` y `recurrence_rule` son mutuamente excluyentes; si
`type = MEDICATION_REMINDER` debe existir exactamente uno.

## Enums compartidos (backend / móvil)

```
BloodType          A | B | AB | O
RhFactor           POSITIVE | NEGATIVE
AllergyCategory    MEDICATION | FOOD | ENVIRONMENTAL | INSECT | OTHER
AllergySeverity    MILD | MODERATE | SEVERE | ANAPHYLAXIS | UNKNOWN
AllergyStatus      ACTIVE | RESOLVED | SUSPECTED
DoseUnit           MG | ML | MCG | G | IU | DROPS | PUFFS | TABLET | CAPSULE | OTHER
MedicationRoute    ORAL | IV | IM | TOPICAL | INHALED | SUBLINGUAL | RECTAL | OTHER
ExportFormat       JSON | CSV
ExportStatus       PENDING | READY | FAILED | EXPIRED | REVOKED
AlertType          MEDICATION_REMINDER | APPOINTMENT | ALLERGY_WARNING | VITAL_ANOMALY | EMERGENCY
AlertSeverity      LOW | MEDIUM | HIGH | CRITICAL
```

## Reglas transversales

### Mitigación de IDOR (brechas lógicas en la nube)

- Todo repositorio filtra por `user_id = current_user.id` tomado del JWT.
- `user_id` nunca se acepta del cliente.
- Un ID ajeno responde `404` (no `403`) para no filtrar existencia.
- `EmergencyExport` y su token de descarga se validan también contra el dueño.

### Sanitización de payloads

- `extra="forbid"` en todos los schemas.
- Longitudes acotadas, enums cerrados, teléfono E.164, fechas ISO.
- JSON de `reminder_times` y `sections` con allowlist.
- Rechazo de HTML, caracteres de control y trim previo.
- ORM parametrizado (sin SQL crudo) para bloquear inyección SQL/NoSQL.

### PHI

- Cifrado en reposo: Room/SQLCipher + Keystore en móvil; cifrado de columna o
  de base en servidor.
- Nunca en logs ni en mensajes de error.
- `prescription_number` enmascarado en export salvo petición explícita.

### Conflictos offline-first

- `version` + `updated_at` + `deleted_at` cubren el merge.
- LWW en cliente; `409` con la versión del servidor en el backend.

## Entidades futuras (no incluidas)

- `PrescriptionScan` — imagen de receta capturada con cámara.
- `IncidentLocation` — geolocalización del incidente (GPS, degradable).

## Pendientes de decisión

1. ¿El tipo de sangre queda en `MedicalProfile` 1:1 o como registro CRUD
   independiente?
2. ¿Las alertas se respaldan en la nube o permanecen 100 % locales?
   (Recomendación: local + backup cifrado opcional.)
3. ¿La exportación incluye PDF o solo `JSON` / `CSV` como pide el README?
