import argparse
import git
import markovify
import os
import random
import sys
from collections import OrderedDict
from faker import Faker


def list_commits(repo):
    commits = list(repo.iter_commits('--all'))
    for idx, c in enumerate(commits):
        print(f"{idx}: {c.hexsha[:8]} {c.author.name} <{c.author.email}> {c.summary}")
    return commits


def make_email_from_name(set_name: str):
    first_name, last_name = set_name.lower().split()
    return f"{first_name}.{last_name}@{Faker().domain_name()}"


def generate_random_author(old_name, old_email):
    new_name = Faker().name()
    new_email = make_email_from_name(new_name)
    return new_name, new_email


def get_commit_markov_model():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    commits_file = os.path.join(base_dir, "good_commits.txt")
    with open(commits_file, encoding="utf-8") as f:
        nltext = f.read()
    return markovify.NewlineText(nltext)


def generate_random_git_message():
    global commit_msg_model
    return commit_msg_model.make_sentence() or "Fix minor typos"


def change_authors(repo, commits):
    authors = OrderedDict()
    for c in commits:
        key = (c.author.name, c.author.email)
        authors[key] = None

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

    print("\nRewriting commits... (destructive, make a backup!)")
    repo.git.filter_branch(
        "--env-filter", env_filter_script,
        "--tag-name-filter", "cat", "--", "--all"
    )
    print("\nDone. Remember to force-push if it's a remote repo!")

def change_messages(repo):
    print("Randomizing commit messages using good_commits.txt...\n")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    commits_file = os.path.join(base_dir, "good_commits.txt")
    if not os.path.exists(commits_file):
        print(f"Error: {commits_file} not found.")
        sys.exit(1)

    # Pass the absolute path explicitly to the inline Python
    msg_filter_script = (
        f"python3 -c 'import markovify; "
        f"text=open(r\"{commits_file}\",encoding=\"utf-8\").read(); "
        f"m=markovify.NewlineText(text); "
        f"import sys; print(m.make_sentence() or \"Update project files\")'"
    )

    print("\nRewriting commit messages... (destructive, make a backup!)")
    repo.git.filter_branch(
        "--msg-filter", msg_filter_script,
        "--tag-name-filter", "cat", "--", "--all"
    )
    print("\nDone. Remember to force-push if it's a remote repo!")

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
    print("2. Change commit messages")
    choice = input("Select [1/2]: ").strip() or "1"

    if choice == "1":
        change_authors(repo, commits)
    elif choice == "2":
        change_messages(repo)
    else:
        print("Invalid choice. Exiting.")


global commit_msg_model
commit_msg_model = get_commit_markov_model()
