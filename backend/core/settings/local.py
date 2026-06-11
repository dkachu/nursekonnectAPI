"""Local development settings."""

from __future__ import annotations

from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": env("POSTGRES_DB", "nursekonnect"),  # noqa: F405
        "USER": env("POSTGRES_USER", "nursekonnect"),  # noqa: F405
        "PASSWORD": env("POSTGRES_PASSWORD", "nursekonnect"),  # noqa: F405
        "HOST": env("POSTGRES_HOST", "localhost"),  # noqa: F405
        "PORT": env("POSTGRES_PORT", "5432"),  # noqa: F405
        "CONN_MAX_AGE": env_int("POSTGRES_CONN_MAX_AGE", 60),  # noqa: F405
    }
}
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
