# Contributing to Nexus AI Hub

Thank you for your interest in contributing! This guide will help you get started.

## Getting Started

1. **Fork** the repository and clone your fork locally.
2. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Install the project** in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=nexus_ai_hub
```

### Linting & Formatting

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
ruff check src/ tests/
ruff format src/ tests/
```

### Type Checking

```bash
mypy src/
```

## Pull Request Guidelines

- Keep PRs focused — one feature or fix per PR.
- Write clear commit messages.
- Add tests for new functionality.
- Ensure all tests pass before submitting.
- Update documentation if your change affects usage or APIs.

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) conventions.
- Use type hints for all function signatures.
- Write docstrings for public classes and functions.
- Keep line length under 100 characters.

## Reporting Bugs

Use the [Bug Report](https://github.com/ljbudgie/nexus-ai-hub/issues/new?template=bug_report.md) issue template.

## Suggesting Features

Use the [Feature Request](https://github.com/ljbudgie/nexus-ai-hub/issues/new?template=feature_request.md) issue template.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
