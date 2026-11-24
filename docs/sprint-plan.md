# Cronograma de sprints — LifeSync Mobile (4 semanas)

| Sprint | Semana | Meta | Entregables clave | Estado |
|---|---|---|---|---|
| 1 | 1 | Planeación, arquitectura e identidad blindada | GitFlow, API Singleton, OAuth2 + JWT RS256, Clean Architecture, Keystore, navegación protegida, 14 pruebas | ✅ Completado |
| 2 | 2 | Historial médico y permisos en runtime | Modelo `MedicalRecord`, cifrado local de datos sensibles, solicitud de permisos (cámara/almacenamiento/biometría), UI de historial | ⏳ Planificado |
| 3 | 3 | Consumo e inyección asíncrona de datos en la nube | Sincronización bidireccional offline-first, WorkManager, manejo de conflictos, stream de datos | ⏳ Planificado |
| 4 | 4 | Calidad, endurecimiento y liberación | Pruebas UI/instrumentadas, auditoría de seguridad, firma, AAB, simulación de despliegue en tiendas | ⏳ Planificado |

## Sprint 1 — Detalle (Unidad I + bases de la Unidad II)

**Backend**
- [x] Configuración centralizada (`Settings` con `lru_cache`).
- [x] `DatabaseManager` Singleton con SQLAlchemy async + `aiosqlite`.
- [x] Endpoint de registro con hash bcrypt (sin texto plano).
- [x] Endpoint OAuth 2.0 `/auth/token` con JWT firmado RS256 (RSA-4096).
- [x] Endpoints `/auth/me` y `/auth/refresh`.

**OAuth 2.0 extendido (post-Sprint 1)**
- [x] Registro de clientes con `redirect_uri` y scopes permitidos.
- [x] Authorization Code + PKCE (`/oauth/authorize`, un solo uso, S256).
- [x] Refresh tokens opacos con rotación y detección de reutilización.
- [x] Revocación (RFC 7009) e introspección (RFC 7662).
- [x] Discovery (RFC 8414), OpenID Discovery y JWKS (RFC 7517).
- [x] Cliente Kotlin: flujo PKCE en navegador externo + revocación al cerrar sesión.

**Frontend móvil**
- [x] GitFlow con ramificación restrictiva (`main`/`develop`/`feature`/`release`/`hotfix`).
- [x] Arquitectura limpia por capas (`domain` / `data` / `presentation` / `core`).
- [x] Navegación protegida: `auth_graph` vs `main_graph`.
- [x] Consumo asíncrono (Retrofit `suspend` + corrutinas + `Flow`).

**Seguridad y privacidad**
- [x] Prohibición de contraseñas en texto plano/cifrado simple.
- [x] JWT en `EncryptedSharedPreferences` respaldado por Android Keystore.
- [x] Sin tráfico cleartext salvo el emulador de desarrollo.

**Pruebas**
- [x] 46 pruebas backend en verde (14 de Sprint 1 + 32 del flujo OAuth).
- [x] Pruebas unitarias móviles de repositorio y PKCE.

## Definition of Done

PR aprobado por el Scrum Master · CI verde · sin secretos versionados ·
documentación actualizada · artefacto de release simulado.
