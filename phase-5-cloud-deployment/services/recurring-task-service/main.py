"""
Recurring Task Service - Creates next occurrence when recurring tasks are completed.

Subscribes to:
  - `task-events` topic: Listens for `task.completed` events.
    When a recurring task is completed, creates the next occurrence
    via Dapr service invocation to the backend API.
"""

import logging
import os
from datetime import datetime, timedelta, UTC

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("recurring-task-service")

app = FastAPI(title="Recurring Task Service", version="1.0.0")

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
BACKEND_APP_ID = "backend"


def _calculate_next_due_date(current_due: str, recurring_type: str) -> str | None:
    """Calculate the next due date based on the recurring type."""
    try:
        due = datetime.fromisoformat(current_due)
    except (ValueError, TypeError):
        return None

    deltas = {
        "daily": timedelta(days=1),
        "weekly": timedelta(weeks=1),
        "monthly": timedelta(days=30),  # Approximate
        "yearly": timedelta(days=365),
    }

    delta = deltas.get(recurring_type)
    if not delta:
        return None

    next_due = due + delta
    # If the calculated date is in the past, advance from now
    now = datetime.now(UTC)
    while next_due < now:
        next_due += delta

    return next_due.isoformat()


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "recurring-task-service"}


@app.get("/dapr/subscribe")
async def subscribe():
    """Dapr subscription configuration."""
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/events/task-events",
        },
    ]


@app.post("/events/task-events")
async def handle_task_event(request: Request):
    """Process task events - specifically task.completed for recurring tasks.

    When a recurring task is completed, this service creates the next
    occurrence by invoking the backend API via Dapr service invocation.
    """
    try:
        body = await request.json()
        event_data = body.get("data", body)
        event_type = event_data.get("event_type")

        # Only process task.completed events
        if event_type != "task.completed":
            return JSONResponse(content={"status": "SUCCESS"}, status_code=200)

        task_data = event_data.get("data", {})
        recurring = task_data.get("recurring", "none")
        user_id = event_data.get("user_id")

        # Skip non-recurring tasks
        if recurring == "none" or not recurring:
            return JSONResponse(content={"status": "SUCCESS"}, status_code=200)

        task_title = task_data.get("title", "")
        description = task_data.get("description")
        priority = task_data.get("priority", "medium")
        due_date = task_data.get("due_date")
        tags = task_data.get("tags", [])

        # Calculate next due date
        next_due = _calculate_next_due_date(due_date, recurring) if due_date else None

        logger.info(
            f"Recurring task completed: '{task_title}' ({recurring}). "
            f"Creating next occurrence with due date: {next_due}"
        )

        # Create next occurrence via Dapr service invocation
        new_task = {
            "title": task_title,
            "description": description,
            "priority": priority,
            "recurring": recurring,
            "tags": tags,
        }
        if next_due:
            new_task["due_date"] = next_due

        url = f"{DAPR_BASE_URL}/v1.0/invoke/{BACKEND_APP_ID}/method/api/tasks"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                json=new_task,
                headers={
                    "Content-Type": "application/json",
                    "X-User-Id": user_id or "",
                },
            )

            if response.status_code in (200, 201):
                logger.info(f"Next occurrence created for '{task_title}'")
            else:
                logger.warning(
                    f"Failed to create next occurrence ({response.status_code}): "
                    f"{response.text}"
                )

        return JSONResponse(content={"status": "SUCCESS"}, status_code=200)
    except Exception as e:
        logger.error(f"Error processing task event: {e}")
        return JSONResponse(content={"status": "SUCCESS"}, status_code=200)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
