#!/usr/bin/env bash
# Creates the Myfreelab project skeleton in the home directory of mylab.
# Safe to re-run: never overwrites an existing .env.
set -euo pipefail

BASE="$HOME/Myfreelab"
mkdir -p "$BASE"
chmod 700 "$BASE"

# .env: empty template for secrets, filled in manually by the owner.
if [ ! -e "$BASE/.env" ]; then
  : > "$BASE/.env"
fi
chmod 600 "$BASE/.env"

# .env.example: variable names only, no real values.
cat > "$BASE/.env.example" <<'EOF'
# Copy to .env and fill in real values. Never commit .env.
# The variable list will be agreed on with the project owner.
EOF
chmod 644 "$BASE/.env.example"

cat > "$BASE/.gitignore" <<'EOF'
# Secrets
.env
.env.*
!.env.example

# SSH and private keys
ssh/
.ssh/
id_*
!id_*.pub
*.pem
*.key

# Python
__pycache__/
*.py[cod]
.venv/
venv/

# Node / React
node_modules/
dist/
build/

# Streamlit local secrets
.streamlit/secrets.toml

# OS / editors
.DS_Store
.vscode/
.idea/
*.log
EOF
chmod 644 "$BASE/.gitignore"

# Standard ~/.ssh with correct permissions.
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"
touch "$HOME/.ssh/authorized_keys"
chmod 600 "$HOME/.ssh/authorized_keys"

cd "$HOME"
ls -la Myfreelab/
