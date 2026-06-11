"""Celery tasks for care request workflows."""

from __future__ import annotations

from celery import shared_task
from django.conf import settings
from django.db import OperationalError

from apps.requests.workflows import CareRequestWorkflowService


@shared_task(
    bind=True,
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def send_journey_warning_task(self, care_request_id: int) -> dict[str, object]:
    """Send a warning when an accepted nurse has not started journey after 30 minutes."""
    return (
        CareRequestWorkflowService().send_journey_warning(care_request_id=care_request_id).as_dict()
    )


@shared_task(
    bind=True,
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def cancel_stalled_assignment_task(self, care_request_id: int) -> dict[str, object]:
    """Unassign stalled nurse and return request to matching after 60 minutes."""
    return (
        CareRequestWorkflowService()
        .cancel_stalled_assignment(care_request_id=care_request_id)
        .as_dict()
    )


class CareRequestWorkflowScheduler:
    """Schedule delayed care request workflow tasks."""

    def schedule_after_acceptance(self, *, care_request_id: int) -> dict[str, bool]:
        """Schedule warning and auto-cancellation checks after nurse acceptance."""
        if getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False) and not getattr(
            settings, "CELERY_WORKFLOW_SCHEDULE_IN_EAGER", False
        ):
            return {"warning_scheduled": False, "cancellation_scheduled": False}

        send_journey_warning_task.apply_async(
            args=[care_request_id],
            countdown=settings.JOURNEY_WARNING_AFTER_MINUTES * 60,
        )
        cancel_stalled_assignment_task.apply_async(
            args=[care_request_id],
            countdown=settings.JOURNEY_CANCEL_AFTER_MINUTES * 60,
        )
        return {"warning_scheduled": True, "cancellation_scheduled": True}
