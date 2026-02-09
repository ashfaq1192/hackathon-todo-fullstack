"""
Audit Service - Records all task lifecycle events for audit trail.

Subscribes to:
  - `task-events` topic: Logs all CRUD operations (create, update, complete, delete).

Stores events in memory for demo purposes. In production, this would
persist to a database, object storage, or a dedicated audit log system.
"""

import logging
from collections import deque
from datetime import datetime, UTC

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("audit-service")

app = FastAPI(title="Audit Service", version="1.0.0")

# In-memory audit log (bounded to prevent memory issues in demo)
MAX_AUDIT_ENTRIES = 1000
audit_log: deque[dict] = deque(maxlen=MAX_AUDIT_ENTRIES)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "audit-service"}


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
    """Process and store all task lifecycle events.

    Event types: task.created, task.updated, task.completed, task.deleted
    """
    try:
        body = await request.json()
        event_data = body.get("data", body)

        event_type = event_data.get("event_type", "unknown")
        user_id = event_data.get("user_id", "unknown")
        timestamp = event_data.get("timestamp", datetime.now(UTC).isoformat())
        task_data = event_data.get("data", {})

        audit_entry = {
            "event_type": event_type,
            "user_id": user_id,
            "timestamp": timestamp,
            "received_at": datetime.now(UTC).isoformat(),
            "task_id": task_data.get("id"),
            "task_title": task_data.get("title", ""),
            "details": task_data,
        }

        audit_log.append(audit_entry)

        logger.info(
            f"AUDIT: [{event_type}] user={user_id} "
            f"task_id={task_data.get('id')} title='{task_data.get('title', '')}'"
        )

        return JSONResponse(content={"status": "SUCCESS"}, status_code=200)
    except Exception as e:
        logger.error(f"Error processing audit event: {e}")
        return JSONResponse(content={"status": "SUCCESS"}, status_code=200)


@app.get("/audit/logs")
async def get_audit_logs(
    user_id: str | None = None,
    event_type: str | None = None,
    limit: int = 50,
):
    """Query the audit log with optional filters.

    Args:
        user_id: Filter by user ID.
        event_type: Filter by event type (task.created, task.updated, etc.).
        limit: Maximum number of entries to return (default 50).
    """
    entries = list(audit_log)

    if user_id:
        entries = [e for e in entries if e["user_id"] == user_id]
    if event_type:
        entries = [e for e in entries if e["event_type"] == event_type]

    # Return most recent first
    entries.reverse()
    return {"total": len(entries), "entries": entries[:limit]}


@app.get("/audit/stats")
async def get_audit_stats():
    """Get summary statistics of audit events."""
    from collections import Counter

    entries = list(audit_log)
    event_counts = Counter(e["event_type"] for e in entries)
    user_counts = Counter(e["user_id"] for e in entries)

    return {
        "total_events": len(entries),
        "events_by_type": dict(event_counts),
        "events_by_user": dict(user_counts),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
