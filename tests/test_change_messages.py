from fakit.cli import change_messages

def test_change_messages_random(temp_repo):
    repo = temp_repo
    commits = list(repo.iter_commits('HEAD'))

    old_messages = {c.message.strip() for c in commits}

    # Apply commit message changes
    change_messages(repo, commits)

    new_messages = {c.message.strip() for c in repo.iter_commits('HEAD')}

    # Assert all messages changed
    assert old_messages.isdisjoint(new_messages), f"Some commit messages were not changed: {old_messages & new_messages}"
