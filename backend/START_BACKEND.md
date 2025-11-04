# 🚀 Starting the Backend Server

This guide will help you set up and run the TubeGenius backend server locally.

## 📋 Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.13+** - Required Python version
- **PostgreSQL** - Database server (running locally or remotely)
- **pip** or **uv** - Python package manager

### Checking Prerequisites

```bash
# Check Python version
python3 --version  # Should be 3.13 or higher

# Check if PostgreSQL is installed
psql --version

# Check if pip is available
python3 -m pip --version
```

## 🛠️ Setup Options

You have two options for managing dependencies:

### Option 1: Using pip (Traditional Method)

### Option 2: Using uv (Recommended - Faster)

If you don't have `uv` installed, install it first:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After installation, restart your terminal or run:

```bash
source $HOME/.cargo/env
```

## 📝 Step-by-Step Setup

### Step 1: Navigate to Backend Directory

```bash
cd /home/saad/Desktop/Hassaan/Tubegenius/backend
```

### Step 2: Install Dependencies

**Using pip:**

```bash
python3 -m pip install -r requirements.txt
```

**Using uv:**

```bash
uv sync
```

### Step 3: Create Environment File

Create a `.env.backend` file in the backend directory:

```bash
# Create the file
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

# OR use DATABASE_URL (for Railway, Heroku, etc.)
# DATABASE_URL=postgresql://user:password@host:port/dbname

# Frontend URL
FRONTEND_URL=http://localhost:3000/

# Google OAuth (Optional)
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret
GOOGLE_OAUTH2_REDIRECT_URI=http://localhost:3000/

# Email Configuration (Brevo/SendGrid)
DEFAULT_FROM_EMAIL=noreply@tubegenius.com
BREVO_API_KEY=your-brevo-api-key

# Stripe Configuration (Optional)
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret
STRIPE_TEST_SECRET_KEY=your-stripe-test-secret-key
STRIPE_LIVE_MODE=False

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4.1
TITLE_GENERATION_API_KEY=your-openai-api-key
TITLE_GENERATION_MODEL=gpt-4.1

# YouTube Transcript Proxy (Optional)
TRANSCRIPT_PROXY_USERNAME=your-proxy-username
TRANSCRIPT_PROXY_PASSWORD=your-proxy-password

# Tolt Affiliate Configuration (Optional)
TOLT_API_KEY=your-tolt-api-key
TOLT_API_BASE_URL=https://api.tolt.com/v1

# Trial Limits
TRIAL_OUTLINE_LIMIT=10
```

**Generate a secret key:**

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 4: Set Up Database

Make sure PostgreSQL is running:

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # On Linux

# Or start it manually
sudo systemctl start postgresql
```

Create the database (if it doesn't exist):

```bash
# Connect to PostgreSQL
psql -U postgres

# In PostgreSQL prompt:
CREATE DATABASE db;
\q
```

### Step 5: Run Migrations

Apply database migrations:

**Using pip:**

```bash
python3 manage.py migrate
```

**Using uv:**

```bash
uv run python manage.py migrate
```

### Step 6: Create Superuser (Optional)

Create an admin user to access the Django admin panel:

**Using pip:**

```bash
python3 manage.py createsuperuser
```

**Using uv:**

```bash
uv run python manage.py createsuperuser
```

Follow the prompts to enter username, email, and password.

**Or use the non-interactive command:**

```bash
# Using pip
python3 manage.py create_superuser_noninteractive --email admin@example.com --password yourpassword

# Using uv
uv run python manage.py create_superuser_noninteractive --email admin@example.com --password yourpassword
```

### Step 7: Start the Development Server

**Using pip:**

```bash
python3 manage.py runserver
```

**Using uv:**

```bash
uv run python manage.py runserver
```

The server will start at: **http://localhost:8000**

To run on a specific host and port:

```bash
python3 manage.py runserver 0.0.0.0:8000  # Accessible from network
python3 manage.py runserver 8001          # Different port
```

## 🎯 Quick Reference Commands

### Development Commands

```bash
# Start server
python3 manage.py runserver              # pip
uv run python manage.py runserver        # uv

# Run migrations
python3 manage.py migrate                # pip
uv run python manage.py migrate          # uv

# Create migrations (after model changes)
python3 manage.py makemigrations         # pip
uv run python manage.py makemigrations    # uv

# Create superuser
python3 manage.py createsuperuser        # pip
uv run python manage.py createsuperuser  # uv
```

### Database Commands

```bash
# Show migration status
python3 manage.py showmigrations

# Rollback last migration
python3 manage.py migrate app_name zero

# Load initial data (if available)
python3 manage.py loaddata fixtures.json
```

### Testing Commands

```bash
# Run all tests
python3 manage.py test                   # pip
uv run python manage.py test             # uv

# Run specific app tests
python3 manage.py test users

# Run with pytest (if configured)
pytest                                    # pip
uv run pytest                            # uv
```

### Utility Commands

```bash
# Django shell
python3 manage.py shell                  # pip
uv run python manage.py shell            # uv

# Collect static files
python3 manage.py collectstatic

# Check for issues
python3 manage.py check
```

## 🌐 Access Points

Once the server is running, you can access:

- **API Base URL**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/api/schema/swagger-ui/
- **API Schema (JSON)**: http://localhost:8000/api/schema/
- **Django Admin**: http://localhost:8000/admin/
- **Health Check**: http://localhost:8000/api/health/

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Error

**Error**: `django.db.utils.OperationalError: connection to server failed`

**Solution**:

- Check if PostgreSQL is running: `sudo systemctl status postgresql`
- Verify database credentials in `.env.backend`
- Ensure database exists: `psql -U postgres -l`

#### 2. Module Not Found Error

**Error**: `ModuleNotFoundError: No module named 'django'`

**Solution**:

- Reinstall dependencies: `pip install -r requirements.txt` or `uv sync`
- Check if virtual environment is activated (if using one)
- Verify Python version: `python3 --version` should be 3.13+

#### 3. Migration Errors

**Error**: `django.db.migrations.exceptions.InconsistentMigrationHistory`

**Solution**:

```bash
# Reset migrations (WARNING: This will delete data)
python3 manage.py migrate --fake-initial
```

#### 4. Port Already in Use

**Error**: `Error: That port is already in use`

**Solution**:

```bash
# Use a different port
python3 manage.py runserver 8001

# Or find and kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```

#### 5. Environment Variables Not Loading

**Error**: Settings not being read from `.env.backend`

**Solution**:

- Ensure `.env.backend` is in the `backend/` directory
- Check file permissions: `chmod 644 .env.backend`
- Verify the file name is exactly `.env.backend` (not `.env.backend.txt`)

#### 6. Import Errors

**Error**: `ImportError: cannot import name 'X'`

**Solution**:

- Clear Python cache: `find . -type d -name __pycache__ -exec rm -r {} +`
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

## 🔐 Security Notes

1. **Never commit `.env.backend`** to version control
2. Use strong `SECRET_KEY` values in production
3. Set `DEBUG=0` in production environments
4. Use secure database passwords
5. Keep API keys secure and rotate them regularly

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [UV Package Manager](https://github.com/astral-sh/uv)

## 🆘 Getting Help

If you encounter issues:

1. Check the error logs in the terminal output
2. Verify all prerequisites are installed
3. Ensure environment variables are set correctly
4. Check database connectivity
5. Review the troubleshooting section above

---

**Happy Coding! 🎉**
