import sys
from typing import Dict, List, Optional, Union
from pydantic import BaseModel
from pathlib import Path
from basic_factory.git import Git, GitConfig
from github import Github
import os

from loguru import logger

# Request/Response Models
class FileContent(BaseModel):
    path: str
    content: str

class CreateBranchRequest(BaseModel):
    branch_name: str
    base_branch: str = "main"

class CommitFilesRequest(BaseModel):
    branch_name: str
    files: List[FileContent]
    commit_message: str
    push: bool = True  # Option to push after commit

class PushBranchRequest(BaseModel):
    branch_name: str

class CreatePRRequest(BaseModel):
    title: str
    description: str
    branch_name: str
    base_branch: str = "main"

class WorkflowStatusRequest(BaseModel):
    pr_number: int

class GitResponse(BaseModel):
    success: bool
    message: str
    error: Optional[str] = None
    data: Optional[Dict] = None

# Tool Implementations
class GitTools:
    def __init__(self, repo_path: Union[str, Path] = "."):
        self.repo_path = Path(repo_path)
        self.git = Git(GitConfig(self.repo_path))
        self.github = Github(os.getenv("GITHUB_TOKEN"))
        self.repo_name = os.getenv("GITHUB_REPO")  # e.g. "basicmachines-co/basic-factory"

    async def create_branch(self, request: CreateBranchRequest) -> GitResponse:
        """Create a new branch from base branch"""
        try:
            await self.git.checkout(request.base_branch)
            await self.git.pull()  # Ensure base is up to date
            await self.git.create_branch(request.branch_name)
            await self.git.checkout(request.branch_name)

            return GitResponse(
                success=True,
                message=f"Created and checked out branch: {request.branch_name}",
                data={"branch_name": request.branch_name}
            )
        except Exception as e:
            return GitResponse(
                success=False,
                message="Failed to create branch",
                error=str(e)
            )

    async def commit_files(self, request: CommitFilesRequest) -> GitResponse:
        """Add and commit files to a branch, optionally pushing to remote"""
        try:
            # Ensure we're on the right branch
            await self.git.checkout(request.branch_name)

            # Write and add files
            for file in request.files:
                file_path = self.repo_path / file.path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(file.content)
                await self.git.add(file.path)

            # Commit changes
            await self.git.commit(request.commit_message)
            commit_sha = await self.git.get_current_commit_sha()

            # Push if requested
            if request.push:
                await self.git.push(request.branch_name)

            return GitResponse(
                success=True,
                message=f"Committed files to branch: {request.branch_name}",
                data={
                    "branch_name": request.branch_name,
                    "commit_sha": commit_sha,
                    "pushed": request.push
                }
            )
        except Exception as e:
            return GitResponse(
                success=False,
                message="Failed to commit files",
                error=str(e)
            )

    async def push_branch(self, request: PushBranchRequest) -> GitResponse:
        """Push a branch to the remote repository"""
        try:
            await self.git.push(request.branch_name)
            return GitResponse(
                success=True,
                message=f"Pushed branch: {request.branch_name}",
                data={"branch_name": request.branch_name}
            )
        except Exception as e:
            return GitResponse(
                success=False,
                message="Failed to push branch",
                error=str(e)
            )

    async def create_pull_request(self, request: CreatePRRequest) -> GitResponse:
        """Create a pull request on GitHub"""
        try:
            repo = self.github.get_repo(self.repo_name)
            pr = repo.create_pull(
                title=request.title,
                body=request.description,
                head=request.branch_name,
                base=request.base_branch
            )

            return GitResponse(
                success=True,
                message=f"Created pull request: {pr.title}",
                data={
                    "pr_number": pr.number,
                    "pr_url": pr.html_url,
                    "branch": request.branch_name
                }
            )
        except Exception as e:
            return GitResponse(
                success=False,
                message="Failed to create pull request",
                error=str(e)
            )

    async def get_workflow_status(self, request: WorkflowStatusRequest) -> GitResponse:
        """Get status of GitHub Actions workflows for a PR"""
        try:
            repo = self.github.get_repo(self.repo_name)
            pr = repo.get_pull(request.pr_number)

            # Get workflow runs for the PR's head commit
            runs = list(repo.get_workflow_runs(
                head_sha=pr.head.sha
            ))

            status_info = [{
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "url": run.html_url
            } for run in runs]

            return GitResponse(
                success=True,
                message=f"Retrieved workflow status for PR #{request.pr_number}",
                data={
                    "pr_number": request.pr_number,
                    "workflow_runs": status_info
                }
            )
        except Exception as e:
            return GitResponse(
                success=False,
                message="Failed to get workflow status",
                error=str(e)
            )

# FastAPI endpoints
from fastapi import FastAPI


# Configure loguru
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "basic_factory.log",  # Log to file as well
    rotation="500 MB",    # Rotate when file reaches 500MB
    retention="10 days",  # Keep logs for 10 days
    level="INFO"
)

app = FastAPI()
git_tools = GitTools()

@app.post("/tools/git/create-branch")
async def create_branch_endpoint(request: CreateBranchRequest) -> GitResponse:
    return await git_tools.create_branch(request)

@app.post("/tools/git/commit-files")
async def commit_files_endpoint(request: CommitFilesRequest) -> GitResponse:
    return await git_tools.commit_files(request)

@app.post("/tools/git/push-branch")
async def push_branch_endpoint(request: PushBranchRequest) -> GitResponse:
    return await git_tools.push_branch(request)

@app.post("/tools/git/create-pr")
async def create_pr_endpoint(request: CreatePRRequest) -> GitResponse:
    return await git_tools.create_pull_request(request)

@app.post("/tools/git/workflow-status")
async def workflow_status_endpoint(request: WorkflowStatusRequest) -> GitResponse:
    return await git_tools.get_workflow_status(request)