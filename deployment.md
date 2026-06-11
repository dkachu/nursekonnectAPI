# Deployment Guide

## Runtime Services

- Django API served by Gunicorn
- Nginx reverse proxy
- PostgreSQL with PostGIS
- Redis
- Celery worker
- Celery Beat

## Production Settings

Use `core.settings` with `DJANGO_ENV=production` and configure all secrets through environment variables.

Required production controls:

- `DJANGO_DEBUG=false`
- strong `DJANGO_SECRET_KEY`
- restricted `DJANGO_ALLOWED_HOSTS`
- HTTPS at Nginx or upstream load balancer
- private PostgreSQL and Redis networking
- persistent PostgreSQL backups

## Release Flow

1. Build the backend image.
2. Run tests.
3. Apply migrations.
4. Collect static files.
5. Start Gunicorn, Celery worker, and Celery Beat.
6. Verify `/healthz/`.
7. Monitor logs, queue depth, database connectivity, and error rates.
