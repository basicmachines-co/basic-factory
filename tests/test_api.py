import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
from basic_factory.git import Git, GitConfig, GitError
from basic_factory.api import (
    GitTools, CommitFilesRequest,
    FileContent, app  # Import git_tools singleton
)
from fastapi.testclient import TestClient

# Fixtures
@pytest.fixture
def git_config():
    return GitConfig(
        repo_path=Path("/fake/repo"),
        git_path="git"
    )


@pytest.fixture
def mock_git_instance():
    """Create a mock Git instance with all methods we need"""
    instance = AsyncMock()

    # Configure all the method responses
    instance.checkout = AsyncMock(return_value="checkout success")
    instance.pull = AsyncMock(return_value="pull success")
    instance.create_branch = AsyncMock(return_value="branch created")
    instance.add = AsyncMock(return_value="add success")
    instance.commit = AsyncMock(return_value="commit success")
    instance.push = AsyncMock(return_value="push success")
    instance.get_current_commit_sha = AsyncMock(return_value="abc123")
    # Set repo_path for file operations
    instance.repo_path = Path("/fake/repo")

    return instance

@pytest.fixture
def mock_git(mock_git_instance):
    """Create Git class mock that returns our instance"""
    with patch('basic_factory.api.Git') as mock_cls:
        mock_cls.return_value = mock_git_instance
        yield mock_cls

@pytest.fixture
def mock_process():
    process = AsyncMock()
    process.communicate = AsyncMock(return_value=(b"success output", b""))
    process.returncode = 0
    return process

@pytest.fixture
def mock_github():
    with patch('basic_factory.api.Github') as mock:
        mock_repo = MagicMock()
        mock_repo.get_pull = MagicMock(return_value=MagicMock())
        mock.return_value.get_repo = MagicMock(return_value=mock_repo)
        yield mock

@pytest.fixture
def mock_git_tools(mock_git_instance):
    """Create GitTools with mocked Git instance"""
    tools = GitTools(".")
    tools.git = mock_git_instance
    return tools

@pytest.fixture
def client(mock_git_tools):
    """Create test client with proper dependency injection"""
    # Important: Patch the actual git_tools instance used by the app
    with patch('basic_factory.api.git_tools', mock_git_tools):
        return TestClient(app)

# Git Wrapper Tests
@pytest.mark.asyncio
async def test_git_run_command_success(git_config, mock_process):
    with patch('asyncio.create_subprocess_exec', return_value=mock_process) as mock_exec:
        git = Git(git_config)
        result = await git._run_command(["status"])

        assert result == "success output"
        mock_exec.assert_called_once()
        mock_process.communicate.assert_called_once()

@pytest.mark.asyncio
async def test_git_run_command_failure(git_config):
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(b"", b"error message"))
    mock_process.returncode = 1

    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        git = Git(git_config)
        with pytest.raises(GitError) as exc_info:
            await git._run_command(["status"])

        assert "error message" in str(exc_info.value)

# API Endpoint Tests
def test_create_branch_endpoint_success(client, mock_git_instance):
    """Test successful branch creation"""
    response = client.post(
        "/tools/git/create-branch",
        json={
            "branch_name": "feature/test",
            "base_branch": "main"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "branch_name" in data["data"]

    # Verify mock calls
    mock_git_instance.checkout.assert_called_once_with("main")
    mock_git_instance.pull.assert_called_once()
    mock_git_instance.create_branch.assert_called_once_with("feature/test")

def test_create_branch_endpoint_failure(client, mock_git_instance):
    """Test branch creation failure"""
    # Make checkout raise an error
    mock_git_instance.checkout.side_effect = GitError(
        "Failed to checkout", ["git", "checkout"], "error output"
    )

    response = client.post(
        "/tools/git/create-branch",
        json={
            "branch_name": "feature/test",
            "base_branch": "main"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "Failed to checkout" in data["error"]


def test_commit_files_endpoint_success(client, mock_git_instance, tmp_path):
    """Test successful file commit"""
    response = client.post(
        "/tools/git/commit-files",
        json={
            "branch_name": "feature/test",
            "files": [
                {"path": "test.py", "content": "print('hello')"}
            ],
            "commit_message": "Test commit",
            "push": True
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["commit_sha"] == "abc123"

    # Verify mock calls
    mock_git_instance.checkout.assert_called_once_with("feature/test")
    mock_git_instance.add.assert_called()
    mock_git_instance.commit.assert_called_once_with("Test commit")
    mock_git_instance.push.assert_called_once_with("feature/test")

def test_commit_files_endpoint_failure(client, mock_git_instance):
    """Test file commit failure"""
    mock_git_instance.commit.side_effect = GitError(
        "Failed to commit", ["git", "commit"], "error output"
    )

    response = client.post(
        "/tools/git/commit-files",
        json={
            "branch_name": "feature/test",
            "files": [
                {"path": "test.py", "content": "print('hello')"}
            ],
            "commit_message": "Test commit",
            "push": True
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "Failed to commit" in data["error"]


def test_commit_files_writes_files(client, mock_git_instance, tmp_path):
    """Test that files are actually written to disk"""
    test_repo = tmp_path / "test_repo"
    test_repo.mkdir()
    mock_git_instance.repo_path = test_repo

    response = client.post(
        "/tools/git/commit-files",
        json={
            "branch_name": "feature/test",
            "files": [
                {"path": "test.py", "content": "print('hello')"}
            ],
            "commit_message": "Test commit",
            "push": True
        }
    )

    # Verify file was written to the correct location
    test_file = test_repo / "test.py"
    assert test_file.exists()
    assert test_file.read_text() == "print('hello')"

    # Verify git commands were called
    mock_git_instance.add.assert_called_once_with("test.py")
    mock_git_instance.commit.assert_called_once_with("Test commit")


def test_commit_files_failure(client, mock_git_instance):
    """Test handling of commit failure"""
    mock_git_instance.commit.side_effect = GitError(
        "Failed to commit",
        ["git", "commit", "-m", "Test commit"],
        "Nothing to commit"
    )

    response = client.post(
        "/tools/git/commit-files",
        json={
            "branch_name": "feature/test",
            "files": [
                {"path": "test.py", "content": "print('hello')"}
            ],
            "commit_message": "Test commit",
            "push": True
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "Failed to commit" in data["error"]

@pytest.mark.asyncio
async def test_gittools_commit_files_direct(mock_git_instance, tmp_path):
    """Test GitTools commit_files method directly"""
    tools = GitTools(str(tmp_path))
    tools.git = mock_git_instance

    request = CommitFilesRequest(
        branch_name="feature/test",
        files=[FileContent(path="test.py", content="print('hello')")],
        commit_message="Test commit",
        push=True
    )

    response = await tools.commit_files(request)

    assert response.success is True
    assert response.data["commit_sha"] == "abc123"

    # Verify the expected calls were made
    mock_git_instance.checkout.assert_called_once_with("feature/test")
    mock_git_instance.add.assert_called()
    mock_git_instance.commit.assert_called_once_with("Test commit")
    mock_git_instance.push.assert_called_once_with("feature/test")


@pytest.mark.asyncio
async def test_git_tools_methods(mock_git_instance, tmp_path):
    """Test GitTools methods directly"""
    tools = GitTools(str(tmp_path))
    tools.git = mock_git_instance

    # Test commit_files
    request = CommitFilesRequest(
        branch_name="feature/test",
        files=[FileContent(path="test.py", content="print('hello')")],
        commit_message="Test commit",
        push=True
    )

    response = await tools.commit_files(request)
    assert response.success is True
    assert response.data["commit_sha"] == "abc123"