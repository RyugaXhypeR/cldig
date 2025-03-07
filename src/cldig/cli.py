from pathlib import Path

import click
import git
from rich.align import Align
from rich.console import Console, Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Column, Table
from rich.tree import Tree

from .git_utils import first_bad_commit
from .llm import suggest

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

    console.print(
        f"[bold blue]Scanned {num_revs} revisions in {num_steps} steps.[/bold blue]"
    )
    console.print(
        f"[bold green]✔ Found the first bad commit:[/bold green] [bold yellow]{commit.hexsha}[/bold yellow]"
    )

    show_diff_view(commit)

    if diff_only:
        return

    show_suggestion(commit)


def show_diff_view(commit: git.Commit) -> None:
    """Display the diff view containing summary of changes made in `commit`
    along with a diff tree.
    """

    working_dir = Path(commit.repo.working_dir).name

    tree = Tree(label="Diff Tree", guide_style="bright_black", hide_root=True)
    root = tree.add(
        f":file_folder: [bold bright_yellow]{working_dir}[/]", guide_style="bright_blue"
    )

    for filepath in commit.stats.files:
        *parts, file = Path(filepath).parts
        node = root

        for part in parts:
            node = node.add(f":file_folder: [bold cyan]{part}[/]")

        diff_text = commit.repo.git.show(commit.hexsha, "--", filepath)
        syntax = Syntax(diff_text, "diff", theme="monokai", word_wrap=True)
        node.add(
            Group(
                f"📄 [bold magenta]{file}[/]",
                Panel(syntax, border_style="bright_black"),
            )
        )

    stat_table = get_stat_table(commit)
    console.print(
        Panel(
            Group(Align(stat_table, align="center"), tree),
            title="[b green]Diff View[/]",
        )
    )


def get_stat_table(commit: git.Commit) -> Table:
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

    return table


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
