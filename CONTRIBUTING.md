# Contributing to Writer's Coach

Thank you for your interest in contributing! This project follows a strict incremental development approach with self-review at each step.

## Development Setup

1. **Prerequisites**: Node.js >= 18.0.0, pnpm >= 8.0.0
2. **Install**: `pnpm install`
3. **Environment**: Copy `.env.example` to `.env` and configure

## Workflow

### Making Changes

```bash
# Create a branch
git checkout -b feature/your-feature

# Make changes and test iteratively
pnpm typecheck  # Type check
pnpm lint       # Lint code
pnpm test       # Run tests
pnpm build      # Build all packages

# Format before committing
pnpm format
```

### Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:

```
feat(api): add revision history endpoint
fix(metrics): correct passive voice detection
docs(readme): update setup instructions
```

### Pre-commit Hooks

Husky will automatically:

- Run lint-staged to format and lint changed files
- Validate commit message format

### Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Input validated with Zod schemas
- [ ] No secrets committed
- [ ] RLS enforced on Supabase queries (where applicable)
- [ ] Guardrails coverage present (where applicable)
- [ ] Reasonable error handling and logging
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] `pnpm lint` passes
- [ ] `pnpm typecheck` passes
- [ ] `pnpm test` passes
- [ ] `pnpm build` succeeds

### Self-Review

Each PR should include a self-review comment addressing:

- What changed and why
- Any trade-offs or decisions made
- Testing approach
- Potential impacts or risks

## Code Guidelines

### TypeScript

- Use strict mode (enforced by tsconfig)
- Prefer `type` over `interface` for simple types
- Use Zod for runtime validation
- Avoid `any` - use `unknown` if needed

### Security

- Never commit secrets or API keys
- Use environment variables
- Enforce Supabase RLS policies
- Validate all user inputs

### Testing

- Unit tests for packages (especially `@writers-coach/metrics`)
- Integration tests for API endpoints
- E2E smoke tests for critical flows
- Aim for meaningful coverage, not just high percentages

### Documentation

- Update README for user-facing changes
- Add JSDoc comments for public APIs
- Include examples in complex functions

## Project Structure

```
/apps          - Deployable applications
  /api         - NestJS backend
  /web         - Next.js frontend
  /extension   - Chrome extension
/packages      - Reusable packages
  /shared      - Types and schemas
  /llm         - LLM provider abstraction
  /metrics     - Readability metrics
  /ui          - React components
/tooling       - Shared configs
```

## Questions?

Open an issue for:

- Bug reports
- Feature requests
- Documentation improvements
- General questions

Thank you for contributing! 🎉
