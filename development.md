# Development Guide

## Prerequisites

- Python 3.12+
- Docker Desktop
- PostgreSQL/PostGIS through Docker Compose
- Redis through Docker Compose

## Environment

Create `.env` from `.env.example` for Docker-based development.

For local Django commands, run from `backend/` and use `core.settings`.
The default environment mode is `DJANGO_ENV=local`.

```powershell
cd backend
..\.venv\Scripts\python.exe manage.py check
..\.venv\Scripts\python.exe -m pytest
```

## Tooling

```powershell
..\.venv\Scripts\python.exe -m ruff check .
..\.venv\Scripts\python.exe -m black --check .
```

## Database

The default database engine is PostGIS:

```text
django.contrib.gis.db.backends.postgis
```

Local database services are expected to run through Docker Compose.
