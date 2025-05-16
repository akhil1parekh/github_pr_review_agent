from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class AnalyzePRRequest(BaseModel):
    """Request model for analyzing a PR."""

    repo: str = Field(..., description="GitHub repository in the format 'owner/repo'")
    pr_number: int = Field(..., description="Pull request number")
    github_token: Optional[str] = Field(
        None, description="GitHub token (optional if using default token)"
    )
    analysis_depth: Optional[str] = Field(
        "standard", description="Analysis depth: 'basic', 'standard', or 'deep'"
    )
    focus_areas: Optional[List[str]] = Field(
        [],
        description="Areas to focus on: 'style', 'bugs', 'performance', 'best_practices'",
    )

    @field_validator("repo")
    def validate_repo(cls, v):
        if not "/" in v:
            raise ValueError("Repository must be in the format 'owner/repo'")
        return v

    @field_validator("pr_number")
    def validate_pr_number(cls, v):
        if v <= 0:
            raise ValueError("Pull request number must be positive")
        return v

    @field_validator("analysis_depth")
    def validate_analysis_depth(cls, v):
        if v not in ["basic", "standard", "deep"]:
            raise ValueError("Analysis depth must be 'basic', 'standard', or 'deep'")
        return v

    @field_validator("focus_areas")
    def validate_focus_areas(cls, v):
        valid_areas = ["style", "bugs", "performance", "best_practices"]
        for area in v:
            if area not in valid_areas:
                raise ValueError(
                    f"Invalid focus area: {area}. Must be one of {valid_areas}"
                )
        return v


class AnalyzePRResponse(BaseModel):
    """Response model for analyzing a PR."""

    task_id: str = Field(..., description="Task ID for tracking the analysis")
    status: str = Field(
        ..., description="Task status: 'queued', 'in_progress', 'completed', 'failed'"
    )
    message: str = Field(..., description="Status message")
    created_at: datetime = Field(..., description="Task creation time")


class TaskStatusResponse(BaseModel):
    """Response model for task status."""

    task_id: str = Field(..., description="Task ID")
    status: str = Field(
        ..., description="Task status: 'queued', 'in_progress', 'completed', 'failed'"
    )
    progress: Optional[float] = Field(None, description="Task progress (0.0 to 1.0)")
    message: str = Field(..., description="Status message")
    created_at: datetime = Field(..., description="Task creation time")
    updated_at: datetime = Field(..., description="Last update time")


class IssueModel(BaseModel):
    """Model for a code issue."""

    type: str = Field(
        ..., description="Issue type: 'style', 'bug', 'performance', 'best_practice'"
    )
    file: str = Field(..., description="File path")
    line: int = Field(..., description="Line number")
    issue: str = Field(..., description="Issue description")
    severity: str = Field(..., description="Issue severity: 'low', 'medium', 'high'")
    suggestion: str = Field(..., description="Suggestion for fixing the issue")


class AnalysisResultResponse(BaseModel):
    """Response model for analysis results."""

    task_id: str = Field(..., description="Task ID")
    status: str = Field(..., description="Task status: 'completed', 'failed'")
    pr_details: Dict[str, Any] = Field(..., description="Pull request details")
    summary: str = Field(..., description="Analysis summary")
    issues: List[IssueModel] = Field(..., description="List of issues found")
    created_at: datetime = Field(..., description="Task creation time")
    completed_at: Optional[datetime] = Field(None, description="Task completion time")


class ErrorResponse(BaseModel):
    """Response model for errors."""

    detail: str = Field(..., description="Error detail")
    status_code: int = Field(..., description="HTTP status code")
    error_code: str = Field(..., description="Error code")
