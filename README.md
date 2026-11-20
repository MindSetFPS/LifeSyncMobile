# LifeSync Mobile

Solución móvil multiplataforma de asistencia e historial médico de emergencia.
Este repositorio contiene el **Sprint 1**: arquitectura limpia, autenticación
OAuth 2.0 con JWT firmado y almacenamiento seguro por hardware.

```
backend/   API FastAPI (Singleton DB, OAuth2, JWT RS256, bcrypt)
mobile/    Cliente Kotlin nativo (Clean Architecture, Compose, Hilt, Keystore)
docs/      Arquitectura, seguridad, pruebas, GitFlow, release, sprints
scripts/   Generación de llaves RSA y helper GitFlow
```

## Inicio rápido

```bash
# Backend
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e ".[test]"
python ../scripts/generate_keys.py keys           # genera backend/keys/*.pem
.venv/bin/uvicorn app.main:app --reload            # http://localhost:8000/docs

# Pruebas
.venv/bin/python -m pytest
```

El emulador Android alcanza el backend en `http://10.0.2.2:8000/api/v1/`
(valor por defecto en `mobile/app/build.gradle.kts`). Si el puerto 8000 está
ocupado, se puede redirigir la compilación sin editar código:

```bash
./gradlew assembleDebug -Plifesync.apiBaseUrl=http://10.0.2.2:8001/api/v1/
```

## GitFlow

Consultar `docs/gitflow.md`. Rama activa de trabajo:
`feature/sprint-1-auth-architecture` → `develop` → `main`.

## Estado

Sprint 1 ✅ · Sprints 2-4 planificados en `docs/sprint-plan.md`.
