# NurseKonnect Operations Runbook

## Daily Health Checks

```bash
curl -fsS https://<api-host>/healthz/
curl -fsS https://<api-host>/api/schema/
docker compose exec -T backend python manage.py check --deploy
docker compose exec -T backend celery -A core inspect ping
docker compose exec -T redis redis-cli ping
```

## Monitoring Targets

- API 5xx rate
- API latency by endpoint
- PostgreSQL connection count and slow queries
- PostGIS spatial query timing
- Redis memory and eviction count
- Celery queue depth
- Celery task failures and retries
- Auth login failures
- OTP resend/verify spikes
- Medical access logs by actor and patient
- Request auto-cancellations
- OSRM error rate and latency

## Celery Operations

Workers process:

- request matching workflows
- journey warning tasks
- stalled assignment cancellation tasks
- notification workflows
- audit/compliance queue work

Useful commands:

```bash
docker compose exec -T backend celery -A core inspect active
docker compose exec -T backend celery -A core inspect reserved
docker compose exec -T backend celery -A core inspect stats
```

## Redis Operations

Redis is used for:

- Celery broker
- Celery result backend
- Django cache
- DRF throttle state

Useful commands:

```bash
docker compose exec -T redis redis-cli ping
docker compose exec -T redis redis-cli info memory
docker compose exec -T redis redis-cli info stats
```

## PostgreSQL/PostGIS Operations

Recommended checks:

```sql
SELECT PostGIS_Version();
SELECT schemaname, tablename, indexname FROM pg_indexes WHERE schemaname = 'public';
SELECT * FROM pg_stat_activity WHERE state <> 'idle';
```

Spatial query pattern:

- Use PostGIS radius filtering first.
- Route only filtered candidates through OSRM.
- Never rank the entire nurse network in Python.

## Incident Response

### Suspected Medical Data Exposure

1. Disable affected endpoint or revoke affected credentials.
2. Preserve `AuditLog` and `MedicalAccessLog`.
3. Identify actors, patients, resources, timestamps, and IP addresses.
4. Rotate credentials if token compromise is suspected.
5. Prepare patient/admin notification according to legal guidance.

### Celery Backlog

1. Check Redis availability.
2. Inspect active/reserved tasks.
3. Scale worker replicas.
4. Check for failing task retries.
5. Confirm journey warning/cancellation tasks are not delayed beyond SLA.

### OSRM Outage

1. Confirm OSRM health and latency.
2. Matching will skip failed route estimates.
3. Restore private OSRM endpoint.
4. Review unmatched request backlog.

## Backup And Recovery

- Back up PostgreSQL at least daily.
- Test restore into staging regularly.
- Retain audit and medical access logs according to healthcare compliance policy.
- Redis is operational state; PostgreSQL remains the source of truth.

## Release Checklist

- Full test suite passes.
- Coverage is at least 90%.
- `ruff check backend` passes.
- `black --check backend` passes.
- `python manage.py makemigrations --check --dry-run` passes.
- `python manage.py check --deploy` passes with production secrets.
- `/healthz/`, `/api/schema/`, Swagger, and ReDoc load.
- Celery worker responds to ping.
- Redis responds `PONG`.
