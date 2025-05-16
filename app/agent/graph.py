from typing import Dict, List, Any, TypedDict, Literal
from langgraph.graph import StateGraph, END, START
from app.agent.tools import github_tool, code_analysis_tool, planning_tool


# Define the state schema
class AgentState(TypedDict):
    """State for the PR review agent."""

    # PR information
    pr_details: Dict[str, Any]
    files_changed: List[Dict[str, Any]]

    # Analysis plan and progress
    analysis_plan: List[str]
    current_step: int

    # Analysis results
    analysis_results: Dict[str, List[Dict[str, Any]]]

    # Summary
    summary: str

    # Status
    status: Literal["not_started", "in_progress", "completed", "failed"]
    error: str


# Define the nodes
def fetch_pr_data(state: AgentState) -> AgentState:
    """Fetch PR data from GitHub."""
    try:
        repo = state["pr_details"]["repo"]
        pr_number = state["pr_details"]["pr_number"]

        # Fetch PR details
        pr_details = github_tool.fetch_pr_details(repo, pr_number)
        state["pr_details"].update(pr_details)

        # Fetch files changed
        files_changed = github_tool.fetch_pr_files(repo, pr_number)
        state["files_changed"] = files_changed

        state["status"] = "in_progress"
        return state
    except Exception as e:
        state["status"] = "failed"
        state["error"] = f"Error fetching PR data: {str(e)}"
        return state


def create_analysis_plan(state: AgentState) -> AgentState:
    """Create a plan for analyzing the PR."""
    try:
        # Create a plan
        plan = planning_tool.create_plan(state["pr_details"], state["files_changed"])
        state["analysis_plan"] = plan
        state["current_step"] = 0

        return state
    except Exception as e:
        state["status"] = "failed"
        state["error"] = f"Error creating analysis plan: {str(e)}"
        return state


def analyze_code_style(state: AgentState) -> AgentState:
    """Analyze code style and formatting."""
    try:
        style_issues = []

        for file in state["files_changed"]:
            if file["status"] != "removed" and file["content"]:
                issues = code_analysis_tool.analyze_style(
                    file["content"], file["filename"]
                )
                for issue in issues:
                    issue["file"] = file["filename"]
                style_issues.extend(issues)

        state["analysis_results"]["style_issues"] = style_issues
        return state
    except Exception as e:
        state["status"] = "failed"
        state["error"] = f"Error analyzing code style: {str(e)}"
        return state


def analyze_bugs(state: AgentState) -> AgentState:
    """Analyze potential bugs and errors."""
    try:
        bugs = []

        for file in state["files_changed"]:
            if file["status"] != "removed" and file["content"]:
                issues = code_analysis_tool.analyze_bugs(
                    file["content"], file["filename"]
                )
                for issue in issues:
                    issue["file"] = file["filename"]
                bugs.extend(issues)

        state["analysis_results"]["bugs"] = bugs
        return state
    except Exception as e:
        state["status"] = "failed"
        state["error"] = f"Error analyzing bugs: {str(e)}"
        return state


def analyze_performance(state: AgentState) -> AgentState:
    """Analyze performance issues."""
    try:
        performance_issues = []

        for file in state["files_changed"]:
            if file["status"] != "removed" and file["content"]:
                issues = code_analysis_tool.analyze_performance(
                    file["content"], file["filename"]
                )
                for issue in issues:
                    issue["file"] = file["filename"]
                performance_issues.extend(issues)

        state["analysis_results"]["performance_issues"] = performance_issues
        return state
    except Exception as e:
        state["status"] = "failed"
        state["error"] = f"Error analyzing performance: {str(e)}"
        return state


def analyze_best_practices(state: AgentState) -> AgentState:
    """Analyze adherence to best practices."""
    try:
        best_practices_issues = []

        for file in state["files_changed"]:
            if file["status"] != "removed" and file["content"]:
                issues = code_analysis_tool.analyze_best_practices(
                    file["content"], file["filename"]
                )
                for issue in issues:
                    issue["file"] = file["filename"]
                best_practices_issues.extend(issues)

        state["analysis_results"]["best_practices"] = best_practices_issues
        return state
    except Exception as e:
        state["status"] = "failed"
        state["error"] = f"Error analyzing best practices: {str(e)}"
        return state


def create_summary(state: AgentState) -> AgentState:
    """Create a summary of the analysis results."""
    try:
        summary = planning_tool.create_summary(state["analysis_results"])
        state["summary"] = summary
        state["status"] = "completed"
        return state
    except Exception as e:
        state["status"] = "failed"
        state["error"] = f"Error creating summary: {str(e)}"
        return state


def build_graph() -> StateGraph:
    """Build the agent graph."""
    # Create a new graph
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("fetch_pr_data", fetch_pr_data)
    graph.add_node("create_analysis_plan", create_analysis_plan)
    graph.add_node("analyze_code_style", analyze_code_style)
    graph.add_node("analyze_bugs", analyze_bugs)
    graph.add_node("analyze_performance", analyze_performance)
    graph.add_node("analyze_best_practices", analyze_best_practices)
    graph.add_node("create_summary", create_summary)

    # Connect processing nodes back to router
    graph.add_edge(START, "fetch_pr_data")
    graph.add_edge("fetch_pr_data", "create_analysis_plan")
    graph.add_edge("create_analysis_plan", "analyze_code_style")
    graph.add_edge("analyze_code_style", "analyze_bugs")
    graph.add_edge("analyze_bugs", "analyze_performance")
    graph.add_edge("analyze_performance", "analyze_best_practices")
    graph.add_edge("analyze_best_practices", "create_summary")
    graph.add_edge("create_summary", END)

    return graph


def create_initial_state(repo: str, pr_number: int) -> AgentState:
    """Create the initial state for the agent."""
    return {
        "pr_details": {
            "repo": repo,
            "pr_number": pr_number,
        },
        "files_changed": [],
        "analysis_plan": [],
        "current_step": 0,
        "analysis_results": {
            "style_issues": [],
            "bugs": [],
            "performance_issues": [],
            "best_practices": [],
        },
        "summary": "",
        "status": "not_started",
        "error": "",
    }


def run_agent(repo: str, pr_number: int) -> AgentState:
    """Run the agent to analyze a PR."""
    # Create the initial state
    initial_state = create_initial_state(repo, pr_number)

    # Build the graph
    graph = build_graph()

    # Compile and run the graph
    try:
        graph_app = graph.compile()
        final_state = graph_app.invoke(initial_state)
        return final_state
    except Exception as e:
        initial_state["status"] = "failed"
        initial_state["error"] = f"Failed to run the graph: {str(e)}"
        return initial_state
