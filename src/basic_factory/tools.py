"""Tools for Claude to interact with git repos."""
from dataclasses import dataclass
from typing import List
from basic_factory.git import Git
from basic_factory.github import GitHub

@dataclass
class FileChange:
    """File content to add or modify."""
    path: str
    content: str

@dataclass
class PullRequest:
    """Pull request to create."""
    branch: str
    title: str
    body: str
    files: List[FileChange]

async def create_pull_request(
        git: Git,
        github: GitHub,
        pr: PullRequest,
        base_branch: str = "main"
) -> str:
    """Create a pull request with the specified changes."""
    # Create new branch
    git.create_branch(pr.branch)

    # Add/modify files
    for file in pr.files:
        git.add_file(file.path, file.content)

    # Commit and push
    git.commit_changes(pr.title)
    git.push_branch(pr.branch)

    # Create PR
    pr_number = await github.create_pr(
        title=pr.title,
        body=pr.body,
        head=pr.branch,
        base=base_branch
    )

    return pr_number

# Define the tool schema for Claude
TOOL_SCHEMA = {
    "name": "create_pull_request",
    "description": "Create a GitHub pull request with code changes",
    "parameters": {
        "type": "object",
        "properties": {
            "branch": {"type": "string", "description": "Name of the feature branch"},
            "title": {"type": "string", "description": "PR title"},
            "body": {"type": "string", "description": "PR description"},
            "files": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"}
                    }
                }
            }
        },
        "required": ["branch", "title", "body", "files"]
    }
}