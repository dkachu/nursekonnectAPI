FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=core.settings \
    DJANGO_ENV=production

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        binutils \
        curl \
        gdal-bin \
        libgdal-dev \
        libgeos-dev \
        libpq-dev \
        libproj-dev \
        netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt requirements/production.txt requirements/dev.txt /app/requirements/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements/production.txt

COPY . /app

RUN groupadd --system nursekonnect \
    && useradd --system --gid nursekonnect --home-dir /app nursekonnect \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R nursekonnect:nursekonnect /app \
    && chmod +x /app/docker/entrypoint.sh

USER nursekonnect

ENTRYPOINT ["sh", "/app/docker/entrypoint.sh"]
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]

FROM base AS validation

USER root
RUN pip install --no-cache-dir -r requirements/dev.txt
USER nursekonnect

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz/', timeout=3).read()"

FROM base AS runtime

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz/', timeout=3).read()"
