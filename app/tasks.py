from typing import Dict, Any, Optional
import json
from datetime import datetime
import redis

from app.core.celery_app import celery_app
from app.core.config import settings
from app.agent.graph import run_agent

# Connect to Redis
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True,
)


def update_task_status(
    task_id: str, status: str, message: str, progress: Optional[float] = None
) -> None:
    """Update task status in Redis."""
    # Convert None values to empty strings for Redis
    task_data = {
        "task_id": task_id,
        "status": status,
        "message": message,
        "progress": str(progress) if progress is not None else "",
        "created_at": redis_client.hget(f"task:{task_id}", "created_at")
        or datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    redis_client.hset(f"task:{task_id}", mapping=task_data)


def store_task_results(task_id: str, results: Dict[str, Any]) -> None:
    """Store task results in Redis."""
    # Store the results as a JSON string
    redis_client.set(f"results:{task_id}", json.dumps(results))

    # Update the task status
    update_task_status(
        task_id=task_id,
        status="completed",
        message="PR analysis completed successfully",
        progress=1.0,
    )


# Register the task with Celery
@celery_app.task(bind=True, name="app.tasks.analyze_pr_task")
def analyze_pr_task(
    self, task_id: str, repo: str, pr_number: int, analysis_depth: str = "standard"
) -> Dict[str, Any]:
    """Analyze a GitHub pull request."""
    try:
        # Update task status to in_progress
        update_task_status(
            task_id=task_id,
            status="in_progress",
            message="Starting PR analysis",
            progress=0.1,
        )

        # Run the agent
        update_task_status(
            task_id=task_id,
            status="in_progress",
            message="Fetching PR data",
            progress=0.2,
        )

        final_state = run_agent(repo, pr_number)

        if final_state["status"] == "failed":
            # Update task status to failed
            update_task_status(
                task_id=task_id,
                status="failed",
                message=f"PR analysis failed: {final_state['error']}",
                progress=None,
            )
            return {"status": "failed", "error": final_state["error"]}

        # Prepare results
        results = {
            "task_id": task_id,
            "status": "completed",
            "pr_details": final_state["pr_details"],
            "summary": final_state["summary"],
            "issues": [],
            "created_at": redis_client.hget(f"task:{task_id}", "created_at")
            or datetime.utcnow().isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
        }

        # Combine all issues
        for issue_type, issues in final_state["analysis_results"].items():
            for issue in issues:
                issue["type"] = issue_type.replace("_issues", "")
                results["issues"].append(issue)

        # Store results
        store_task_results(task_id, results)

        return results

    except Exception as e:
        # Update task status to failed
        update_task_status(
            task_id=task_id,
            status="failed",
            message=f"PR analysis failed: {str(e)}",
            progress=None,
        )

        # Re-raise the exception for Celery to handle
        raise


def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    """Get task status from Redis."""
    task_data = redis_client.hgetall(f"task:{task_id}")

    if not task_data:
        return None

    # Convert progress to float if it exists and is not empty
    if (
        "progress" in task_data
        and task_data["progress"]
        and task_data["progress"] != ""
    ):
        task_data["progress"] = float(task_data["progress"])
    elif "progress" in task_data and (
        not task_data["progress"] or task_data["progress"] == ""
    ):
        task_data["progress"] = None

    return task_data


def get_task_results(task_id: str) -> Optional[Dict[str, Any]]:
    """Get task results from Redis."""
    results_json = redis_client.get(f"results:{task_id}")

    if not results_json:
        return None

    return json.loads(results_json)
