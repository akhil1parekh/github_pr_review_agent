# GitHub PR Review Agent

An autonomous code review agent system that uses AI to analyze GitHub pull requests. The system implements a goal-oriented AI agent that can plan and execute code reviews independently, process them asynchronously using Celery, and interact with developers through a structured API.

## Features

- Analyzes GitHub pull requests for:
  - Code style and formatting issues
  - Potential bugs or errors
  - Performance improvements
  - Best practices
- Asynchronous processing with Celery
- RESTful API with FastAPI
- Goal-oriented AI agent using LangGraph

## Tech Stack

- Python 3.8+
- FastAPI
- Celery
- Redis (or PostgreSQL)
- LangGraph
- OpenAI API (or other LLM provider)

## Setup

### Prerequisites

- GitHub API token
- OpenAI API key (or other LLM provider)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/akhil1parekh/github_pr_review_agent.git
   cd github_pr_review_agent
   ```
   
2. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
   
3. Edit the `.env` file with your API keys and configuration.

4. Create virtualenv and install the requirments using
   ```bash
   chmod +x ./setup.sh
   ./setup.sh
   ```
   or
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

6. Start the service using
   ```bash
   ./run_dev.sh
   ```

# API Usage

### Analyze a Pull Request

```bash
curl -X POST "http://localhost:8000/analyze-pr" \
  -H "Content-Type: application/json" \
  -d '{
    "repo": "username/repo",
    "pr_number": 123,
    "analysis_depth": "standard"
  }'
```

Response:
```json
{
  "task_id": "task-uuid-123",
  "status": "queued",
  "message": "PR analysis task has been queued",
  "created_at": "2025-05-14T10:30:00Z"
}
```

### Check Task Status

```bash
curl -X GET "http://localhost:8000/status/task-uuid-123"
```

Response:
```json
{
  "task_id": "task-uuid-123",
  "status": "in_progress",
  "progress": 0.65,
  "message": "Analyzing code for bugs and performance issues",
  "created_at": "2025-05-14T10:30:00Z",
  "updated_at": "2025-05-14T10:32:30Z"
}
```

### Get Analysis Results

```bash
curl -X GET "http://localhost:8000/results/task-uuid-123"
```

Response:
```json
{
  "task_id": "task-uuid-123",
  "status": "completed",
  "pr_details": {
    "repo": "username/repo",
    "pr_number": 123,
    "title": "Add new feature",
    "author": "contributor"
  },
  "summary": "This PR adds a new feature with good code quality. There are 2 minor style issues and 1 potential performance improvement.",
  "issues": [
    {
      "type": "style",
      "file": "src/main.py",
      "line": 42,
      "description": "Variable name doesn't follow snake_case convention",
      "severity": "low",
      "suggestion": "Rename 'myVar' to 'my_var'"
    },
    {
      "type": "performance",
      "file": "src/utils.py",
      "line": 78,
      "description": "Inefficient list comprehension could be optimized",
      "severity": "medium",
      "suggestion": "Use a generator expression instead of a list comprehension"
    }
  ],
  "created_at": "2025-05-14T10:30:00Z",
  "completed_at": "2025-05-14T10:35:12Z"
}
```

## License

MIT
