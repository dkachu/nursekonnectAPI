"""Test settings."""

from __future__ import annotations

from .base import *  # noqa: F403
from .base import env

SECRET_KEY = "test-secret-key-with-at-least-thirty-two-bytes"
DEBUG = False
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": env("POSTGRES_TEST_DB", env("POSTGRES_DB", "nursekonnect")),
        "USER": env("POSTGRES_TEST_USER", env("POSTGRES_USER", "nursekonnect")),
        "PASSWORD": env("POSTGRES_TEST_PASSWORD", env("POSTGRES_PASSWORD", "nursekonnect")),
        "HOST": env("POSTGRES_TEST_HOST", "localhost"),
        "PORT": env("POSTGRES_TEST_PORT", "5433"),
    }
}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "nursekonnect-tests",
    }
}
