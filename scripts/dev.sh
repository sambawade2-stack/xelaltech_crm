#!/bin/bash
set -e
echo "=== FinTrack CRM — Démarrage développement ==="
docker compose up -d db redis
echo "Attente base de données..."
sleep 3
python manage.py migrate
python manage.py seed_data
python manage.py runserver
