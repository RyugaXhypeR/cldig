import re
import shlex

import git

REVISION_STEPS_RE = re.compile(r"(?P<revisions>\d+) revisions.*(?P<steps>\d+) steps")


def first_bad_commit(
    repo: git.Repo, version_good: str, version_bad: str, predicate: str
) -> tuple[git.Commit, int, int]:
    """Performs a Git bisect to find the first bad commit based on a predicate command."""

    predicate_tokens = shlex.split(predicate)

    summary = repo.git.bisect("start", version_bad, version_good)
    repo.git.bisect("run", *predicate_tokens)
    commit = repo.git.bisect("view", "--format=%H")
    repo.git.bisect("reset")

    if (match := REVISION_STEPS_RE.search(summary)) is None:
        raise git.CommandError("Unable to extract number of revisions and steps")

    return repo.commit(commit), int(match["revisions"]), int(match["steps"])
