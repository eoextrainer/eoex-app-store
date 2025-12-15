#!/usr/bin/env bash
set -euo pipefail

# Copy canonical docker/.env into backend/.env for local development
# Usage: ./scripts/sync_env.sh [source_env_path]

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_SRC="$REPO_ROOT/docker/.env"
SRC=${1:-$DEFAULT_SRC}
DEST="$REPO_ROOT/backend/.env"

if [ ! -f "$SRC" ]; then
  echo "Source env file not found: $SRC" >&2
  exit 1
fi

cp -f "$SRC" "$DEST"
chmod 600 "$DEST"
echo "Copied $SRC -> $DEST (permissions set to 600)."
