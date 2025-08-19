# Pre-commit Setup for TubeGenius

This document explains how to set up and use pre-commit hooks to automatically enforce code quality standards in the TubeGenius project.

## 🎯 What is Pre-commit?

Pre-commit is a framework that manages pre-commit hooks for Git. It automatically runs quality checks before each commit, ensuring that only high-quality code reaches your repository.

## 🚀 Quick Setup

### Unix/macOS

```bash
chmod +x scripts/setup-pre-commit.sh
./scripts/setup-pre-commit.sh
```

### Windows PowerShell

```powershell
.\scripts\setup-pre-commit.ps1
```

## 🔧 What Gets Checked

### Frontend (JavaScript/TypeScript)

- **ESLint** - Code quality and style
- **Prettier** - Code formatting
- **TypeScript** - Type checking
- **File validation** - JSON, YAML, Markdown

### Backend (Python)

- **Ruff** - Fast Python linting and formatting
- **Bandit** - Security vulnerability scanning
- **Django checks** - Configuration validation
- **Migration checks** - Database migration validation

### General

- **File size limits** - Prevents large files
- **Merge conflicts** - Detects unresolved conflicts
- **Conventional commits** - Enforces commit message format
- **Shell scripts** - Validates shell script syntax

## 📋 Available Hooks

| Hook                  | Purpose                       | Files                                                |
| --------------------- | ----------------------------- | ---------------------------------------------------- |
| `trailing-whitespace` | Remove trailing whitespace    | All                                                  |
| `end-of-file-fixer`   | Ensure files end with newline | All                                                  |
| `eslint`              | JavaScript/TypeScript linting | `.js`, `.jsx`, `.ts`, `.tsx`                         |
| `prettier`            | Code formatting               | `.js`, `.jsx`, `.ts`, `.tsx`, `.json`, `.css`, `.md` |
| `typescript-check`    | TypeScript compilation        | `.ts`, `.tsx`                                        |
| `ruff`                | Python linting                | `.py`                                                |
| `ruff-format`         | Python formatting             | `.py`                                                |
| `bandit`              | Security scanning             | `.py`                                                |
| `django-check`        | Django validation             | `.py`                                                |
| `markdownlint`        | Markdown validation           | `.md`                                                |
| `shellcheck`          | Shell script validation       | `.sh`, `.bash`                                       |

## 🎮 Usage

### Automatic (Recommended)

Pre-commit hooks run automatically when you commit:

```bash
git add .
git commit -m "feat: add new feature"
# Hooks run automatically, commit only succeeds if all checks pass
```

### Manual

Run hooks manually when needed:

```bash
# Run on staged files
pre-commit run

# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run eslint --all-files
pre-commit run ruff --all-files
```

### Skip Hooks (Emergency Only)

```bash
git commit -m "feat: emergency fix" --no-verify
```

## 🔄 Workflow

1. **Make changes** to your code
2. **Stage files** with `git add .`
3. **Pre-commit runs** automatically
4. **Auto-fixes applied** for formatting issues
5. **Manual fixes needed** for complex issues
6. **Commit succeeds** only when all checks pass

## 🛠️ Configuration

The pre-commit configuration is in `.pre-commit-config.yaml`. Key features:

- **Auto-fix enabled** for ESLint and Ruff
- **File type filtering** for efficient execution
- **Local hooks** for project-specific checks
- **Conventional commit** message validation

## 🚨 Troubleshooting

### Hook Fails

```bash
# See detailed error
pre-commit run --verbose

# Run specific hook to debug
pre-commit run eslint --verbose
```

### Auto-fix Issues

```bash
# Manually fix formatting
npm run format          # Frontend
uv run ruff format .    # Backend
```

### Skip Hooks Temporarily

```bash
# Skip all hooks for one commit
git commit -m "feat: temporary commit" --no-verify

# Skip specific hook
SKIP=eslint git commit -m "feat: skip eslint"
```

### Reinstall Hooks

```bash
# Remove existing hooks
pre-commit uninstall

# Reinstall hooks
pre-commit install
pre-commit install --hook-type commit-msg
```

## 📚 Commands Reference

| Command                                     | Description                 |
| ------------------------------------------- | --------------------------- |
| `pre-commit install`                        | Install pre-commit hooks    |
| `pre-commit install --hook-type commit-msg` | Install commit message hook |
| `pre-commit run`                            | Run hooks on staged files   |
| `pre-commit run --all-files`                | Run hooks on all files      |
| `pre-commit run <hook-id>`                  | Run specific hook           |
| `pre-commit uninstall`                      | Remove pre-commit hooks     |
| `pre-commit clean`                          | Clean pre-commit cache      |

## 🔗 Integration with VS Code

Pre-commit works seamlessly with VS Code:

- **Real-time feedback** from ESLint and other tools
- **Auto-formatting** on save (if configured)
- **Git integration** through VS Code's Git panel
- **Terminal integration** for running pre-commit commands

## 🎉 Benefits

- **Automatic quality enforcement** - No more forgetting to run checks
- **Consistent code style** - Team-wide formatting standards
- **Early error detection** - Catch issues before they reach CI/CD
- **Faster development** - Auto-fixing reduces manual work
- **Better collaboration** - Consistent code quality across team

## 🆘 Need Help?

- Check the [pre-commit documentation](https://pre-commit.com/)
- Review the `.pre-commit-config.yaml` file
- Run `pre-commit run --verbose` for detailed error messages
- Ask the team for assistance with specific hook failures

---

**Remember**: Pre-commit hooks are your friend! They ensure code quality and save time by catching issues early. 🛡️
