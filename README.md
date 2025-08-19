# Fakit

**Fakit** is a simple tool to batch-manipulate Git repositories, allowing you to:

- Change authors
- Change commit messages
- Change commit dates
- Randomize commit details automatically
- Cleanup old Git refs after rewriting

It’s mainly designed for anonymizing or faking commits for testing, demos, or academic projects.

Or if you just are messing around.

This project uses [Faker](https://github.com/joke2k/faker) to brilliantly generate names and emails.

---

## Features

1. **Change Authors**

   - Randomize names and emails using [Faker](https://faker.readthedocs.io/).
   - Or manually specify new names and emails per author.
   - Rewrites all commits with a safe backup.

2. **Change Commit Messages**

   - Generates random commit messages using a `good_commits.txt` corpus.
   - Supports Markov-chain-based message generation via [markovify](https://github.com/jsvine/markovify).
   - Spinner shows progress during long rewrite operations.

3. **Change Commit Dates**

   - Offset commits by a specified number of years into the past or future.
   - Randomizes day/month/time within the offset range.
   - Interactive prompts guide you through base offset and range selection.

4. **Cleanup Original References**

   - Optionally deletes `refs/original` and runs Git garbage collection.
   - Keeps repo clean for consecutive `fakit` operations.

5. **Spinner Feedback**

   - Long operations like rewriting commits now show a simple ncurses-style spinner.
   - Smooth progress indication without flooding the terminal.

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

You’ll be prompted to choose an operation:

```bash
Choose operation:
1. Change authors
2. Change commit messages
3. Change commit dates
Select [1/2/3]:
```

Follow the interactive prompts for each operation.

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
