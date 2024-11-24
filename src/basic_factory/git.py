"""Git operations for basic-factory."""
from pathlib import Path
import subprocess
from typing import Protocol
from dataclasses import dataclass
import pygit2


@dataclass
class GitConfig:
    """Configuration for git operations."""
    repo_path: Path
    author_name: str = "Basic Factory"
    author_email: str = "bot@basicmachines.co"


class Git:
    """Git operations implementation using pygit2 and git CLI."""

    def __init__(self, config: GitConfig):
        self.config = config
        self.repo = pygit2.Repository(str(config.repo_path))

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

    def create_branch(self, name: str) -> None:
        """Create and checkout a new branch from current HEAD."""
        # Create and checkout branch using git commands
        self._run_git("checkout", "-b", name)

    def add_file(self, path: str, content: str) -> None:
        """Add or update a file with the given content."""
        # Ensure parent directories exist
        full_path = self.config.repo_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file content
        full_path.write_text(content)

        # Stage the file using git command
        self._run_git("add", path)

    def commit_changes(self, message: str) -> str:
        """Commit staged changes and return the commit hash."""
        # Create commit using git command
        self._run_git("commit", "-m", message)

        # Get and return commit hash
        return self._run_git("rev-parse", "HEAD")


def create_hello_world(git: Git) -> None:
    """Create hello world example files."""
    # Create and switch to feature branch
    git.create_branch("feature/hello-world")

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