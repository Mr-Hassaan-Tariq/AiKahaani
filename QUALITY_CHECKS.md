# Quality Checks & Pre-commit Hooks

This document describes the comprehensive quality assurance setup for the TubeGenius project.

## 🎯 Overview

The project uses a multi-layered approach to ensure code quality:

1. **Pre-commit hooks** - Basic file checks before each commit
2. **Local development checks** - Comprehensive quality validation on your machine
3. **CI/CD integration** - Automated checks in GitHub Actions
4. **VS Code integration** - Real-time feedback during development

## 🔧 Pre-commit Hooks

Pre-commit hooks run automatically before each commit and ensure:

### General File Checks
- ✅ **Case conflicts** - Check for files with case conflicts
- ✅ **JSON validation** - Validate JSON files
- ✅ **Merge conflicts** - Detect unresolved merge conflicts
- ✅ **Symlinks** - Check for broken symlinks
- ✅ **TOML validation** - Validate TOML files
- ✅ **YAML validation** - Validate YAML files
- ✅ **End of files** - Ensure files end with newline
- ✅ **Trailing whitespace** - Remove trailing whitespace
- ✅ **Large files** - Prevent large files from being committed
- ✅ **Debug statements** - Remove debug statements from Python
- ✅ **Docstring first** - Ensure docstrings come first in Python files

### Python Backend Checks
- ✅ **Ruff linting** - Fast Python linting with auto-fix
- ✅ **Ruff formatting** - Consistent Python code formatting

### Commit Message Formatting
- ✅ **Conventional commits** - Ensure commit messages follow conventional format

## 🚀 Local Quality Checks

Run comprehensive quality checks manually on your development machine:

```bash
# Run all checks
./scripts/check-all.sh

# Or use npm scripts
npm run check
```

### Available Scripts

| Script | Description |
|--------|-------------|
| `npm run check` | Run all quality checks |
| `npm run check:pre-commit` | Run pre-commit hooks only |
| `npm run check:frontend` | Frontend checks only |
| `npm run check:backend` | Backend checks only |
| `npm run format` | Format all code |
| `npm run install:hooks` | Install pre-commit hooks |
| `npm run update:hooks` | Update pre-commit hooks |

## 🔄 CI/CD Integration

GitHub Actions provides comprehensive automated checks:

### Workflows

1. **Lint Workflow** (`.github/workflows/lint.yml`)
   - Fast basic checks using pre-commit hooks
   - Runs on every push and PR
   - No external dependencies required

2. **CI Workflow** (`.github/workflows/ci.yml`)
   - Comprehensive checks split into jobs:
     - **Pre-commit**: Basic file checks
     - **Frontend**: ESLint, Prettier, TypeScript, Build
     - **Backend**: Ruff, Bandit, Django migrations
     - **Security**: npm audit, safety checks

### CI vs Local Checks

| Check Type | Local | CI | Notes |
|------------|-------|----|-------|
| Pre-commit hooks | ✅ | ✅ | Basic file checks |
| Frontend linting | ✅ | ✅ | ESLint, Prettier, TypeScript |
| Frontend build | ✅ | ✅ | Production build verification |
| Backend linting | ✅ | ✅ | Ruff linting and formatting |
| Security scanning | ✅ | ✅ | Bandit for Python, npm audit |
| Dependency checks | ✅ | ✅ | Lockfile validation |

## 📋 What Gets Checked

### Frontend (Next.js/React/TypeScript)
- **ESLint**: Code quality and style
- **Prettier**: Code formatting
- **TypeScript**: Type safety
- **Dependencies**: Package.json validation
- **Build**: Production build verification

### Backend (Django/Python)
- **Ruff**: Fast linting and formatting
- **Bandit**: Security vulnerability scanning
- **Migrations**: Django migration validation
- **Tests**: Test suite execution (optional)
- **Dependencies**: UV lockfile validation

### General
- **File integrity**: JSON, YAML, TOML validation
- **Code style**: Consistent formatting across all files
- **Security**: Vulnerability scanning
- **Documentation**: Docstring requirements

## 🛠️ Setup Instructions

### 1. Install Dependencies

```bash
# Install pre-commit
pip install pre-commit --break-system-packages

# Install frontend dependencies
cd frontend && pnpm install

# Install backend dependencies
cd backend && uv sync
```

### 2. Install Pre-commit Hooks

```bash
# Install hooks
pre-commit install

# Or use npm script
npm run install:hooks
```

### 3. VS Code Setup

Install recommended extensions:
- **Prettier** - Code formatting
- **ESLint** - JavaScript/TypeScript linting
- **Tailwind CSS** - CSS framework support
- **Python** - Python language support

## 🔄 Workflow

### Development Workflow

1. **Write code** with VS Code providing real-time feedback
2. **Save files** - Auto-formatting applied
3. **Stage changes** - `git add .`
4. **Commit** - Pre-commit hooks run automatically
5. **Push** - CI/CD runs comprehensive checks

### Pre-commit Hook Flow

```
git commit
    ↓
Pre-commit hooks run
    ↓
General file checks
    ↓
Python linting & formatting
    ↓
Commit proceeds (if all pass)
```

### CI/CD Flow

```
Push to GitHub
    ↓
GitHub Actions triggered
    ↓
Lint workflow (fast)
    ↓
CI workflow (comprehensive)
    ↓
Pre-commit job
    ↓
Frontend job
    ↓
Backend job
    ↓
Security job
    ↓
All checks pass ✅
```

## 🚨 Troubleshooting

### Common Issues

#### Pre-commit Hooks Fail
```bash
# Run hooks manually to see detailed output
pre-commit run --all-files

# Fix formatting issues
npm run format

# Update hooks if needed
npm run update:hooks
```

#### CI/CD Failures
- **Lint workflow fails**: Check basic file formatting and Python code
- **Frontend job fails**: Check ESLint, Prettier, TypeScript, or build issues
- **Backend job fails**: Check Ruff, Bandit, or Django migration issues
- **Security job fails**: Check for security vulnerabilities in dependencies

#### Local vs CI Differences
- **Local checks pass, CI fails**: Usually due to missing dependencies or environment differences
- **CI passes, local fails**: Check if you have all required tools installed locally

### Configuration Files

- **`.pre-commit-config.yaml`** - Pre-commit hook configuration
- **`.github/workflows/lint.yml`** - Fast CI checks
- **`.github/workflows/ci.yml`** - Comprehensive CI checks
- **`scripts/check-all.sh`** - Manual check script
- **`package.json`** - Root npm scripts
- **`frontend/eslint.config.mjs`** - ESLint configuration
- **`frontend/.prettierrc`** - Prettier configuration
- **`backend/pyproject.toml`** - Python tool configuration

## 📊 Quality Metrics

The setup ensures:

- **100%** of commits pass basic quality checks
- **Comprehensive** CI/CD validation for all code
- **Consistent** code formatting across the project
- **Type safety** for frontend code
- **Security** scanning for backend code
- **Zero** linting errors in production code
- **Automated** quality enforcement

## 🔗 Related Documentation

- [Linting Guide](frontend/LINTING.md) - Frontend linting details
- [README](README.md) - Project overview
- [Frontend README](frontend/README.md) - Frontend-specific guide

## 🤝 Contributing

When contributing to the project:

1. **Follow** the established code style
2. **Run** quality checks before submitting PRs
3. **Address** any linting or formatting issues
4. **Test** your changes thoroughly
5. **Document** any new features or changes

The quality checks help maintain high code standards and ensure a smooth development experience for all contributors.
