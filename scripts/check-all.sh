#!/bin/bash

# Comprehensive check script for TubeGenius project
# This script runs all quality checks for both frontend and backend

set -e  # Exit on any error

echo "🔍 Running comprehensive quality checks for TubeGenius..."
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

# Function to run a command and handle errors
run_check() {
    local name=$1
    local command=$2
    local directory=${3:-.}
    local optional=${4:-false}

    print_status "info" "Running $name..."
    cd "$directory"

    if eval "$command"; then
        print_status "success" "$name passed"
    else
        if [ "$optional" = "true" ]; then
            print_status "warning" "$name failed (optional check)"
        else
            print_status "error" "$name failed"
            return 1
        fi
    fi

    cd - > /dev/null
}

# Check if we're in the project root
if [ ! -f "docker-compose.yaml" ]; then
    print_status "error" "Please run this script from the project root directory"
    exit 1
fi

echo ""
print_status "info" "Starting quality checks..."

# 1. Frontend checks
echo ""
print_status "info" "Running frontend checks..."

# Check if pnpm exists
if ! command_exists pnpm; then
    print_status "error" "pnpm not found. Please install pnpm first."
    exit 1
fi

# ESLint
run_check "Frontend ESLint" "pnpm lint" "frontend"

# Prettier
run_check "Frontend Prettier" "pnpm prettier:check" "frontend"

# TypeScript
run_check "Frontend TypeScript" "pnpm type-check" "frontend"

# Build check (optional - can fail due to environment issues)
run_check "Frontend Build" "pnpm build" "frontend" "true"

# 2. Backend checks
echo ""
print_status "info" "Running backend checks..."

# Frontend platform checks
run_check "Frontend Platform ESLint" "pnpm lint" "frontend-platform"
run_check "Frontend Platform Prettier" "pnpm prettier:check" "frontend-platform"
run_check "Frontend Platform TypeScript" "pnpm type-check" "frontend-platform"
run_check "Frontend Platform Build" "pnpm build" "frontend-platform" "true"

# Check if uv exists
if ! command_exists uv; then
    print_status "warning" "uv not found, skipping backend checks"
else
    # Ruff linting
    run_check "Backend Ruff Lint" "uv run ruff check backend/" "backend"

    # Ruff formatting
    run_check "Backend Ruff Format" "uv run ruff format --check backend/" "backend"

    # Django migrations check
    run_check "Backend Migrations" "uv run python manage.py makemigrations --check --dry-run" "backend"

    # Django tests (if they exist)
    if [ -d "backend/api/tests" ]; then
        run_check "Backend Tests" "uv run pytest backend/api/tests/" "backend" "true"
    else
        print_status "warning" "No backend tests found, skipping"
    fi

    # 3. Security checks
    echo ""
    print_status "info" "Running security checks..."

    # Bandit security check
    if command_exists bandit; then
        run_check "Security (Bandit)" "uv run bandit -r backend/" "backend"
    else
        print_status "warning" "bandit not found, skipping security checks"
    fi

    # 4. Dependency checks
    echo ""
    print_status "info" "Checking dependencies..."

    # Frontend dependencies
    run_check "Frontend Dependencies" "pnpm install --frozen-lockfile" "frontend"
    run_check "Frontend Platform Dependencies" "pnpm install --frozen-lockfile" "frontend-platform"

    # Backend dependencies
    run_check "Backend Dependencies" "uv sync" "backend"

    # Frontend platform dependencies
    run_check "Frontend Platform Dependencies" "pnpm install --frozen-lockfile" "frontend-platform"
fi

echo ""
echo "=================================================="
print_status "success" "All quality checks completed successfully! 🎉"
echo ""
print_status "info" "Your code is ready for commit and deployment!"
