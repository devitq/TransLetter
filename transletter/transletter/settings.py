import os
from pathlib import Path

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

load_dotenv(override=False)

# Common settings

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "secret_key")
DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() in ("true", "1", "yes", "y")
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(" ")
INTERNAL_IPS = os.getenv("DJANGO_INTERNAL_IPS", "127.0.0.1").split(" ")

INSTALLED_APPS = [
    # Other
    "sorl.thumbnail",
    "django_cleanup.apps.CleanupConfig",
    "djmoney",
    "plans",
    "ordered_model",
    "django_recaptcha",
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
    "burse.apps.BurseConfig",
    "projects.apps.ProjectsConfig",
    "rating.apps.RatingConfig",
    "resume.apps.ResumeConfig",
    "translator_request.apps.TranslatorRequestConfig",
    "notifications.apps.NotificationsConfig",
    "translation_request.apps.TranslationRequestConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    # Projects's middleware
    "accounts.middleware.Accounts",
]
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
ROOT_URLCONF = "transletter.urls"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
PLANS_CURRENCY = "USD"
COMMISION = 0.05

# Files settings

TRANSLATION_FILE_FORMATS = ("po", "json")
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STATIC_URL = os.getenv("STATIC_URL", "static/")
STATICFILES_DIRS = [
    BASE_DIR / "static_dev",
]
STATIC_ROOT = BASE_DIR / "static"
STORAGE_NAME = os.getenv("STORAGE_NAME", "default").lower()

# ReCaptcha settings

RECAPTCHA_ENABLED = os.getenv("RECAPTCHA_ENABLED", "false").lower() in (
    "true",
    "1",
    "yes",
    "y",
)
RECAPTCHA_PUBLIC_KEY = os.getenv("RECAPTCHA_PUBLIC_KEY", "public_key")
RECAPTCHA_PRIVATE_KEY = os.getenv("RECAPTCHA_PRIVATE_KEY", "private_key")

# Debug settings

if DEBUG:
    DEFAULT_USER_IS_ACTIVE = os.getenv(
        "DEFAULT_USER_IS_ACTIVE",
        "true",
    ).lower() in ("true", "1", "yes", "y")
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
else:
    DEFAULT_USER_IS_ACTIVE = os.getenv(
        "DEFAULT_USER_IS_ACTIVE",
        "false",
    ).lower() in ("true", "1", "yes", "y")

# Database settings

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

# Localization settings

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

# Auth settings

LOGIN_URL = reverse_lazy("accounts:login")
LOGIN_REDIRECT_URL = reverse_lazy("dashboard:index")
LOGOUT_REDIRECT_URL = reverse_lazy("accounts:login")
AUTHENTICATION_BACKENDS = ("accounts.backends.AuthenticationBackend",)
MAX_AUTH_ATTEMPTS = int(os.getenv("DJNAGO_MAX_AUTH_ATTEMPTS", 3))
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

# Sorl settings

THUMBNAIL_PRESERVE_FORMAT = True
THUMBNAIL_REDIS_URL = os.getenv("REDIS_URL", None)
THUMBNAIL_STORAGE = "django.core.files.storage.FileSystemStorage"
if THUMBNAIL_REDIS_URL:
    THUMBNAIL_KVSTORE = "sorl.thumbnail.kvstores.redis_kvstore.KVStore"

# Email settings

EMAIL = os.getenv("EMAIL", "example@mail.com")
USE_REAL_EMAIL = os.getenv("USE_REAL_EMAIL", "false").lower() in (
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
    EMAIL_USE_TLS = False
    EMAIL_USE_SSL = True
else:
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = BASE_DIR / "send_mail"
DEFAULT_FROM_EMAIL = EMAIL

# For HTTPs

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

# Logger settings

LOGGING_DIR = BASE_DIR / "logs"

if not LOGGING_DIR.exists():
    LOGGING_DIR.mkdir(parents=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
        },
        "database": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "database"],
            "propagate": True,
        },
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["database"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
