from typing import Dict, List, Any
from app.services.github import github_service


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
