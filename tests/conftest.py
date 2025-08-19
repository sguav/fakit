import pytest
import tempfile
import shutil
import os
import git

@pytest.fixture
def temp_repo():
    temp_dir = tempfile.mkdtemp()
    repo = git.Repo.init(temp_dir)

    # Initial commit
    file_path = os.path.join(temp_dir, "file.txt")
    with open(file_path, "w") as f:
        f.write("initial")
    repo.index.add(["file.txt"])
    repo.index.commit("Initial commit")

    # Second commit
    with open(file_path, "a") as f:
        f.write("\nsecond line")
    repo.index.add(["file.txt"])
    repo.index.commit("Second commit")

    yield repo
    shutil.rmtree(temp_dir)
