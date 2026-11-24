# LifeSync Mobile

# PROYECTO INTEGRADOR DE UN MES: LIFESYNC MOBILE

## Asignatura: Desarrollo Móvil Integral

### Metodología de Trabajo: Scrum en Equipos de 4 a 5 integrantes

### Método de Evaluación: Demostración técnica 100% presencial en laptops por estaciones de trabajo.

## Objetivo del Proyecto

Diseñar, codificar, probar y simular la liberación de una solución móvil multiplataforma de asistencia e historial médico de emergencia llamada "LifeSync Mobile". La aplicación implementará de forma nativa patrones de diseño arquitectónicos, principios avanzados de criptografía de hardware, consumo e inyección asíncrona de datos en la nube, control riguroso de permisos en tiempo de ejecución, y un esquema formal de pruebas de software antes de generar el paquete final de distribución para las tiendas virtuales.

## CRONOGRAMA DE SPRINTS (PLAN DE TRABAJO DE 4 SEMANAS)

### Semana 1: Sprint 1 – Planeación, Arquitectura e Identidad Blindada (Cubre la Unidad I y bases de la Unidad II)

Meta del Sprint: Establecer el marco de versionamiento, la estructura de directorios de la app, el modelado del backend y un sistema de
autenticación remota asíncrono con persistencia local cifrada por hardware.

    • Entregables del Backend:

        o Configuración del API centralizada (Node.js/FastAPI) aplicando el patrón Singleton para la conexión a la base de datos.

        o Endpoint de autenticación remota que valide credenciales e implemente el flujo de OAuth 2.0 regresando un token JWT firmado criptográficamente.

    • Entregables del Frontend Móvil:

        o Configuración de la plataforma de control de versiones con la estrategia GitFlow y ramificación restrictiva (PRs aprobados por el Scrum Master).

        o Esquematización de una arquitectura limpia por capas y flujos de navegación protegidos (separación estricta de pilas de pantallas para usuarios autenticados y no autenticados).

    • Controles de Codificación Segura y Privacidad:

        o Queda estrictamente prohibido guardar contraseñas en texto plano o cifrado simple en la base de datos.

        o La app móvil debe almacenar el token JWT utilizando contenedores seguros basados en hardware nativo: Expo SecureStore o Flutter Secure Storage (abstrayendo Keystore y Keychain).

# Semana 2: Sprint 2 – Core de Historial Clínico y Protección contra Inyecciones (Cubre la Unidad II)

# Meta del Sprint: Desarrollar los servicios de envío y consumo asíncrono de datos sensibles de salud, garantizando la sanitización de payloads y la mitigación de brechas lógicas en la nube.

    • Entregables del Backend:
        o Endpoints protegidos por middleware para operaciones CRUD de registros de salud (Alergias, tipo de sangre, medicamentos controlados y contactos de emergencia).
        o Implementación de validación de esquemas en el servidor (Zod o class-validator) para bloquear ataques de inyección SQL/NoSQL en la base de datos central.
    • Entregables del Frontend Móvil:
        o Interfaz con componentes dinámicos y adaptables para capturar el perfil del paciente.
        o Configuración de un Interceptor HTTP Global en el cliente móvil que extraiga el JWT del contenedor seguro e inyecte automáticamente la cabecera Authorization: Bearer <JWT> en cada petición de red.

    • Controles de Codificación Segura y Privacidad:
        o Validación sintáctica en formularios locales del teléfono antes del envío para optimizar rendimiento.
        o Mitigación obligatoria de vulnerabilidades de Referencia

# Directa Insegura a Objetos (IDOR) en el servidor: la nube debe validar que el request.auth.uid sea el legítimo dueño del registro médico que se intenta leer o editar.

Semana 3: Sprint 3 – Gestión de Alertas, Sensores Nativos y Manejo de Estados (Cubre las Unidades I, II y III)

Meta del Sprint: Enlazar las capacidades de hardware del dispositivo para la atención de incidentes mediante máquinas de estados y optimizar el diseño lógico de software.

    • Entregables del Backend:

        o Implementación del patrón de diseño Strategy enfocado en la exportación del historial clínico de emergencia. El servidor en la nube debe procesar los metadatos y transformarlos bajo demanda a formatos diferenciados (JSON para sistemas médicos o CSV para aseguradoras).

    • Entregables del Frontend Móvil:

        o Implementación del patrón de diseño Observer asociado a un módulo de alertas médicas locales que se activen cuando el teléfono detecte anomalías o recordatorios de medicamentos críticos.

        o Mapeo teórico y práctico de una Máquina de Estados para gestionar la solicitud asíncrona de permisos de hardware.

    • Controles de Codificación Segura y Privacidad:

        o Configuración declarativa obligatoria en los archivos raíz (AndroidManifest.xml / Info.plist) para restringir el uso de sensores: Cámara (para escanear recetas) y GPS (para la geolocalización del incidente).

        o Implementación de Degradación Gradual de Funcionalidades (Graceful Degradation): si el usuario deniega el permiso de GPS, la app no debe lanzar un crash; debe deshabilitar únicamente el rastreo en la nube y permitir el funcionamiento offline del historial clínico.

Semana 4: Sprint 4 – Suite de Pruebas, Hardening y Paquetes de Distribución (Cubre la Unidad III)

Meta del Sprint: Ejecutar la auditoría estática del software, compilar variantes de producción limpias y generar los artefactos criptográficamente firmados exigidos por las tiendas.

• Entregables del Equipo:

o Suite de Pruebas Unitarias (Jest o PyTest) con cobertura sobre las funciones lógicas del parseo de datos y validaciones de tokens.

o Configuración del firewall del sistema operativo mediante el archivo Network Security Config en Android (cleartextTrafficPermitted="false") o NSAppTransportSecurity en iOS para bloquear tajantemente cualquier petición de red HTTP que no viaje cifrada por TLS/HTTPS.
    o Ejecución de un Análisis Estático de Seguridad (SAST) sobre las dependencias para descartar llaves expuestas (hardcoded secrets) y vulnerabilidades críticas conocidos en librerías de terceros (npm audit / Snyk).

    o Generación de los archivos de distribución oficiales firmados con llaves privadas en modo Release: Android App Bundle (.aab) para Google Play Store y el paquete .ipa para Apple App Store.
DINÁMICA DE EVALUACIÓN EN EL AULA (PROTOCOLO PRESENCIAL)

La demostración final emulará el ecosistema de entrega de una empresa de ingeniería de software profesional dividida en 3 estaciones físicas obligatorias:
• Estación 1: Backend, Nube y Seguridad del Servidor (Laptop 1): El Lead Backend Engineer demostrará el servidor en vivo. Realizará pruebas desde Postman enviando payloads corruptos
    o IDs alterados de otros usuarios para comprobar que las reglas de la nube bloquean inyecciones e IDORs. Se abrirá la base de datos (pgAdmin/Compass) para validar que las contraseñas no sean legibles.

• Estación 2: App Móvil, Interfaz y Simulación de Fallas (Laptop 2 y Smartphones):

El Lead Frontend y el Diseñador UI desplegarán la aplicación en un dispositivo físico. Se evaluará la fluidez visual de la app, el almacenamiento cifrado y la denegación de permisos en tiempo de ejecución. Prueba de fuego en vivo: El docente ordenará activar el "Modo Avión" en el teléfono para evaluar si la app maneja la desconexión asíncrona de la nube sin sufrir crasheos.

• Estación 3: Scrum Master, QA y Auditoría de Código (Laptop 3):

El DevSecOps proyectará el tablero ágil (Jira/Trello) para demostrar la correspondencia de las Historias de Usuario con el trabajo entregado. Abrirá el repositorio en GitHub/GitLab para validar el historial de Pull Requests firmadas y ejecutará en vivo la suite de pruebas unitarias y el reporte SAST de dependencias.

Finalmente, mostrará el archivo ejecutable firmado final (.aab o .ipa) listo para la tienda.

REPARTO DE PUNTUACIÓN DE LA RÚBRICA

1. Arquitectura, Patrones y Flujo Ágil (25%): Separación real de entornos, uso de GitFlow y transiciones correctas en el tablero Scrum de Jira. Evidencia clara de los patrones Singleton, Strategy y Observer.

2. Codificación Segura y Criptografía (25%): Contraseñas con hashing asíncrono fuerte, tokens resguardados en hardware seguro, deshabilitación de tráfico cleartext y control de IDORs en el servidor.

3. Core de Negocio y Sensores Nativos (20%): Funcionamiento correcto del historial clínico, carga de imágenes, alertas locales y la máquina de estados para la degradación asíncrona de los permisos del S.O..

4. Suite de Pruebas y Calidad (15%): Ejecución exitosa de pruebas unitarias automatizadas y código alineado a principios SOLID sin strings confidenciales expuestas en los manifiestos ni en los componentes.

5. Plan de Liberación y Artefactos (15%): Documentación del proceso de auditoría estática y la entrega del archivo binario comprimido de distribución final compilado en modo Release listo para tiendas oficiales.

---

Solución móvil multiplataforma de asistencia e historial médico de emergencia.
Este repositorio contiene el **Sprint 1**: arquitectura limpia, autenticación
OAuth 2.0 con JWT firmado y almacenamiento seguro por hardware.

```
backend/   API FastAPI (Singleton DB, OAuth 2.0, JWT RS256, bcrypt)
mobile/    Cliente Kotlin nativo (Clean Architecture, Compose, Hilt, Keystore)
docs/      Arquitectura, seguridad, pruebas, GitFlow, release, sprints
scripts/   Llaves RSA, alta de clientes OAuth y helper GitFlow
```

## OAuth 2.0

El backend implementa OAuth 2.0 con `Authorization Code + PKCE`, refresh tokens
con rotación y detección de reutilización, revocación, introspección y
descubrimiento:

| Capacidad | Endpoint | RFC |
|---|---|---|
| Metadatos | `/.well-known/oauth-authorization-server` | 8414 |
| Llave pública | `/.well-known/jwks.json` | 7517 |
| Autorización + PKCE | `GET/POST /api/v1/oauth/authorize` | 6749 / 7636 / 8252 |
| Token (todos los grants) | `POST /api/v1/auth/token` | 6749 |
| Revocación | `POST /api/v1/auth/revoke` | 7009 |
| Introspección | `POST /api/v1/auth/introspect` | 7662 |

El password grant del Sprint 1 se conserva por compatibilidad; el flujo
recomendado para la app es Authorization Code + PKCE en el navegador externo.
Registro de clientes adicionales:

```bash
python scripts/register_oauth_client.py --client-id mi-web --name "Mi Web" \
    --redirect-uri https://app.example/callback --scope "read" --confidential
```

## Inicio rápido

```bash
# Backend
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e ".[test]"
python ../scripts/generate_keys.py keys           # genera backend/keys/*.pem
.venv/bin/uvicorn app.main:app --reload            # http://localhost:8000/docs

# Pruebas
.venv/bin/python -m pytest
```

El emulador Android alcanza el backend en `http://10.0.2.2:8000/api/v1/`
(valor por defecto en `mobile/app/build.gradle.kts`). Si el puerto 8000 está
ocupado, se puede redirigir la compilación sin editar código:

```bash
./gradlew assembleDebug -Plifesync.apiBaseUrl=http://10.0.2.2:8001/api/v1/
```

Guía paso a paso para levantar el backend y correr la app en el emulador:
[`docs/run_app.md`](docs/run_app.md).

## GitFlow

Consultar `docs/gitflow.md`. Rama activa de trabajo:
`feature/sprint-1-auth-architecture` → `develop` → `main`.

## Estado

Sprint 1 ✅ · Sprints 2-4 planificados en `docs/sprint-plan.md`.
