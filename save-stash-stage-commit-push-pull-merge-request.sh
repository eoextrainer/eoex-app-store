#!/bin/bash
# save-stash-stage-commit-push-pull-merge-request.sh
# Usage: ./save-stash-stage-commit-push-pull-merge-request.sh "commit message"

set -e

# Save VS Code workspace state
echo "Saving VS Code workspace..."
code --add .

git status

echo "Stashing local changes (if any)..."
git stash save "Auto-stash before workflow $(date)" || true

echo "Pulling latest changes from current branch..."
git pull --rebase

echo "Applying stashed changes (if any)..."
git stash pop || true

echo "Staging all changes..."
git add .

echo "Committing changes..."
if [ -z "$1" ]; then
  msg="chore: update $(date +'%Y-%m-%d %H:%M')"
else
  msg="$1"
fi
git commit -m "$msg" || echo "No changes to commit."

echo "Pushing to current branch..."
git push

echo "Creating pull/merge request (manual step):"
echo "Visit: https://github.com/eoextrainer/eoex-app-store/pulls to open a PR if needed."
