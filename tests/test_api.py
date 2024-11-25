import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
from basic_factory.git import Git, GitConfig, GitError
from basic_factory.api import (
    GitTools, CreateBranchRequest, CommitFilesRequest,
    FileContent
)
from fastapi.testclient import TestClient

# Fixtures
@pytest.fixture
def git_config():
    return GitConfig(repo_path=Path("/fake/repo"))

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
def test_app():
    from basic_factory.api import app
    return app

@pytest.fixture
def client(test_app):
    return TestClient(test_app)

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

@pytest.mark.asyncio
async def test_git_pull(git_config, mock_process):
    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        git = Git(git_config)
        result = await git.pull("origin", "main")
        assert result == "success output"

@pytest.mark.asyncio
async def test_git_checkout(git_config, mock_process):
    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        git = Git(git_config)
        result = await git.checkout("main")
        assert result == "success output"

# API Endpoint Tests
def test_create_branch_endpoint_success(client, mock_github):
    with patch('basic_factory.api.Git') as mock_git:
        # Setup mock git instance
        mock_git_instance = AsyncMock()
        mock_git_instance.checkout = AsyncMock(return_value="checkout success")
        mock_git_instance.pull = AsyncMock(return_value="pull success")
        mock_git_instance.create_branch = AsyncMock(return_value="branch created")
        mock_git.return_value = mock_git_instance

        response = client.post(
            "/tools/git/create-branch",
            json={"branch_name": "feature/test", "base_branch": "main"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "branch_name" in data["data"]

def test_create_branch_endpoint_failure(client, mock_github):
    with patch('basic_factory.api.Git') as mock_git:
        # Setup mock git to raise an exception
        mock_git_instance = AsyncMock()
        mock_git_instance.checkout = AsyncMock(side_effect=GitError(
            "Failed to checkout", ["git", "checkout"], "error output"
        ))
        mock_git.return_value = mock_git_instance

        response = client.post(
            "/tools/git/create-branch",
            json={"branch_name": "feature/test", "base_branch": "main"}
        )

        assert response.status_code == 200  # We return 200 with error in response
        data = response.json()
        assert data["success"] is False
        assert data["error"] is not None

def test_commit_files_endpoint_success(client, mock_github):
    with patch('basic_factory.api.Git') as mock_git:
        mock_git_instance = AsyncMock()
        mock_git_instance.checkout = AsyncMock(return_value="checkout success")
        mock_git_instance.add = AsyncMock(return_value="add success")
        mock_git_instance.commit = AsyncMock(return_value="commit success")
        mock_git_instance.push = AsyncMock(return_value="push success")
        mock_git_instance.get_current_commit_sha = AsyncMock(return_value="abc123")
        mock_git.return_value = mock_git_instance

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

# Test file writing
def test_commit_files_writes_files(tmp_path, client, mock_github):
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    with patch('basic_factory.api.Git') as mock_git:
        mock_git_instance = AsyncMock()
        mock_git_instance.repo_path = repo_path
        for method in ['checkout', 'add', 'commit', 'push', 'get_current_commit_sha']:
            setattr(mock_git_instance, method, AsyncMock(return_value="success"))
        mock_git.return_value = mock_git_instance

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

        # Verify file was written
        test_file = repo_path / "test.py"
        assert test_file.exists()
        assert test_file.read_text() == "print('hello')"

# Integration-style test (still mocked but testing full flow)
@pytest.mark.asyncio
async def test_full_branch_and_commit_flow(tmp_path, mock_github):
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    tools = GitTools(str(repo_path))

    # Create branch
    branch_request = CreateBranchRequest(
        branch_name="feature/test",
        base_branch="main"
    )
    branch_response = await tools.create_branch(branch_request)
    assert branch_response.success

    # Commit files
    commit_request = CommitFilesRequest(
        branch_name="feature/test",
        files=[
            FileContent(path="test.py", content="print('hello')")
        ],
        commit_message="Test commit",
        push=True
    )
    commit_response = await tools.commit_files(commit_request)
    assert commit_response.success

    # Verify file exists
    test_file = repo_path / "test.py"
    assert test_file.exists()
    assert test_file.read_text() == "print('hello')"