#!/usr/bin/env bash
# Helper de GitFlow para LifeSync Mobile.
# Uso: ./scripts/gitflow.sh feature|release|hotfix <nombre>
set -euo pipefail

KIND="${1:-}"
NAME="${2:-}"

start_feature() {
  git fetch origin --prune
  git checkout develop
  git pull --ff-only origin develop
  git checkout -b "feature/${NAME}" develop
  echo "Rama creada: feature/${NAME}  ->  PR a develop (aprobación del Scrum Master)."
}

start_release() {
  git fetch origin --prune
  git checkout develop
  git pull --ff-only origin develop
  git checkout -b "release/${NAME}" develop
  echo "Rama creada: release/${NAME}. Bump de versión; PR a main Y a develop."
}

start_hotfix() {
  git fetch origin --prune
  git checkout main
  git pull --ff-only origin main
  git checkout -b "hotfix/${NAME}" main
  echo "Rama creada: hotfix/${NAME}. PR a main Y a develop."
}

case "$KIND" in
  feature) [[ -n "$NAME" ]] || { echo "Uso: $0 feature <nombre>"; exit 1; }; start_feature ;;
  release) [[ -n "$NAME" ]] || { echo "Uso: $0 release <versión>"; exit 1; }; start_release ;;
  hotfix)  [[ -n "$NAME" ]] || { echo "Uso: $0 hotfix <nombre>"; exit 1; }; start_hotfix ;;
  *) echo "Uso: $0 {feature|release|hotfix} <nombre>"; exit 1 ;;
esac
