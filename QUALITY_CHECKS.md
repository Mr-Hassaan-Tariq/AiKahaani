# Quality Checks

This document describes the quality assurance setup for the TubeGenius project.

## 🎯 Overview

The project uses a simplified approach to ensure code quality:

1. **Local development checks** - Comprehensive quality validation on your machine
2. **CI/CD integration** - Automated checks in GitHub Actions
3. **VS Code integration** - Real-time feedback during development

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
| `npm run check:frontend` | Frontend checks only |
| `npm run check:backend` | Backend checks only |
| `npm run format` | Format frontend code |

## 🔄 CI/CD Integration

GitHub Actions provides automated checks:

### Frontend Checks Workflow (`.github/workflows/lint.yml`)
- **ESLint**: Code quality and style
- **Prettier**: Code formatting
- **Build**: Production build verification

## 📋 What Gets Checked

### Frontend (Next.js/React/TypeScript)
- **ESLint**: Code quality and style
- **Prettier**: Code formatting
- **TypeScript**: Type safety
- **Build**: Production build verification

### Backend (Django/Python)
- **Ruff**: Fast linting and formatting
- **Bandit**: Security vulnerability scanning
- **Migrations**: Django migration validation
- **Tests**: Test suite execution (optional)
- **Dependencies**: UV lockfile validation

## 🛠️ Setup Instructions

### 1. Install Dependencies

```bash
# Install frontend dependencies
cd frontend && pnpm install

# Install backend dependencies
cd backend && uv sync
```

### 2. VS Code Setup

Install recommended extensions:
- **Prettier** - Code formatting
- **ESLint** - JavaScript/TypeScript linting
- **Tailwind CSS** - CSS framework support
- **Python** - Python language support

## 🔄 Workflow

### Development Workflow

1. **Write code** with VS Code providing real-time feedback
2. **Save files** - Auto-formatting applied
3. **Run checks** - `./scripts/check-all.sh` or `npm run check`
4. **Commit** - Code is ready for deployment
5. **Push** - CI/CD runs automated checks

### CI/CD Flow

```
Push to GitHub
    ↓
GitHub Actions triggered
    ↓
Frontend Checks workflow
    ↓
Install dependencies
    ↓
Run ESLint
    ↓
Run Prettier check
    ↓
Build frontend
    ↓
All checks pass ✅
```

## 🚨 Troubleshooting

### Common Issues

#### Frontend Build Fails
- Check Node.js version compatibility
- Verify all dependencies are installed
- Review ESLint and TypeScript errors

#### Backend Checks Fail
```bash
# Install missing dependencies
cd backend && uv sync

# Run specific checks
uv run ruff check .
uv run ruff format --check .
```

#### CI/CD Failures
- **ESLint fails**: Check for code quality issues
- **Prettier fails**: Check for formatting issues
- **Build fails**: Check for TypeScript or dependency issues

### Configuration Files

- **`.github/workflows/lint.yml`** - Frontend CI checks
- **`scripts/check-all.sh`** - Manual check script
- **`package.json`** - Root npm scripts
- **`frontend/eslint.config.mjs`** - ESLint configuration
- **`frontend/.prettierrc`** - Prettier configuration
- **`backend/pyproject.toml`** - Python tool configuration

## 📊 Quality Metrics

The setup ensures:

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
