"""
Django settings for resume_analyzer project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-&gkv)8#8e#4o66-ew(dn*8#d0oiv((%@613_ebhx(gh6$dcr$3"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "named_entity_recognition",
    "candidate_matching",
    "resume_classification",
    "chatbot",
    "resume_generation",
    "resume_analytics",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "resume_analyzer.middleware.LoginRequiredMiddleware",
]

ROOT_URLCONF = "resume_analyzer.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = "resume_analyzer.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

NER_MEDIA_ROOT = BASE_DIR / "named_entity_recognition/uploads"
NER_MEDIA_URL = "/named_entity_recognition/uploads/"

RA_MEDIA_ROOT = BASE_DIR / "resume_analytics/uploads"
RA_MEDIA_URL = "/resume_analytics/uploads/"

CM_MEDIA_ROOT = BASE_DIR / "candidate_matching/uploads"
CM_MEDIA_URL = "/candidate_matching/uploads/"

RC_MEDIA_ROOT = BASE_DIR / "resume_classification/uploads"
RC_MEDIA_URL = "/resume_classification/uploads/"

RG_MEDIA_ROOT = BASE_DIR / "resume_generation/uploads"
RG_MEDIA_URL = "/resume_generation/uploads/"

CB_MEDIA_ROOT = BASE_DIR / "chatbot/uploads"
CB_MEDIA_URL = "/chatbot/uploads/"

CB_INDX_MEDIA_ROOT = BASE_DIR / "chatbot/index"
CB_INDX_MEDIA_URL = "/chatbot/index/"

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

AUTHENTICATION_BACKENDS = [
    'resume_analyzer.authentication_backends.CustomBackend',  # Path to your custom backend
    'django.contrib.auth.backends.ModelBackend',    # Default backend (optional)
]

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# List of URLs that should be accessible without login
EXEMPT_URLS = ['/login/']
