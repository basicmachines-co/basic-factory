"""GitHub API operations for basic-factory."""
from dataclasses import dataclass
from github import Github
from github.Repository import Repository


@dataclass
class GitHubConfig:
    """Configuration for GitHub operations."""
    token: str
    repo_owner: str
    repo_name: str


class GitHubOps:
    """GitHub API operations."""

    def __init__(self, config: GitHubConfig):
        self.config = config
        self.github = Github(config.token)
        self.repo = self.github.get_repo(f"{config.repo_owner}/{config.repo_name}")

    def create_pull_request(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main"
    ) -> str:
        """Create a pull request and return its URL."""
        pr = self.repo.create_pull(
            title=title,
            body=body,
            head=head_branch,
            base=base_branch
        )
        return pr.html_url


def create_hello_world_pr(github: GitHubOps) -> str:
    """Create pull request for hello world example."""
    title = "Add hello world function"
    body = """This PR adds a basic hello world function with tests.

Changes:
- Add hello_world() function in hello.py
- Add corresponding test in test_hello.py"""

    return github.create_pull_request(
        title=title,
        body=body,
        head_branch="feature/hello-world"
    )