import pytest
from unittest.mock import patch, MagicMock

from app.agent.graph import (
    create_initial_state,
    build_graph,
    run_agent,
    fetch_pr_data,
    create_analysis_plan,
    analyze_code_style,
    analyze_bugs,
    analyze_performance,
    analyze_best_practices,
    create_summary,
)


@pytest.fixture
def mock_github_tool():
    """Mock GitHub tool."""
    with patch("app.agent.graph.github_tool") as mock_tool:
        # Mock PR details
        mock_tool.fetch_pr_details.return_value = {
            "repo": "owner/repo",
            "pr_number": 123,
            "title": "Test PR",
            "description": "This is a test PR",
            "author": "test-user",
            "created_at": "2025-05-14T10:30:00Z",
            "updated_at": "2025-05-14T10:35:00Z",
            "state": "open",
            "mergeable": True,
            "labels": [],
            "commits": 1,
            "additions": 10,
            "deletions": 5,
            "changed_files": 2,
        }

        # Mock files changed
        mock_tool.fetch_pr_files.return_value = [
            {
                "filename": "src/main.py",
                "status": "modified",
                "additions": 5,
                "deletions": 2,
                "changes": 7,
                "patch": "@@ -1,5 +1,8 @@\n...",
                "content": "def main():\n    print('Hello, world!')\n\nif __name__ == '__main__':\n    main()",
            },
            {
                "filename": "src/utils.py",
                "status": "added",
                "additions": 5,
                "deletions": 0,
                "changes": 5,
                "patch": "@@ -0,0 +1,5 @@\n...",
                "content": "def helper():\n    return 'Helper function'\n",
            },
        ]

        yield mock_tool


@pytest.fixture
def mock_planning_tool():
    """Mock planning tool."""
    with patch("app.agent.graph.planning_tool") as mock_tool:
        # Mock create plan
        mock_tool.create_plan.return_value = [
            "Analyze code style for all files",
            "Check for potential bugs",
            "Evaluate performance issues",
            "Review adherence to best practices",
        ]

        # Mock create summary
        mock_tool.create_summary.return_value = "This PR looks good overall. There are a few minor style issues and one potential bug."

        yield mock_tool


@pytest.fixture
def mock_code_analysis_tool():
    """Mock code analysis tool."""
    with patch("app.agent.graph.code_analysis_tool") as mock_tool:
        # Mock style analysis
        mock_tool.analyze_style.return_value = [
            {
                "line": 2,
                "issue": "Use double quotes instead of single quotes",
                "severity": "low",
                "suggestion": "Change 'Hello, world!' to \"Hello, world!\"",
            }
        ]

        # Mock bug analysis
        mock_tool.analyze_bugs.return_value = [
            {
                "line": 1,
                "issue": "Function lacks docstring",
                "severity": "medium",
                "suggestion": "Add a docstring to the main() function",
            }
        ]

        # Mock performance analysis
        mock_tool.analyze_performance.return_value = []

        # Mock best practices analysis
        mock_tool.analyze_best_practices.return_value = [
            {
                "line": 1,
                "issue": "Function lacks type hints",
                "severity": "low",
                "suggestion": "Add type hints to the main() function",
            }
        ]

        yield mock_tool


def test_create_initial_state():
    """Test creating initial state."""
    state = create_initial_state("owner/repo", 123)

    assert state["pr_details"]["repo"] == "owner/repo"
    assert state["pr_details"]["pr_number"] == 123
    assert state["status"] == "not_started"
    assert state["files_changed"] == []
    assert state["analysis_plan"] == []
    assert state["current_step"] == 0
    assert "style_issues" in state["analysis_results"]
    assert "bugs" in state["analysis_results"]
    assert "performance_issues" in state["analysis_results"]
    assert "best_practices" in state["analysis_results"]


def test_fetch_pr_data(mock_github_tool):
    """Test fetching PR data."""
    state = create_initial_state("owner/repo", 123)

    result = fetch_pr_data(state)

    assert result["status"] == "in_progress"
    assert result["pr_details"]["title"] == "Test PR"
    assert len(result["files_changed"]) == 2
    assert result["files_changed"][0]["filename"] == "src/main.py"
    assert result["files_changed"][1]["filename"] == "src/utils.py"


def test_create_analysis_plan(mock_planning_tool):
    """Test creating analysis plan."""
    state = create_initial_state("owner/repo", 123)
    state["files_changed"] = [{"filename": "src/main.py"}]

    result = create_analysis_plan(state)

    assert len(result["analysis_plan"]) == 4
    assert "Analyze code style" in result["analysis_plan"][0]
    assert result["current_step"] == 0


def test_analyze_code_style(mock_code_analysis_tool):
    """Test analyzing code style."""
    state = create_initial_state("owner/repo", 123)
    state["files_changed"] = [
        {
            "filename": "src/main.py",
            "status": "modified",
            "content": "def main():\n    print('Hello, world!')",
        }
    ]

    result = analyze_code_style(state)

    assert len(result["analysis_results"]["style_issues"]) == 1
    assert result["analysis_results"]["style_issues"][0]["line"] == 2
    assert result["analysis_results"]["style_issues"][0]["file"] == "src/main.py"


def test_analyze_bugs(mock_code_analysis_tool):
    """Test analyzing bugs."""
    state = create_initial_state("owner/repo", 123)
    state["files_changed"] = [
        {
            "filename": "src/main.py",
            "status": "modified",
            "content": "def main():\n    print('Hello, world!')",
        }
    ]

    result = analyze_bugs(state)

    assert len(result["analysis_results"]["bugs"]) == 1
    assert result["analysis_results"]["bugs"][0]["line"] == 1
    assert result["analysis_results"]["bugs"][0]["file"] == "src/main.py"


def test_analyze_performance(mock_code_analysis_tool):
    """Test analyzing performance."""
    state = create_initial_state("owner/repo", 123)
    state["files_changed"] = [
        {
            "filename": "src/main.py",
            "status": "modified",
            "content": "def main():\n    print('Hello, world!')",
        }
    ]

    result = analyze_performance(state)

    assert len(result["analysis_results"]["performance_issues"]) == 0


def test_analyze_best_practices(mock_code_analysis_tool):
    """Test analyzing best practices."""
    state = create_initial_state("owner/repo", 123)
    state["files_changed"] = [
        {
            "filename": "src/main.py",
            "status": "modified",
            "content": "def main():\n    print('Hello, world!')",
        }
    ]

    result = analyze_best_practices(state)

    assert len(result["analysis_results"]["best_practices"]) == 1
    assert result["analysis_results"]["best_practices"][0]["line"] == 1
    assert result["analysis_results"]["best_practices"][0]["file"] == "src/main.py"


def test_create_summary(mock_planning_tool):
    """Test creating summary."""
    state = create_initial_state("owner/repo", 123)
    state["analysis_results"] = {
        "style_issues": [{"line": 2, "issue": "Style issue"}],
        "bugs": [{"line": 1, "issue": "Bug"}],
        "performance_issues": [],
        "best_practices": [{"line": 1, "issue": "Best practice issue"}],
    }

    result = create_summary(state)

    assert result["status"] == "completed"
    assert "This PR looks good overall" in result["summary"]


@patch("app.agent.graph.build_graph")
def test_run_agent(
    mock_build_graph, mock_github_tool, mock_planning_tool, mock_code_analysis_tool
):
    """Test running the agent."""
    # Mock the graph
    mock_graph_instance = MagicMock()
    mock_build_graph.return_value = mock_graph_instance

    # Mock the compiled graph and its invoke method
    mock_compiled_graph = MagicMock()
    mock_graph_instance.compile.return_value = mock_compiled_graph

    # Mock the final state
    final_state = {
        "pr_details": {
            "repo": "owner/repo",
            "pr_number": 123,
            "title": "Test PR",
        },
        "files_changed": [{"filename": "src/main.py"}],
        "analysis_plan": ["Analyze code style"],
        "current_step": 1,
        "analysis_results": {
            "style_issues": [{"line": 2, "issue": "Style issue"}],
            "bugs": [],
            "performance_issues": [],
            "best_practices": [],
        },
        "summary": "This PR looks good",
        "status": "completed",
        "error": "",
    }
    mock_compiled_graph.invoke.return_value = final_state

    # Run the agent
    result = run_agent("owner/repo", 123)

    # Check the result
    assert result["status"] == "completed"
    assert result["summary"] == "This PR looks good"
    assert len(result["analysis_results"]["style_issues"]) == 1

    # Check if the graph was built and invoked
    mock_build_graph.assert_called_once()
    mock_graph_instance.compile.assert_called_once()
    mock_compiled_graph.invoke.assert_called_once()
