# ⚡ Quick Start Guide

## 🚀 Start Backend (Django)

```bash
# 1. Navigate to backend
cd /home/saad/Desktop/Hassaan/Tubegenius/backend

# 2. Install dependencies
uv sync                    # Recommended: Using UV (works on all systems)

# NOTE: If you prefer pip, create a virtual environment first:
# python3 -m venv venv
# source venv/bin/activate
# pip install -r requirements.txt

# 3. Create .env.backend file (if not exists)
# Copy template and fill in values (see LOCAL_SETUP.md)

# 4. Ensure PostgreSQL is running
sudo systemctl start postgresql

# 5. Create database (if not exists)
sudo -u postgres psql
CREATE DATABASE db;
\q

# 6. Run migrations
uv run python manage.py migrate
# OR
python3 manage.py migrate

# 7. Create superuser (optional)
uv run python manage.py createsuperuser
# OR
python3 manage.py createsuperuser

# 8. Start server
uv run python manage.py runserver
# OR
python3 manage.py runserver
```

**Backend will run at**: http://localhost:8000

---

## 🎨 Start Frontend (Next.js)

### Web App (Main Frontend)

```bash
# Option 1: From root directory
cd /home/saad/Desktop/Hassaan/Tubegenius
pnpm install
pnpm web-app

# Option 2: From web-app directory
cd /home/saad/Desktop/Hassaan/Tubegenius/web-app
pnpm install
pnpm dev
```

**Web app will run at**: http://localhost:3000

### Admin Panel (Optional)

```bash
cd /home/saad/Desktop/Hassaan/Tubegenius
pnpm admin-panel

# OR
cd admin-panel
pnpm install
pnpm dev
```

### Website (Optional)

```bash
cd /home/saad/Desktop/Hassaan/Tubegenius
pnpm website

# OR
cd website
pnpm install
pnpm dev
```

---

## 📋 Prerequisites Checklist

- [ ] Python 3.13+ installed
- [ ] PostgreSQL installed and running
- [ ] Node.js 20.18.0+ installed
- [ ] pnpm 9.14.0+ installed
- [ ] `.env.backend` file created with required variables
- [ ] PostgreSQL database `db` created
- [ ] OpenAI API key (for script generation)

---

## 🔗 Access Points

- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/api/schema/swagger-ui/
- **Django Admin**: http://localhost:8000/admin/
- **Health Check**: http://localhost:8000/health/
- **Web App**: http://localhost:3000

---

## 🆘 Quick Troubleshooting

### Backend won't start?

```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Check migrations
python3 manage.py migrate

# Check environment file
ls -la backend/.env.backend
```

### Frontend won't start?

```bash
# Clear and reinstall
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### Port already in use?

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

---

## 📚 Full Documentation

- **Complete Setup Guide**: See `LOCAL_SETUP.md`
- **Backend Review**: See `BACKEND_REVIEW.md`
- **Backend Details**: See `backend/START_BACKEND.md`

---

**Need help?** Check the troubleshooting section in `LOCAL_SETUP.md`
