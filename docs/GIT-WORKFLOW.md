# Git Workflow and Commit Conventions

This document defines the Git workflow, branching strategy, and commit conventions for Project Echo.

## Branching Strategy

### Main Branches

- **`main`**: Production-ready code. Always stable and deployable.
- **`develop`**: Integration branch for features. Merged to `main` for releases.

### Feature Branches

- **`feature/{story-number}-{description}`**: Feature development
  - Example: `feature/1.1-project-repository-structure`
  - Created from `develop`
  - Merged back to `develop` when complete

### Other Branches

- **`hotfix/{description}`**: Critical bug fixes for production
  - Created from `main`
  - Merged to both `main` and `develop`
- **`release/{version}`**: Release preparation
  - Created from `develop`
  - Merged to `main` and `develop` when ready

## Commit Conventions

We use **Conventional Commits** format for clear, consistent commit messages.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **`feat`**: New feature
- **`fix`**: Bug fix
- **`docs`**: Documentation changes
- **`style`**: Code style changes (formatting, no logic change)
- **`refactor`**: Code refactoring (no feature change or bug fix)
- **`test`**: Adding or updating tests
- **`chore`**: Maintenance tasks (dependencies, build, etc.)
- **`perf`**: Performance improvements

### Examples

```bash
# Feature
feat(backend): add health check endpoint

# Bug fix
fix(frontend): correct channel card display issue

# Documentation
docs(architecture): update deployment section

# Refactoring
refactor(shared): extract common video processing logic

# Test
test(backend): add unit tests for channel service
```

### Scope

Scope indicates the area of code affected:
- `backend`, `frontend`, `shared`
- `api`, `ui`, `config`
- Component/service name (e.g., `channel-service`, `dashboard`)

### Subject

- Use imperative mood ("add" not "added" or "adds")
- First letter lowercase
- No period at the end
- Maximum 50 characters

### Body (Optional)

- Explain **what** and **why**, not **how**
- Wrap at 72 characters
- Use present tense

### Footer (Optional)

- Reference issues: `Closes #123`
- Breaking changes: `BREAKING CHANGE: description`

## Workflow Example

```bash
# Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/1.1-project-repository-structure

# Make changes and commit
git add .
git commit -m "feat(structure): create backend directory structure"
git commit -m "feat(structure): add frontend React setup"
git commit -m "docs(structure): add multi-repo architecture guide"

# Push and create pull request
git push origin feature/1.1-project-repository-structure

# After PR approval, merge to develop
git checkout develop
git merge feature/1.1-project-repository-structure
git push origin develop
```

## Pull Request Guidelines

### PR Title

Use same format as commit messages:
```
feat(backend): add health check endpoint
```

### PR Description

Include:
- **What:** Brief description of changes
- **Why:** Reason for the change
- **How:** Implementation approach (if complex)
- **Testing:** How to test the changes
- **Related:** Link to story/issue

### PR Checklist

- [ ] Code follows project standards
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] All tests pass
- [ ] Linting passes

## Channel Repository Workflow

Channel repositories use simpler workflow:

- **`main`**: Only branch (no develop branch needed)
- **Direct commits** to main for configuration changes
- **Feature branches** only for significant changes

## Best Practices

1. **Commit Often:** Small, focused commits are easier to review
2. **Write Clear Messages:** Future you (and others) will thank you
3. **Test Before Committing:** Run tests locally
4. **Review Before Pushing:** `git log` to review commits
5. **Keep Branches Updated:** Regularly merge `develop` into feature branches

## Branch Protection Rules

For `main` branch (if configured):
- Require pull request reviews
- Require status checks to pass
- Require branches to be up to date
- No force pushes

---

**Note:** These conventions help maintain a clean Git history and make collaboration easier, especially for AI agents reviewing code changes.
