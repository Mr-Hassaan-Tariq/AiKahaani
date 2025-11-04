# Creating Superuser on Railway

## Method 1: Using Railway CLI (Recommended)

### Prerequisites:

1. Install Railway CLI:

   ```bash
   npm i -g @railway/cli
   ```

2. Login to Railway:

   ```bash
   railway login
   ```

3. Link your project (if not already linked):
   ```bash
   railway link
   ```

### Create Superuser:

```bash
railway run python manage.py createsuperuser
```

This will prompt you for:

- Username
- Email address
- Password (and confirmation)

---

## Method 2: Using Railway Dashboard (Web Interface)

1. Go to your Railway project dashboard
2. Navigate to your service
3. Click on the "Shell" or "Connect" button
4. This opens a terminal in your Railway environment
5. Run:
   ```bash
   python manage.py createsuperuser
   ```

---

## Method 3: If you're already in Railway Shell

If you're already inside the Railway shell/container and Django is not available:

### Check if you're in the correct directory:

```bash
cd /app
ls -la manage.py
```

### If Django is not installed, check the build environment:

Railway uses nixpacks which should install dependencies during build. Check if there's a virtual environment or if packages are installed elsewhere:

```bash
# Check Python version
python --version

# Check if Django is installed in a different location
python -c "import sys; print('\n'.join(sys.path))"

# Try to find Django
find /app -name "django" -type d 2>/dev/null
```

### If you need to install dependencies manually:

```bash
# Check if pip is available
python -m pip --version

# Install dependencies
python -m pip install -r requirements.txt

# Then create superuser
python manage.py createsuperuser
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'django'"

**Solution 1**: Make sure you're in the correct directory (`/app`):

```bash
cd /app
python manage.py createsuperuser
```

**Solution 2**: Check if Railway build completed successfully. The dependencies should be installed during the build process.

**Solution 3**: If dependencies are missing, you may need to trigger a rebuild:

- Go to Railway dashboard
- Navigate to your service
- Click "Redeploy" or "Rebuild"

---

## Notes

- Railway uses nixpacks builder which automatically detects Python projects and installs dependencies
- Your `railway.json` shows `startCommand: "python manage.py migrate && python manage.py runserver 0.0.0.0:$PORT"`
- This means Django should be available when the service runs
- If Django is not available in the shell, it might be a path/environment issue
