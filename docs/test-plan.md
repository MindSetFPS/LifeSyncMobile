# Esquema formal de pruebas de software — Sprint 1

## Pirámide de pruebas

| Nivel | Objeto | Herramienta | Estado |
|---|---|---|---|
| Unitario (backend) | `security.hash_password`, `decode_token`, servicios | pytest | 14/14 ✅ |
| Integración (backend) | Endpoints + DB real (SQLite temporal) + llaves RSA efímeras | FastAPI `TestClient` | incluido arriba |
| Unitario (móvil) | Casos de uso y `AuthRepositoryImpl` con dobles | JUnit4 + Truth + Turbine + `kotlinx-coroutines-test` | escrito, requiere Android SDK/Gradle |
| Contrato (móvil↔API) | DTOs y mappings | pruebas de repositorio con `FakeAuthApiService` | escrito |
| UI / navegación | Flujo autenticado vs no autenticado | Compose Test (sprint 2) | planificado |
| Seguridad | Firma RS256, expiración, manipulación de token, hash | pytest (ver tabla inferior) | ✅ |

## Casos cubiertos (backend)

| Prueba | Verificación |
|---|---|
| `test_health` | Disponibilidad del servicio |
| `test_register_does_not_leak_password` | La respuesta no expone password/hash |
| `test_password_is_stored_only_as_bcrypt_hash` | DB contiene hash `$2`, nunca texto plano |
| `test_register_validates_payload` | 422 ante password corto / correo inválido |
| `test_register_rejects_duplicate_email` | 409 ante correo duplicado |
| `test_login_returns_rs256_signed_tokens` | Header `alg=RS256`, payload verificado |
| `test_login_rejects_wrong_password` | 401 + `WWW-Authenticate: Bearer` |
| `test_me_requires_bearer_token` | Ruta protegida sin token → 401 |
| `test_me_returns_profile_with_valid_token` | Perfil correcto con JWT válido |
| `test_me_rejects_tampered_token` | Token manipulado → 401 |
| `test_access_token_cannot_be_used_as_refresh` | Separación de tipos de token |
| `test_refresh_rotates_valid_tokens` | Rotación de access token |
| `test_expired_token_is_rejected` | Token expirado → 401 |

## Ejecución

```bash
# Backend (entorno aislado)
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e ".[test]"
.venv/bin/python -m pytest

# Móvil (requiere Android SDK 35 + JDK 17)
cd mobile
gradle wrapper --gradle-version 8.11.1
./gradlew testDebugUnitTest
./gradlew assembleDebug
```

## Criterios de aceptación para el merge

1. `pytest` en verde (0 fallos).
2. `./gradlew testDebugUnitTest` en verde.
3. Sin secretos, llaves `.pem`, `.env` ni `.db` versionados.
4. PR aprobado por el Scrum Master y CI en verde (GitHub Actions).
5. Cobertura mínima del 80% en `core/security.py` y `services/auth_service.py` (sprint 2).
