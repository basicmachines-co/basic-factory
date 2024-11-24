"""Tests for GitHub operations."""
import os
import pytest
from basic_factory.github import GitHubConfig, GitHubOps


@pytest.fixture
def github_ops():
    """Create GitHubOps instance using environment variables."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        pytest.skip("GITHUB_TOKEN environment variable not set")

    config = GitHubConfig(
        token=token,
        repo_owner="basicmachines-co",
        repo_name="basic-factory"
    )
    return GitHubOps(config)


def test_create_pr(github_ops):
    """Test creating a pull request.

    Note: This test requires:
    1. GITHUB_TOKEN environment variable set
    2. feature/hello-world branch pushed to GitHub
    """
    pr_url = github_ops.create_pull_request(
        title="Test PR: Hello World",
        body="Testing PR creation via GitHub API",
        head_branch="feature/hello-world"
    )

    assert "github.com" in pr_url
    assert "/pull/" in pr_url