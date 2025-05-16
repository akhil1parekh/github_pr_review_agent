import pytest
from unittest.mock import patch, MagicMock

from app.services.github import GitHubService


@pytest.fixture
def mock_github():
    """Mock GitHub API."""
    with patch("app.services.github.Github") as mock_github:
        # Mock repository
        mock_repo = MagicMock()
        mock_github.return_value.get_repo.return_value = mock_repo
        
        # Mock pull request
        mock_pr = MagicMock()
        mock_repo.get_pull.return_value = mock_pr
        
        # Set PR attributes
        mock_pr.title = "Test PR"
        mock_pr.body = "This is a test PR"
        mock_pr.user.login = "test-user"
        mock_pr.created_at.isoformat.return_value = "2025-05-14T10:30:00Z"
        mock_pr.updated_at.isoformat.return_value = "2025-05-14T10:35:00Z"
        mock_pr.state = "open"
        mock_pr.mergeable = True
        
        # Mock labels
        mock_label_bug = MagicMock()
        mock_label_bug.name = "bug"
        mock_label_enhancement = MagicMock()
        mock_label_enhancement.name = "enhancement"
        mock_pr.labels = [mock_label_bug, mock_label_enhancement]
        
        mock_pr.commits = 1
        mock_pr.additions = 10
        mock_pr.deletions = 5
        mock_pr.changed_files = 2
        
        # Mock files
        mock_file1 = MagicMock()
        mock_file1.filename = "src/main.py"
        mock_file1.status = "modified"
        mock_file1.additions = 5
        mock_file1.deletions = 2
        mock_file1.changes = 7
        mock_file1.patch = "@@ -1,5 +1,8 @@\n..."
        mock_file1.sha = "abc123"
        
        mock_file2 = MagicMock()
        mock_file2.filename = "src/utils.py"
        mock_file2.status = "added"
        mock_file2.additions = 5
        mock_file2.deletions = 0
        mock_file2.changes = 5
        mock_file2.patch = "@@ -0,0 +1,5 @@\n..."
        mock_file2.sha = "def456"
        
        mock_pr.get_files.return_value = [mock_file1, mock_file2]
        
        # Mock file content
        mock_content_file = MagicMock()
        mock_content_file.decoded_content.decode.return_value = "def main():\n    print('Hello, world!')"
        mock_repo.get_contents.return_value = mock_content_file
        
        # Mock diff
        mock_pr.diff.return_value = "diff --git a/src/main.py b/src/main.py\n..."
        
        # Mock comments
        mock_comment = MagicMock()
        mock_comment.id = 123
        mock_comment.user.login = "test-user"
        mock_comment.body = "This is a comment"
        mock_comment.created_at.isoformat.return_value = "2025-05-14T10:40:00Z"
        mock_comment.updated_at.isoformat.return_value = "2025-05-14T10:40:00Z"
        
        mock_pr.get_comments.return_value = [mock_comment]
        
        # Mock create comment
        mock_pr.create_issue_comment.return_value = mock_comment
        
        yield mock_github


def test_get_repository(mock_github):
    """Test getting a repository."""
    service = GitHubService(token="test-token")
    
    repo = service.get_repository("owner/repo")
    
    mock_github.return_value.get_repo.assert_called_once_with("owner/repo")
    assert repo == mock_github.return_value.get_repo.return_value


def test_get_pull_request(mock_github):
    """Test getting a pull request."""
    service = GitHubService(token="test-token")
    
    pr = service.get_pull_request("owner/repo", 123)
    
    mock_github.return_value.get_repo.assert_called_once_with("owner/repo")
    mock_github.return_value.get_repo.return_value.get_pull.assert_called_once_with(123)
    assert pr == mock_github.return_value.get_repo.return_value.get_pull.return_value


def test_get_pr_details(mock_github):
    """Test getting PR details."""
    service = GitHubService(token="test-token")
    
    details = service.get_pr_details("owner/repo", 123)
    
    assert details["repo"] == "owner/repo"
    assert details["pr_number"] == 123
    assert details["title"] == "Test PR"
    assert details["description"] == "This is a test PR"
    assert details["author"] == "test-user"
    assert details["created_at"] == "2025-05-14T10:30:00Z"
    assert details["updated_at"] == "2025-05-14T10:35:00Z"
    assert details["state"] == "open"
    assert details["mergeable"] == True
    assert details["labels"] == ["bug", "enhancement"]
    assert details["commits"] == 1
    assert details["additions"] == 10
    assert details["deletions"] == 5
    assert details["changed_files"] == 2


def test_get_pr_files(mock_github):
    """Test getting PR files."""
    service = GitHubService(token="test-token")
    
    files = service.get_pr_files("owner/repo", 123)
    
    assert len(files) == 2
    assert files[0]["filename"] == "src/main.py"
    assert files[0]["status"] == "modified"
    assert files[0]["additions"] == 5
    assert files[0]["deletions"] == 2
    assert files[0]["changes"] == 7
    assert files[0]["patch"] == "@@ -1,5 +1,8 @@\n..."
    assert files[0]["content"] == "def main():\n    print('Hello, world!')"
    
    assert files[1]["filename"] == "src/utils.py"
    assert files[1]["status"] == "added"


def test_get_file_content(mock_github):
    """Test getting file content."""
    service = GitHubService(token="test-token")
    
    # Create a mock file
    mock_file = MagicMock()
    mock_file.filename = "src/main.py"
    mock_file.status = "modified"
    mock_file.sha = "abc123"
    
    content = service._get_file_content("owner/repo", mock_file)
    
    mock_github.return_value.get_repo.assert_called_with("owner/repo")
    mock_github.return_value.get_repo.return_value.get_contents.assert_called_with("src/main.py", ref="abc123")
    assert content == "def main():\n    print('Hello, world!')"


def test_get_file_content_removed_file(mock_github):
    """Test getting content of a removed file."""
    service = GitHubService(token="test-token")
    
    # Create a mock file
    mock_file = MagicMock()
    mock_file.filename = "src/main.py"
    mock_file.status = "removed"
    
    content = service._get_file_content("owner/repo", mock_file)
    
    assert content is None
    mock_github.return_value.get_repo.return_value.get_contents.assert_not_called()


def test_get_pr_diff(mock_github):
    """Test getting PR diff."""
    service = GitHubService(token="test-token")
    
    diff = service.get_pr_diff("owner/repo", 123)
    
    assert diff == "diff --git a/src/main.py b/src/main.py\n..."


def test_get_pr_comments(mock_github):
    """Test getting PR comments."""
    service = GitHubService(token="test-token")
    
    comments = service.get_pr_comments("owner/repo", 123)
    
    assert len(comments) == 1
    assert comments[0]["id"] == 123
    assert comments[0]["user"] == "test-user"
    assert comments[0]["body"] == "This is a comment"
    assert comments[0]["created_at"] == "2025-05-14T10:40:00Z"
    assert comments[0]["updated_at"] == "2025-05-14T10:40:00Z"


def test_add_pr_comment(mock_github):
    """Test adding a PR comment."""
    service = GitHubService(token="test-token")
    
    comment = service.add_pr_comment("owner/repo", 123, "New comment")
    
    mock_github.return_value.get_repo.return_value.get_pull.return_value.create_issue_comment.assert_called_once_with("New comment")
    assert comment["id"] == 123
    assert comment["user"] == "test-user"
    assert comment["body"] == "This is a comment"
