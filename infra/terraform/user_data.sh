#!/bin/bash
# Bootstraps the instance: install Docker, fetch the repo, run the prod stack.
set -euxo pipefail

dnf update -y
dnf install -y docker git
systemctl enable --now docker

# Docker Compose v2 plugin.
mkdir -p /usr/local/lib/docker/cli-plugins
curl -fsSL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

cd /opt
git clone "${repo_url}" app
cd app

# Materialise the environment file from the template, injecting secrets.
cp .env.example .env
sed -i "s#^DJANGO_SETTINGS_MODULE=.*#DJANGO_SETTINGS_MODULE=config.settings.prod#" .env
sed -i "s#^DJANGO_DEBUG=.*#DJANGO_DEBUG=False#" .env
sed -i "s#^DJANGO_SECRET_KEY=.*#DJANGO_SECRET_KEY=${django_secret_key}#" .env
sed -i "s#^DJANGO_ALLOWED_HOSTS=.*#DJANGO_ALLOWED_HOSTS=${allowed_hosts}#" .env
sed -i "s#^POSTGRES_PASSWORD=.*#POSTGRES_PASSWORD=${postgres_password}#" .env
# HTTP-only demo box: no TLS terminated here, so skip the HTTPS redirect.
echo "DJANGO_SECURE_SSL_REDIRECT=False" >> .env

docker compose -f docker-compose.prod.yml up --build -d
