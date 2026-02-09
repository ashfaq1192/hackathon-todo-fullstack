"""
Notification Service - Consumes reminder events from Kafka via Dapr Pub/Sub.

Subscribes to:
  - `reminders` topic: Sends notifications when task due dates are reached.

Also handles Dapr cron binding input for periodic reminder checks.
"""

import logging
from datetime import datetime, UTC

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("notification-service")

app = FastAPI(title="Notification Service", version="1.0.0")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "notification-service"}


@app.get("/dapr/subscribe")
async def subscribe():
    """Dapr subscription configuration - declarative subscriptions."""
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "reminders",
            "route": "/events/reminders",
        },
    ]


@app.post("/events/reminders")
async def handle_reminder(request: Request):
    """Process reminder events from the reminders topic.

    Event payload:
        {
            "event_type": "reminder.scheduled",
            "timestamp": "...",
            "user_id": "...",
            "data": {
                "task_id": 123,
                "task_title": "...",
                "due_date": "...",
                "priority": "high"
            }
        }
    """
    try:
        body = await request.json()
        event_data = body.get("data", body)

        task_data = event_data.get("data", {})
        task_id = task_data.get("task_id")
        task_title = task_data.get("task_title", "Unknown task")
        due_date = task_data.get("due_date")
        user_id = event_data.get("user_id", "unknown")
        priority = task_data.get("priority", "medium")

        logger.info(
            f"NOTIFICATION: Task '{task_title}' (ID: {task_id}) is due at {due_date} "
            f"for user {user_id} [priority: {priority}]"
        )

        # In production, this would send push notifications, emails, or WebSocket messages.
        # For the hackathon demo, logging serves as proof of the event flow.

        return JSONResponse(
            content={
                "status": "SUCCESS",
                "message": f"Notification processed for task {task_id}",
            },
            status_code=200,
        )
    except Exception as e:
        logger.error(f"Error processing reminder event: {e}")
        # Return SUCCESS to prevent Dapr from retrying (dead letter instead)
        return JSONResponse(content={"status": "SUCCESS"}, status_code=200)


@app.post("/reminder-cron")
async def handle_cron_binding(request: Request):
    """Handle Dapr cron binding trigger for periodic reminder checks.

    This endpoint is called by the `reminder-cron` Dapr binding component
    at the configured schedule interval.
    """
    logger.info(f"Cron trigger received at {datetime.now(UTC).isoformat()}")
    # In production: query tasks with upcoming due dates and send reminders
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
