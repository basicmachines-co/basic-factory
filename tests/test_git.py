"""Tests for git operations."""
from pathlib import Path
import pytest
import pygit2
from basic_factory.git import Git, GitConfig


@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary git repository with initial commit."""
    # Create and init repo
    repo_path = tmp_path / "test_repo"
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

    # Create and return Git instance
    config = GitConfig(repo_path)
    return Git(config)


def test_create_hello_world(git_repo):
    """Test creating hello world example."""
    from basic_factory.git import create_hello_world

    # Create hello world files
    create_hello_world(git_repo)

    # Verify branch was created
    assert git_repo.repo.head.shorthand == "feature/hello-world"

    # Verify files exist
    hello_path = git_repo.config.repo_path / "src/basic_factory/hello.py"
    test_path = git_repo.config.repo_path / "tests/test_hello.py"
    assert hello_path.exists()
    assert test_path.exists()

    # Verify content
    assert "Hello from Basic Factory" in hello_path.read_text()
    assert "test_hello_world" in test_path.read_text()