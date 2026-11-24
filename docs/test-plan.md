# Esquema formal de pruebas de software — Sprint 1

## Pirámide de pruebas

| Nivel | Objeto | Herramienta | Estado |
|---|---|---|---|
| Unitario (backend) | `security.hash_password`, `decode_token`, `verify_pkce`, servicios | pytest | 46/46 ✅ |
| Integración (backend) | Endpoints + DB real (SQLite temporal) + llaves RSA efímeras | FastAPI `TestClient` | incluido arriba |
| Unitario (móvil) | Casos de uso, `AuthRepositoryImpl`, PKCE con dobles | JUnit4 + Truth + Turbine + `kotlinx-coroutines-test` | 18/18 ✅ |
| Contrato (móvil↔API) | DTOs y mappings | pruebas de repositorio con `FakeAuthApiService` | ✅ |
| UI / navegación | Flujo autenticado vs no autenticado | Compose Test (sprint 2) | planificado |
| Seguridad | Firma RS256, expiración, manipulación de token, hash, PKCE | pytest (ver tabla inferior) | ✅ |

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

## Casos cubiertos (OAuth 2.0 extendido)

| Prueba | Verificación |
|---|---|
| `test_authorization_server_metadata_is_published` | Endpoints y grants anunciados (RFC 8414) |
| `test_openid_configuration_matches_oauth_metadata` | Consistencia OIDC/OAuth |
| `test_jwks_verifies_issued_tokens` | La JWK pública verifica un JWT real |
| `test_jwks_does_not_leak_private_material` | Solo campos públicos de la JWK |
| `test_access_token_advertises_kid` | Cabecera `kid` presente |
| `test_unknown_client_is_rejected` | `invalid_client` con 401 |
| `test_confidential_client_requires_correct_secret` | Secreto validado con bcrypt |
| `test_confidential_client_accepts_http_basic` | Autenticación Basic RFC 7617 |
| `test_scope_outside_client_allowlist_is_rejected` | `invalid_scope` (400) |
| `test_authorize_requires_pkce` | Sin PKCE → `invalid_request` |
| `test_authorize_rejects_unregistered_redirect_uri` | Anti open-redirect |
| `test_authorization_code_flow_issues_tokens` | Flujo completo con PKCE |
| `test_authorization_code_is_single_use` | Replay del código → `invalid_grant` |
| `test_authorization_code_rejects_wrong_pkce_verifier` | Verifier incorrecto → rechazo |
| `test_authorization_code_rejects_redirect_mismatch` | `redirect_uri` atado al código |
| `test_denied_consent_returns_access_denied` | `error=access_denied` con `state` |
| `test_wrong_password_keeps_consent_page` | No filtra credenciales al redirect |
| `test_refresh_token_rotation_and_reuse_detection` | Reutilización revoca la familia |
| `test_refresh_tokens_are_not_persisted_in_clear` | Solo hash SHA-256 en DB |
| `test_revocation_invalidates_refresh_token` | RFC 7009 |
| `test_revocation_of_unknown_token_still_returns_200` | Idempotencia RFC 7009 §2.2 |
| `test_introspection_reports_active_access_token` | RFC 7662 |
| `test_introspection_reports_inactive_for_garbage` | `active: false` |
| `test_unsupported_grant_type_is_reported` | `unsupported_grant_type` |
| `test_error_response_is_not_cacheable` | `no-store` / `no-cache` |
| `test_me_works_with_authorization_code_token` | Token del flujo PKCE válido |
| `test_password_grant_honours_requested_scope` | Scopes respetados |
| `test_password_grant_without_offline_access_issues_no_refresh` | Sin `offline_access`, sin refresh |

## Casos cubiertos (móvil)

| Prueba | Verificación |
|---|---|
| `PkceTest` | Vector de RFC 7636 Apéndice B, longitud y alfabeto |
| `startAuthorization arma la URL con PKCE S256` | URL con challenge/state correctos |
| `canje del codigo usa el verifier y persiste los tokens` | Verifier correcto + Keystore |
| `un state que no coincide es rechazado` | Protección CSRF |
| `el codigo de autorizacion solo puede canjearse una vez` | Estado consumido |
| `logout revoca el refresh token y limpia el almacenamiento` | RFC 7009 en el cliente |
| `logout limpia el almacenamiento aunque la revocacion falle` | Cierre local garantizado |

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
