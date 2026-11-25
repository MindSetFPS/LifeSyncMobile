# Memory

## Local environment — do not re-download

- Everything needed is already installed. Do not download, install or re-verify JDKs or toolchains unless the user explicitly asks.
- The system `java` is 25 (incompatible with Gradle 8.11.1). Use the existing JDK 21:
  `JAVA_HOME=/home/daniel/.local/share/jdks/temurin-21`
- The Android SDK is already configured in `mobile/local.properties`, and Gradle wrapper 8.11.1 is cached in `~/.gradle`.
- The backend uses the existing virtualenv at `backend/.venv`.

## Commands

- Backend tests: `cd backend && .venv/bin/python -m pytest`
- Mobile unit tests: `cd mobile && JAVA_HOME=/home/daniel/.local/share/jdks/temurin-21 ./gradlew testDebugUnitTest --no-daemon`
