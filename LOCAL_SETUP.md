# 🚀 TubeGenius - Local Development Setup Guide

This guide will help you set up and run the TubeGenius project locally on your machine.

## 📋 Prerequisites

Before starting, ensure you have the following installed:

### Required:

- **Python 3.13+** - For Django backend
- **PostgreSQL 12+** - Database server
- **Node.js 20.18.0+** - For Next.js frontend
- **pnpm 9.14.0+** - Package manager for frontend
- **Git** - Version control

### Optional but Recommended:

- **UV** - Fast Python package manager (alternative to pip)
- **Docker & Docker Compose** - For containerized development

### Checking Prerequisites

```bash
# Check Python version
python3 --version  # Should be 3.13 or higher

# Check PostgreSQL
psql --version

# Check Node.js
node --version  # Should be 20.18.0 or higher

# Check pnpm
pnpm --version  # Should be 9.14.0 or higher

# Check Docker (optional)
docker --version
docker compose version
```

## 🏗️ Project Structure

```
Tubegenius/
├── backend/          # Django REST API (Python)
├── web-app/          # Main Next.js frontend application
├── admin-panel/      # Admin panel Next.js application
├── website/          # Marketing website Next.js application
└── docker-compose.yaml  # Docker setup (may need updates)
```

## 🎯 Quick Start Options

You have two main options for running the project:

1. **Local Development (Recommended for development)**
2. **Docker Compose (Easier setup, but may need configuration)**

---

## 📦 Option 1: Local Development Setup

### Step 1: Backend Setup

#### 1.1 Navigate to Backend Directory

```bash
cd /home/saad/Desktop/Hassaan/Tubegenius/backend
```

#### 1.2 Install Python Dependencies

**Option A: Using UV (Recommended - Faster & Works on All Systems)**

```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# Install dependencies
uv sync
```

**Option B: Using pip with Virtual Environment**

**⚠️ Important**: On newer Linux systems (Debian/Ubuntu), you cannot install packages directly to system Python. You must use a virtual environment.

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# When done, deactivate with:
# deactivate
```

**Note**: UV handles virtual environments automatically, so Option A is recommended.

#### 1.3 Create Environment File

Create a `.env.backend` file in the `backend/` directory:

```bash
cd /home/saad/Desktop/Hassaan/Tubegenius/backend
touch .env.backend
```

Add the following configuration to `.env.backend`:

```env
# Django Settings
DEBUG=1
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-base64-32

# Database Configuration
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=db
DATABASE_USER=postgres
DATABASE_PASSWORD=change-password

# Frontend URL
FRONTEND_URL=http://localhost:3000/

# Google OAuth (Optional - leave empty if not using)
GOOGLE_OAUTH2_CLIENT_ID=
GOOGLE_OAUTH2_CLIENT_SECRET=
GOOGLE_OAUTH2_REDIRECT_URI=http://localhost:3000/

# Email Configuration (Optional - leave empty if not using)
DEFAULT_FROM_EMAIL=noreply@tubegenius.com
BREVO_API_KEY=

# Stripe Configuration (Optional - leave empty if not using)
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_TEST_SECRET_KEY=
STRIPE_LIVE_MODE=False

# OpenAI Configuration (Required for script generation)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4.1
TITLE_GENERATION_API_KEY=your-openai-api-key
TITLE_GENERATION_MODEL=gpt-4.1

# YouTube Transcript Proxy (Optional)
TRANSCRIPT_PROXY_USERNAME=
TRANSCRIPT_PROXY_PASSWORD=

# Tolt Affiliate Configuration (Optional)
TOLT_API_KEY=
TOLT_API_BASE_URL=https://api.tolt.com/v1

# Trial Limits
TRIAL_OUTLINE_LIMIT=10
```

**Generate a Django secret key:**

```bash
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and replace `your-secret-key-here-generate-with-openssl-rand-base64-32` in `.env.backend`.

#### 1.4 Set Up PostgreSQL Database

**Start PostgreSQL:**

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL if not running
sudo systemctl start postgresql

# Enable PostgreSQL to start on boot
sudo systemctl enable postgresql
```

**Create the database:**

```bash
# Connect to PostgreSQL as postgres user
sudo -u postgres psql

# In PostgreSQL prompt, create database:
CREATE DATABASE db;

# Create user if needed (optional, postgres user usually works)
# CREATE USER postgres WITH PASSWORD 'change-password';
# GRANT ALL PRIVILEGES ON DATABASE db TO postgres;

# Exit PostgreSQL
\q
```

#### 1.5 Run Database Migrations

```bash
# Using UV
uv run python manage.py migrate

# OR using pip
python3 manage.py migrate
```

#### 1.6 Create Superuser (Optional but Recommended)

```bash
# Using UV
uv run python manage.py createsuperuser

# OR using pip
python3 manage.py createsuperuser
```

Follow the prompts to enter username, email, and password.

**Or use non-interactive command:**

```bash
# Using UV
uv run python manage.py create_superuser_noninteractive --email admin@example.com --password yourpassword

# OR using pip
python3 manage.py create_superuser_noninteractive --email admin@example.com --password yourpassword
```

#### 1.7 Start Backend Server

```bash
# Using UV
uv run python manage.py runserver

# OR using pip
python3 manage.py runserver
```

The backend will be available at: **http://localhost:8000**

**To run on a specific host/port:**

```bash
# Accessible from network
python3 manage.py runserver 0.0.0.0:8000

# Different port
python3 manage.py runserver 8001
```

### Step 2: Frontend Setup

#### 2.1 Install Root Dependencies

```bash
cd /home/saad/Desktop/Hassaan/Tubegenius
pnpm install
```

#### 2.2 Set Up Web App (Main Frontend)

```bash
cd /home/saad/Desktop/Hassaan/Tubegenius/web-app

# Install dependencies
pnpm install

# Create .env.local file (if needed)
# Check web-app/README.md for environment variables
```

**Start the web app:**

```bash
# From web-app directory
pnpm dev

# OR from root directory
cd /home/saad/Desktop/Hassaan/Tubegenius
pnpm web-app
```

The web app will be available at: **http://localhost:3000**

#### 2.3 Set Up Admin Panel (Optional)

```bash
cd /home/saad/Desktop/Hassaan/Tubegenius/admin-panel

# Install dependencies
pnpm install

# Start admin panel
pnpm dev

# OR from root directory
cd /home/saad/Desktop/Hassaan/Tubegenius
pnpm admin-panel
```

#### 2.4 Set Up Website (Optional)

```bash
cd /home/saad/Desktop/Hassaan/Tubegenius/website

# Install dependencies
pnpm install

# Start website
pnpm dev

# OR from root directory
cd /home/saad/Desktop/Hassaan/Tubegenius
pnpm website
```

---

## 🐳 Option 2: Docker Compose Setup

**Note:** The current `docker-compose.yaml` may need updates as it references a `frontend` directory that doesn't exist. The actual frontend is in `web-app`.

### Step 1: Update Docker Compose (If Needed)

The docker-compose.yaml references `frontend` but should reference `web-app`. You may need to update it or create Dockerfiles.

### Step 2: Create Environment Files

Create `.env.backend` in the root directory (same as above).

Create `.env.frontend` in the root directory for frontend:

```env
NEXTAUTH_SECRET=your-nextauth-secret-generate-with-openssl-rand-base64-32
NEXTAUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Generate NextAuth secret:**

```bash
openssl rand -base64 32
```

### Step 3: Start with Docker Compose

```bash
cd /home/saad/Desktop/Hassaan/Tubegenius

# Start all services
docker compose up

# OR start in background
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

---

## 🌐 Access Points

Once everything is running, you can access:

### Backend:

- **API Base URL**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/api/schema/swagger-ui/
- **API Schema (JSON)**: http://localhost:8000/api/schema/
- **Django Admin**: http://localhost:8000/admin/
- **Health Check**: http://localhost:8000/health/

### Frontend:

- **Web App**: http://localhost:3000
- **Admin Panel**: http://localhost:3001 (if configured)
- **Website**: http://localhost:3002 (if configured)

---

## 🔧 Common Development Commands

### Backend Commands

```bash
cd /home/saad/Desktop/Hassaan/Tubegenius/backend

# Start server
uv run python manage.py runserver          # UV
python3 manage.py runserver                # pip

# Run migrations
uv run python manage.py migrate            # UV
python3 manage.py migrate                  # pip

# Create migrations (after model changes)
uv run python manage.py makemigrations     # UV
python3 manage.py makemigrations           # pip

# Create superuser
uv run python manage.py createsuperuser   # UV
python3 manage.py createsuperuser         # pip

# Django shell
uv run python manage.py shell              # UV
python3 manage.py shell                    # pip

# Run tests
uv run pytest                              # UV
pytest                                     # pip

# Check for issues
uv run python manage.py check              # UV
python3 manage.py check                    # pip
```

### Frontend Commands

```bash
# From root directory
pnpm web-app          # Start web app
pnpm admin-panel      # Start admin panel
pnpm website          # Start website

# From individual directories
cd web-app && pnpm dev
cd admin-panel && pnpm dev
cd website && pnpm dev

# Build for production
cd web-app && pnpm build
cd admin-panel && pnpm build
cd website && pnpm build

# Linting and formatting
cd web-app && pnpm lint
cd web-app && pnpm lint:fix
cd web-app && pnpm prettier:fix
```

---

## 🐛 Troubleshooting

### Backend Issues

#### Database Connection Error

**Error**: `django.db.utils.OperationalError: connection to server failed`

**Solution**:

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Verify database exists
psql -U postgres -l

# Check database credentials in .env.backend
```

#### Module Not Found Error

**Error**: `ModuleNotFoundError: No module named 'django'`

**Solution**:

```bash
# Reinstall dependencies (recommended)
uv sync

# OR if using pip, ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt

# Verify Python version
python3 --version  # Should be 3.13+
```

**Note**: If you get "externally-managed-environment" error, use `uv sync` instead or create a virtual environment first.

#### Port Already in Use

**Error**: `Error: That port is already in use`

**Solution**:

```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
lsof -ti:8000 | xargs kill -9

# OR use a different port
python3 manage.py runserver 8001
```

#### Environment Variables Not Loading

**Solution**:

- Ensure `.env.backend` is in the `backend/` directory
- Check file permissions: `chmod 644 .env.backend`
- Verify file name is exactly `.env.backend` (not `.env.backend.txt`)

### Frontend Issues

#### Port Already in Use

```bash
# Find and kill process on port 3000
lsof -ti:3000 | xargs kill -9

# OR change port in package.json scripts
```

#### Module Not Found

```bash
# Clear node_modules and reinstall
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

#### Build Errors

```bash
# Clear Next.js cache
rm -rf .next
pnpm dev
```

---

## 📚 Additional Resources

- **Backend Documentation**: `backend/START_BACKEND.md`
- **Backend API**: http://localhost:8000/api/schema/swagger-ui/
- **Django Documentation**: https://docs.djangoproject.com/
- **Next.js Documentation**: https://nextjs.org/docs
- **UV Documentation**: https://github.com/astral-sh/uv

---

## ✅ Quick Checklist

- [ ] Python 3.13+ installed
- [ ] PostgreSQL installed and running
- [ ] Node.js 20.18.0+ installed
- [ ] pnpm 9.14.0+ installed
- [ ] Backend dependencies installed (`uv sync` or `pip install -r requirements.txt`)
- [ ] `.env.backend` file created and configured
- [ ] PostgreSQL database `db` created
- [ ] Database migrations run (`python manage.py migrate`)
- [ ] Superuser created (optional)
- [ ] Backend server running (`python manage.py runserver`)
- [ ] Frontend dependencies installed (`pnpm install`)
- [ ] Frontend running (`pnpm dev`)

---

## 🎉 You're All Set!

Once everything is running:

1. Backend API: http://localhost:8000
2. API Docs: http://localhost:8000/api/schema/swagger-ui/
3. Django Admin: http://localhost:8000/admin/
4. Web App: http://localhost:3000

Happy coding! 🚀
