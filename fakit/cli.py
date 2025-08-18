import argparse
import git
import sys

def list_commits(repo):
    commits = list(repo.iter_commits('--all'))
    for idx, c in enumerate(commits):
        print(f"{idx}: {c.hexsha[:8]} {c.author.name} <{c.author.email}> {c.summary}")
    return commits

def change_authors(repo, commits):
    new_name = input("New author name: ").strip()
    new_email = input("New author email: ").strip()
    print("Rewriting commits...")

    # Use filter-branch equivalent via git command
    # This is destructive, create a backup first!
    repo.git.filter_branch(
        "--env-filter",
        f'export GIT_AUTHOR_NAME="{new_name}"; '
        f'export GIT_AUTHOR_EMAIL="{new_email}"; '
        f'export GIT_COMMITTER_NAME="{new_name}"; '
        f'export GIT_COMMITTER_EMAIL="{new_email}"; ',
        "--tag-name-filter", "cat", "--", "--all"
    )

    print("Done. Remember: force-push if it's a remote repo!")

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
