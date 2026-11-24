# Controles de codificación segura y privacidad — Sprint 1

## 1. Contraseñas

- **Prohibido** guardar contraseñas en texto plano o con cifrado reversible simple.
- El backend persiste únicamente `hashed_password` generado con **bcrypt** (salt aleatorio,
  `rounds=12`, coste adaptativo). Se aplica pre-hash SHA-256 + Base64 para evitar el límite
  de 72 bytes de bcrypt.
- La verificación usa `bcrypt.checkpw` (comparación en tiempo constante).
- Las respuestas de la API (`UserOut`) nunca incluyen el hash ni la contraseña.
- Validación: mínimo 8 caracteres, `EmailStr` en registro.

## 2. Llaves y JWT

- Par de llaves **RSA-4096** generado por `scripts/generate_keys.py` (privada `0600`).
- Algoritmo **RS256**: firma asimétrica. El cliente solo necesita la llave pública;
  la privada nunca se envía ni se versiona (`backend/keys/*.pem` en `.gitignore`).
- Claims obligatorios: `sub`, `iat`, `exp`, `jti`, `type`, `scope`.
- Access token: 15 min. Refresh token: 7 días. Distinción por claim `type` para evitar
  confusión de tokens (verificado en `decode_token`).
- `decode_token` valida firma, expiración y claims requeridos.

## 3. Almacenamiento en el dispositivo (Kotlin)

- `SecureTokenStorage` usa **EncryptedSharedPreferences** con `MasterKey` AES-256-GCM
  alojado en el **Android Keystore** (respaldado por hardware/TEE cuando disponible).
- Claves cifradas con AES256-SIV y valores con AES256-GCM.
- Equivale a Expo SecureStore / Flutter Secure Storage, pero de forma nativa.
- `android:allowBackup="false"` evita que los tokens se incluyan en backups.
- `HttpLoggingInterceptor` en `BASIC` (debug) / `NONE` (release): nunca registra
  cabeceras `Authorization` ni cuerpos con credenciales.

## 4. Permisos en tiempo de ejecución

- Sprint 1 solicita únicamente `android.permission.INTERNET` (permiso normal,
  concedido automáticamente al instalar).
- Tráfico cleartext deshabilitado por defecto; se exceptúa solo `10.0.2.2` (emulador
  de desarrollo) mediante `network_security_config.xml`. Producción exige HTTPS/TLS.

## 5. Protección de la API

- `BearerAuthMiddleware` valida firma, expiración y `type=access` de toda ruta
  bajo `/api/v1` antes de llegar al router. Las rutas ausentes o con token
  inválido devuelven 401 con `WWW-Authenticate: Bearer`.
- Lista blanca del middleware: `/health`, documentación, `/.well-known/*`,
  `/api/v1/auth/{register,token,refresh,revoke,introspect}` y
  `/api/v1/oauth/authorize` (validan sus propias credenciales o cookies).
- `get_current_user` reutiliza el payload validado por el middleware y carga el
  usuario activo; si se invoca sin middleware (pruebas unitarias) valida el
  token con `OAuth2PasswordBearer` como respaldo.
- La propiedad del recurso (anti-IDOR) se verifica en los repositorios, que
  filtran siempre por el `user_id` del token; un recurso ajeno responde 404.
- Mensajes de error genéricos ante credenciales inválidas (evita user enumeration).
- Conflicto de registro devuelve 409 sin revelar si la cuenta está activa.

## 6. OAuth 2.0 endurecido

- **Clientes registrados**: la tabla `oauth_clients` define `redirect_uri`
  permitidos y scopes autorizados. `redirect_uri` se compara de forma
  **exacta** (no por prefijo), lo que bloquea redirecciones abiertas.
- **Clientes públicos vs confidenciales**: la app nativa es un cliente
  público sin secreto y se apoya en PKCE. Los clientes de servidor guardan
  `client_secret` solo como hash bcrypt y pueden autenticarse con HTTP Basic
  (RFC 7617) o en el cuerpo.
- **Authorization Code + PKCE**: `code_challenge_method` debe ser `S256`;
  el código es de un solo uso, expira en 60 s y está atado a `client_id` y
  `redirect_uri`. El `code_verifier` nunca viaja en el redirect.
- **Anti-CSRF**: el estado del flujo (`client_id`, `redirect_uri`, `scope`,
  PKCE, `state`) viaja firmado en una cookie `HttpOnly` + `SameSite=Lax`; el
  POST de consentimiento solo acepta el estado de esa cookie.
- **Navegador externo**: el flujo se abre con `Intent.ACTION_VIEW`, nunca en
  un WebView (RFC 8252 §8.12), para que el usuario vea el dominio real.
- **Rotación de refresh tokens**: los tokens son opacos, se persisten solo
  como hash SHA-256. Reutilizar un token ya rotado **revoca la familia
  completa** (detección de robo, RFC 6819 §5.2.2.3).
- **Revocación real**: `POST /auth/revoke` (RFC 7009) invalida los refresh
  tokens pendientes; el logout de la app lo invoca y luego limpia el Keystore.
- **Introspección**: `POST /auth/introspect` (RFC 7662) permite a un recurso
  verificar el token y obtener `scope`/`client_id`.
- **Scopes**: el servidor valida los scopes solicitados contra la lista del
  cliente y los emite en el claim `scope` del JWT; un cliente no puede pedir
  un scope que no tenga autorizado (`invalid_scope`). Los endpoints de recurso
  de Sprint 2 podrán exigirlos con la dependencia `require_scope`.
- **Descubrimiento**: `/.well-known/oauth-authorization-server` (RFC 8414) y
  `/.well-known/jwks.json` (RFC 7517) publican únicamente material público.
  Los JWT llevan `kid` para permitir la rotación de llaves sin romper clientes.
- **Respuestas de error**: RFC 6749 §5.2 (`error`, `error_description`) con
  `Cache-Control: no-store` y `Pragma: no-cache`.

## 7. Pendiente para sprints posteriores

- Rate limiting y bloqueo por intentos fallidos (recomendado en `/auth/token`).
- MFA / biometría para desbloquear el historial médico.
- Certificate pinning.
- `id_token` (OpenID Connect) si se requiere identidad federada.
- Persistir el `state` PKCE cifrado en disco para sobrevivir al cierre del
  proceso; hoy vive solo en memoria y el flujo se reinicia.
