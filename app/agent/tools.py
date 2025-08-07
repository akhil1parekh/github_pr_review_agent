from typing import Dict, List, Any
from app.services import github_service, llm_service


class GitHubTool:
    """Tool for fetching GitHub PR data."""

    @staticmethod
    def fetch_pr_details(repo: str, pr_number: int) -> Dict[str, Any]:
        """Fetch PR details."""
        return github_service.get_pr_details(repo, pr_number)

    @staticmethod
    def fetch_pr_files(repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """Fetch files changed in PR."""
        return github_service.get_pr_files(repo, pr_number)

    @staticmethod
    def fetch_pr_diff(repo: str, pr_number: int) -> str:
        """Fetch PR diff."""
        return github_service.get_pr_diff(repo, pr_number)

    @staticmethod
    def fetch_pr_comments(repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """Fetch PR comments."""
        return github_service.get_pr_comments(repo, pr_number)

    @staticmethod
    def add_pr_comment(repo: str, pr_number: int, body: str) -> Dict[str, Any]:
        """Add comment to PR."""
        return github_service.add_pr_comment(repo, pr_number, body)

    @staticmethod
    def get_pr_head_sha(repo: str, pr_number: int) -> str:
        """Get the HEAD SHA of the pull request."""
        return github_service.get_pr_head_sha(repo, pr_number)

    @staticmethod
    def add_pr_review_comment(
        repo: str,
        pr_number: int,
        commit_sha: str,
        body: str,
        path: str,
        line: int,
    ) -> Dict[str, Any]:
        """Add an inline review comment to a pull request."""
        return github_service.add_pr_review_comment(
            repo, pr_number, commit_sha, body, path, line
        )


class CodeAnalysisTool:
    """Tool for analyzing code."""

    @staticmethod
    def analyze_style(
        pr_details: Dict[str, Any], patch: str, filename: str
    ) -> List[Dict[str, Any]]:
        """Analyze code style and formatting."""
        return llm_service.analyze_code_style(pr_details, patch, filename)

    @staticmethod
    def analyze_bugs(
        pr_details: Dict[str, Any], patch: str, filename: str
    ) -> List[Dict[str, Any]]:
        """Analyze potential bugs and errors."""
        return llm_service.analyze_bugs(pr_details, patch, filename)

    @staticmethod
    def analyze_performance(
        pr_details: Dict[str, Any], patch: str, filename: str
    ) -> List[Dict[str, Any]]:
        """Analyze performance issues."""
        return llm_service.analyze_performance(pr_details, patch, filename)

    @staticmethod
    def analyze_best_practices(
        pr_details: Dict[str, Any], patch: str, filename: str
    ) -> List[Dict[str, Any]]:
        """Analyze adherence to best practices."""
        return llm_service.analyze_best_practices(pr_details, patch, filename)

    @staticmethod
    def analyze_semantic_issues(
        pr_details: Dict[str, Any], patch: str, filename: str
    ) -> List[Dict[str, Any]]:
        """Analyze semantic and logical issues."""
        return llm_service.analyze_semantic_issues(pr_details, patch, filename)


class PlanningTool:
    """Tool for planning and summarizing."""

    @staticmethod
    def create_plan(
        pr_details: Dict[str, Any], files_changed: List[Dict[str, Any]]
    ) -> List[str]:
        """Create a plan for analyzing the PR."""
        return llm_service.create_plan(pr_details, files_changed)

    @staticmethod
    def create_summary(analysis_results: Dict[str, List[Dict[str, Any]]]) -> str:
        """Create a summary of the analysis results."""
        return llm_service.create_summary(analysis_results)


github_tool = GitHubTool()
code_analysis_tool = CodeAnalysisTool()
planning_tool = PlanningTool()
