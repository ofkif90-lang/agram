import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
import os

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
DEBUG = False
ALLOWED_HOSTS = [
    "agram-production.up.railway.app",
]
INSTALLED_APPS = ["django.contrib.staticfiles",
                   "django.contrib.contenttypes", 
                  "django.contrib.auth",
                    "downloader",
                    'django.contrib.sitemaps',
                    ]
MIDDLEWARE = ["agram.middleware.SecurityHeadersMiddleware",
                  'whitenoise.middleware.WhiteNoiseMiddleware',
                         
                         "agram.middleware.RemoveRobotsTagMiddleware",                  ]




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



STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"



SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True