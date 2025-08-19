# tests/test_change_dates.py
import pytest
import os
import git
from datetime import datetime
from fakit.cli import change_dates

@pytest.fixture
def temp_repo(tmp_path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    repo = git.Repo.init(repo_path)

    # Create some commits
    for i in range(3):
        f = repo_path / f"file{i}.txt"
        f.write_text(f"Content {i}")
        repo.index.add([str(f)])
        repo.index.commit(f"Commit {i}")

    return repo

def test_change_dates(temp_repo, monkeypatch):
    repo = temp_repo
    commits = list(repo.iter_commits('--all'))

    # Record original dates
    original_dates = [c.committed_datetime for c in commits]

    # Monkeypatch input to provide a 1-year offset
    monkeypatch.setattr("builtins.input", lambda prompt="": "1")

    # Run change_dates
    change_dates(repo, commits)

    # Get new dates
    new_dates = [c.committed_datetime for c in repo.iter_commits('--all')]

    # Assert that at least one commit date changed
    assert any(o != n for o, n in zip(original_dates, new_dates)), "No commit dates were changed"
