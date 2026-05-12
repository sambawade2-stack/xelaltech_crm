#!/bin/sh
set -e

echo "[entrypoint] Attente de la base de données..."
python manage.py wait_for_db

echo "[entrypoint] Application des migrations..."
python manage.py migrate --noinput

echo "[entrypoint] Création de la table de cache..."
python manage.py createcachetable 2>/dev/null || true

echo "[entrypoint] Démarrage de Gunicorn sur 0.0.0.0:8000..."
exec gunicorn config.wsgi:application --config /app/gunicorn.conf.py
