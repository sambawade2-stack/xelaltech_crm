#!/bin/sh
set -e

echo "[entrypoint] Attente de la base de données..."
python manage.py wait_for_db 2>/dev/null || sleep 5

echo "[entrypoint] Application des migrations..."
python manage.py migrate --noinput

echo "[entrypoint] Démarrage de Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
