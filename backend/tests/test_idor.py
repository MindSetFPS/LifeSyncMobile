"""Pruebas dedicadas a la mitigación de IDOR (Referencia Directa Insegura a Objetos).

Contrato verificado para cada entidad clínica:

* Un usuario autenticado nunca puede listar, leer, actualizar ni borrar
  registros de otro usuario.
* El servidor responde 404 (no 403) ante un recurso ajeno, de modo que no se
  filtra su existencia.
* Los identificadores que manda el cliente en el cuerpo no permiten pisar un
  registro de otro dueño.
* Las referencias cruzadas (alertas -> contacto/alergia/medicamento) también
  se acotan al dueño del token.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

REGISTER = "/api/v1/auth/register"
TOKEN = "/api/v1/auth/token"
PASSWORD = "SuperSegura123!"


def _headers(client: TestClient, email: str) -> dict[str, str]:
    client.post(
        REGISTER,
        json={"email": email, "full_name": "Paciente Test", "password": PASSWORD},
    )
    response = client.post(TOKEN, data={"username": email, "password": PASSWORD})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


# (colección, payload válido de creación, payload válido de actualización,
#  campo que debe permanecer intacto en el registro del dueño)
ENTITY_CASES = [
    (
        "allergies",
        {
            "allergen_name": "Penicilina",
            "category": "MEDICATION",
            "severity": "SEVERE",
            "reaction": "Anafilaxia",
        },
        {"notes": "hack"},
        ("allergen_name", "Penicilina"),
    ),
    (
        "medications",
        {
            "name": "Tramadol",
            "dosage": "50",
            "dose_unit": "MG",
            "route": "ORAL",
            "frequency_text": "Cada 8 horas",
            "start_date": "2026-01-01",
        },
        {"dosage": "999"},
        ("name", "Tramadol"),
    ),
    (
        "emergency-contacts",
        {
            "full_name": "Ana",
            "relationship": "Madre",
            "phone_primary": "+5215555555555",
            "priority": 0,
        },
        {"relationship": "Hackeado"},
        ("full_name", "Ana"),
    ),
    (
        "medical-alerts",
        {
            "type": "APPOINTMENT",
            "severity": "MEDIUM",
            "title": "Cita",
            "message": "Consulta",
        },
        {"title": "Hackeado"},
        ("title", "Cita"),
    ),
]


@pytest.mark.parametrize(
    "collection,create_payload,patch_payload,intact_field",
    ENTITY_CASES,
    ids=[case[0] for case in ENTITY_CASES],
)
def test_intruder_cannot_touch_foreign_record(
    client: TestClient,
    collection: str,
    create_payload: dict,
    patch_payload: dict,
    intact_field: tuple[str, object],
) -> None:
    owner = _headers(client, f"owner-{collection}@lifesync.mx")
    intruder = _headers(client, f"intruder-{collection}@lifesync.mx")

    created = client.post(
        f"/api/v1/{collection}", json=create_payload, headers=owner
    )
    assert created.status_code == 201, created.text
    record_id = created.json()["id"]

    # Listar jamás expone el registro ajeno.
    listed = client.get(f"/api/v1/{collection}", headers=intruder)
    assert listed.status_code == 200
    assert record_id not in [item["id"] for item in listed.json()]

    # Leer, actualizar y borrar responden 404 (no 403: no se filtra existencia).
    assert (
        client.get(f"/api/v1/{collection}/{record_id}", headers=intruder).status_code
        == 404
    )
    assert (
        client.patch(
            f"/api/v1/{collection}/{record_id}",
            json=patch_payload,
            headers=intruder,
        ).status_code
        == 404
    )
    assert (
        client.delete(f"/api/v1/{collection}/{record_id}", headers=intruder).status_code
        == 404
    )

    # El dueño conserva el registro y su contenido original.
    owned = client.get(f"/api/v1/{collection}/{record_id}", headers=owner)
    assert owned.status_code == 200
    field, expected = intact_field
    assert owned.json()[field] == expected


def test_medical_profile_is_isolated_per_user(client: TestClient) -> None:
    owner = _headers(client, "profile-owner@lifesync.mx")
    intruder = _headers(client, "profile-intruder@lifesync.mx")

    created = client.put(
        "/api/v1/medical-profile",
        json={"blood_type": "O", "rh_factor": "NEGATIVE"},
        headers=owner,
    )
    assert created.status_code == 200, created.text

    # El intruso no ve el perfil ajeno.
    assert client.get("/api/v1/medical-profile", headers=intruder).status_code == 404

    # Crear el propio perfil no sobrescribe el del dueño.
    own = client.put(
        "/api/v1/medical-profile",
        json={"blood_type": "A", "rh_factor": "POSITIVE"},
        headers=intruder,
    )
    assert own.status_code == 200

    assert own.json()["id"] != created.json()["id"]
    assert client.get("/api/v1/medical-profile", headers=owner).json()["blood_type"] == "O"


def test_create_with_foreign_id_is_rejected(client: TestClient) -> None:
    owner = _headers(client, "id-owner@lifesync.mx")
    intruder = _headers(client, "id-intruder@lifesync.mx")
    shared_id = "11111111-1111-4111-8111-111111111111"

    created = client.post(
        "/api/v1/allergies",
        json={
            "id": shared_id,
            "allergen_name": "Penicilina",
            "category": "MEDICATION",
            "severity": "SEVERE",
        },
        headers=owner,
    )
    assert created.status_code == 201, created.text

    # Reutilizar el id de otro usuario no sobrescribe ni revela el registro.
    hijack = client.post(
        "/api/v1/allergies",
        json={
            "id": shared_id,
            "allergen_name": "Intruso",
            "category": "MEDICATION",
            "severity": "MILD",
        },
        headers=intruder,
    )
    assert hijack.status_code == 409
    assert "Intruso" not in hijack.text

    assert client.get("/api/v1/allergies", headers=intruder).json() == []
    owned = client.get(f"/api/v1/allergies/{shared_id}", headers=owner)
    assert owned.status_code == 200
    assert owned.json()["allergen_name"] == "Penicilina"


def test_alert_cannot_reference_foreign_records(client: TestClient) -> None:
    owner = _headers(client, "ref-owner@lifesync.mx")
    intruder = _headers(client, "ref-intruder@lifesync.mx")

    allergy_id = client.post(
        "/api/v1/allergies",
        json={
            "allergen_name": "Penicilina",
            "category": "MEDICATION",
            "severity": "SEVERE",
        },
        headers=owner,
    ).json()["id"]

    by_related = client.post(
        "/api/v1/medical-alerts",
        json={
            "type": "ALLERGY_WARNING",
            "severity": "HIGH",
            "title": "Alerta",
            "message": "Reacción",
            "related_type": "ALLERGY",
            "related_id": allergy_id,
        },
        headers=intruder,
    )
    assert by_related.status_code == 404

    contact_id = client.post(
        "/api/v1/emergency-contacts",
        json={
            "full_name": "Luis",
            "relationship": "Hermano",
            "phone_primary": "+5215555555556",
            "priority": 0,
        },
        headers=owner,
    ).json()["id"]

    by_escalation = client.post(
        "/api/v1/medical-alerts",
        json={
            "type": "APPOINTMENT",
            "severity": "MEDIUM",
            "title": "Cita",
            "message": "Consulta",
            "escalate_to_contact_id": contact_id,
        },
        headers=intruder,
    )
    assert by_escalation.status_code == 404


def test_exports_are_isolated_per_user(client: TestClient) -> None:
    owner = _headers(client, "export-owner@lifesync.mx")
    intruder = _headers(client, "export-intruder@lifesync.mx")

    export_id = client.post(
        "/api/v1/emergency-exports", json={"format": "JSON"}, headers=owner
    ).json()["id"]

    assert client.get("/api/v1/emergency-exports", headers=intruder).json() == []
    assert (
        client.get(f"/api/v1/emergency-exports/{export_id}", headers=intruder).status_code
        == 404
    )
    assert (
        client.get(
            f"/api/v1/emergency-exports/{export_id}/download", headers=intruder
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/api/v1/emergency-exports/{export_id}/revoke", headers=intruder
        ).status_code
        == 404
    )

    # El dueño sigue pudiendo descargarlo: el intento ajeno no lo revocó.
    assert (
        client.get(
            f"/api/v1/emergency-exports/{export_id}/download", headers=owner
        ).status_code
        == 200
    )
