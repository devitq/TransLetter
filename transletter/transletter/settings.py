import os
from pathlib import Path

from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

load_dotenv(override=False)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "secret_key")

DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() in ("true", "1", "yes", "y")

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(" ")

INTERNAL_IPS = os.getenv("DJANGO_INTERNAL_IPS", "127.0.0.1").split(" ")

MAX_AUTH_ATTEMPTS = int(os.getenv("DJNAGO_MAX_AUTH_ATTEMPTS", 3))

MEDIA_URL = "/media/"

if DEBUG:
    DEFAULT_USER_IS_ACTIVE = True
else:
    DEFAULT_USER_IS_ACTIVE = os.getenv(
        "DEFAULT_USER_IS_ACTIVE",
        "false",
    ).lower() in ("true", "1", "yes", "y")

INSTALLED_APPS = [
    # Other
    "django_cleanup.apps.CleanupConfig",
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Project's apps
    "landing.apps.LandingConfig",
    "accounts.apps.AccountsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Other
    "django.middleware.locale.LocaleMiddleware",
]

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

ROOT_URLCONF = "transletter.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "transletter.wsgi.application"

DB_NAME = os.getenv("DB_NAME", "sqlite").lower()

if DB_NAME == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        },
    }
elif DB_NAME == "postgresql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRE_DB_NAME", "postgres"),
            "USER": os.getenv("POSTGRE_DB_USER", "default"),
            "PASSWORD": os.getenv("POSTGRE_DB_PASSWORD", "password"),
            "HOST": os.getenv("POSTGRE_DB_HOST", "localhost"),
            "PORT": os.getenv("POSTGRE_DB_PORT", "5432"),
        },
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]

LANGUAGE_CODE = os.getenv("DEFAULT_LANGUAGE_CODE", "en-us")

LANGUAGES = (
    ("en", _("English")),
    ("ru", _("Russian")),
)

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = os.getenv("STATIC_URL", "static/")

STATICFILES_DIRS = [
    BASE_DIR / "static_dev",
]

STATIC_ROOT = BASE_DIR / "static"

MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTHENTICATION_BACKENDS = ("accounts.backends.AuthenticationBackend",)

LOGIN_URL = "/auth/login"

LOGIN_REDIRECT_URL = "/"

LOGOUT_REDIRECT_URL = "/auth/login"

USE_REAL_EMAIL = os.getenv("USE_REAL_EMAIL", "true").lower() in (
    "true",
    "1",
    "yes",
    "y",
)

if USE_REAL_EMAIL:
    EMAIL_HOST = os.getenv("EMAIL_HOST", "localhost")

    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")

    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")

    EMAIL_PORT = os.getenv("EMAIL_PORT", 25)

    EMAIL = os.getenv("EMAIL", "")
else:
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"

    EMAIL_FILE_PATH = BASE_DIR / "send_mail"

    EMAIL = "example@mail.com"

DEPLOYING_ON_HTTPS = os.getenv("DEPLOYING_ON_HTTPS", "false").lower() in (
    "true",
    "1",
    "yes",
    "y",
)

if DEPLOYING_ON_HTTPS:
    SECURE_HSTS_SECONDS = True

    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    SECURE_HSTS_PRELOAD = True
