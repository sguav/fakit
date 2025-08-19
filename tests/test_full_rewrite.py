from fakit.cli import change_authors, change_messages

def test_full_rewrite(temp_repo, monkeypatch):
    repo = temp_repo
    commits = list(repo.iter_commits('HEAD'))

    # Monkeypatch input for random author changes
    monkeypatch.setattr("builtins.input", lambda prompt="": "y")

    # Call both feature functions
    change_authors(repo, commits)
    change_messages(repo, commits)

    # Collect new authors and messages
    new_authors = {(c.author.name, c.author.email) for c in repo.iter_commits('HEAD')}
    new_messages = {c.message.strip() for c in repo.iter_commits('HEAD')}

    # Old authors/messages from initial commits
    old_authors = {(c.author.name, c.author.email) for c in commits}
    old_messages = {c.message.strip() for c in commits}

    # Assert all rewritten
    assert old_authors.isdisjoint(new_authors), f"Some authors were not changed: {old_authors & new_authors}"
    assert old_messages.isdisjoint(new_messages), f"Some commit messages were not changed: {old_messages & new_messages}"
