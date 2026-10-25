#!/usr/bin/env bash
# Makes browsers re-check the HTML of every site on each visit, so updates show up at once.
# CSS, JS, fonts and images keep their long cache (they are versioned in the HTML).
# Run on the server:  sudo bash ~/Myfreelab/deploy/fix_html_cache.sh
# Safe to re-run. If nginx rejects the new config, the old files are restored.
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Run with sudo: sudo bash $0" >&2
  exit 1
fi

STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="/root/nginx-backup-$STAMP"
mkdir -p "$BACKUP"

SITES="myfreelab.ru photo.myfreelab.ru robotex.myfreelab.ru salon.myfreelab.ru club.myfreelab.ru psy.myfreelab.ru"

for site in $SITES; do
  conf="/etc/nginx/sites-available/$site"
  [ -f "$conf" ] || { echo "skip $site (no config)"; continue; }
  if grep -q 'location = /index.html' "$conf"; then
    echo "ok   $site (already patched)"
    continue
  fi
  cp -a "$conf" "$BACKUP/$site"
  python3 - "$conf" <<'PY'
import re, sys
path = sys.argv[1]
text = open(path, encoding="utf-8").read()
block = """    location = /index.html {
        add_header Cache-Control "no-cache" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }

"""
m = re.search(r"^([ \t]*)location / \{", text, re.M)
if not m:
    sys.exit("no 'location / {' found in " + path)
text = text[:m.start()] + block + text[m.start():]
open(path, "w", encoding="utf-8").write(text)
PY
  echo "done $site"
done

if nginx -t; then
  systemctl reload nginx
  echo "nginx reloaded. Backups: $BACKUP"
else
  echo "nginx test FAILED, restoring old configs" >&2
  for f in "$BACKUP"/*; do
    [ -e "$f" ] && cp -a "$f" "/etc/nginx/sites-available/$(basename "$f")"
  done
  nginx -t && systemctl reload nginx
  exit 1
fi

for site in $SITES; do
  printf "%-26s" "$site"
  curl -sSI "https://$site/" | grep -i '^cache-control' | tr -d '\r' || echo "(no header)"
done
