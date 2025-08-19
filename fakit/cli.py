import argparse
import git
import markovify
import os
import random
import subprocess
import sys
import tempfile
from collections import OrderedDict
from datetime import datetime, timedelta
from faker import Faker
from fakit.spinner import Spinner

# ------------------------
# Helpers
# ------------------------

def list_commits(repo):
    commits = list(repo.iter_commits('--all'))
    for idx, c in enumerate(commits):
        print(f"{idx}: {c.hexsha[:8]} {c.author.name} <{c.author.email}> {c.summary}")
    return commits


def make_email_from_name(set_name: str):
    first_name, last_name, *rest = set_name.lower().split()
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

def generate_commit_message_safe():
    import os, markovify

    base_dir = os.path.dirname(os.path.abspath(__file__))
    commits_file = os.path.join(base_dir, "good_commits.txt")
    if not os.path.exists(commits_file):
        return "Update project files"

    text = open(commits_file, encoding="utf-8").read()
    model = markovify.NewlineText(text)
    msg = model.make_sentence()
    return msg.strip() if msg else "Update project files"

# ------------------------
# Features
# ------------------------

def cleanup_backup_refs(repo):
    choice = input("\nDo you want to remove backup refs and clean git history? [y/N]: ").strip().lower()
    if choice != 'y':
        print("Skipping cleanup. Backup refs remain.")
        return

    try:
        # Delete all refs under refs/original/
        refs = repo.git.for_each_ref('--format=%(refname)', 'refs/original/').splitlines()
        for ref in refs:
            try:
                repo.git.update_ref('-d', ref)
                print(f"Deleted {ref}")
            except Exception:
                pass

        # Expire reflog and prune unreachable commits
        repo.git.reflog('expire', '--expire=now', '--all')
        repo.git.gc('--prune=now')
        print("Cleanup done.")
    except Exception as e:
        print(f"Failed to cleanup refs: {e}")

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
    spinner = Spinner("Rewriting authors")
    spinner.start()

    cmd = [
        "git", "filter-branch", "-f",
        "--env-filter", env_filter_script,
        "--tag-name-filter", "cat",
        "--", "--all"
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    spinner.stop()
    print("\nDone. Remember to force-push if it's a remote repo!")


def change_dates(repo, commits):
    if not commits:
        print("No commits found. Exiting.")
        return

    # Sort commits by original date
    commits = sorted(commits, key=lambda c: c.committed_datetime)
    n = len(commits)

    first_commit_date = commits[0].committed_datetime
    last_commit_date = commits[-1].committed_datetime
    years_range_orig = (last_commit_date - first_commit_date).days / 365.25

    print(f"Current commit range: {first_commit_date.date()} -> {last_commit_date.date()}")
    print(f"Approximate range in years: {years_range_orig:.2f}")

    # Base offset from today (negative = past, positive = future)
    try:
        base_offset = float(input("Enter base offset in years (negative for past, positive for future) [0]: ") or "0")
    except ValueError:
        base_offset = 0

    try:
        range_years = float(input("Enter range in years: ") or "0")
    except ValueError:
        range_years = 0

    if range_years == 0:
        print("No range specified. Exiting.")
        return

    today = datetime.now()

    # Determine start and end dates according to the sign of base_offset
    if base_offset >= 0:
        start_date = today + timedelta(days=base_offset*365)
        end_date = start_date + timedelta(days=abs(range_years)*365)
    else:
        start_date = today + timedelta(days=base_offset*365)
        end_date = start_date - timedelta(days=abs(range_years)*365)

    print(f"\nNew commit range will be: {start_date.date()} -> {end_date.date()}")

    env_filter_lines = []
    for i, c in enumerate(commits):
        # Linear interpolation between start and end dates
        t = i / max(n-1, 1)
        if base_offset >= 0:
            commit_date = start_date + t * (end_date - start_date)
        else:
            commit_date = start_date + t * (end_date - start_date)  # negative range
        # Add small random jitter within one day
        commit_date += timedelta(seconds=random.randint(0, 24*3600 - 1))
        timestamp = int(commit_date.timestamp())

        env_filter_lines.append(f'''
if [ "$GIT_COMMIT" = "{c.hexsha}" ]; then
    export GIT_AUTHOR_DATE="{timestamp}"
    export GIT_COMMITTER_DATE="{timestamp}"
fi
''')

    env_filter_script = "\n".join(env_filter_lines)

    print("\nRewriting commit dates... (destructive, make a backup!)")
    spinner = Spinner("Rewriting dates")
    spinner.start()

    cmd = [
        "git", "filter-branch", "-f",
        "--env-filter", env_filter_script,
        "--tag-name-filter", "cat",
        "--", "--all"
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    spinner.stop()
    print("\nDone. Remember to force-push if it's a remote repo!")

def change_messages(repo, commits):

    print("Randomizing commit messages using good_commits.txt...\n")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    commits_file = os.path.join(base_dir, "good_commits.txt")
    if not os.path.exists(commits_file):
        print(f"Error: {commits_file} not found.")
        sys.exit(1)

    # Create a temporary Python script to generate safe commit messages
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as tmp_script:
        tmp_script.write(f"""\
#!/usr/bin/env python3
import markovify
import os
commits_file = r"{commits_file}"
text = open(commits_file, encoding='utf-8').read()
model = markovify.NewlineText(text)
msg = model.make_sentence()
print(msg.strip() if msg else "Update project files")
""")
        tmp_script_path = tmp_script.name  # <--- use this path

    os.chmod(tmp_script_path, 0o755)

    spinner = Spinner("Rewriting messages")
    spinner.start()

    cmd = [
        "git", "filter-branch", "-f",
        "--msg-filter", tmp_script_path,  # <--- corrected
        "--tag-name-filter", "cat",
        "--", "--all"
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    spinner.stop()

    # Remove temporary script
    os.remove(tmp_script_path)
    print("\nDone. Remember to force-push if it's a remote repo!")

# ------------------------
# CLI
# ------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Fakit - Fake git repository automation tool\n\n"
            "Operations:\n"
            "  1. Change authors (optionally randomize names/emails)\n"
            "  2. Change commit messages (using markov-generated messages)\n"
            "  3. Change commit dates (with base offset and range in years)\n\n"
            "After any operation, Fakit will prompt you to remove backup refs "
            "(refs/original) and clean git history to avoid duplicate commits.\n"
            "This helps keep the repo clean for subsequent fakit operations.\n\n"
            "WARNING: All operations are destructive! Make a backup if needed."
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )
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
    print("3. Change commit dates")
    choice = input("Select [1/2/3]: ").strip() or "1"

    if choice == "1":
        change_authors(repo, commits)
    elif choice == "2":
        change_messages(repo, commits)
    elif choice == "3":
        change_dates(repo, commits)
    else:
        print("Invalid choice. Exiting.")

    # Prompt for cleanup after any operation
    cleanup_backup_refs(repo)

if __name__ == "__main__":
    main()

# ------------------------
# Global model
# ------------------------
global commit_msg_model
commit_msg_model = get_commit_markov_model()
