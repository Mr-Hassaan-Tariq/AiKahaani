# Creating a Superuser on the Server

## Quick Reference

### If using Docker on the server:

```bash
docker compose exec api uv run -- python manage.py createsuperuser
```

### If running directly on the server (SSH access):

```bash
cd /path/to/backend
python manage.py createsuperuser
```

Or if using `uv`:

```bash
cd /path/to/backend
uv run -- python manage.py createsuperuser
```

### If deployed on Railway:

**Option 1: Using Railway Dashboard (Recommended)**

1. Go to https://railway.app
2. Select your project and service
3. Click "Shell" or "Connect" button
4. Run: `python manage.py createsuperuser`

**Option 2: Using Railway Dashboard with Non-Interactive Command (Easiest)**

1. Go to Railway Dashboard → Your Project → Your Service
2. Click "Variables" tab
3. Add these environment variables:
   - `DJANGO_SUPERUSER_EMAIL` = your-email@example.com
   - `DJANGO_SUPERUSER_USERNAME` = admin
   - `DJANGO_SUPERUSER_PASSWORD` = your-secure-password
4. Click "Shell" or "Connect" button
5. Run: `python manage.py create_superuser_noninteractive`
6. (Optional) Remove the environment variables after creating the superuser for security

**Option 3: Using Railway CLI**
The `railway run` command runs locally with Railway env vars, not on the server.
Use the Railway Dashboard shell instead.

### If deployed on Heroku:

```bash
heroku run python manage.py createsuperuser
```

### If deployed on Render:

```bash
render run python manage.py createsuperuser
```

## What the command will ask:

1. **Username** - Enter your desired username
2. **Email address** - Enter your email address
3. **Password** - Enter a secure password (you'll be asked to confirm it)

## Note:

Make sure your database migrations are up to date before creating a superuser:

```bash
python manage.py migrate
```

## Non-Interactive Superuser Creation

For Railway or automated deployments, you can create a superuser non-interactively:

### Using Environment Variables:

```bash
export DJANGO_SUPERUSER_EMAIL=admin@example.com
export DJANGO_SUPERUSER_USERNAME=admin
export DJANGO_SUPERUSER_PASSWORD=your-secure-password
python manage.py create_superuser_noninteractive
```

### Using Command Arguments:

```bash
python manage.py create_superuser_noninteractive \
  --email admin@example.com \
  --username admin \
  --password your-secure-password
```
