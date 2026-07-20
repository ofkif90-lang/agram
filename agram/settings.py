import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "agram-dev-secret-key-change-in-production-2024"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = ["django.contrib.staticfiles", "django.contrib.contenttypes", "django.contrib.auth", "downloader"]
MIDDLEWARE = ["agram.middleware.SecurityHeadersMiddleware",
                  'whitenoise.middleware.WhiteNoiseMiddleware',
]
ROOT_URLCONF = "agram.urls"
WSGI_APPLICATION = "agram.wsgi.application"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": []},
}]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
LANGUAGE_CODE = "ar"
TIME_ZONE = "Africa/Cairo"
USE_I18N = True
USE_TZ = False
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"