#!/bin/bash

# Setup script for pre-commit hooks in TubeGenius project
# This script installs and configures pre-commit hooks

set -e  # Exit on any error

echo "🔧 Setting up pre-commit hooks for TubeGenius..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "success")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "error")
            echo -e "${RED}❌ $message${NC}"
            ;;
        "warning")
            echo -e "${YELLOW}⚠️  $message${NC}"
            ;;
        "info")
            echo -e "${BLUE}ℹ️  $message${NC}"
            ;;
    esac
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if we're in the project root
if [ ! -f ".pre-commit-config.yaml" ]; then
    print_status "error" "Please run this script from the project root directory"
    exit 1
fi

echo ""
print_status "info" "Checking prerequisites..."

# Check Python
if ! command_exists python3; then
    print_status "error" "Python 3 is required but not installed"
    exit 1
fi

# Check pip
if ! command_exists pip; then
    print_status "error" "pip is required but not installed"
    exit 1
fi

# Check Node.js
if ! command_exists node; then
    print_status "error" "Node.js is required but not installed"
    exit 1
fi

# Check pnpm
if ! command_exists pnpm; then
    print_status "error" "pnpm is required but not installed"
    exit 1
fi

# Check uv
if ! command_exists uv; then
    print_status "warning" "uv not found, installing..."
    pip install uv
fi

print_status "success" "All prerequisites are satisfied"

echo ""
print_status "info" "Installing pre-commit..."

# Install pre-commit
if pip install pre-commit; then
    print_status "success" "pre-commit installed successfully"
else
    print_status "error" "Failed to install pre-commit"
    exit 1
fi

echo ""
print_status "info" "Installing pre-commit hooks..."

# Install the git hook scripts
if pre-commit install; then
    print_status "success" "Pre-commit hooks installed successfully"
else
    print_status "error" "Failed to install pre-commit hooks"
    exit 1
fi

# Install commit-msg hook for conventional commits
if pre-commit install --hook-type commit-msg; then
    print_status "success" "Commit-msg hook installed successfully"
else
    print_status "error" "Failed to install commit-msg hook"
    exit 1
fi

echo ""
print_status "info" "Installing frontend dependencies..."

# Install frontend dependencies
cd frontend
if pnpm install; then
    print_status "success" "Frontend dependencies installed"
else
    print_status "error" "Failed to install frontend dependencies"
    exit 1
fi
cd ..

echo ""
print_status "info" "Installing backend dependencies..."

# Install backend dependencies
cd backend
if uv sync; then
    print_status "success" "Backend dependencies installed"
else
    print_status "error" "Failed to install backend dependencies"
    exit 1
fi
cd ..

echo ""
print_status "info" "Running pre-commit on all files..."

# Run pre-commit on all files to ensure everything is set up correctly
if pre-commit run --all-files; then
    print_status "success" "Pre-commit setup completed successfully!"
else
    print_status "warning" "Pre-commit setup completed with some warnings"
fi

echo ""
echo "=================================================="
print_status "success" "Pre-commit hooks are now configured! 🎉"
echo ""
print_status "info" "What happens now:"
echo "  • Every commit will automatically run quality checks"
echo "  • Code will be automatically formatted"
echo "  • Linting errors will be caught before commit"
echo "  • Security issues will be detected"
echo ""
print_status "info" "Available commands:"
echo "  • pre-commit run --all-files    # Run all checks on all files"
echo "  • pre-commit run                # Run checks on staged files"
echo "  • pre-commit run --hook-stage manual  # Run checks manually"
echo ""
print_status "info" "Your code quality is now automatically protected! 🛡️"
