# Setup script for pre-commit hooks in TubeGenius project (Windows PowerShell)
# This script installs and configures pre-commit hooks

param(
    [switch]$Force
)

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "Setting up pre-commit hooks for TubeGenius..." -ForegroundColor Blue
Write-Host "==================================================" -ForegroundColor Blue

# Function to print colored output
function Write-Status {
    param(
        [string]$Status,
        [string]$Message
    )

    switch ($Status) {
        "success" { Write-Host "SUCCESS: $Message" -ForegroundColor Green }
        "error"   { Write-Host "ERROR: $Message" -ForegroundColor Red }
        "warning" { Write-Host "WARNING: $Message" -ForegroundColor Yellow }
        "info"    { Write-Host "INFO: $Message" -ForegroundColor Blue }
    }
}

# Function to check if a command exists
function Test-Command {
    param([string]$Command)

    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Check if we're in the project root
if (-not (Test-Path ".pre-commit-config.yaml")) {
    Write-Status "error" "Please run this script from the project root directory"
    exit 1
}

Write-Host ""
Write-Status "info" "Checking prerequisites..."

# Check Python
if (-not (Test-Command "python")) {
    Write-Status "error" "Python is required but not installed"
    exit 1
}

# Check pip
if (-not (Test-Command "pip")) {
    Write-Status "error" "pip is required but not installed"
    exit 1
}

# Check Node.js
if (-not (Test-Command "node")) {
    Write-Status "error" "Node.js is required but not installed"
    exit 1
}

# Check pnpm
if (-not (Test-Command "pnpm")) {
    Write-Status "error" "pnpm is required but not installed"
    exit 1
}

# Check uv
if (-not (Test-Command "uv")) {
    Write-Status "warning" "uv not found, installing..."
    try {
        pip install uv
        Write-Status "success" "uv installed successfully"
    }
    catch {
        Write-Status "error" "Failed to install uv"
        exit 1
    }
}

Write-Status "success" "All prerequisites are satisfied"

Write-Host ""
Write-Status "info" "Installing pre-commit..."

# Install pre-commit
try {
    pip install pre-commit
    Write-Status "success" "pre-commit installed successfully"
}
catch {
    Write-Status "error" "Failed to install pre-commit"
    exit 1
}

Write-Host ""
Write-Status "info" "Installing pre-commit hooks..."

# Install the git hook scripts
try {
    pre-commit install
    Write-Status "success" "Pre-commit hooks installed successfully"
}
catch {
    Write-Status "error" "Failed to install pre-commit hooks"
    exit 1
}

# Install commit-msg hook for conventional commits
try {
    pre-commit install --hook-type commit-msg
    Write-Status "success" "Commit-msg hook installed successfully"
}
catch {
    Write-Status "error" "Failed to install commit-msg hook"
    exit 1
}

Write-Host ""
Write-Status "info" "Installing frontend dependencies..."

# Install frontend dependencies
Set-Location frontend
try {
    pnpm install
    Write-Status "success" "Frontend dependencies installed"
}
catch {
    Write-Status "error" "Failed to install frontend dependencies"
    exit 1
}
Set-Location ..

Write-Host ""
Write-Status "info" "Installing backend dependencies..."

# Install backend dependencies
Set-Location backend
try {
    uv sync
    Write-Status "success" "Backend dependencies installed"
}
catch {
    Write-Status "error" "Failed to install backend dependencies"
    exit 1
}
Set-Location ..

Write-Host ""
Write-Status "info" "Running pre-commit on all files..."

# Run pre-commit on all files to ensure everything is set up correctly
try {
    pre-commit run --all-files
    Write-Status "success" "Pre-commit setup completed successfully!"
}
catch {
    Write-Status "warning" "Pre-commit setup completed with some warnings"
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Blue
Write-Status "success" "Pre-commit hooks are now configured!"
Write-Host ""
Write-Status "info" "What happens now:"
Write-Host "  - Every commit will automatically run quality checks"
Write-Host "  - Code will be automatically formatted"
Write-Host "  - Linting errors will be caught before commit"
Write-Host "  - Security issues will be detected"
Write-Host ""
Write-Status "info" "Available commands:"
Write-Host "  - pre-commit run --all-files    # Run all checks on all files"
Write-Host "  - pre-commit run                # Run checks on staged files"
Write-Host "  - pre-commit run --hook-stage manual  # Run checks manually"
Write-Host ""
Write-Status "info" "Your code quality is now automatically protected!"
