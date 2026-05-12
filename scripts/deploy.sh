#!/bin/bash
set -e

echo "=== FinTrack CRM — Déploiement ==="

# Pull latest code
git pull origin main

# Build and restart
docker compose build --no-cache
docker compose down
docker compose up -d

# Run migrations
docker compose exec web python manage.py migrate --noinput
docker compose exec web python manage.py collectstatic --noinput

echo "=== Déploiement terminé ==="
docker compose ps
