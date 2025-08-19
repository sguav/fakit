# Fakit

**fakit** is a command-line tool designed to automate the anonymization and modification of Git repositories. It allows users to:

* Randomize commit authorship (names and emails)
* Alter commit messages using a Markov chain model trained on a corpus of good commit messages
* Rewriting commit history

The tool is particularly useful for preparing repositories for public sharing, ensuring that sensitive information such as author identities and commit messages are anonymized.

Or if you just are messing around.

This project uses [Faker](https://github.com/joke2k/faker) to brilliantly generate names and emails.

---

## Features

* **Change Authors**: Randomize or manually edit commit authorship across the entire repository history.
* **Change Commit Messages**: Generate new commit messages using a Markov chain model trained on a dataset of high-quality commit messages.
* **Safe Rewriting**: Utilizes `git filter-branch` to rewrite commit history, ensuring that changes are applied consistently and can be reverted if necessary.

---

## Installation

### Prerequisites

* Python 3.7 or higher
* Git
* A virtual environment tool (e.g., `venv` or `virtualenv`)

### Steps

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/sguav/fakit.git
   cd fakit
   ```



2. **Set Up a Virtual Environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

   or use the provided `setup.sh` covering also step `3` to install dependencies:

   ```bash
   source ./setup.sh
   ```



3. **Install Dependencies**:

   ```bash
   pip install -r requirements-dev.txt
   ```



4. **Install the Package in Editable Mode**:

   ```bash
   pip install -e .
   ```



---

## Usage


To start the interactive prompts:

```bash
fakit /path/to/repo
```

Follow the prompts to either randomize authorship or manually edit author details.
Alternatively rewrite commit messages using a Markov chain model trained on a dataset of generally acceptable commit messages.

---

## Development

### Running Tests

To run the test suite:

```bash
pytest
```



Tests are located in the `tests/` directory and are structured to test individual features independently.

### Adding New Tests

To add new tests:

1. Create a new test file in the `tests/` directory.
2. Define test functions prefixed with `test_`.
3. Use fixtures from `conftest.py` for shared setup.
4. Ensure tests are independent and isolated.

For example, to test the `change-authors` feature:

```python
def test_change_authors(temp_repo):
    # Arrange
    repo = temp_repo
    original_authors = get_commit_authors(repo)

    # Act
    fakit.change_authors(repo)

    # Assert
    new_authors = get_commit_authors(repo)
    assert original_authors != new_authors
```



---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
