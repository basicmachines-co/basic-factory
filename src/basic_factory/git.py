"""Git operations for basic-factory."""
from pathlib import Path
import subprocess
from typing import Protocol
from dataclasses import dataclass


@dataclass
class GitConfig:
    """Configuration for git operations."""
    repo_path: Path
    author_name: str = "Basic Factory"
    author_email: str = "bot@basicmachines.co"


class Git:
    """Git operations implementation using git CLI."""

    def __init__(self, config: GitConfig):
        self.config = config

    def _run_git(self, *args: str) -> str:
        """Run git command in repo directory."""
        result = subprocess.run(
            ["git", *args],
            cwd=self.config.repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()

    def get_current_branch(self) -> str:
        """Get name of current branch."""
        return self._run_git("branch", "--show-current")

    def create_branch(self, name: str) -> None:
        """Create and checkout a new branch from current HEAD."""
        self._run_git("checkout", "-b", name)

    def checkout_branch(self, name: str) -> None:
        """Checkout existing branch."""
        self._run_git("checkout", name)

    def add_file(self, path: str, content: str) -> None:
        """Add or update a file with the given content."""
        full_path = self.config.repo_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        self._run_git("add", path)

    def commit_changes(self, message: str) -> str:
        """Commit staged changes and return the commit hash."""
        self._run_git("commit", "-m", message)
        return self._run_git("rev-parse", "HEAD")

    def push_branch(self, branch_name: str, remote: str = "origin") -> None:
        """Push branch to remote."""
        try:
            self._run_git("push", "-u", remote, branch_name)
        except subprocess.CalledProcessError as e:
            if "remote rejected" in e.stderr:
                raise RuntimeError(f"Failed to push to remote: {e.stderr}")
            raise


def create_hello_world(git: Git, stay_on_branch: bool = False) -> tuple[str, str]:
    """Create hello world example files.

    Args:
        git: Git instance to use for operations
        stay_on_branch: If True, remain on created branch

    Returns:
        Tuple of (original_branch, new_branch)
    """
    original_branch = git.get_current_branch()
    new_branch = "feature/hello-world"

    # Create and switch to feature branch
    git.create_branch(new_branch)

    # Add hello.py
    hello_content = '''"""Hello world module."""

def hello_world() -> str:
    """Return a friendly greeting."""
    return "Hello from Basic Factory!"
'''
    git.add_file("src/basic_factory/hello.py", hello_content)

    # Add test_hello.py
    test_content = '''"""Test hello world module."""
from basic_factory.hello import hello_world

def test_hello_world():
    """Test hello_world function."""
    assert hello_world() == "Hello from Basic Factory!"
'''
    git.add_file("tests/test_hello.py", test_content)

    # Commit changes
    git.commit_changes("Add hello world function with tests")

    # Push branch to remote
    git.push_branch(new_branch)

    # Return to original branch unless asked to stay
    if not stay_on_branch:
        git.checkout_branch(original_branch)

    return original_branch, new_branch