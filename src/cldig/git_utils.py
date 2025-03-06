import re

import shlex

import git


def first_bad_commit(
    repo: git.Repo, version_good: str, version_bad: str, predicate: str
) -> tuple[git.Commit, int]:
    """Performs a Git bisect to find the first bad commit based on a predicate command."""

    predicate_tokens = shlex.split(predicate)

    summary = repo.git._call_process("bisect", "start", version_bad, version_good)
    repo.git._call_process("bisect", "run", *predicate_tokens)
    commit = repo.git._call_process("bisect", "view", "--format=%H")
    repo.git._call_process("bisect", "log").splitlines()
    repo.git._call_process("bisect", "reset")

    num_revisions, num_steps = re.findall(r"\d+", summary)[:2]

    return repo.commit(commit), num_revisions, num_steps


def get_diff(commit: git.Commit) -> git.Diff:
    return commit.repo.git.diff(f"{commit.hexsha}^!")
