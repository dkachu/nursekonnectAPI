#!/usr/bin/env sh
set -eu

if [ -n "${POSTGRES_HOST:-}" ]; then
  until nc -z "$POSTGRES_HOST" "${POSTGRES_PORT:-5432}"; do
    echo "Waiting for PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT:-5432}..."
    sleep 2
  done
fi

if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
  python manage.py migrate --noinput
fi

if [ "${COLLECT_STATIC:-false}" = "true" ]; then
  python manage.py collectstatic --noinput
fi

exec "$@"
