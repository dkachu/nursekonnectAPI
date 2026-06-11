# NurseKonnect Backend

Django REST Framework backend for NurseKonnect. This foundation contains the production-ready project structure, custom email-only user model, PostGIS database configuration, Redis cache configuration, Celery wiring, JWT settings, Docker support, and test/tooling configuration.

Business workflows are intentionally not implemented in this phase.

## Local Commands

```powershell
cd backend
..\.venv\Scripts\python.exe manage.py check
..\.venv\Scripts\python.exe -m pytest
```

## Settings

- Django settings module: `core.settings`
- Local mode: `DJANGO_ENV=local`
- Test mode: `DJANGO_ENV=test`
- Production mode: `DJANGO_ENV=production`
