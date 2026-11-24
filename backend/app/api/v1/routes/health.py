"""Rutas CRUD de las entidades clínicas.

Todas las operaciones exigen Bearer JWT y acotan las consultas al `user_id`
del token. Un recurso ajeno responde 404 (no 403) para no filtrar existencia.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import CurrentUser
from app.core.database import get_db
from app.models.allergy import Allergy
from app.models.emergency_contact import EmergencyContact
from app.models.enums import AlertRelatedType, ExportFormat
from app.models.medical_alert import MedicalAlert
from app.models.medical_profile import MedicalProfile
from app.models.medication import Medication
from app.repositories.health_repository import HealthRepository
from app.schemas.health import (
    AllergyCreate,
    AllergyOut,
    AllergyUpdate,
    EmergencyContactCreate,
    EmergencyContactOut,
    EmergencyContactUpdate,
    EmergencyExportCreate,
    EmergencyExportOut,
    MedicalAlertCreate,
    MedicalAlertOut,
    MedicalAlertUpdate,
    MedicalProfileCreate,
    MedicalProfileOut,
    MedicationCreate,
    MedicationOut,
    MedicationUpdate,
)
from app.services.export_service import (
    ExportExpiredError,
    ExportService,
    ExportUnavailableError,
)
from app.services.health_service import ConflictError, HealthService, NotFoundError

router = APIRouter(tags=["health"])

SessionDep = Annotated[AsyncSession, Depends(get_db)]
LimitQuery = Annotated[int, Query(ge=1, le=500)]
OffsetQuery = Annotated[int, Query(ge=0)]


def _not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado"
    )


def _conflict(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


# --------------------------------------------------------------------------- #
# Perfil clínico (1:1)
# --------------------------------------------------------------------------- #


@router.get(
    "/medical-profile",
    response_model=MedicalProfileOut,
    summary="Obtener el perfil clínico propio",
)
async def get_medical_profile(
    current_user: CurrentUser, session: SessionDep
) -> MedicalProfileOut:
    profile = await HealthService(session, MedicalProfile).get_single(
        current_user.id
    )
    if profile is None:
        raise _not_found()
    return MedicalProfileOut.model_validate(profile)


@router.put(
    "/medical-profile",
    response_model=MedicalProfileOut,
    summary="Crear o actualizar el perfil clínico propio",
)
async def upsert_medical_profile(
    payload: MedicalProfileCreate,
    current_user: CurrentUser,
    session: SessionDep,
) -> MedicalProfileOut:
    service = HealthService(session, MedicalProfile)
    try:
        existing = await service.get_single(current_user.id)
        if existing is None:
            profile = await service.create_record(current_user.id, payload)
        else:
            profile = await service.update_record(
                current_user.id, existing.id, payload
            )
    except ConflictError as exc:
        raise _conflict(str(exc)) from exc
    return MedicalProfileOut.model_validate(profile)


# --------------------------------------------------------------------------- #
# Alergias
# --------------------------------------------------------------------------- #


@router.get(
    "/allergies",
    response_model=list[AllergyOut],
    summary="Listar alergias propias",
)
async def list_allergies(
    current_user: CurrentUser,
    session: SessionDep,
    limit: LimitQuery = 100,
    offset: OffsetQuery = 0,
) -> list[AllergyOut]:
    records = await HealthService(session, Allergy).list_records(
        current_user.id, limit=limit, offset=offset
    )
    return [AllergyOut.model_validate(record) for record in records]


@router.post(
    "/allergies",
    response_model=AllergyOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una alergia propia",
)
async def create_allergy(
    payload: AllergyCreate, current_user: CurrentUser, session: SessionDep
) -> AllergyOut:
    try:
        record = await HealthService(session, Allergy).create_record(
            current_user.id, payload
        )
    except ConflictError as exc:
        raise _conflict(str(exc)) from exc
    return AllergyOut.model_validate(record)


@router.get(
    "/allergies/{allergy_id}",
    response_model=AllergyOut,
    summary="Obtener una alergia propia",
)
async def get_allergy(
    allergy_id: str, current_user: CurrentUser, session: SessionDep
) -> AllergyOut:
    try:
        record = await HealthService(session, Allergy).get_record(
            current_user.id, allergy_id
        )
    except NotFoundError as exc:
        raise _not_found() from exc
    return AllergyOut.model_validate(record)


@router.patch(
    "/allergies/{allergy_id}",
    response_model=AllergyOut,
    summary="Actualizar una alergia propia",
)
async def update_allergy(
    allergy_id: str,
    payload: AllergyUpdate,
    current_user: CurrentUser,
    session: SessionDep,
) -> AllergyOut:
    try:
        record = await HealthService(session, Allergy).update_record(
            current_user.id, allergy_id, payload
        )
    except NotFoundError as exc:
        raise _not_found() from exc
    except ConflictError as exc:
        raise _conflict(str(exc)) from exc
    return AllergyOut.model_validate(record)


@router.delete(
    "/allergies/{allergy_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una alergia propia (borrado lógico)",
)
async def delete_allergy(
    allergy_id: str, current_user: CurrentUser, session: SessionDep
) -> Response:
    try:
        await HealthService(session, Allergy).delete_record(
            current_user.id, allergy_id
        )
    except NotFoundError as exc:
        raise _not_found() from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --------------------------------------------------------------------------- #
# Medicamentos
# --------------------------------------------------------------------------- #


@router.get(
    "/medications",
    response_model=list[MedicationOut],
    summary="Listar medicamentos propios",
)
async def list_medications(
    current_user: CurrentUser,
    session: SessionDep,
    limit: LimitQuery = 100,
    offset: OffsetQuery = 0,
) -> list[MedicationOut]:
    records = await HealthService(session, Medication).list_records(
        current_user.id, limit=limit, offset=offset
    )
    return [MedicationOut.model_validate(record) for record in records]


@router.post(
    "/medications",
    response_model=MedicationOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un medicamento propio",
)
async def create_medication(
    payload: MedicationCreate, current_user: CurrentUser, session: SessionDep
) -> MedicationOut:
    try:
        record = await HealthService(session, Medication).create_record(
            current_user.id, payload
        )
    except ConflictError as exc:
        raise _conflict(str(exc)) from exc
    return MedicationOut.model_validate(record)


@router.get(
    "/medications/{medication_id}",
    response_model=MedicationOut,
    summary="Obtener un medicamento propio",
)
async def get_medication(
    medication_id: str, current_user: CurrentUser, session: SessionDep
) -> MedicationOut:
    try:
        record = await HealthService(session, Medication).get_record(
            current_user.id, medication_id
        )
    except NotFoundError as exc:
        raise _not_found() from exc
    return MedicationOut.model_validate(record)


@router.patch(
    "/medications/{medication_id}",
    response_model=MedicationOut,
    summary="Actualizar un medicamento propio",
)
async def update_medication(
    medication_id: str,
    payload: MedicationUpdate,
    current_user: CurrentUser,
    session: SessionDep,
) -> MedicationOut:
    try:
        record = await HealthService(session, Medication).update_record(
            current_user.id, medication_id, payload
        )
    except NotFoundError as exc:
        raise _not_found() from exc
    except ConflictError as exc:
        raise _conflict(str(exc)) from exc
    return MedicationOut.model_validate(record)


@router.delete(
    "/medications/{medication_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un medicamento propio (borrado lógico)",
)
async def delete_medication(
    medication_id: str, current_user: CurrentUser, session: SessionDep
) -> Response:
    try:
        await HealthService(session, Medication).delete_record(
            current_user.id, medication_id
        )
    except NotFoundError as exc:
        raise _not_found() from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --------------------------------------------------------------------------- #
# Contactos de emergencia
# --------------------------------------------------------------------------- #


@router.get(
    "/emergency-contacts",
    response_model=list[EmergencyContactOut],
    summary="Listar contactos de emergencia propios",
)
async def list_contacts(
    current_user: CurrentUser,
    session: SessionDep,
    limit: LimitQuery = 100,
    offset: OffsetQuery = 0,
) -> list[EmergencyContactOut]:
    records = await HealthService(session, EmergencyContact).list_records(
        current_user.id, limit=limit, offset=offset
    )
    return [EmergencyContactOut.model_validate(record) for record in records]


@router.post(
    "/emergency-contacts",
    response_model=EmergencyContactOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un contacto de emergencia propio",
)
async def create_contact(
    payload: EmergencyContactCreate,
    current_user: CurrentUser,
    session: SessionDep,
) -> EmergencyContactOut:
    try:
        record = await HealthService(session, EmergencyContact).create_record(
            current_user.id, payload
        )
    except ConflictError as exc:
        raise _conflict(str(exc)) from exc
    return EmergencyContactOut.model_validate(record)


@router.get(
    "/emergency-contacts/{contact_id}",
    response_model=EmergencyContactOut,
    summary="Obtener un contacto de emergencia propio",
)
async def get_contact(
    contact_id: str, current_user: CurrentUser, session: SessionDep
) -> EmergencyContactOut:
    try:
        record = await HealthService(session, EmergencyContact).get_record(
            current_user.id, contact_id
        )
    except NotFoundError as exc:
        raise _not_found() from exc
    return EmergencyContactOut.model_validate(record)


@router.patch(
    "/emergency-contacts/{contact_id}",
    response_model=EmergencyContactOut,
    summary="Actualizar un contacto de emergencia propio",
)
async def update_contact(
    contact_id: str,
    payload: EmergencyContactUpdate,
    current_user: CurrentUser,
    session: SessionDep,
) -> EmergencyContactOut:
    try:
        record = await HealthService(session, EmergencyContact).update_record(
            current_user.id, contact_id, payload
        )
    except NotFoundError as exc:
        raise _not_found() from exc
    except ConflictError as exc:
        raise _conflict(str(exc)) from exc
    return EmergencyContactOut.model_validate(record)


@router.delete(
    "/emergency-contacts/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un contacto de emergencia propio (borrado lógico)",
)
async def delete_contact(
    contact_id: str, current_user: CurrentUser, session: SessionDep
) -> Response:
    service = HealthService(session, EmergencyContact)
    try:
        contact = await service.get_record(current_user.id, contact_id)
    except NotFoundError as exc:
        raise _not_found() from exc
    if contact.priority == 0:
        raise _conflict(
            "Reasigna la prioridad del contacto principal antes de eliminarlo"
        )
    await service.delete_record(current_user.id, contact_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --------------------------------------------------------------------------- #
# Alertas médicas
# --------------------------------------------------------------------------- #


async def _validate_alert_references(
    session: AsyncSession,
    user_id: str,
    *,
    related_type: AlertRelatedType | None,
    related_id: str | None,
    escalate_to_contact_id: str | None,
) -> None:
    """Impide referencias a registros de otro usuario (brecha lógica)."""
    if escalate_to_contact_id is not None:
        contact = await HealthRepository(
            session, EmergencyContact
        ).get_for_user(user_id, escalate_to_contact_id)
        if contact is None:
            raise _not_found()

    if related_id is None or related_type is None:
        return

    model = {
        AlertRelatedType.ALLERGY: Allergy,
        AlertRelatedType.MEDICATION: Medication,
        AlertRelatedType.CONTACT: EmergencyContact,
    }.get(related_type)
    if model is None:
        return
    record = await HealthRepository(session, model).get_for_user(
        user_id, related_id
    )
    if record is None:
        raise _not_found()


@router.get(
    "/medical-alerts",
    response_model=list[MedicalAlertOut],
    summary="Listar alertas médicas propias",
)
async def list_alerts(
    current_user: CurrentUser,
    session: SessionDep,
    limit: LimitQuery = 100,
    offset: OffsetQuery = 0,
) -> list[MedicalAlertOut]:
    records = await HealthService(session, MedicalAlert).list_records(
        current_user.id, limit=limit, offset=offset
    )
    return [MedicalAlertOut.model_validate(record) for record in records]


@router.post(
    "/medical-alerts",
    response_model=MedicalAlertOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una alerta médica propia",
)
async def create_alert(
    payload: MedicalAlertCreate,
    current_user: CurrentUser,
    session: SessionDep,
) -> MedicalAlertOut:
    await _validate_alert_references(
        session,
        current_user.id,
        related_type=payload.related_type,
        related_id=payload.related_id,
        escalate_to_contact_id=payload.escalate_to_contact_id,
    )
    try:
        record = await HealthService(session, MedicalAlert).create_record(
            current_user.id, payload
        )
    except ConflictError as exc:
        raise _conflict(str(exc)) from exc
    return MedicalAlertOut.model_validate(record)


@router.get(
    "/medical-alerts/{alert_id}",
    response_model=MedicalAlertOut,
    summary="Obtener una alerta médica propia",
)
async def get_alert(
    alert_id: str, current_user: CurrentUser, session: SessionDep
) -> MedicalAlertOut:
    try:
        record = await HealthService(session, MedicalAlert).get_record(
            current_user.id, alert_id
        )
    except NotFoundError as exc:
        raise _not_found() from exc
    return MedicalAlertOut.model_validate(record)


@router.patch(
    "/medical-alerts/{alert_id}",
    response_model=MedicalAlertOut,
    summary="Actualizar una alerta médica propia",
)
async def update_alert(
    alert_id: str,
    payload: MedicalAlertUpdate,
    current_user: CurrentUser,
    session: SessionDep,
) -> MedicalAlertOut:
    service = HealthService(session, MedicalAlert)
    try:
        existing = await service.get_record(current_user.id, alert_id)
    except NotFoundError as exc:
        raise _not_found() from exc

    related_type = payload.related_type
    if related_type is None and payload.related_id is not None:
        related_type = existing.related_type
    await _validate_alert_references(
        session,
        current_user.id,
        related_type=related_type,
        related_id=payload.related_id,
        escalate_to_contact_id=payload.escalate_to_contact_id,
    )

    try:
        record = await service.update_record(current_user.id, alert_id, payload)
    except ConflictError as exc:
        raise _conflict(str(exc)) from exc
    return MedicalAlertOut.model_validate(record)


@router.delete(
    "/medical-alerts/{alert_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una alerta médica propia (borrado lógico)",
)
async def delete_alert(
    alert_id: str, current_user: CurrentUser, session: SessionDep
) -> Response:
    try:
        await HealthService(session, MedicalAlert).delete_record(
            current_user.id, alert_id
        )
    except NotFoundError as exc:
        raise _not_found() from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --------------------------------------------------------------------------- #
# Exportación del historial clínico
# --------------------------------------------------------------------------- #


@router.get(
    "/emergency-exports",
    response_model=list[EmergencyExportOut],
    summary="Listar exportaciones propias",
)
async def list_exports(
    current_user: CurrentUser,
    session: SessionDep,
    limit: LimitQuery = 100,
    offset: OffsetQuery = 0,
) -> list[EmergencyExportOut]:
    records = await ExportService(session).list_exports(
        current_user.id, limit=limit, offset=offset
    )
    return [EmergencyExportOut.model_validate(record) for record in records]


@router.post(
    "/emergency-exports",
    response_model=EmergencyExportOut,
    status_code=status.HTTP_201_CREATED,
    summary="Generar un snapshot del historial de emergencia",
)
async def create_export(
    payload: EmergencyExportCreate,
    current_user: CurrentUser,
    session: SessionDep,
) -> EmergencyExportOut:
    record = await ExportService(session).create_export(current_user, payload)
    return EmergencyExportOut.model_validate(record)


@router.get(
    "/emergency-exports/{export_id}",
    response_model=EmergencyExportOut,
    summary="Obtener una exportación propia",
)
async def get_export(
    export_id: str, current_user: CurrentUser, session: SessionDep
) -> EmergencyExportOut:
    try:
        record = await ExportService(session).get_export(
            current_user.id, export_id
        )
    except ExportUnavailableError as exc:
        raise _not_found() from exc
    return EmergencyExportOut.model_validate(record)


@router.get(
    "/emergency-exports/{export_id}/download",
    summary="Descargar el snapshot generado",
    response_class=Response,
)
async def download_export(
    export_id: str, current_user: CurrentUser, session: SessionDep
) -> Response:
    try:
        record, data = await ExportService(session).download(
            current_user.id, export_id
        )
    except ExportUnavailableError as exc:
        raise _not_found() from exc
    except ExportExpiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_410_GONE, detail=str(exc)
        ) from exc

    extension = "json" if record.format == ExportFormat.JSON else "csv"
    media_type = (
        "application/json"
        if record.format == ExportFormat.JSON
        else "text/csv"
    )
    return Response(
        content=data,
        media_type=media_type,
        headers={
            "Content-Disposition": (
                f'attachment; filename="lifesync-export-{record.id}.{extension}"'
            ),
            "X-Content-SHA256": record.content_sha256 or "",
        },
    )


@router.post(
    "/emergency-exports/{export_id}/revoke",
    response_model=EmergencyExportOut,
    summary="Revocar una exportación propia",
)
async def revoke_export(
    export_id: str, current_user: CurrentUser, session: SessionDep
) -> EmergencyExportOut:
    try:
        record = await ExportService(session).revoke(
            current_user.id, export_id
        )
    except ExportUnavailableError as exc:
        raise _not_found() from exc
    return EmergencyExportOut.model_validate(record)
