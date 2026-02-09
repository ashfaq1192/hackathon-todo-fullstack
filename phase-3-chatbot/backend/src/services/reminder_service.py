"""
Reminder service for scheduling task reminders via Dapr Jobs API.

When a task with a due_date is created or updated, this service schedules
a reminder job via Dapr. The job triggers the notification-service at the
scheduled time to send a notification to the user.

For local development without Dapr, reminders are logged but not scheduled.
"""

import logging
import os
from datetime import datetime, UTC

import httpx

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
DAPR_ENABLED = os.getenv("DAPR_ENABLED", "false").lower() == "true"


async def schedule_reminder(task_id: int, task_title: str, due_date: datetime, user_id: str) -> bool:
    """Schedule a reminder for a task using Dapr Jobs API.

    Args:
        task_id: The task's database ID
        task_title: Task title for notification display
        due_date: When to trigger the reminder
        user_id: Owner of the task

    Returns:
        True if scheduled successfully, False otherwise
    """
    if not DAPR_ENABLED:
        logger.debug(f"Dapr disabled, skipping reminder schedule for task {task_id}")
        return False

    job_name = f"reminder-task-{task_id}"

    # Calculate the schedule time (ISO 8601)
    schedule_time = due_date.isoformat()

    job_data = {
        "data": {
            "task_id": task_id,
            "task_title": task_title,
            "user_id": user_id,
            "due_date": schedule_time,
            "scheduled_at": datetime.now(UTC).isoformat(),
        },
        "schedule": schedule_time,
        "repeats": 1,
    }

    url = f"{DAPR_BASE_URL}/v1.0-alpha1/jobs/{job_name}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.put(url, json=job_data)
            if response.status_code in (200, 201, 204):
                logger.info(f"Scheduled reminder for task {task_id} at {schedule_time}")
                return True
            else:
                logger.warning(f"Failed to schedule reminder ({response.status_code}): {response.text}")
                return False
    except httpx.ConnectError:
        logger.debug(f"Dapr sidecar not reachable, skipping reminder for task {task_id}")
        return False
    except Exception as e:
        logger.error(f"Reminder scheduling error for task {task_id}: {e}")
        return False


async def cancel_reminder(task_id: int) -> bool:
    """Cancel a scheduled reminder for a task.

    Args:
        task_id: The task's database ID

    Returns:
        True if cancelled successfully, False otherwise
    """
    if not DAPR_ENABLED:
        return False

    job_name = f"reminder-task-{task_id}"
    url = f"{DAPR_BASE_URL}/v1.0-alpha1/jobs/{job_name}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.delete(url)
            if response.status_code in (200, 204):
                logger.info(f"Cancelled reminder for task {task_id}")
                return True
            elif response.status_code == 404:
                logger.debug(f"No reminder found for task {task_id}")
                return True
            else:
                logger.warning(f"Failed to cancel reminder ({response.status_code})")
                return False
    except httpx.ConnectError:
        logger.debug(f"Dapr sidecar not reachable, skipping reminder cancel for task {task_id}")
        return False
    except Exception as e:
        logger.error(f"Reminder cancel error for task {task_id}: {e}")
        return False
