"""Command line interface for basic-factory."""
from pathlib import Path
from typing import Optional
import typer
from basic_factory.git import Git, GitConfig
from basic_factory.github import GitHubOps, GitHubConfig

app = typer.Typer(
    name="basic-factory",
    help="AI-assisted software development workflow tools.",
    no_args_is_help=True
)

@app.command()
def hello_world(
        repo_path: Path = typer.Option(
            Path("."),
            exists=True,
            dir_okay=True,
            file_okay=False,
            help="Path to repository"
        ),
        token: Optional[str] = typer.Option(
            None,
            envvar="GITHUB_TOKEN",
            help="GitHub token (or set GITHUB_TOKEN env var)"
        ),
        owner: str = typer.Option(
            "basicmachines-co",
            help="GitHub repository owner"
        ),
        repo: str = typer.Option(
            "basic-factory",
            help="GitHub repository name"
        ),
):
    """Create hello world example with PR."""
    # Set up git operations
    git_config = GitConfig(
        repo_path=repo_path,
        author_name="Basic Factory Bot",
        author_email="bot@basicmachines.co"
    )
    git = Git(git_config)

    typer.echo("Creating hello world example...")

    # Create and commit changes
    from basic_factory.git import create_hello_world
    create_hello_world(git)

    typer.echo("✅ Created and committed changes")

    # Create PR if token provided
    if token:
        github_config = GitHubConfig(
            token=token,
            repo_owner=owner,
            repo_name=repo
        )
        github = GitHubOps(github_config)

        typer.echo("Creating pull request...")
        from basic_factory.github import create_hello_world_pr
        pr_url = create_hello_world_pr(github)
        typer.echo(f"✅ Created PR: {pr_url}")
    else:
        typer.echo("⚠️  No GitHub token provided - skipping PR creation")


@app.command()
def version():
    """Show version information."""
    from basic_factory import __version__
    typer.echo(f"Basic Factory v{__version__}")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()