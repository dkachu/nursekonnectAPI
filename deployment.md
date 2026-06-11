# NurseKonnect Deployment Runbook

## Required Stack

- Docker and Docker Compose
- Python 3.12 runtime inside the backend image
- PostgreSQL 16 with PostGIS
- Redis 7
- Gunicorn
- Nginx reverse proxy
- Celery worker and Celery beat

## Required Production Environment

```text
DJANGO_SETTINGS_MODULE=core.settings
DJANGO_ENV=production
DJANGO_SECRET_KEY=<long random secret>
MEDICAL_DATA_FERNET_KEY=<Fernet key>
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=<api host>
DJANGO_CSRF_TRUSTED_ORIGINS=https://<api host>
DJANGO_CORS_ALLOWED_ORIGINS=https://<frontend host>
DJANGO_SECURE_SSL_REDIRECT=true
POSTGRES_DB=<database>
POSTGRES_USER=<user>
POSTGRES_PASSWORD=<password>
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
OSRM_BASE_URL=<private OSRM endpoint>
```

## Build

```bash
docker compose build
```

## Deploy

```bash
docker compose up -d
```

The backend entrypoint waits for PostgreSQL, applies migrations when `RUN_MIGRATIONS=true`, and collects static files when `COLLECT_STATIC=true`.

## Smoke Checks

```bash
docker compose ps
docker compose exec -T backend python manage.py check --deploy
curl -fsS http://localhost:8000/healthz/
curl -fsS http://localhost:8000/api/schema/
docker compose exec -T backend celery -A core inspect ping
docker compose exec -T redis redis-cli ping
```

Expected:

- API health returns `{"status":"ok"}`.
- Django deploy check has no issues.
- Celery worker replies to `inspect ping`.
- Redis replies `PONG`.

## Database Requirements

- PostGIS extension must be available before migrations.
- Spatial indexes are created by geography `PointField(..., spatial_index=True)`.
- Application models include indexes for status, ownership, freshness, offers, tracking, audit, and soft deletes.

## Rollback

1. Stop new traffic at the load balancer.
2. Restore the previous backend image tag.
3. Restart backend, worker, and beat services.
4. Verify `/healthz/`, Celery ping, Redis ping, and error logs.
5. Restore database backup only if a migration is known to be destructive.

## Production Notes

- Do not expose PostgreSQL or Redis publicly.
- Use TLS at Nginx or an upstream load balancer.
- Keep `DJANGO_SECURE_SSL_REDIRECT=true` behind a correctly configured proxy.
- Rotate `DJANGO_SECRET_KEY` and `MEDICAL_DATA_FERNET_KEY` only with an explicit key-rotation plan.
- Use a private OSRM endpoint before launch.
