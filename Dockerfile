FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Bake static files into image (whitenoise sert directement depuis l'app)
RUN SECRET_KEY=build-dummy-key \
    DB_NAME=dummy DB_USER=dummy DB_PASSWORD=dummy DB_HOST=localhost DB_PORT=3306 \
    REDIS_URL=redis://localhost:6379/0 \
    ALLOWED_HOSTS=localhost \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    python manage.py collectstatic --noinput --clear 2>/dev/null || true

RUN mkdir -p /app/logs /app/media && \
    addgroup --system django && \
    adduser --system --ingroup django django && \
    chown -R django:django /app

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER django

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
