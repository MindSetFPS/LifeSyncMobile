# Simulación de liberación — LifeSync Mobile v0.1.0 (Sprint 1)

> Simulación: no se generan binarios reales ni se sube a tiendas. Documenta el
> procedimiento reproducible y sus comprobaciones.

## 1. Versionado

- SemVer `0.1.0`: `0.x` (pre-1.0), `1` (Sprint 1), `0` (parche).
- `versionName = "0.1.0-sprint1"`, `versionCode = 1` (`mobile/app/build.gradle.kts`).
- API: `version = "0.1.0"` en `backend/pyproject.toml` y `FastAPI(version=...)`.

## 2. Secuencia GitFlow simulada

```bash
# 1. Cerrar la feature
git add . && git commit -m "feat(sprint-1): arquitectura, auth OAuth2/JWT y almacenamiento seguro"
git push -u origin feature/sprint-1-auth-architecture
# PR feature/... -> develop (aprobación Scrum Master + CI verde)

# 2. Release
./scripts/gitflow.sh release 0.1.0
# bump de versión; PR release/0.1.0 -> main  y  release/0.1.0 -> develop

# 3. Tag y merge a main
git tag -a v0.1.0 -m "LifeSync Mobile 0.1.0 - Sprint 1"
git push origin v0.1.0
```

## 3. Compilación y pruebas previas al paquete

```bash
cd backend && .venv/bin/python -m pytest                      # 14/14
cd ../mobile && ./gradlew clean testDebugUnitTest assembleRelease bundleRelease
```

Con el keystore configurado (ver sección 4), los artefactos son:

```
mobile/app/build/outputs/apk/release/app-release.apk          # firmado
mobile/app/build/outputs/bundle/release/app-release.aab       # firmado
```

Sin keystore disponible (desarrollo local / PRs), la variante release se genera
sin firmar y no debe subirse a la tienda.

## 4. Firma (real) — paso a paso

La firma se declara en `mobile/app/build.gradle.kts` (`signingConfigs.release`) y
se activa solo si existe el keystore indicado en `LIFESYNC_KEYSTORE_FILE`. Lee
estas variables de entorno:

| Variable | Contenido |
|---|---|
| `LIFESYNC_KEYSTORE_FILE` | Ruta al `.jks` de upload |
| `LIFESYNC_KEYSTORE_PASSWORD` | Contraseña del keystore |
| `LIFESYNC_KEY_ALIAS` | Alias de la llave |
| `LIFESYNC_KEY_PASSWORD` | Contraseña de la llave |

Sin keystore, la variante release se compila **sin firmar** y no sirve para la
tienda. El keystore **nunca** se versiona (`.gitignore` excluye `*.jks`,
`*.keystore` y `keystore.properties`).

### 4.1 Crear la llave de upload (solo una vez)

```bash
mkdir -p ~/.keys
export JAVA_HOME=/home/daniel/.local/share/jdks/temurin-21
"$JAVA_HOME/bin/keytool" -genkeypair -v -keystore ~/.keys/lifesync-upload.jks -alias lifesync -keyalg RSA -keysize 4096 -validity 10000 -dname "CN=LifeSync, OU=Mobile, O=LifeSync, L=CDMX, ST=CDMX, C=MX"
```

`keytool` pedirá:

1. `Enter keystore password:` → escribe y anota la contraseña.
2. `Re-enter new password:` → repítela.
3. `Enter key password for <lifesync>` → pulsa **Enter** (usa la misma).

Queda creado `~/.keys/lifesync-upload.jks`. **No borres el archivo ni olvides la
contraseña.**

### 4.2 Compilar el AAB firmado en local

```bash
export LIFESYNC_KEYSTORE_FILE="$HOME/.keys/lifesync-upload.jks"
export LIFESYNC_KEYSTORE_PASSWORD='TU_CONTRASEÑA'
export LIFESYNC_KEY_ALIAS='lifesync'
export LIFESYNC_KEY_PASSWORD='TU_CONTRASEÑA'
```

```bash
cd mobile
JAVA_HOME=/home/daniel/.local/share/jdks/temurin-21 ./gradlew clean bundleRelease
```

El artefacto firmado queda en
`mobile/app/build/outputs/bundle/release/app-release.aab`. Para comprobarlo:

```bash
"$JAVA_HOME/bin/jarsigner" -verify app/build/outputs/bundle/release/app-release.aab
```

Debe imprimir `jar verified.` (si dice `jar is unsigned`, faltan las variables).

### 4.3 Configurar GitHub para que el CI lo haga solo

**a)** Convierte la llave a texto base64:

```bash
base64 -w0 ~/.keys/lifesync-upload.jks > ~/.keys/keystore.b64
cat ~/.keys/keystore.b64
```

Copia la línea completa que imprime.

**b)** En GitHub: repo → **Settings** → **Secrets and variables** → **Actions** →
**New repository secret**. Crea estos cuatro:

| Secret | Contenido |
|---|---|
| `LIFESYNC_KEYSTORE_BASE64` | lo copiado del `cat` de `keystore.b64` |
| `LIFESYNC_KEYSTORE_PASSWORD` | contraseña del keystore |
| `LIFESYNC_KEY_ALIAS` | `lifesync` |
| `LIFESYNC_KEY_PASSWORD` | contraseña de la llave |

**c)** Lanza el build de release de una de estas dos formas:

- Push de un tag:
```bash
git tag -a v0.1.0 -m "LifeSync Mobile 0.1.0"
git push origin v0.1.0
```
- O en GitHub: **Actions** → `CI - LifeSync Mobile` → **Run workflow**.

**d)** Al terminar, descarga el artefacto `lifesync-release-aab` de la ejecución.
Ese es el `.aab` firmado que se sube a Google Play Console.

### 4.4 Qué hace el job `release` (`.github/workflows/ci.yml`)

Restaura el keystore desde `LIFESYNC_KEYSTORE_BASE64`, compila `bundleRelease` con
las variables de firma, verifica el resultado con `jarsigner` (falla si el AAB
no está firmado) y publica `app-release.aab` como artefacto. Google Play App
Signing custodia la llave de aplicación; al Play Console se sube el **AAB**
firmado con la upload key.

### 4.5 iOS (.ipa): pendiente

El repositorio solo contiene la app Android nativa (Kotlin); no existe proyecto
Xcode. El `.ipa` requiere crear la app iOS, una cuenta Apple Developer y un
runner macOS con certificado de distribución.

## 5. Publicación simulada en tiendas

| Paso | Resultado esperado |
|---|---|
| Crear app en Play Console | Paquete `com.lifesync.mobile` |
| Subir AAB firmado | Track interno (alpha) |
| Metadatos | Título "LifeSync Mobile", categoría Salud, descripción del Sprint 1 |
| Política de privacidad | URL obligatoria; declara cifrado local y JWT |
| Permisos declarados | Solo `INTERNET` |
| Revisión | "Listo para publicación" en track interno |
| Rollback | Promoción de la versión anterior desde "Historial de versiones" |

## 6. Checklist de salida (Go/No-Go)

- [x] CI en verde (`pytest` + `testDebugUnitTest`)
- [x] Sin secretos/llaves en el repositorio
- [x] Doble pila de navegación protegida
- [x] Token JWT solo en Keystore (nunca `SharedPreferences` plano)
- [x] Mensajes de error sin información sensible
- [x] Firma de release configurada (`signingConfigs` + job CI)
- [ ] Subida a Play Console (requiere credenciales del propietario)
- [ ] Pruebas UI/instrumentadas (Sprint 2)

## 7. Notas de versión 0.1.0 (Sprint 1)

- Autenticación remota OAuth 2.0 con JWT firmado RS256 (RSA-4096).
- Contraseñas almacenadas solo como hash bcrypt saltado.
- JWT persistido en Android Keystore mediante `EncryptedSharedPreferences`.
- Arquitectura limpia por capas y navegación protegida (grafo autenticado/no autenticado).
- API centralizada con conexión Singleton y renovación automática de tokens.
- Verificación en emulador: login, perfil, persistencia de sesión y logout.
- Pruebas: 14/14 backend (pytest), 9/9 móvil (JUnit JVM).
