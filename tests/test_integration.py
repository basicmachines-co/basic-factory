"""Integration tests using actual repository."""
from pathlib import Path
import pytest
from basic_factory.git import Git, GitConfig

pytestmark = pytest.mark.integration

@pytest.fixture
def working_repo():
    """Create Git instance using current repository."""
    # Get the repo root (where .git is located)
    repo_path = Path.cwd()
    if not (repo_path / ".git").exists():
        pytest.skip("Must be run from repository root")

    config = GitConfig(
        repo_path=repo_path,
        author_name="Basic Factory Bot",
        author_email="bot@basicmachines.co"
    )
    return Git(config)


# def test_create_hello_world_integration(working_repo):
#     """Test creating hello world example in actual repo."""
#     from basic_factory.git import create_hello_world
#
#     # Create hello world files
#     create_hello_world(working_repo)
#
#     try:
#         # Verify branch was created
#         assert working_repo.repo.head.shorthand == "feature/hello-world"
#
#         # Verify files exist
#         hello_path = working_repo.config.repo_path / "src/basic_factory/hello.py"
#         test_path = working_repo.config.repo_path / "tests/test_hello.py"
#         assert hello_path.exists()
#         assert test_path.exists()
#
#         # Verify content
#         assert "Hello from Basic Factory" in hello_path.read_text()
#         assert "test_hello_world" in test_path.read_text()
#
#     finally:
#         # Cleanup: Switch back to main branch
#         # Note: In real usage you might want to keep the branch,
#         # but for testing we'll clean up
#         working_repo._run_git("checkout", "main")
#         #working_repo._run_git("branch", "-D", "feature/hello-world")