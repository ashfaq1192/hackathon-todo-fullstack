"""
Event publisher for Dapr Pub/Sub integration.

Publishes task lifecycle events to Kafka topics via the Dapr sidecar HTTP API.
When Dapr is not available (local dev), events are logged but not published.

Topics:
  - task-events: All CRUD operations (create, update, complete, delete)
  - reminders: Scheduled when tasks have due_date set
  - task-updates: Real-time sync events for connected clients
"""

import logging
import os
from datetime import datetime, UTC
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Dapr sidecar HTTP endpoint
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
PUBSUB_NAME = "kafka-pubsub"

# Feature flag: disable publishing in local dev without Dapr
DAPR_ENABLED = os.getenv("DAPR_ENABLED", "false").lower() == "true"


async def _publish_event(topic: str, data: dict[str, Any]) -> bool:
    """Publish an event to a Dapr pub/sub topic.

    Args:
        topic: Kafka topic name (task-events, reminders, task-updates)
        data: Event payload

    Returns:
        True if published successfully, False otherwise
    """
    if not DAPR_ENABLED:
        logger.debug(f"Dapr disabled, skipping publish to {topic}: {data.get('event_type', 'unknown')}")
        return False

    url = f"{DAPR_BASE_URL}/v1.0/publish/{PUBSUB_NAME}/{topic}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
            )
            if response.status_code in (200, 204):
                logger.info(f"Published to {topic}: {data.get('event_type', 'unknown')}")
                return True
            else:
                logger.warning(f"Dapr publish failed ({response.status_code}): {response.text}")
                return False
    except httpx.ConnectError:
        logger.debug(f"Dapr sidecar not reachable at {url}, skipping event")
        return False
    except Exception as e:
        logger.error(f"Event publish error for {topic}: {e}")
        return False


def _build_event(event_type: str, task_data: dict[str, Any], user_id: str) -> dict[str, Any]:
    """Build a standardized event payload."""
    return {
        "event_type": event_type,
        "timestamp": datetime.now(UTC).isoformat(),
        "user_id": user_id,
        "data": task_data,
    }


def _task_to_dict(task) -> dict[str, Any]:
    """Convert a Task model instance to a serializable dict."""
    return {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "complete": task.complete,
        "priority": task.priority.value if hasattr(task.priority, "value") else str(task.priority),
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "recurring": task.recurring.value if hasattr(task.recurring, "value") else str(task.recurring),
        "tags": task.tags or [],
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }


async def publish_task_created(task, user_id: str) -> None:
    """Publish task-created event to task-events and task-updates topics."""
    task_data = _task_to_dict(task)
    event = _build_event("task.created", task_data, user_id)

    await _publish_event("task-events", event)
    await _publish_event("task-updates", event)

    # Schedule reminder if task has a due date
    if task.due_date:
        await publish_reminder_scheduled(task, user_id)


async def publish_task_updated(task, user_id: str, updated_fields: list[str] | None = None) -> None:
    """Publish task-updated event to task-events and task-updates topics."""
    task_data = _task_to_dict(task)
    if updated_fields:
        task_data["updated_fields"] = updated_fields

    event = _build_event("task.updated", task_data, user_id)

    await _publish_event("task-events", event)
    await _publish_event("task-updates", event)

    # Reschedule reminder if due_date was updated
    if updated_fields and "due_date" in updated_fields and task.due_date:
        await publish_reminder_scheduled(task, user_id)


async def publish_task_completed(task, user_id: str) -> None:
    """Publish task-completed event to task-events and task-updates topics.

    The recurring-task-service consumes task.completed events from
    task-events topic to auto-create next occurrence for recurring tasks.
    """
    task_data = _task_to_dict(task)
    event = _build_event("task.completed", task_data, user_id)

    await _publish_event("task-events", event)
    await _publish_event("task-updates", event)


async def publish_task_deleted(task_id: int, task_title: str, user_id: str) -> None:
    """Publish task-deleted event to task-events and task-updates topics."""
    task_data = {"id": task_id, "title": task_title}
    event = _build_event("task.deleted", task_data, user_id)

    await _publish_event("task-events", event)
    await _publish_event("task-updates", event)


async def publish_reminder_scheduled(task, user_id: str) -> None:
    """Publish reminder event to reminders topic when a task has a due date."""
    if not task.due_date:
        return

    reminder_data = {
        "task_id": task.id,
        "task_title": task.title,
        "due_date": task.due_date.isoformat(),
        "user_id": user_id,
        "priority": task.priority.value if hasattr(task.priority, "value") else str(task.priority),
    }
    event = _build_event("reminder.scheduled", reminder_data, user_id)

    await _publish_event("reminders", event)
