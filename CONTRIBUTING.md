# Contributing to CodeBundle Pro

First off, thank you for considering contributing to CodeBundle Pro! It's people like you that make this tool better for everyone.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A GitHub account

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/codebundle.git
   cd codebundle
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/original/codebundle.git
   ```

## Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

4. Run tests to verify setup:
   ```bash
   pytest
   ```

## How to Contribute

### Reporting Bugs

Before creating a bug report, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the behavior
- **Expected behavior** vs **actual behavior**
- **Environment details** (OS, Python version, package version)
- **Code samples** or error messages if applicable

### Suggesting Features

Feature suggestions are welcome! Please include:

- **Clear description** of the feature
- **Use case** - why would this feature be useful?
- **Possible implementation** ideas if you have any

### Code Contributions

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following our coding standards

3. Write or update tests as needed

4. Run the test suite:
   ```bash
   pytest --cov=codebundle
   ```

5. Commit your changes following our commit guidelines

6. Push to your fork and create a pull request

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) guidelines
- Use [Black](https://black.readthedocs.io/) for formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Maximum line length: 88 characters

### Type Hints

- All public functions should have type hints
- Use `typing` module for complex types
- Run `mypy` to check types

### Documentation

- Use docstrings for all public modules, functions, classes, and methods
- Follow [Google style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Keep docstrings up-to-date with code changes

### Testing

- Write tests for all new functionality
- Maintain test coverage above 80%
- Use pytest fixtures appropriately
- Mark slow tests with `@pytest.mark.slow`

Example test:

```python
import pytest
from pathlib import Path
from codebundle.core.scanner import FileScanner


def test_scanner_finds_python_files(tmp_path: Path):
    """Test that scanner correctly finds Python files."""
    # Create test files
    (tmp_path / "test.py").write_text("print('hello')")
    (tmp_path / "test.txt").write_text("not python")
    
    # Scan for Python files
    scanner = FileScanner(
        root_path=tmp_path,
        include_extensions=[".py"],
    )
    files = scanner.scan_all()
    
    assert len(files) == 1
    assert files[0].extension == ".py"
```

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - A new feature
- `fix:` - A bug fix
- `docs:` - Documentation only changes
- `style:` - Changes that do not affect code meaning
- `refactor:` - Code change that neither fixes a bug nor adds a feature
- `test:` - Adding or correcting tests
- `chore:` - Changes to build process or auxiliary tools

Examples:
```
feat: add support for YAML output format
fix: correct encoding detection for UTF-16 files
docs: update installation instructions
test: add tests for glob pattern filtering
```

## Pull Request Process

1. **Update documentation** if you change functionality
2. **Update tests** for new or changed functionality
3. **Update CHANGELOG.md** with your changes
4. **Ensure CI passes** - all tests, linting, and type checking
5. **Request review** from maintainers

### PR Checklist

- [ ] Code follows the project's style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Commit messages follow guidelines

## Questions?

Feel free to open an issue for questions or discussions about the project.

Thank you for contributing! 🎉
