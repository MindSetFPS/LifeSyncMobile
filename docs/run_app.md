# Ejecutar la app en el emulador de Android

Guía de comandos para levantar el backend y correr la app móvil dentro del
emulador. Se usan dos terminales: una para el servidor y otra para el emulador
y la app.

## Requisitos (una sola vez)

- **JDK 21** en `~/.local/share/jdks/temurin-21` (el `java` del sistema es JDK 25
  y Gradle 8.11 no lo soporta).
- **Android SDK** en `~/Android/Sdk`.
- **AVD** llamado `LifeSync` (Pixel 7, API 35).

Comprobar que existen:

```bash
~/.local/share/jdks/temurin-21/bin/java -version
"$HOME/Android/Sdk/emulator/emulator" -list-avds
```

Si falta el AVD, crearlo (descarga plataforma + imagen de sistema):

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export JAVA_HOME="$HOME/.local/share/jdks/temurin-21"
SDK="$ANDROID_HOME/cmdline-tools/latest/bin"
yes | "$SDK/sdkmanager" "platforms;android-35" "system-images;android-35;google_apis;x86_64" "platform-tools" "emulator"
echo no | "$SDK/avdmanager" create avd -n LifeSync -k "system-images;android-35;google_apis;x86_64" -d pixel_7
```

## 1. Backend (Terminal 1)

```bash
cd backend
.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Las llaves RSA se generan solas en `backend/keys/` al arrancar.
- Comprobación rápida: `curl http://127.0.0.1:8000/health` → `{"status":"ok",...}`
- Documentación interactiva: <http://localhost:8000/docs>

Si aún no existe el entorno virtual:

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## 2. Emulador (Terminal 2)

```bash
"$HOME/Android/Sdk/emulator/emulator" -avd LifeSync -gpu auto &
```

Esperar a que aparezca la pantalla de inicio del emulador.

## 3. Compilar, instalar y abrir la app (Terminal 2)

```bash
cd mobile
export JAVA_HOME="$HOME/.local/share/jdks/temurin-21"
export ANDROID_HOME="$HOME/Android/Sdk"
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n com.lifesync.mobile/.MainActivity
```

Atajo en una sola línea (desde `mobile/`):

```bash
JAVA_HOME="$HOME/.local/share/jdks/temurin-21" ANDROID_HOME="$HOME/Android/Sdk" \
  ./gradlew assembleDebug && adb install -r app/build/outputs/apk/debug/app-debug.apk \
  && adb shell am start -n com.lifesync.mobile/.MainActivity
```

## Notas y solución de problemas

- **`JAVA_HOME` es obligatorio** para Gradle; sin él falla con
  `Unsupported class file major version`. Exportarlo una vez por terminal:
  `export JAVA_HOME="$HOME/.local/share/jdks/temurin-21"`.
- La app alcanza el backend en `http://10.0.2.2:8000/api/v1/` (alias del
  `localhost` de la máquina visto desde el emulador).
- Si el puerto 8000 está ocupado, redirigir la URL sin tocar código:
  `./gradlew assembleDebug -Plifesync.apiBaseUrl=http://10.0.2.2:8001/api/v1/`
- Mensaje **"System UI isn't responding"** tras un arranque en frío: pulsar
  **Wait**; es normal mientras el emulador termina de estabilizarse.
- Ver logs de la app en vivo: `adb logcat --pid=$(adb shell pidof com.lifesync.mobile)`
- Reinstalar tras cambios de código: repetir solo `./gradlew assembleDebug` +
  `adb install -r ...`.
- Detener el emulador: `adb emu kill`.
