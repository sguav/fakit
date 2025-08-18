import argparse
import git
import sys
from collections import OrderedDict

def list_commits(repo):
    commits = list(repo.iter_commits('--all'))
    for idx, c in enumerate(commits):
        print(f"{idx}: {c.hexsha[:8]} {c.author.name} <{c.author.email}> {c.summary}")
    return commits

def change_authors(repo, commits):
    # Collect unique authors (preserve order)
    authors = OrderedDict()
    for c in commits:
        key = (c.author.name, c.author.email)
        authors[key] = None

    replacements = {}
    print("\nProvide new author info (leave blank to skip/change nothing):")
    for name, email in authors.keys():
        print(f"\nOriginal author: {name} <{email}>")
        new_name = input(f"  New name [{name}]: ").strip() or name
        new_email = input(f"  New email [{email}]: ").strip() or email
        replacements[(name, email)] = (new_name, new_email)

    # Apply changes via git filter-branch
    print("\nRewriting commits... (this is destructive, make a backup first!)")
    for old, new in replacements.items():
        old_name, old_email = old
        new_name, new_email = new
        if (old_name, old_email) == (new_name, new_email):
            continue  # skip unchanged
        repo.git.filter_branch(
            "--env-filter",
            f'''
if [ "$GIT_AUTHOR_NAME" = "{old_name}" ] && [ "$GIT_AUTHOR_EMAIL" = "{old_email}" ]; then
    export GIT_AUTHOR_NAME="{new_name}"
    export GIT_AUTHOR_EMAIL="{new_email}"
    export GIT_COMMITTER_NAME="{new_name}"
    export GIT_COMMITTER_EMAIL="{new_email}"
fi
''',
            "--tag-name-filter", "cat", "--", "--all"
        )

    print("\nDone. Remember: force-push if it's a remote repo!")

def main():
    parser = argparse.ArgumentParser(description="Fakit - Fake git repo automation tool")
    parser.add_argument("path", help="Path to git repository")
    args = parser.parse_args()

    try:
        repo = git.Repo(args.path)
    except git.exc.InvalidGitRepositoryError:
        print("Error: not a git repository.")
        sys.exit(1)

    commits = list_commits(repo)

    print("\nChoose operation:")
    print("1. Change authors")
    choice = input("Select [1]: ").strip() or "1"

    if choice == "1":
        change_authors(repo, commits)
    else:
        print("Invalid choice. Exiting.")
