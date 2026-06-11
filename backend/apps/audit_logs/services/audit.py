"""General audit logging service."""

from __future__ import annotations

from typing import Any

from apps.audit_logs.models import AuditLog


class AuditLogService:
    """Persist append-only audit records for sensitive platform actions."""

    def record(
        self,
        *,
        actor: object | None,
        action: str,
        resource: str,
        resource_id: str | int,
        ip_address: str | None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Create an audit log entry."""
        return AuditLog.objects.create(
            actor=actor if getattr(actor, "is_authenticated", False) else None,
            action=action,
            resource=resource,
            resource_id=str(resource_id),
            ip_address=ip_address,
            metadata=metadata or {},
        )
