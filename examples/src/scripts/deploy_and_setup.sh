#!/usr/bin/env bash
set -euo pipefail

# One-command helper: sync env, start compose, wait for health, create admin, open browser
# Usage: ./scripts/deploy_and_setup.sh [email] [password] [first_name] [last_name] [role] [base_url]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR}/.."

EMAIL=${1:-manager@example.com}
PASSWORD=${2:-StrongPass123!}
FIRST_NAME=${3:-Admin}
LAST_NAME=${4:-User}
ROLE=${5:-manager}
BASE_URL=${6:-http://localhost}

echo "1/5 - Syncing env into backend"
"${REPO_ROOT}/scripts/sync_env.sh"

echo "2/5 - Starting docker-compose"
cd "${REPO_ROOT}/docker"
# Check docker access
if ! docker info > /dev/null 2>&1; then
  echo "ERROR: Cannot access Docker daemon. You may need to run this script with sudo or add your user to the 'docker' group and re-login." >&2
  echo "To add your user to the docker group (recommended):" >&2
  echo "  sudo usermod -aG docker \$USER && newgrp docker" >&2
  exit 1
fi

docker compose up -d --build

echo "3/5 - Waiting for API to be healthy"
RETRIES=20
SLEEP=3
OK=1
for i in $(seq 1 $RETRIES); do
  if curl -sSf --connect-timeout 3 "$BASE_URL/api/v1" > /dev/null 2>&1; then
    OK=0
    break
  fi
  echo "API not ready yet (attempt $i/$RETRIES). Retrying in $SLEEP seconds..."
  sleep $SLEEP
done

if [ $OK -ne 0 ]; then
  echo "API not reachable at $BASE_URL/api/v1 after $RETRIES attempts." >&2
  docker compose ps
  docker compose logs --tail 200
  exit 2
fi

echo "4/5 - Creating admin user via API"
cd "${REPO_ROOT}"
./scripts/create_admin.sh "$EMAIL" "$PASSWORD" "$FIRST_NAME" "$LAST_NAME" "$ROLE" "$BASE_URL"

echo "5/5 - Opening application in default browser"
xdg-open "$BASE_URL" || echo "xdg-open failed or not available; please open $BASE_URL in your browser"

echo "Deployment and setup complete."
