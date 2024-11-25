from dataclasses import dataclass
from pathlib import Path
import asyncio
from typing import Optional, List, Union
from loguru import logger

@dataclass
class GitConfig:
    repo_path: Path
    git_path: str = "git"

class GitError(Exception):
    """Custom exception for git command failures"""
    def __init__(self, message: str, cmd: List[str], stderr: str):
        self.cmd = cmd
        self.stderr = stderr
        super().__init__(f"{message}\nCommand: {' '.join(cmd)}\nError: {stderr}")

class Git:
    def __init__(self, config: GitConfig):
        self.config = config
        self.repo_path = config.repo_path
        logger.info(f"Initialized Git wrapper for repo: {self.repo_path}")

    async def _run_command(self, args: List[str], check: bool = True) -> str:
        """
        Run git command asynchronously using asyncio.create_subprocess_exec
        
        Args:
            args: List of command arguments
            check: Whether to raise exception on non-zero exit code
            
        Returns:
            Command output as string
        """
        cmd = [self.config.git_path, *args]
        cmd_str = " ".join(cmd)
        
        logger.info(f"Running git command: {cmd_str}")
        logger.info(f"Working directory: {self.repo_path}")
        
        try:
            # Create subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(self.repo_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for completion and get output
            stdout, stderr = await process.communicate()
            stdout_str = stdout.decode().strip()
            stderr_str = stderr.decode().strip()
            
            if stdout_str:
                logger.info(f"Command output:\n{stdout_str}")
            if stderr_str:
                logger.info(f"Command stderr:\n{stderr_str}")
                
            if check and process.returncode != 0:
                logger.error(f"Git command failed with exit code {process.returncode}")
                logger.error(f"Command: {cmd_str}")
                logger.error(f"Error output: {stderr_str}")
                raise GitError(
                    "Git command failed",
                    cmd,
                    stderr_str
                )
            
            logger.info(f"Git command completed successfully")
            return stdout_str
            
        except Exception as e:
            logger.exception(f"Error executing git command: {cmd_str}")
            raise

    async def pull(self, remote: str = "origin", branch: Optional[str] = None) -> str:
        """Pull changes from remote repository"""
        logger.info(f"Pulling from {remote}" + (f" branch {branch}" if branch else ""))
        args = ["pull", remote]
        if branch:
            args.append(branch)
        return await self._run_command(args)

    async def checkout(self, branch: str) -> str:
        """Checkout a branch"""
        logger.info(f"Checking out branch: {branch}")
        return await self._run_command(["checkout", branch])

    async def create_branch(self, branch: str) -> str:
        """Create a new branch"""
        logger.info(f"Creating new branch: {branch}")
        return await self._run_command(["checkout", "-b", branch])

    async def add(self, path: Union[str, Path]) -> str:
        """Add file(s) to git staging"""
        logger.info(f"Adding path to git: {path}")
        return await self._run_command(["add", str(path)])

    async def commit(self, message: str) -> str:
        """Create a commit with the given message"""
        logger.info(f"Creating commit with message: {message}")
        return await self._run_command(["commit", "-m", message])

    async def push(self, branch: str, remote: str = "origin") -> str:
        """Push branch to remote"""
        logger.info(f"Pushing branch {branch} to remote {remote}")
        return await self._run_command(["push", "-u", remote, branch])

    async def get_current_branch(self) -> str:
        """Get name of current branch"""
        logger.info("Getting current branch name")
        return await self._run_command(["rev-parse", "--abbrev-ref", "HEAD"])

    async def get_current_commit_sha(self) -> str:
        """Get SHA of current commit"""
        logger.info("Getting current commit SHA")
        return await self._run_command(["rev-parse", "HEAD"])

    async def status(self) -> str:
        """Get git status output"""
        logger.info("Getting git status")
        return await self._run_command(["status"])