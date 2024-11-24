"""Tests for git operations."""
from pathlib import Path
import pytest
import pygit2
from basic_factory.git import Git, GitConfig


@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary git repository with initial commit."""
    # Create source and remote repo paths
    repo_path = tmp_path / "test_repo"
    remote_path = tmp_path / "remote_repo"

    # Initialize remote repo first (bare repository)
    remote_repo = pygit2.init_repository(str(remote_path), bare=True)

    # Create and init source repo
    repo_path.mkdir()
    repo = pygit2.init_repository(str(repo_path))

    # Create initial commit so we have a HEAD reference
    signature = pygit2.Signature("Test User", "test@example.com")

    # Create empty tree for initial commit
    tree = repo.TreeBuilder().write()

    # Create initial commit
    repo.create_commit(
        'refs/heads/main',  # This creates the main branch
        signature,
        signature,
        "Initial commit",
        tree,
        []  # No parent commits
    )

    # Add remote
    repo.remotes.create("origin", str(remote_path))

    # Create and return Git instance
    config = GitConfig(repo_path)
    return Git(config)


def test_create_hello_world(git_repo):
    """Test creating hello world example."""
    from basic_factory.git import create_hello_world

    # Create hello world files
    create_hello_world(git_repo, stay_on_branch=True)  # Stay on the new branch

    # Verify branch was created
    current_branch = git_repo.get_current_branch()
    assert current_branch == "feature/hello-world"

    # Verify files exist
    hello_path = git_repo.config.repo_path / "src/basic_factory/hello.py"
    test_path = git_repo.config.repo_path / "tests/test_hello.py"
    assert hello_path.exists()
    assert test_path.exists()

    # Verify content
    assert "Hello from Basic Factory" in hello_path.read_text()
    assert "test_hello_world" in test_path.read_text()