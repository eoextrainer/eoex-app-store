#!/bin/bash
# git-auto-workflow.sh
# Usage: ./git-auto-workflow.sh "commit message"
# This script saves, stashes, stages, commits, pushes, and merges changes through ready -> qa -> prod -> main.

set -e

READY_BRANCH="ready"
QA_BRANCH="qa"
PROD_BRANCH="prod"
MAIN_BRANCH="main"
REPO_URL="git@github.com:eoextrainer/eoex-app-store.git"

# Save VS Code workspace state
code --add .

echo "Checking out $READY_BRANCH..."
git checkout $READY_BRANCH

echo "Stashing local changes (if any)..."
git stash save "Auto-stash before workflow $(date)" || true

echo "Pulling latest changes from $READY_BRANCH..."
git pull --rebase origin $READY_BRANCH

echo "Applying stashed changes (if any)..."
git stash pop || true

echo "Staging all changes..."
git add .

if [ -z "$1" ]; then
  msg="chore: update $(date +'%Y-%m-%d %H:%M')"
else
  msg="$1"
fi

echo "Committing changes..."
git commit -m "$msg" || echo "No changes to commit."

echo "Pushing to $READY_BRANCH..."
git push origin $READY_BRANCH

# Merge ready -> qa
echo "Merging $READY_BRANCH into $QA_BRANCH..."
git checkout $QA_BRANCH
git pull origin $QA_BRANCH
git merge $READY_BRANCH --no-edit
git push origin $QA_BRANCH

# Merge qa -> prod
echo "Merging $QA_BRANCH into $PROD_BRANCH..."
git checkout $PROD_BRANCH
git pull origin $PROD_BRANCH
git merge $QA_BRANCH --no-edit
git push origin $PROD_BRANCH

# Merge prod -> main
echo "Merging $PROD_BRANCH into $MAIN_BRANCH..."
git checkout $MAIN_BRANCH
git pull origin $MAIN_BRANCH
git merge $PROD_BRANCH --no-edit
git push origin $MAIN_BRANCH

echo "Workflow complete. All changes have been merged up to main."
echo "Visit: https://github.com/eoextrainer/eoex-app-store/pulls to open or review PRs if needed."
