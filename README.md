# NurseKonnect

NurseKonnect is a fullstack healthcare platform for home-based care in Kenya. This repository is organized with a Django REST Framework backend and a separate frontend workspace.

## Structure

```text
backend/
frontend/
docker/
docker-compose.yml
.env.example
```

The current implementation is the backend foundation only. It includes the Django project structure, custom email-only user model, PostGIS settings, Redis/Celery configuration, JWT/DRF configuration, Docker, Nginx, Ruff, Black, and Pytest setup.

## Backend Smoke Commands

```powershell
cd backend
..\.venv\Scripts\python.exe manage.py check
..\.venv\Scripts\python.exe -m pytest
```

## Docker

```powershell
Copy-Item .env.example .env
docker compose up --build
```
