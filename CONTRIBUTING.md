# Contributing to Karumi Toolkit

Thank you for your interest in contributing! We welcome contributions from the community.

## How to Contribute

### Reporting Issues

1. Check if the issue already exists
2. Provide a clear description
3. Include steps to reproduce
4. Add relevant code snippets or logs

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Write tests for new functionality
5. Run tests: `make test`
6. Run linter: `make lint`
7. Format code: `make format`
8. Commit with clear message: `git commit -m "Add feature: description"`
9. Push to branch: `git push origin feature/my-feature`
10. Open a Pull Request

## Development Setup

```bash
make dev
source venv/bin/activate
```

## Code Style

- Follow PEP 8
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use type hints where appropriate

### Format & Lint

```bash
make format
make lint
```

## Testing Requirements

- Write tests for all new features
- Ensure all tests pass: `make test`
- Aim for >80% code coverage

## Pull Request Guidelines

- Include a clear title and description
- Reference any related issues
- Provide rationale for changes
- Update documentation as needed
- Keep commits focused and atomic

## Areas for Contribution

### High Priority

- [ ] Additional authentication methods (Kerberos, LDAP)
- [ ] LLM orchestration integration
- [ ] Additional language support
- [ ] Performance optimizations
- [ ] Enhanced error recovery

### Good First Issues

- Documentation improvements
- Additional test cases
- Code examples
- Bug fixes with clear reproduction steps

### Medium Priority

- Advanced screenshot comparison
- Video recording of sessions
- Integration with CI/CD platforms
- Cloud deployment templates

## Getting Help

- Open an issue for questions
- Check existing issues and discussions
- Review documentation
- Look at existing examples

## Code Review Process

1. Maintainers review submission
2. Feedback provided if needed
3. Changes addressed by contributor
4. Approved and merged when ready

## Commit Message Guidelines

```
[type]: [scope] - [brief description]

[Detailed explanation if needed]

Type: feat, fix, docs, test, refactor, perf, style
Scope: validators, testing, monitoring, automation
```

Examples:
- `feat: validators - add CAPTCHA detection`
- `fix: testing - handle stale elements better`
- `docs: add Docker deployment guide`

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to:
- Open a discussion
- Ask in issues
- Comment on PRs

Happy contributing! 🎉
