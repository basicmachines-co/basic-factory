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
        stay_on_branch: bool = typer.Option(
            False,
            "--stay-on-branch",
            "-s",
            help="Stay on the created feature branch"
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

    print("Creating hello world example...")

    try:
        # Create, commit, and push changes
        from basic_factory.git import create_hello_world
        original_branch, new_branch = create_hello_world(git, stay_on_branch)

        print("✅ Created, committed, and pushed changes")

        if stay_on_branch:
            print(f"[yellow]ℹ️  Staying on branch: {new_branch}[/yellow]")
        else:
            print(f"[green]↩️  Returned to branch: {original_branch}[/green]")

        # Create PR if token provided
        if token:
            github_config = GitHubConfig(
                token=token,
                repo_owner=owner,
                repo_name=repo
            )
            github = GitHubOps(github_config)

            print("Creating pull request...")
            from basic_factory.github import create_hello_world_pr
            pr_url = create_hello_world_pr(github)
            print(f"✅ Created PR: {pr_url}")
        else:
            print("[yellow]⚠️  No GitHub token provided - skipping PR creation[/yellow]")

    except Exception as e:
        print(f"[red]❌ Error: {str(e)}[/red]", err=True)
        raise typer.Exit(1)


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