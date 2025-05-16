import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Path

from app.api.models import (
    AnalyzePRRequest,
    AnalyzePRResponse,
    TaskStatusResponse,
    AnalysisResultResponse,
)
from app.tasks import analyze_pr_task, get_task, get_task_results, update_task_status

router = APIRouter()


@router.post("/analyze-pr", response_model=AnalyzePRResponse, status_code=202)
async def analyze_pr(request: AnalyzePRRequest):
    """
    Analyze a GitHub pull request.

    This endpoint initiates an asynchronous task to analyze a GitHub pull request.
    The task will fetch the PR details, analyze the code, and generate a report.

    Returns a task ID that can be used to check the status and retrieve the results.
    """
    # Generate a task ID
    task_id = str(uuid.uuid4())

    # Create a timestamp
    created_at = datetime.utcnow()

    # Update task status to queued
    update_task_status(
        task_id=task_id,
        status="queued",
        message="PR analysis task has been queued",
        progress=0.0,
    )

    # Queue the task
    # background_tasks.add_task(
    analyze_pr_task.delay(
        task_id=task_id,
        repo=request.repo,
        pr_number=request.pr_number,
        analysis_depth=request.analysis_depth,
    )

    return {
        "task_id": task_id,
        "status": "queued",
        "message": "PR analysis task has been queued",
        "created_at": created_at,
    }


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str = Path(..., description="Task ID")):
    """
    Get the status of a task.

    This endpoint retrieves the status of a PR analysis task.

    Returns the task status, progress, and other details.
    """
    task = get_task(task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail=f"Task with ID {task_id} not found",
        )

    return task


@router.get("/results/{task_id}", response_model=AnalysisResultResponse)
async def get_task_results_endpoint(task_id: str = Path(..., description="Task ID")):
    """
    Get the results of a completed task.

    This endpoint retrieves the results of a completed PR analysis task.

    Returns the analysis results, including issues found and a summary.
    """
    # Check if the task exists
    task = get_task(task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail=f"Task with ID {task_id} not found",
        )

    # Check if the task is completed
    if task["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Task with ID {task_id} is not completed yet (status: {task['status']})",
        )

    # Get the results
    results = get_task_results(task_id)

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"Results for task with ID {task_id} not found",
        )

    return results
