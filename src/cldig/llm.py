from textwrap import dedent

from openai import OpenAI
import git

client = OpenAI()


class LLMSuggestionError(Exception):
    ...


def suggest(commit: git.Commit) -> str:
    """Generate a suggestion for a given commit using OpenAI."""

    commit_message = commit.message.strip()
    diff_text = commit.repo.git.show(commit.hexsha, "--pretty=format:", "--unified=0")

    prompt = dedent(
        f"""Below is the first bad commit that caused a test-case to fail.
        Your job is to try and identify the change that caused the error
        and create a short suggestion on how to fix it.

        Commit message:\n{commit_message!r}
        Diff text:\n{diff_text}
        """
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    suggestion = response.choices[0].message.content
    if suggestion is None:
        raise LLMSuggestionError("Couldn't generate suggestion!")

    return suggestion.strip()
