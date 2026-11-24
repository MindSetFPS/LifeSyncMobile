"""Pruebas de integración de las rutas clínicas (CRUD, IDOR y export)."""

from __future__ import annotations

import json

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


def _allergy_payload(**overrides: object) -> dict:
    payload = {
        "allergen_name": "Penicilina",
        "category": "MEDICATION",
        "severity": "SEVERE",
        "reaction": "Anafilaxia",
    }
    payload.update(overrides)
    return payload


def test_requires_bearer_token(client: TestClient) -> None:
    assert client.get("/api/v1/allergies").status_code == 401


def test_allergy_crud_flow(client: TestClient) -> None:
    headers = _headers(client, "ana@lifesync.mx")

    created = client.post(
        "/api/v1/allergies", json=_allergy_payload(), headers=headers
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["status"] == "ACTIVE"
    assert body["version"] == 1
    assert body["is_emergency_relevant"] is True

    allergy_id = body["id"]
    listed = client.get("/api/v1/allergies", headers=headers)
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [allergy_id]

    patched = client.patch(
        f"/api/v1/allergies/{allergy_id}",
        json={"notes": "Confirmada por alergología"},
        headers=headers,
    )
    assert patched.status_code == 200
    assert patched.json()["version"] == 2
    assert patched.json()["notes"] == "Confirmada por alergología"

    deleted = client.delete(f"/api/v1/allergies/{allergy_id}", headers=headers)
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/allergies/{allergy_id}", headers=headers).status_code == 404
    assert client.get("/api/v1/allergies", headers=headers).json() == []


def test_idor_other_users_records_are_invisible(client: TestClient) -> None:
    owner = _headers(client, "owner@lifesync.mx")
    intruder = _headers(client, "intruder@lifesync.mx")
    allergy_id = client.post(
        "/api/v1/allergies", json=_allergy_payload(), headers=owner
    ).json()["id"]

    assert client.get("/api/v1/allergies", headers=intruder).json() == []
    assert (
        client.get(f"/api/v1/allergies/{allergy_id}", headers=intruder).status_code
        == 404
    )
    assert (
        client.patch(
            f"/api/v1/allergies/{allergy_id}",
            json={"notes": "hack"},
            headers=intruder,
        ).status_code
        == 404
    )
    assert (
        client.delete(
            f"/api/v1/allergies/{allergy_id}", headers=intruder
        ).status_code
        == 404
    )


def test_payload_sanitization_rejects_markup(client: TestClient) -> None:
    headers = _headers(client, "xss@lifesync.mx")
    response = client.post(
        "/api/v1/allergies",
        json=_allergy_payload(allergen_name="<script>alert(1)</script>"),
        headers=headers,
    )
    assert response.status_code == 422


def test_medical_profile_upsert(client: TestClient) -> None:
    headers = _headers(client, "profile@lifesync.mx")

    assert client.get("/api/v1/medical-profile", headers=headers).status_code == 404

    first = client.put(
        "/api/v1/medical-profile",
        json={"blood_type": "O", "rh_factor": "NEGATIVE"},
        headers=headers,
    )
    assert first.status_code == 200, first.text
    assert first.json()["blood_type"] == "O"

    second = client.put(
        "/api/v1/medical-profile",
        json={"chronic_conditions": "Asma"},
        headers=headers,
    )
    assert second.status_code == 200
    assert second.json()["blood_type"] == "O"
    assert second.json()["chronic_conditions"] == "Asma"

    fetched = client.get("/api/v1/medical-profile", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["id"] == first.json()["id"]


def test_emergency_contact_priority_rules(client: TestClient) -> None:
    headers = _headers(client, "contacts@lifesync.mx")
    base = {
        "full_name": "Ana",
        "relationship": "Madre",
        "phone_primary": "+5215555555555",
    }

    primary = client.post(
        "/api/v1/emergency-contacts",
        json={**base, "priority": 0},
        headers=headers,
    )
    assert primary.status_code == 201, primary.text

    duplicate = client.post(
        "/api/v1/emergency-contacts",
        json={**base, "priority": 0},
        headers=headers,
    )
    assert duplicate.status_code == 409

    assert (
        client.delete(
            f"/api/v1/emergency-contacts/{primary.json()['id']}",
            headers=headers,
        ).status_code
        == 409
    )

    secondary = client.post(
        "/api/v1/emergency-contacts",
        json={**base, "priority": 1},
        headers=headers,
    )
    assert secondary.status_code == 201
    assert (
        client.delete(
            f"/api/v1/emergency-contacts/{secondary.json()['id']}",
            headers=headers,
        ).status_code
        == 204
    )


def test_alert_cannot_reference_another_users_contact(client: TestClient) -> None:
    owner = _headers(client, "alert-owner@lifesync.mx")
    intruder = _headers(client, "alert-intruder@lifesync.mx")

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

    response = client.post(
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
    assert response.status_code == 404


def test_medication_controlled_rule(client: TestClient) -> None:
    headers = _headers(client, "meds@lifesync.mx")
    base = {
        "name": "Tramadol",
        "dosage": "50",
        "dose_unit": "MG",
        "route": "ORAL",
        "frequency_text": "Cada 8 horas",
        "start_date": "2026-01-01",
    }
    invalid = client.post(
        "/api/v1/medications",
        json={**base, "is_controlled": True},
        headers=headers,
    )
    assert invalid.status_code == 422

    valid = client.post(
        "/api/v1/medications",
        json={
            **base,
            "is_controlled": True,
            "controlled_schedule": "II",
            "prescriber_name": "Dra. Pérez",
        },
        headers=headers,
    )
    assert valid.status_code == 201, valid.text
    assert valid.json()["is_controlled"] is True


def test_export_generates_downloadable_snapshot(client: TestClient) -> None:
    headers = _headers(client, "export@lifesync.mx")

    client.put(
        "/api/v1/medical-profile",
        json={"blood_type": "A", "rh_factor": "POSITIVE"},
        headers=headers,
    )
    client.post(
        "/api/v1/allergies",
        json=_allergy_payload(),
        headers=headers,
    )
    client.post(
        "/api/v1/medications",
        json={
            "name": "Tramadol",
            "dosage": "50",
            "dose_unit": "MG",
            "route": "ORAL",
            "frequency_text": "Cada 8 horas",
            "start_date": "2026-01-01",
            "is_controlled": True,
            "controlled_schedule": "II",
            "prescriber_name": "Dra. Pérez",
            "prescription_number": "ABC1234",
        },
        headers=headers,
    )
    client.post(
        "/api/v1/emergency-contacts",
        json={
            "full_name": "Ana",
            "relationship": "Madre",
            "phone_primary": "+5215555555555",
            "priority": 0,
        },
        headers=headers,
    )

    created = client.post(
        "/api/v1/emergency-exports",
        json={"format": "JSON"},
        headers=headers,
    )
    assert created.status_code == 201, created.text
    export = created.json()
    assert export["status"] == "READY"
    assert export["record_count"] == 4
    assert export["strategy"] == "json_medical"
    assert "storage_key" not in export
    assert "download_token_hash" not in export

    download = client.get(
        f"/api/v1/emergency-exports/{export['id']}/download",
        headers=headers,
    )
    assert download.status_code == 200
    assert download.headers["content-type"].startswith("application/json")
    assert download.headers["x-content-sha256"] == export["content_sha256"]

    payload = json.loads(download.content)
    assert payload["patient"]["full_name"] == "Paciente Test"
    assert payload["profile"]["blood_type"] == "A"
    assert payload["allergies"][0]["allergen_name"] == "Penicilina"
    assert payload["medications"][0]["prescription_number"] == "***34"
    assert payload["emergency_contacts"][0]["priority"] == 0

    other = _headers(client, "other-export@lifesync.mx")
    assert (
        client.get(
            f"/api/v1/emergency-exports/{export['id']}/download", headers=other
        ).status_code
        == 404
    )

    revoked = client.post(
        f"/api/v1/emergency-exports/{export['id']}/revoke", headers=headers
    )
    assert revoked.status_code == 200
    assert revoked.json()["status"] == "REVOKED"
    assert (
        client.get(
            f"/api/v1/emergency-exports/{export['id']}/download", headers=headers
        ).status_code
        == 404
    )
