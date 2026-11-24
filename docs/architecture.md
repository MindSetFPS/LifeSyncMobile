# Arquitectura de LifeSync Mobile — Sprint 1

## Visión general

```
                ┌──────────────────────────┐        HTTPS / OAuth2
   Kotlin App  ─▶│  FastAPI (API central)   │◀── JWT RS256
  (Clean Arch)  │  Singleton DB + Servicios│
                └───────────┬──────────────┘
                            ▼
                     SQLite (async)
```

## Backend (FastAPI)

| Capa | Responsabilidad | Archivo |
|---|---|---|
| Configuración | Variables centralizadas, `lru_cache` (Singleton) | `backend/app/core/config.py` |
| Persistencia | `DatabaseManager` Singleton, engine + `async_sessionmaker` | `backend/app/core/database.py` |
| Modelo | `User` con `hashed_password` (sin texto plano) | `backend/app/models/user.py` |
| Esquemas | Validación Pydantic (EmailStr, longitud de contraseña) | `backend/app/schemas/auth.py` |
| Repositorio | Único acceso a la tabla `users` | `backend/app/repositories/user_repository.py` |
| Servicio | Registro, autenticación, emisión/renovación de tokens | `backend/app/services/auth_service.py` |
| API | Rutas OAuth: `/auth/register`, `/auth/token`, `/auth/refresh`, `/auth/revoke`, `/auth/introspect`, `/auth/me` y `/oauth/authorize` | `backend/app/api/v1/routes/` |
| Metadatos | Discovery (`/.well-known/*`) y JWKS | `backend/app/api/well_known.py` |
| Clientes | Registro y autenticación de clientes OAuth | `backend/app/services/client_service.py` |
| Tokens | Emisión, rotación, revocación e introspección | `backend/app/services/token_service.py` |
| Códigos | Authorization Code + PKCE de un solo uso | `backend/app/services/authorization_code_service.py` |
| Seguridad | bcrypt + JWT RS256 (RSA-4096) | `backend/app/core/security.py` |

### Flujos OAuth 2.0 soportados

**a) Authorization Code + PKCE (recomendado, RFC 8252) — app móvil**

1. La app genera `code_verifier`/`code_challenge` (S256) y un `state`.
2. Abre `GET /api/v1/oauth/authorize?...` en el **navegador externo**
   (nunca un WebView), mostrando el dominio real al usuario.
3. El backend valida `client_id` y `redirect_uri` contra el registro y
   presenta una página de consentimiento. El estado del flujo viaja firmado
   en una cookie `HttpOnly` (protección CSRF).
4. Tras el login, redirige a `com.lifesync.mobile://oauth2callback?code=...&state=...`.
5. La app verifica `state` y canja el código en `/auth/token` con
   `grant_type=authorization_code` y el `code_verifier`. El código es de un
   solo uso, expira en 60 s y está atado a `client_id` + `redirect_uri`.

**b) Resource Owner Password (heredado de Sprint 1)**

1. `POST /api/v1/auth/register` → hash bcrypt del password, respuesta sin credenciales.
2. `POST /api/v1/auth/token` con `grant_type=password`
   (`username`, `password`, `scope` opcional) → `access_token` + `refresh_token`.
3. `GET /api/v1/auth/me` con `Authorization: Bearer <JWT>` → perfil.

**c) Refresh con rotación**

- `POST /api/v1/auth/token` con `grant_type=refresh_token` (estándar) o
  `POST /api/v1/auth/refresh` (compatibilidad Sprint 1).
- Los refresh tokens son **opacos**, se guardan solo como hash SHA-256 y
  se rotan en cada uso. Reutilizar uno ya rotado revoca la **familia completa**
  (RFC 6819 §5.2.2.3).

**d) Revocación e introspección**

- `POST /api/v1/auth/revoke` (RFC 7009): revoca la familia del refresh token.
  Siempre responde 200, exista o no el token.
- `POST /api/v1/auth/introspect` (RFC 7662): devuelve `active` y metadatos del JWT.

### Descubrimiento y verificación

| Endpoint | Estándar |
|---|---|
| `/.well-known/oauth-authorization-server` | RFC 8414 |
| `/.well-known/openid-configuration` | OpenID Connect Discovery |
| `/.well-known/jwks.json` | RFC 7517 (llave pública RS256, `kid` en la cabecera JWT) |

## Cliente Kotlin (arquitectura limpia por capas)

```
presentation/  ViewModels + Compose (UI state, eventos)
     │
domain/        Modelos, repositorio (interfaz), casos de uso
     │
data/          Retrofit/DTOs, interceptores, repositorio, almacenamiento cifrado
     │
core/          Resource<T>, contrato TokenStorage
```

Flujo de una petición:

```
LoginScreen -> AuthViewModel -> LoginUseCase -> AuthRepositoryImpl
     -> AuthApiService (Retrofit, suspend) -> AuthInterceptor
     -> SecureTokenStorage (Android Keystore) -> JWT guardado
     -> isAuthenticated: StateFlow -> AppNavigation (Grafo "main")
```

### Patrones aplicados

- **Singleton**: `DatabaseManager` (backend) y `settings` (`lru_cache`).
- **Repository**: abstracción de la fuente de datos en ambas plataformas.
- **Use Case**: una operación de negocio por clase, inyectable con `@Inject`.
- **Dependency Injection**: FastAPI `Depends` / Hilt `@Module` + `@Binds`.
- **Interceptor + Authenticator**: inyección del Bearer y refresh concurrente seguro (`Mutex`).
- **Protected navigation**: dos gráficos independientes (`auth_graph`, `main_graph`) con `popUpTo(inclusive = true)`.
- **Resource<T>**: resultado tipado `Success / Error / Loading` — sin excepciones en la UI.

## Async

Backend: `async def` + SQLAlchemy async (`aiosqlite`). Móvil: corrutinas `suspend`,
`viewModelScope`, `Flow`/`StateFlow` y `collectAsStateWithLifecycle`.
