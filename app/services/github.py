from typing import Dict, List, Any, Optional
from github import Github
from github.PullRequest import PullRequest
from github.Repository import Repository
from github.File import File as GithubFile
from app.core.config import settings


class GitHubService:
    """Service for interacting with GitHub API."""

    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub service with token."""
        self.token = token or settings.GITHUB_TOKEN
        self.client = Github(self.token)

    def get_repository(self, repo_name: str) -> Repository:
        """Get repository by name."""
        return self.client.get_repo(repo_name)

    def get_pull_request(self, repo_name: str, pr_number: int) -> PullRequest:
        """Get pull request by number."""
        repo = self.get_repository(repo_name)
        return repo.get_pull(pr_number)

    def get_pr_details(self, repo_name: str, pr_number: int) -> Dict[str, Any]:
        """Get pull request details."""
        pr = self.get_pull_request(repo_name, pr_number)
        return {
            "repo": repo_name,
            "pr_number": pr_number,
            "title": pr.title,
            "description": pr.body or "",
            "author": pr.user.login,
            "created_at": pr.created_at.isoformat(),
            "updated_at": pr.updated_at.isoformat(),
            "state": pr.state,
            "mergeable": pr.mergeable,
            "labels": [label.name for label in pr.labels],
            "commits": pr.commits,
            "additions": pr.additions,
            "deletions": pr.deletions,
            "changed_files": pr.changed_files,
        }

    def get_pr_files(self, repo_name: str, pr_number: int) -> List[Dict[str, Any]]:
        """Get files changed in pull request."""
        pr = self.get_pull_request(repo_name, pr_number)
        files = []

        for file in pr.get_files():
            file_data = {
                "filename": file.filename,
                "status": file.status,  # "added", "modified", "removed"
                "additions": file.additions,
                "deletions": file.deletions,
                "changes": file.changes,
                "patch": file.patch if hasattr(file, "patch") else None,
                "content": self._get_file_content(repo_name, file),
            }
            files.append(file_data)

        return files

    def _get_file_content(self, repo_name: str, file: GithubFile) -> Optional[str]:
        """Get content of a file."""
        if file.status == "removed":
            return None

        try:
            repo = self.get_repository(repo_name)
            # Use file.sha as the ref to get the content at that specific commit
            content_file = repo.get_contents(file.filename, ref=file.sha)
            return content_file.decoded_content.decode("utf-8")
        except Exception as e:
            print(f"Error getting file content: {e}")
            return None

    def get_pr_diff(self, repo_name: str, pr_number: int) -> str:
        """Get pull request diff."""
        pr = self.get_pull_request(repo_name, pr_number)
        return pr.diff()

    def get_pr_comments(self, repo_name: str, pr_number: int) -> List[Dict[str, Any]]:
        """Get pull request comments."""
        pr = self.get_pull_request(repo_name, pr_number)
        comments = []

        for comment in pr.get_comments():
            comment_data = {
                "id": comment.id,
                "user": comment.user.login,
                "body": comment.body,
                "created_at": comment.created_at.isoformat(),
                "updated_at": comment.updated_at.isoformat(),
            }
            comments.append(comment_data)

        return comments

    def add_pr_comment(
        self, repo_name: str, pr_number: int, body: str
    ) -> Dict[str, Any]:
        """Add comment to pull request."""
        pr = self.get_pull_request(repo_name, pr_number)
        comment = pr.create_issue_comment(body)

        return {
            "id": comment.id,
            "user": comment.user.login,
            "body": comment.body,
            "created_at": comment.created_at.isoformat(),
            "updated_at": comment.updated_at.isoformat(),
        }


github_service = GitHubService()
