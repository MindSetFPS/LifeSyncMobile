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

- `OAuth2PasswordBearer` + dependencia `get_current_user`: rutas protegidas devuelven
  401 con `WWW-Authenticate: Bearer`.
- Mensajes de error genéricos ante credenciales inválidas (evita user enumeration).
- Conflicto de registro devuelve 409 sin revelar si la cuenta está activa.

## 6. Pendiente para sprints Posteriores

- Revocar refresh tokens (lista negra con `jti`), rate limiting, MFA y biometría para
  desbloquear el historial médico, certificados pinning (Certificate Pinning).
