# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Project infrastructure improvements:
  - `pyproject.toml` for modern Python packaging
  - `CONTRIBUTING.md` for contributor guidelines
  - `LICENSE` file (MIT)
  - GitHub Actions CI/CD workflow
  - Pre-commit hooks configuration
  - Comprehensive test suite

## [2.0.0] - 2026-02-28

### Added
- **CLI Enhancements**
  - `--version` flag to display version number
  - `-q/--quiet` flag for silent mode
  - `--no-progress` flag to disable progress bar
  - `--line-numbers` option to add line numbers in output
  - `--git-only` option to bundle only Git-tracked files
  - `--warn-sensitive` security warning for sensitive files
  - `--compress` option with support for zip, tar.gz, tar formats

- **Output Formats**
  - HTML output format with responsive design and table of contents
  - Light/dark theme support for HTML output

- **Features**
  - Intelligent file encoding detection (UTF-8, GBK, Big5, etc.)
  - Parallel file processing with ThreadPoolExecutor
  - Real-time progress display with ETA
  - 9 built-in configuration profiles

### Changed
- Refactored to modular architecture
- Improved directory tree rendering

### Fixed
- CLI FilterRule dynamic type creation bug
- Directory tree display showing incorrect hierarchy

## [1.0.0] - Initial Release

### Added
- Basic file scanning and bundling
- Text and Markdown output formats
- Extension-based filtering
- Simple encoding detection
