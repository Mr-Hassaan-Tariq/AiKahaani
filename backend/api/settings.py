from datetime import timedelta
from os import environ
from pathlib import Path

import dj_database_url
from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

######################################################################
# General
######################################################################
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env files
load_dotenv(BASE_DIR / ".env.backend")
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = environ.get("SECRET_KEY", get_random_secret_key())

DEBUG = environ.get("DEBUG", "") == "1"

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "api",
    "tubegenius-backend-production-05e9.up.railway.app",  # Specific Railway domain
    ".railway.app",  # Allow Railway domains
    ".up.railway.app",  # Allow Railway preview domains
    "charmed-simple-asp.ngrok-free.app",
]

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://tubegenius.vercel.app",
    "https://tubegenius-frontend.vercel.app",
    "https://*.vercel.app",
    "https://*.railway.app",
    "https://*.up.railway.app",
    "https://*.netlify.app",
    "https://*.herokuapp.com",
    "https://*.render.com",
    "https://*.fly.dev",
    "https://*.app",
    "https://*.com",
    "https://*.dev",
    "https://*.io",
    "https://*.org",
    "https://*.net",
    "https://charmed-simple-asp.ngrok-free.app",
]

# Allow credentials (cookies, authorization headers)
CORS_ALLOW_CREDENTIALS = True

# Additional CORS settings for development
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True

# CORS headers that are allowed
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# CORS methods that are allowed
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

WSGI_APPLICATION = "api.wsgi.application"

ROOT_URLCONF = "api.urls"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# URL Configuration - Prevent automatic slash appending for API endpoints
APPEND_SLASH = False

######################################################################
# CSRF Configuration
######################################################################
CSRF_TRUSTED_ORIGINS = [
    "https://tubegenius-backend-production-05e9.up.railway.app",
    "https://*.railway.app",
    "https://*.up.railway.app",
    "https://tubegenius.vercel.app",
    "https://tubegenius-frontend.vercel.app",
    "https://*.vercel.app",
    "https://localhost:3000",
    "http://localhost:3000",
    "https://localhost:8000",
    "http://localhost:8000",
]

# CSRF settings for admin panel access
CSRF_COOKIE_SECURE = not DEBUG  # Use secure cookies in production
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript access to CSRF token
CSRF_COOKIE_SAMESITE = "Lax"  # Allow cross-site requests with CSRF protection

######################################################################
# Apps
######################################################################
THIRD_PARTY_APPS = [
    "anymail",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "corsheaders",
    "djstripe",
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "api",
    "users",
    "payments",
    "scripts",
    "django_filters",
] + THIRD_PARTY_APPS

######################################################################
# Middleware
######################################################################
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

######################################################################
# Templates
######################################################################
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

######################################################################
# Database
######################################################################
# Check if DATABASE_URL is provided (Railway standard)
DATABASE_URL = environ.get("DATABASE_URL")

if DATABASE_URL:
    # Parse DATABASE_URL for Railway/Aiven
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}


else:
    # Fallback to individual environment variables for Aiven
    db_user = environ.get("DATABASE_USER", "postgres")
    db_password = environ.get("DATABASE_PASSWORD", "change-password")
    db_name = environ.get("DATABASE_NAME", "db")
    db_host = environ.get("DATABASE_HOST", "localhost")
    db_port = environ.get("DATABASE_PORT", "5432")

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "USER": db_user,
            "PASSWORD": db_password,
            "NAME": db_name,
            "HOST": db_host,
            "PORT": db_port,
        }
    }

######################################################################
# Authentication
######################################################################
AUTH_USER_MODEL = "users.User"

# Google OAuth Configuration
GOOGLE_OAUTH2_CLIENT_ID = environ.get("GOOGLE_OAUTH2_CLIENT_ID", "")
GOOGLE_OAUTH2_CLIENT_SECRET = environ.get("GOOGLE_OAUTH2_CLIENT_SECRET", "")
GOOGLE_OAUTH2_REDIRECT_URI = environ.get(
    "GOOGLE_OAUTH2_REDIRECT_URI", "http://localhost:3000/"
)
# GOOGLE_OAUTH2_PROJECT_ID = environ.get("GOOGLE_OAUTH2_PROJECT_ID", "")

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

######################################################################
# Internationalization
######################################################################
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

######################################################################
# Staticfiles
######################################################################
STATIC_URL = "static/"

######################################################################
# Media
######################################################################
MEDIA_URL = "/media/"

MEDIA_ROOT = environ.get("MEDISA_ROOT", BASE_DIR / "media")

######################################################################
# Rest Framework
######################################################################
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 20,  # Default limit for LimitOffsetPagination
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "users.authentication.JWTAuthenticationWithAccessTokenBlacklist",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        # Global throttle rates (applied to all APIs)
        "anon": "100/hour",  # Anonymous users: 100 requests/hour
        "user": "1000/hour",  # Authenticated users: 1000 requests/hour
        # Method-specific rates (for fine-grained control)
        "get": "100/minute",
        "post": "20/minute",
        "put": "20/minute",
        "delete": "10/minute",
    },
}


# SimpleJWT configuration
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}


EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
DEFAULT_FROM_EMAIL = environ.get("DEFAULT_FROM_EMAIL")


ANYMAIL = {
    "BREVO_API_KEY": environ.get("BREVO_API_KEY"),
}

FRONTEND_URL = environ.get("FRONTEND_URL", "http://localhost:3000/")
######################################################################
# Unfold
######################################################################

######################################################################
# Stripe Configuration
######################################################################
STRIPE_SECRET_KEY = environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = environ.get("STRIPE_WEBHOOK_SECRET")

# DJ-Stripe Configuration
DJSTRIPE_WEBHOOK_SECRET = STRIPE_WEBHOOK_SECRET
DJSTRIPE_USE_NATIVE_S3 = True
DJSTRIPE_FOREIGN_KEY_TO_FIELD = "id"
DJSTRIPE_SECRET_KEY = STRIPE_SECRET_KEY
DJSTRIPE_SUBSCRIBER_MODEL = "users.User"
STRIPE_API_VERSION = "2024-06-20"

# Stripe settings
STRIPE_LIVE_MODE = environ.get("STRIPE_LIVE_MODE", "False").lower() == "true"
STRIPE_TEST_MODE = not STRIPE_LIVE_MODE

if STRIPE_TEST_MODE:
    STRIPE_SECRET_KEY = environ.get("STRIPE_TEST_SECRET_KEY") or STRIPE_SECRET_KEY

# DJ-Stripe Live/Test Mode Settings
DJSTRIPE_LIVE_MODE = STRIPE_LIVE_MODE
DJSTRIPE_TEST_MODE = STRIPE_TEST_MODE

######################################################################
# OPENAI Configuration
######################################################################
OPENAI_API_KEY = environ.get("OPENAI_API_KEY")
