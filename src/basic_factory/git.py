"""Git operations for basic-factory."""
from pathlib import Path
from typing import Protocol
from dataclasses import dataclass
import pygit2


@dataclass
class GitConfig:
    """Configuration for git operations."""
    repo_path: Path
    author_name: str = "Basic Factory"
    author_email: str = "bot@basicmachines.co"


class GitOperations(Protocol):
    """Protocol defining required git operations."""
    def create_branch(self, name: str) -> None:
        """Create and checkout new branch."""
        ...

    def add_file(self, path: str, content: str) -> None:
        """Add or update file with content."""
        ...

    def commit_changes(self, message: str) -> str:
        """Commit staged changes and return commit hash."""
        ...


class Git:
    """Git operations implementation using pygit2."""

    def __init__(self, config: GitConfig):
        self.config = config
        self.repo = pygit2.Repository(str(config.repo_path))

    def create_branch(self, name: str) -> None:
        """Create and checkout a new branch from current HEAD."""
        # Get current HEAD commit
        head = self.repo.head.target
        ref = self.repo.create_branch(name, self.repo.get(head))

        # Checkout the new branch
        self.repo.checkout(ref)

    def add_file(self, path: str, content: str) -> None:
        """Add or update a file with the given content."""
        # Ensure parent directories exist
        full_path = self.config.repo_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file content
        full_path.write_text(content)

        # Stage the file
        index = self.repo.index
        index.add(path)
        index.write()

    def commit_changes(self, message: str) -> str:
        """Commit staged changes and return the commit hash."""
        # Get current user signature
        signature = pygit2.Signature(
            self.config.author_name,
            self.config.author_email
        )

        # Write the index tree
        index = self.repo.index
        tree = index.write_tree()

        # Create the commit
        parent = [self.repo.head.target]
        commit_hash = self.repo.create_commit(
            'HEAD',
            signature,
            signature,
            message,
            tree,
            parent
        )

        return str(commit_hash)


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