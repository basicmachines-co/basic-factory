import pytest
from pathlib import Path
from unittest.mock import AsyncMock
from basic_factory.api import (
    GitTools, CommitFilesRequest, FileContent, app, GitResponse, get_git_tools
)
from fastapi.testclient import TestClient

from basic_factory.git import GitConfig, Git


# Fixtures
@pytest.fixture
def mock_git_tools():
    """Create a mock GitTools with all needed methods"""
    mock = AsyncMock()

    # Configure common responses
    mock.commit_files = AsyncMock(return_value=GitResponse(
        success=True,
        message="Files committed successfully",
        data={
            "branch_name": "feature/test",
            "commit_sha": "abc123",
            "pushed": True
        }
    ))

    mock.create_branch = AsyncMock(return_value=GitResponse(
        success=True,
        message="Branch created successfully",
        data={
            "branch_name": "feature/test"
        }
    ))

    return mock

@pytest.fixture
def client(mock_git_tools):
    """Create test client with dependency override"""
    app.dependency_overrides[get_git_tools] = lambda: mock_git_tools
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

# API Endpoint Tests
def test_create_branch_endpoint_success(client, mock_git_tools):
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

    mock_git_tools.create_branch.assert_called_once()

def test_create_branch_endpoint_failure(client, mock_git_tools):
    """Test branch creation failure"""
    # Configure mock to return error response
    mock_git_tools.create_branch = AsyncMock(return_value=GitResponse(
        success=False,
        message="Failed to create branch",
        error="Failed to checkout"
    ))

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

def test_commit_files_endpoint_success(client, mock_git_tools):
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

    mock_git_tools.commit_files.assert_called_once()

def test_commit_files_endpoint_failure(client, mock_git_tools):
    """Test file commit failure"""
    mock_git_tools.commit_files = AsyncMock(return_value=GitResponse(
        success=False,
        message="Failed to commit files",
        error="Failed to commit"
    ))

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

# Integration Tests for GitTools
@pytest.mark.asyncio
async def test_gittools_integration():
    """Test GitTools with real file operations"""
    # Create a temporary directory
    tmp_path = Path("/tmp/test_repo")
    tmp_path.mkdir(exist_ok=True)

    try:
        # Initialize git repo
        git_config = GitConfig(repo_path=tmp_path)
        git = Git(git_config)

        # Initialize git repo and configure it
        await git._run_command(["init"])
        await git._run_command(["config", "--local", "user.name", "Test User"])
        await git._run_command(["config", "--local", "user.email", "test@example.com"])

        # Create initial commit so we have a HEAD reference
        await git._run_command(["commit", "--allow-empty", "-m", "Initial commit"])

        # Create the feature branch
        await git._run_command(["checkout", "-b", "feature/test"])

        # Now create our GitTools instance
        tools = GitTools(str(tmp_path))

        # Test creating and committing files
        request = CommitFilesRequest(
            branch_name="feature/test",
            files=[FileContent(path="test.py", content="print('hello')")],
            commit_message="Test commit",
            push=False  # Don't push in test
        )

        response = await tools.commit_files(request)
        assert response.success is True

        # Verify file was written
        test_file = tmp_path / "test.py"
        assert test_file.exists()
        assert test_file.read_text() == "print('hello')"

        # Verify git status
        status = await git._run_command(["status"])
        assert "nothing to commit" in status.lower()  # Should be clean after commit

        # Verify we're on the right branch
        branch = await git._run_command(["rev-parse", "--abbrev-ref", "HEAD"])
        assert branch == "feature/test"

    finally:
        # Cleanup
        import shutil
        shutil.rmtree(tmp_path)

# Direct Tests of GitTools Methods
@pytest.mark.asyncio
async def test_gittools_methods(mock_git_tools):
    """Test GitTools methods directly"""
    request = CommitFilesRequest(
        branch_name="feature/test",
        files=[FileContent(path="test.py", content="print('hello')")],
        commit_message="Test commit",
        push=True
    )

    response = await mock_git_tools.commit_files(request)
    assert response.success is True
    assert response.data["commit_sha"] == "abc123"