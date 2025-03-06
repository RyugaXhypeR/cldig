import click
import git

from rich.console import Console
from rich.table import Table, Column
from rich.panel import Panel
from rich.syntax import Syntax

from .git_utils import first_bad_commit, get_diff

console = Console()


@click.command()
@click.option("--good", "-g", required=True, help="Good state of repository")
@click.option("--bad", "-b", required=True, help="Bad state of repository")
@click.option("--test", "-t", required=True, help="Test command")
@click.option("--root", "-r", default=".", help="Git repository root")
@click.option("--diff-only", "-d", is_flag=True, help="Only show `git diff` output")
def cli(good: str, bad: str, test: str, root: str, diff_only: bool) -> None:
    repo = git.Repo(root)
    commit, num_revs, num_steps = first_bad_commit(repo, good, bad, test)

    console.print(f"[bold blue]Scanned {num_revs} revisions in {num_steps} steps.[/bold blue]")
    console.print(
        f"[bold green]✔ Found the first bad commit:[/bold green] [bold yellow]{commit.hexsha}[/bold yellow]"
    )

    show_stat(commit)
    show_diff(commit)

    if diff_only:
        return


def show_diff(commit: git.Commit) -> None:
    """Returns a concise Rich panel with the git diff output for the commit."""
    diff_text = get_diff(commit)

    if not diff_text.strip():
        return Panel(
            "[yellow]No diff available for this commit.[/yellow]",
            title="Diff",
            border_style="red",
        )

    syntax = Syntax(diff_text, "diff", theme="monokai", word_wrap=True)
    console.print(syntax)


def show_stat(commit: git.Commit) -> None:
    """Returns a Rich table summarizing the commit changes."""
    table = Table(
        Column(header="File", justify="left", style="cyan"),
        Column(header="Insertions", justify="right", style="green"),
        Column(header="Deletions", justify="right", style="red"),
        Column(header="Lines", justify="right", style="magenta"),
        title="[bold]Summary of Changes[/bold]",
    )

    for file, details in commit.stats.files.items():
        table.add_row(
            file,
            str(details.get("insertions", 0)),
            str(details.get("deletions", 0)),
            str(details.get("lines", 0)),
        )

    console.print(table)
