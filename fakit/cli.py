import git
import argparse
import sys
import random
import string
from collections import OrderedDict

def list_commits(repo):
    commits = list(repo.iter_commits('--all'))
    for idx, c in enumerate(commits):
        print(f"{idx}: {c.hexsha[:8]} {c.author.name} <{c.author.email}> {c.summary}")
    return commits

def random_string(length=6):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def generate_random_author(old_name, old_email):
    domain = old_email.split("@")[-1] if "@" in old_email else "example.com"
    new_name = f"{random_string(5).capitalize()} {random_string(7).capitalize()}"
    new_email = f"{random_string(8)}@{domain}"
    return new_name, new_email

def change_authors(repo, commits):
    # Collect unique authors (preserve order)
    authors = OrderedDict()
    for c in commits:
        key = (c.author.name, c.author.email)
        authors[key] = None

    # Ask for randomization
    randomize = input("Randomize author names/emails? [y/N]: ").strip().lower() == 'y'

    replacements = {}
    for old_name, old_email in authors.keys():
        if randomize:
            new_name, new_email = generate_random_author(old_name, old_email)
            print(f"Randomized: {old_name} <{old_email}> -> {new_name} <{new_email}>")
        else:
            print(f"\nOriginal author: {old_name} <{old_email}>")
            new_name = input(f"  New name [{old_name}]: ").strip() or old_name
            new_email = input(f"  New email [{old_email}]: ").strip() or old_email
        replacements[(old_name, old_email)] = (new_name, new_email)

    # Build a single --env-filter script
    env_filter_lines = []
    for (old_name, old_email), (new_name, new_email) in replacements.items():
        if (old_name, old_email) != (new_name, new_email):
            env_filter_lines.append(f'''
if [ "$GIT_AUTHOR_NAME" = "{old_name}" ] && [ "$GIT_AUTHOR_EMAIL" = "{old_email}" ]; then
    export GIT_AUTHOR_NAME="{new_name}"
    export GIT_AUTHOR_EMAIL="{new_email}"
    export GIT_COMMITTER_NAME="{new_name}"
    export GIT_COMMITTER_EMAIL="{new_email}"
fi
''')
    env_filter_script = "\n".join(env_filter_lines)

    if env_filter_script.strip() == "":
        print("No changes to apply. Exiting.")
        return

    print("\nRewriting commits in a single pass... (destructive, make a backup!)")
    repo.git.filter_branch(
        "--env-filter", env_filter_script,
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
