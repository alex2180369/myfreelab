#!/usr/bin/env bash
# Runs on the server as mylab. Commits pending changes in ~/repos/<name> and pushes to GitHub.
# Usage: ssh mylab@server 'bash -s' -- <repo-name> "<commit subject>" < push_one.sh
set -uo pipefail

name="$1"; subject="$2"
set -a; . "$HOME/Myfreelab/.env"; set +a
export GIT_ASKPASS="$HOME/repos/askpass.sh" GIT_TERMINAL_PROMPT=0

cd "$HOME/repos/$name" || exit 1
git config user.name "Alexey An"; git config user.email "alex2180369@gmail.com"
git add -A
if git ls-files | grep -E '(^|/)\.env$|\.pem$|(^|/)id_(rsa|ed25519)'; then echo "SECRET FILE STAGED"; exit 1; fi
if ! git diff --cached --quiet; then
  git commit -q -m "$subject" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
fi
git log --oneline | head -5
git push "https://github.com/$GITHUB_USER/$name.git" main 2>&1 | sed "s/$GITHUB_TOKEN/***/g" | tail -3
echo "exit: ${PIPESTATUS[0]}"
