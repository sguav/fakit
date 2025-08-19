from fakit.cli import change_authors
import pytest

def test_change_authors_random(temp_repo, monkeypatch):
    repo = temp_repo
    commits = list(repo.iter_commits('HEAD'))

    # Monkeypatch input to always answer 'y' for randomization
    monkeypatch.setattr("builtins.input", lambda prompt="": "y")

    old_authors = {(c.author.name, c.author.email) for c in commits}

    # Apply author changes
    change_authors(repo, commits)

    new_authors = {(c.author.name, c.author.email) for c in repo.iter_commits('HEAD')}

    # Assert all authors changed
    assert old_authors.isdisjoint(new_authors), f"Some authors were not changed: {old_authors & new_authors}"
