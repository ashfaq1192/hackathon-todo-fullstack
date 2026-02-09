from sqlmodel import Session
from src.models.task import Task # Example import, adjust as needed


def example_tool(
    session: Session,
    user_id: str,
    param1: str,
    param2: int | None = None
) -> dict:
    """
    Example MCP tool for demonstration purposes.
    Replace with your actual tool logic.
    """
    # Example: Create a task for the user
    # new_task = Task(user_id=user_id, title=param1, description=f"Example with param2: {param2}")
    # session.add(new_task)
    # session.commit()
    # session.refresh(new_task)

    return {
        "status": "success",
        "message": f"Example tool executed for user {user_id} with param1='{param1}' and param2='{param2}'.",
        "param1_received": param1,
        "param2_received": param2,
    }
