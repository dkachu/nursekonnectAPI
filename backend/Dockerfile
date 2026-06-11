FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=core.settings \
    DJANGO_ENV=production

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        binutils \
        gdal-bin \
        libgdal-dev \
        libproj-dev \
        netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/production.txt requirements/base.txt /app/requirements/
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
