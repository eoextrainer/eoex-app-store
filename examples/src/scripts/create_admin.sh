#!/usr/bin/env bash
set -euo pipefail

# Robust helper script: prints masked DB connection info and creates an admin user via the API
# Usage: ./create_admin.sh [email] [password] [first_name] [last_name] [role] [base_url] [env_file]
# Example: ./create_admin.sh manager@example.com StrongPass123! Admin User manager http://localhost ./docker/.env

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR}/.."

# Accept optional env file path as 7th argument
USER_PROVIDED_ENV=${7:-}

# Candidate env files (searched in order)
declare -a CANDIDATES=(
  "$REPO_ROOT/docker/.env"
  "$REPO_ROOT/backend/.env"
  "$REPO_ROOT/.env"
)

if [ -n "$USER_PROVIDED_ENV" ]; then
  CANDIDATES=("$USER_PROVIDED_ENV" "${CANDIDATES[@]}")
fi

ENV_FILE=""
for f in "${CANDIDATES[@]}"; do
  if [ -f "$f" ]; then
    ENV_FILE="$f"
    break
  fi
done

if [ -z "$ENV_FILE" ]; then
  echo "No .env file found in candidates: ${CANDIDATES[*]}" >&2
  exit 1
fi

echo "Using env file: $ENV_FILE"

# Load env file safely: source it directly (safe as we control the file)
set -o allexport
# shellcheck disable=SC1090
source "$ENV_FILE" 2>/dev/null || true
set +o allexport

# Defaults
EMAIL=${1:-manager@example.com}
PASSWORD=${2:-StrongPass123!}
FIRST_NAME=${3:-Admin}
LAST_NAME=${4:-User}
ROLE=${5:-manager}
BASE_URL=${6:-http://localhost}

echo "--- Connection Info (passwords masked) ---"
echo "DB Host: ${DB_HOST:-mysql}"
echo "DB Port: ${DB_PORT:-3306}"
echo "DB Name: ${DB_NAME:-dunes_cms}"
echo "DB User: ${DB_USER:-dunes_user}"
echo "DB Password: ********"
echo "MySQL Root: ********"
echo "API Base URL: $BASE_URL"
echo "-----------------------------------------"

# Wait for API to be available (retry)
RETRIES=8
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
  exit 2
fi

echo "Creating user: $EMAIL (role: $ROLE)"
RESP_BODY=$(mktemp)
HTTP_STATUS=$(curl -s -w "%{http_code}" -o "$RESP_BODY" -X POST "$BASE_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\",\"first_name\":\"$FIRST_NAME\",\"last_name\":\"$LAST_NAME\",\"role\":\"$ROLE\"}") || true

cat "$RESP_BODY"
echo

if [[ "$HTTP_STATUS" =~ ^2[0-9][0-9]$ ]]; then
  echo "User created successfully (HTTP $HTTP_STATUS)."
  rm -f "$RESP_BODY"
  exit 0
else
  echo "Failed to create user. HTTP status: $HTTP_STATUS" >&2
  echo "Response saved: $RESP_BODY" >&2
  exit 3
fi
