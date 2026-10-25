#!/usr/bin/env bash
# Publishes static sites from ~/staging to /var/www and sets up Nginx + HTTPS.
# Run on the server as mylab:  sudo bash ~/Myfreelab/deploy/deploy_sites.sh
# Safe to re-run.
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Run with sudo: sudo bash $0" >&2
  exit 1
fi

OWNER_HOME="/home/mylab"
STAGING="$OWNER_HOME/staging"
EMAIL="alex2180369@gmail.com"
SITES="robotex salon club psy"

for name in $SITES; do
  host="$name.myfreelab.ru"
  src="$STAGING/$name"
  dst="/var/www/$host"

  [ -d "$src" ] || { echo "Missing $src" >&2; exit 1; }

  # 1. Files
  mkdir -p "$dst"
  find "$dst" -mindepth 1 -delete
  cp -r "$src"/. "$dst"/
  chown -R root:root "$dst"
  find "$dst" -type d -exec chmod 755 {} +
  find "$dst" -type f -exec chmod 644 {} +

  # 2. Nginx (HTTP only; certbot adds the HTTPS block)
  conf="/etc/nginx/sites-available/$host"
  if [ ! -e "$conf" ]; then
    cat > "$conf" <<EOF
server {
    listen 80;
    server_name $host;
    root $dst;
    index index.html;

    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    gzip on;
    gzip_types text/css application/javascript image/svg+xml text/plain;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location ~* \.(?:css|js|webp|jpg|jpeg|png|svg|woff2)\$ {
        expires 30d;
        add_header Cache-Control "public";
        add_header X-Content-Type-Options "nosniff" always;
    }
}
EOF
  fi
  ln -sf "$conf" "/etc/nginx/sites-enabled/$host"
done

nginx -t
systemctl reload nginx

# 3. HTTPS certificates (skips hosts that already have one)
for name in $SITES; do
  host="$name.myfreelab.ru"
  if [ ! -d "/etc/letsencrypt/live/$host" ]; then
    certbot --nginx -d "$host" --non-interactive --agree-tos -m "$EMAIL" --redirect
  fi
done

nginx -t
systemctl reload nginx

for name in $SITES; do
  host="$name.myfreelab.ru"
  printf "%s -> " "$host"
  curl -sS -o /dev/null -w "%{http_code}\n" "https://$host/" || true
done
