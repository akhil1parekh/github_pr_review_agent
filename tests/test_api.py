import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.main import app
from app.tasks import update_task_status, store_task_results

client = TestClient(app)


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    with patch("app.tasks.redis_client") as mock_redis:
        yield mock_redis


@pytest.fixture
def mock_celery():
    """Mock Celery task."""
    with patch("app.api.endpoints.analyze_pr_task") as mock_task:
        mock_task.delay = MagicMock()
        yield mock_task


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.json()
    assert "version" in response.json()


def test_health_endpoint():
    """Test the health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_pr_endpoint(mock_redis, mock_celery):
    """Test the analyze PR endpoint."""
    # Mock Redis
    mock_redis.hset = MagicMock()
    
    # Test data
    test_data = {
        "repo": "owner/repo",
        "pr_number": 123,
        "analysis_depth": "standard",
    }
    
    # Make request
    response = client.post("/api/v1/analyze-pr", json=test_data)
    
    # Check response
    assert response.status_code == 202
    assert "task_id" in response.json()
    assert response.json()["status"] == "queued"
    
    # Check if Redis was called
    mock_redis.hset.assert_called_once()
    
    # Check if Celery task was called
    mock_celery.delay.assert_called_once()


def test_get_task_status_endpoint(mock_redis):
    """Test the get task status endpoint."""
    # Mock Redis
    task_id = "test-task-id"
    task_data = {
        "task_id": task_id,
        "status": "in_progress",
        "message": "Analyzing code",
        "progress": "0.5",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    mock_redis.hgetall.return_value = task_data
    
    # Make request
    response = client.get(f"/api/v1/status/{task_id}")
    
    # Check response
    assert response.status_code == 200
    assert response.json()["task_id"] == task_id
    assert response.json()["status"] == "in_progress"
    assert response.json()["progress"] == 0.5  # Converted to float


def test_get_task_status_not_found(mock_redis):
    """Test the get task status endpoint when task is not found."""
    # Mock Redis
    mock_redis.hgetall.return_value = {}
    
    # Make request
    response = client.get("/api/v1/status/non-existent-task")
    
    # Check response
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_get_task_results_endpoint(mock_redis):
    """Test the get task results endpoint."""
    # Mock Redis
    task_id = "test-task-id"
    task_data = {
        "task_id": task_id,
        "status": "completed",
        "message": "Analysis completed",
        "progress": "1.0",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    mock_redis.hgetall.return_value = task_data
    
    results_data = {
        "task_id": task_id,
        "status": "completed",
        "pr_details": {
            "repo": "owner/repo",
            "pr_number": 123,
            "title": "Test PR",
        },
        "summary": "This PR looks good",
        "issues": [
            {
                "type": "style",
                "file": "src/main.py",
                "line": 42,
                "issue": "Variable name doesn't follow convention",
                "severity": "low",
                "suggestion": "Rename variable",
            }
        ],
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
    }
    mock_redis.get.return_value = pytest.importorskip("json").dumps(results_data)
    
    # Make request
    response = client.get(f"/api/v1/results/{task_id}")
    
    # Check response
    assert response.status_code == 200
    assert response.json()["task_id"] == task_id
    assert response.json()["status"] == "completed"
    assert len(response.json()["issues"]) == 1


def test_get_task_results_not_completed(mock_redis):
    """Test the get task results endpoint when task is not completed."""
    # Mock Redis
    task_id = "test-task-id"
    task_data = {
        "task_id": task_id,
        "status": "in_progress",
        "message": "Analyzing code",
        "progress": "0.5",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    mock_redis.hgetall.return_value = task_data
    
    # Make request
    response = client.get(f"/api/v1/results/{task_id}")
    
    # Check response
    assert response.status_code == 400
    assert "not completed yet" in response.json()["detail"]
