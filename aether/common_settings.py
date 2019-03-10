import os
from django.urls import reverse_lazy

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Static and mediafile directories
MEDIA_ROOT = os.path.join(BASE_DIR, 'content/media/')
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'content/static/')
STATIC_URL = '/static/'

# Secret key, should be filled with random
SECRET_KEY = ''

DEBUG = False
ALLOWED_HOSTS = []

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Default forum message/thread paging limits
FORUM_MESSAGE_LIMIT = 25
FORUM_THREAD_LIMIT = 25

RAVEN_CONFIG = {
    'dsn': '',
}

# Upload limits
FILE_UPLOAD_PERMISSIONS = 0o644
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 8
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 8

# CSP Headers
CSP_DEFAULT_SRC = ("'self'", )
CSP_IMG_SRC = ("'self'", "*")
CSP_SCRIPT_SRC = ("'self'", "'unsafe-eval'", "https://www.google.com", "https://www.gstatic.com")
CSP_FONT_SRC = ("'self'", "https://use.fontawesome.com", "https://fonts.gstatic.com")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://*.fontawesome.com", "https://fonts.googleapis.com",
                 "https://fonts.gstatic.com")
CSP_FRAME_SRC = ("https://www.youtube.com", "https://youtu.be", "https://www.google.com")
CSP_OBJECT_SRC = ("'none'", )

# CSP Reporting options
CSP_REPORT_URI = reverse_lazy('report_csp')
CSP_REPORT_ONLY = False
CSP_REPORTS_EMAIL_ADMINS = False
CSP_REPORTS_SAVE = False
CSP_REPORTS_LOG = True

# Redirect to forum after login by default
LOGIN_REDIRECT_URL = '/forum'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "aether/static"),
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'aether.utils.hashers.CustomSHA256PasswordHasher'
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}

INSTALLED_APPS = [
    'aether.forum',
    'aether.main_site',
    'aether.api',
    'aether.gallery',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'raven.contrib.django.raven_compat',
    'timezone_field',
    'imagekit',
    'crispy_forms',
    'precise_bbcode',
    'captcha',
    'rest_framework',
    'cspreports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
    'aether.utils.middleware.TimezoneMiddleware',
]

ROOT_URLCONF = 'aether.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'aether.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Log handlers, insert our own database log handler
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry', 'console'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'tasks': {
            'level': 'INFO',
        },
        'raven': {
            'level': 'WARNING',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'WARNING',
            'handlers': ['console'],
            'propagate': False,
        },
        '': {
            'handlers': ['console', 'sentry'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = False
USE_TZ = True

# BBCode downloader limits
BBCODE_CACHE_IMAGE_MAX_SIZE = 8 * 1024 * 1024  # 8M
BBCODE_CACHE_IMAGE_MIME_TYPES = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
]

# Set european looking datetime formatting
DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i'
TIME_FORMAT = 'H:i'

# Default sender for any emails we send outwards
DEFAULT_FROM_EMAIL = 'no-reply@aetherguild.net'

# Cache sessions
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

# Recaptcha for registration
NOCAPTCHA = True

# Use Redis cache
CACHES = {
    'default': {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/12",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    'imagekit': {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/13",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Cache backend for imagekit
IMAGEKIT_CACHE_BACKEND = 'imagekit'

# Celery uses redis as broker
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/11'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ENABLE_UTC = True
CELERY_RESULT_PERSISTENT = False
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': 3600 * 12,
    'fanout_prefix': True,
    'fanout_patterns': True
}
CELERY_TASK_PUBLISH_RETRY_POLICY = {
    'max_retries': 3,
    'interval_start': 300,
    'interval_step': 300,
    'interval_max': 3000,
}


def make_email_conf(debug_mode):
    if debug_mode:
        return 'django.core.mail.backends.console.EmailBackend'
    else:
        return 'django.core.mail.backends.smtp.EmailBackend'
