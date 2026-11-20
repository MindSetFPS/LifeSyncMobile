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
| API | Rutas `/auth/register`, `/auth/token`, `/auth/refresh`, `/auth/me` | `backend/app/api/v1/routes/auth.py` |
| Seguridad | bcrypt + JWT RS256 (RSA-4096) | `backend/app/core/security.py` |

### Flujo OAuth 2.0 (password grant)

1. `POST /api/v1/auth/register` → hash bcrypt del password, respuesta sin credenciales.
2. `POST /api/v1/auth/token` con `application/x-www-form-urlencoded`
   (`username`, `password`, `grant_type=password`) → `access_token` + `refresh_token`.
3. `GET /api/v1/auth/me` con `Authorization: Bearer <JWT>` → perfil.
4. `POST /api/v1/auth/refresh` → rota los tokens.

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
