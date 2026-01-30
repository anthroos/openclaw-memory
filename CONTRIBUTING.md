# Contributing to OpenClaw Memory

Thank you for your interest in contributing!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/anthroos/openclaw-memory.git
cd openclaw-memory
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run tests:
```bash
python3 scripts/token_counter.py --text "test"
python3 scripts/budget_tracker.py --state /tmp/test.json --log-usage --model claude-3-haiku --input-tokens 100 --output-tokens 50
```

## Pull Request Process

1. **Create a feature branch** from `main`:
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes** with clear, atomic commits:
```bash
git commit -m "feat: add new feature"
git commit -m "fix: resolve issue with X"
git commit -m "docs: update README"
```

3. **Follow commit message conventions**:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation only
   - `refactor:` - Code refactoring
   - `test:` - Adding tests
   - `chore:` - Maintenance tasks

4. **Push and create PR**:
```bash
git push origin feature/your-feature-name
```

5. **PR description should include**:
   - What changed and why
   - How to test the changes
   - Screenshots if UI changes

## Code Style

- Python: Follow PEP 8
- Use type hints where possible
- Add docstrings to functions
- Keep functions small and focused

## Reporting Issues

When reporting bugs, please include:
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Relevant log output

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
