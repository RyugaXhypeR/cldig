import click


@click.command()
@click.option("--good", "-g", default=None, help="Good state of repository")
@click.option("--bad", "-b", default=None, help="Bad state of repository")
@click.option(
    "--cmd", "--run", "-c", "-r", default=None, help="Predicate to test against"
)
@click.option("--path", "-p", default=".", help="Path of repository")
@click.option("--openai-key", "-k", default=None, help="OpenAI API key")
@click.option("--diff-only", "-d", default=False, help="Only show `git diff` output")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def cli(
    good: str | None,
    bad: str | None,
    cmd: str | None,
    path: str,
    openai_key: str,
    diff_only: bool,
    verbose: str,
) -> None:
    print(
        f"Command constructued: {good=} {bad=} {cmd=} {path=} {openai_key=} {diff_only=} {verbose=}"
    )
