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

Artefactos esperados:

```
mobile/app/build/outputs/apk/release/app-release-unsigned.apk
mobile/app/build/outputs/bundle/release/app-release.aab
```

## 4. Firma (simulada)

- En producción se requiere un **Android upload key** (`.jks`) guardado en un
  secreto del CI, **nunca** en el repositorio.
- Se configura `signingConfigs` en `app/build.gradle.kts` leyendo variables
  `LIFESYNC_KEYSTORE_*` inyectadas por GitHub Secrets.
- Google Play App Signing custodia la llave de aplicación; se sube el **AAB**.

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
- [ ] Firma real y subida a Play Console (requiere credenciales del propietario)
- [ ] Pruebas UI/instrumentadas (Sprint 2)

## 7. Notas de versión 0.1.0 (Sprint 1)

- Autenticación remota OAuth 2.0 con JWT firmado RS256 (RSA-4096).
- Contraseñas almacenadas solo como hash bcrypt saltado.
- JWT persistido en Android Keystore mediante `EncryptedSharedPreferences`.
- Arquitectura limpia por capas y navegación protegida (grafo autenticado/no autenticado).
- API centralizada con conexión Singleton y renovación automática de tokens.
- Verificación en emulador: login, perfil, persistencia de sesión y logout.
- Pruebas: 14/14 backend (pytest), 9/9 móvil (JUnit JVM).
