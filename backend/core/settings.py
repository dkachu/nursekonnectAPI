"""Django settings for the NurseKonnect project."""

from __future__ import annotations

import os
import sys
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(BASE_DIR / ".env")


def env(name: str, default: str | None = None) -> str | None:
    """Read an environment variable."""
    return os.environ.get(name, default)


def env_bool(name: str, default: bool = False) -> bool:
    """Read a boolean environment variable."""
    value = env(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int) -> int:
    """Read an integer environment variable."""
    value = env(name)
    if value is None:
        return default
    return int(value)


def env_list(name: str, default: str = "") -> list[str]:
    """Read a comma-separated environment variable."""
    value = env(name, default)
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


RUNNING_TESTS = any("pytest" in argument or argument == "test" for argument in sys.argv)
DJANGO_ENV = env("DJANGO_ENV", "test" if RUNNING_TESTS else "local")

SECRET_KEY = env("DJANGO_SECRET_KEY", "unsafe-local-development-key")
MEDICAL_DATA_FERNET_KEY = env("MEDICAL_DATA_FERNET_KEY")
DEBUG = env_bool("DJANGO_DEBUG", DJANGO_ENV == "local")
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.gis",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "apps.common",
    "apps.accounts",
    "apps.patients",
    "apps.nurses",
    "apps.requests",
    "apps.tracking",
    "apps.visits",
    "apps.ratings",
    "apps.notifications",
    "apps.audit_logs",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

if DJANGO_ENV == "test":
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
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.contrib.gis.db.backends.postgis",
            "NAME": env("POSTGRES_DB", "nursekonnect"),
            "USER": env("POSTGRES_USER", "nursekonnect"),
            "PASSWORD": env("POSTGRES_PASSWORD", "nursekonnect"),
            "HOST": env("POSTGRES_HOST", "localhost"),
            "PORT": env("POSTGRES_PORT", "5432"),
            "CONN_MAX_AGE": env_int("POSTGRES_CONN_MAX_AGE", 60),
        }
    }

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
NCK_LICENSE_STATUS_URL = env(
    "NCK_LICENSE_STATUS_URL",
    "https://osp.nckenya.com/LicenseStatus",
)
MAX_LOCATION_AGE_MINUTES = env_int("MAX_LOCATION_AGE_MINUTES", 15)
NEARBY_NURSE_RADIUS_KM = env_int("NEARBY_NURSE_RADIUS_KM", 100)
NEARBY_NURSE_CANDIDATE_LIMIT = env_int("NEARBY_NURSE_CANDIDATE_LIMIT", 50)
MATCHING_NOTIFICATION_BATCH_SIZE = env_int("MATCHING_NOTIFICATION_BATCH_SIZE", 5)
MATCHING_RADIUS_STEPS_KM = [
    int(item) for item in env("MATCHING_RADIUS_STEPS_KM", "10,20,50,100").split(",") if item
]
REQUEST_OFFER_EXPIRY_MINUTES = env_int("REQUEST_OFFER_EXPIRY_MINUTES", 2)
TRACKING_MIN_INTERVAL_SECONDS = env_int("TRACKING_MIN_INTERVAL_SECONDS", 30)
TRACKING_MAX_INTERVAL_SECONDS = env_int("TRACKING_MAX_INTERVAL_SECONDS", 60)
ARRIVAL_VERIFICATION_DISTANCE_METERS = env_int("ARRIVAL_VERIFICATION_DISTANCE_METERS", 100)
JOURNEY_WARNING_AFTER_MINUTES = env_int("JOURNEY_WARNING_AFTER_MINUTES", 30)
JOURNEY_CANCEL_AFTER_MINUTES = env_int("JOURNEY_CANCEL_AFTER_MINUTES", 60)
OSRM_BASE_URL = env("OSRM_BASE_URL", "http://router.project-osrm.org")
OSRM_REQUEST_TIMEOUT_SECONDS = env_int("OSRM_REQUEST_TIMEOUT_SECONDS", 5)

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": env_int("DRF_PAGE_SIZE", 20),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": env("DRF_ANON_THROTTLE_RATE", "100/hour"),
        "user": env("DRF_USER_THROTTLE_RATE", "1000/hour"),
        "auth_register": env("DRF_AUTH_REGISTER_THROTTLE_RATE", "10/hour"),
        "auth_login": env("DRF_AUTH_LOGIN_THROTTLE_RATE", "20/hour"),
        "auth_refresh": env("DRF_AUTH_REFRESH_THROTTLE_RATE", "60/hour"),
        "auth_logout": env("DRF_AUTH_LOGOUT_THROTTLE_RATE", "60/hour"),
        "otp_verify": env("DRF_OTP_VERIFY_THROTTLE_RATE", "10/hour"),
        "otp_resend": env("DRF_OTP_RESEND_THROTTLE_RATE", "5/hour"),
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env_int("JWT_ACCESS_MINUTES", 15)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env_int("JWT_REFRESH_DAYS", 7)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

REDIS_URL = env("REDIS_URL", "redis://localhost:6379/0")
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

CELERY_BROKER_URL = env("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = env_int("CELERY_TASK_TIME_LIMIT_SECONDS", 1800)
CELERY_TASK_DEFAULT_QUEUE = "default"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_ROUTES = {
    "apps.notifications.*": {"queue": "notifications"},
    "apps.audit_logs.*": {"queue": "audit"},
    "apps.requests.tasks.*": {"queue": "matching"},
}

CORS_ALLOWED_ORIGINS = env_list("DJANGO_CORS_ALLOWED_ORIGINS")
CORS_ALLOW_CREDENTIALS = True

AUTH_REFRESH_COOKIE_NAME = env("AUTH_REFRESH_COOKIE_NAME", "nursekonnect_refresh")
AUTH_REFRESH_COOKIE_PATH = env("AUTH_REFRESH_COOKIE_PATH", "/api/auth/")
AUTH_REFRESH_COOKIE_SAMESITE = env("AUTH_REFRESH_COOKIE_SAMESITE", "Lax")
AUTH_REFRESH_COOKIE_SECURE = env_bool("AUTH_REFRESH_COOKIE_SECURE", DJANGO_ENV == "production")

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
CROSS_ORIGIN_OPENER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

if DJANGO_ENV == "local":
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

if DJANGO_ENV == "test":
    SECRET_KEY = "test-secret-key-with-at-least-thirty-two-bytes"
    DEBUG = False
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
    REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"].update(
        {
            "anon": "10000/hour",
            "user": "10000/hour",
            "auth_register": "10000/hour",
            "auth_login": "10000/hour",
            "auth_refresh": "10000/hour",
            "auth_logout": "10000/hour",
            "otp_verify": "10000/hour",
            "otp_resend": "10000/hour",
        }
    )

if DJANGO_ENV == "production":
    if SECRET_KEY == "unsafe-local-development-key":
        raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set in production.")
    if MEDICAL_DATA_FERNET_KEY is None:
        raise ImproperlyConfigured("MEDICAL_DATA_FERNET_KEY must be set in production.")
    DEBUG = False
    SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    AUTH_REFRESH_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
