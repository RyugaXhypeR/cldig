import click
import git
from rich.panel import Panel
from rich.markdown import Markdown
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Column, Table

from .git_utils import first_bad_commit
from .llm import suggest

console = Console()


@click.command()
@click.option("--good", "-g", required=True, help="Good state of repository")
@click.option("--bad", "-b", required=True, help="Bad state of repository")
@click.option("--test", "-t", required=True, help="Test command")
@click.option("--root", "-r", default=".", help="Git repository root")
@click.option("--diff-only", "-d", is_flag=True, help="Only show `git diff` output")
def cli(
    good: str, bad: str, test: str, root: str, diff_only: bool
) -> None:
    repo = git.Repo(root)
    commit, num_revs, num_steps = first_bad_commit(repo, good, bad, test)

    console.print(
        f"[bold blue]Scanned {num_revs} revisions in {num_steps} steps.[/bold blue]"
    )
    console.print(
        f"[bold green]✔ Found the first bad commit:[/bold green] [bold yellow]{commit.hexsha}[/bold yellow]"
    )

    show_stat(commit)
    show_diff(commit)

    if diff_only:
        return

    show_suggestion(commit)


def show_diff(commit: git.Commit) -> None:
    """Display changes made in `commit`"""

    diff_text = commit.repo.git.show(commit.hexsha)
    syntax = Syntax(diff_text, "diff", theme="monokai", word_wrap=True)
    console.print(syntax)


def show_stat(commit: git.Commit) -> None:
    """Display summary of changed files in `commit`"""

    table = Table(
        Column(header="File", justify="left", style="cyan"),
        Column(header="Insertions", justify="right", style="green"),
        Column(header="Deletions", justify="right", style="red"),
        Column(header="Lines", justify="right", style="magenta"),
        title="[bold]Summary of Changes[/bold]",
    )

    for file, details in commit.stats.files.items():
        table.add_row(
            str(file),
            str(details.get("insertions", 0)),
            str(details.get("deletions", 0)),
            str(details.get("lines", 0)),
        )

    console.print(table)


def show_suggestion(commit: git.Commit) -> None:
    """Display the AI-generated suggestion for a commit in a nice format."""

    suggestion = suggest(commit)

    if not suggestion:
        console.print("[bold yellow]No suggestions found.[/bold yellow]")
        return

    panel = Panel(
        Markdown(suggestion),
        title=f"[bold cyan]Suggestion for commit {commit.hexsha[:7]}[/bold cyan]",
        expand=False,
    )

    console.print(panel)
