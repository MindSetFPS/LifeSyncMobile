# Modelo GitFlow y ramificación restrictiva

## Ramas

| Rama | Origen | Destino de PR | Reglas |
|---|---|---|---|
| `main` | — | — | Producción. Solo PRs desde `release/*` o `hotfix/*`. Protegida. |
| `develop` | `main` | — | Integración. Solo PRs desde `feature/*`, `release/*` o `hotfix/*`. Protegida. |
| `feature/<nombre>` | `develop` | `develop` | 1 rama por historia. Borrada tras el merge. |
| `release/<versión>` | `develop` | `main` **y** `develop` | Solo correcciones de estabilización y bump de versión. |
| `hotfix/<nombre>` | `main` | `main` **y** `develop` | Parche de producción urgente. |

Estado actual: `main` → `develop` → `feature/sprint-1-auth-architecture`.

## Reglas de protección (GitHub → Settings → Branches)

Aplicar a `main` y `develop`:

- ✅ Require a pull request before merging
- ✅ Required approvals: **1** (Scrum Master) — dismissal de aprobaciones obsoletas
- ✅ Require status checks: `Backend (FastAPI)`, `Móvil (Kotlin)`
- ✅ Require branches to be up to date before merging
- ✅ Require linear history / no merge commits (squash o rebase)
- ✅ Do not allow force pushes ni deletions
- ✅ Include administrators

Reglas adicionales:
- `main` solo acepta PRs cuyo `head` empiece por `release/` o `hotfix/`.
- `develop` solo acepta PRs cuyo `head` empiece por `feature/`, `release/` o `hotfix/`.
- Las ramas `feature/*` se eliminan automáticamente tras el merge.

## Helper

```bash
./scripts/gitflow.sh feature nombre-de-la-historia
./scripts/gitflow.sh release 0.1.0
./scripts/gitflow.sh hotfix correccion-jwt
```

## Convención de commits

`<tipo>(<alcance>): <descripción>` — tipos: `feat`, `fix`, `test`, `docs`, `refactor`, `chore`, `ci`.

Ejemplos: `feat(auth): endpoint OAuth2 con JWT RS256`, `test(api): cobertura de tokens expirados`.
