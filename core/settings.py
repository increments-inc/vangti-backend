from pathlib import Path
import os
import sys
from decouple import config
from datetime import timedelta
import firebase_admin
from firebase_admin import firestore, credentials
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("DJANGO_SECRET_KEY")

DEBUG = config("DEBUG", cast=bool, default=False)

SALT = "random"

ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS").split(",")

INSTALLED_APPS = [
    # async
    'daphne',

    # default
    "django.contrib.sites",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.gis',

    # packages
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    'debug_toolbar',
    'corsheaders',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'import_export',

    # apps
    'users',
    'subscription',
    'analytics',
    'transactions',
    'web_socket',
    'locations',
    'user_setting',
    'txn_credits',
]

SITE_ID = 1

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        # simple jwt
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    "DEFAULT_RENDERER_CLASSES": (
        "utils.renderer.CustomJSONRenderer",
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),

    # versioning
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'ALLOWED_VERSIONS': ['v1', 'v2'],
    'DEFAULT_VERSION': 'v1',

    "EXCEPTION_HANDLER": "utils.renderer.custom_exception_handler",
    "DEFAULT_PAGINATION_CLASS": "utils.custom_pagination.CustomPagination",
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',

    "PAGE_SIZE": 10,
    # swagger
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": (
        # "rest_framework_simplejwt.tokens.AccessToken",
        "users.auth_jwt.JWTAccessToken",
    ),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Vangti API',
    'DESCRIPTION': 'its in the name',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': r'/api/(?P<version>(v1|v2))',
}

AUTH_USER_MODEL = "users.User"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # cors
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # debug
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # custom
    'core.custom_middleware.CustomMiddleware'
]

# debug toolbar
INTERNAL_IPS = [
    "127.0.0.1",
    "192.168.27.141",
]

# cors
# CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = config("CORS_HOSTS").split(",")
CSRF_TRUSTED_ORIGINS = config("CORS_TRUSTED_ORIGIN").split(",")

ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': config("DB_ENGINE", default="django.db.backends.sqlite3"),
        'NAME': config("DB_NAME", default=BASE_DIR / "db.sqlite3"),
        'USER': config("DB_USER", default=""),
        'PASSWORD': config("DB_PASSWORD", default=""),
        'HOST': config("DB_HOST", default=""),
        'PORT': config("DB_PORT", default=""),
    },
    'location': {
        'ENGINE': config("DB_ENGINE_LOC", default="django.db.backends.sqlite3"),
        'NAME': config("DB_NAME_LOC", default=BASE_DIR / "db1.sqlite3"),
        'USER': config("DB_USER_LOC", default=""),
        'PASSWORD': config("DB_PASSWORD_LOC", default=""),
        'HOST': config("DB_HOST_LOC", default=""),
        'PORT': config("DB_PORT_LOC", default=""),
    },
    'credits': {
        'ENGINE': config("DB_ENGINE_CRE", default="django.db.backends.sqlite3"),
        'NAME': config("DB_NAME_CRE", default=BASE_DIR / "db1.sqlite3"),
        'USER': config("DB_USER", default=""),
        'PASSWORD': config("DB_PASSWORD", default=""),
        'HOST': config("DB_HOST", default=""),
        'PORT': config("DB_PORT", default=""),
    }
}

DATABASE_ROUTERS = [
    'core.db_router.LocationRouter',
    'core.db_router.CreditRouter',
]

# firebase
FIREBASE_API_KEY = config("FIREBASE_API_KEY")
FIREBASE_PROJECT_ID = config("FIREBASE_PROJECT_ID")
cred = credentials.Certificate(os.path.join(BASE_DIR, "credentials.json"))
firebase_admin.initialize_app(cred)

# password validators

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Dhaka'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

STATIC_ROOT = 'static/'

# STATICFILES_DIRS = [BASE_DIR / 'static']


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

GDAL_LIBRARY_PATH = config("GDAL_LIBRARY_PATH")
GEOS_LIBRARY_PATH = config("GEOS_LIBRARY_PATH")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT")
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
# EMAIL_USE_TLS = config("EMAIL_USE_TLS") == "True"
# EMAIL_USE_SSL = config('EMAIL_USE_SSL') == 'True'
DEFAULT_FROM_EMAIL = "Organization Name <demo@domain.com>"

# authentication parameters
REST_SESSION_LOGIN = False
# REST_USE_JWT = True
JWT_AUTH_COOKIE = "access"
JWT_AUTH_REFRESH_COOKIE = "refresh"
# JWT_AUTH_HTTPONLY = True
# JWT_AUTH_SAMESITE = "Lax"  # "None" | "Lax" | "Strict"
# OLD_PASSWORD_FIELD_ENABLED = True
# ACCOUNT_AUTHENTICATION_METHOD = "email"
# ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_EMAIL_VERIFICATION = "none"
# REST_SESSION_LOGIN = False  # Set Session ID and CSRF Token to Cookie
# LOGOUT_ON_PASSWORD_CHANGE = True  # For Cookie Based Login


# redis
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
    }
}

CHANNEL_LAYERS = {
    "default": {
        # "BACKEND": "channels_redis.core.RedisChannelLayer",
        "BACKEND": "channels_redis.pubsub.RedisPubSubChannelLayer",

        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
            "capacity": 5000,
            "channel_capacity": {
                "websocket.send": 50000,
            },
            "expiry": 60,
            "group_expiry": 86400,
        },
    },
}
# ASGI_THREADS = 1000

MEDIA_URL = "/media/"
MEDIA_ROOT = "media"

# Celery settings
CELERY_TIMEZONE = "Asia/Dhaka"
# CELERY_TASK_TRACK_STARTED = True
# CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"
CELERY_BEAT_SCHEDULE = {
    # 'test_task': {
    #     'task': 'web_socket.tasks.test_task',
    #     'schedule': crontab(minute="0", hour='*/3'),
    #     'args': ('hello world',),
    # },
    'user_deletion_routine_task': {
        'task': 'users.tasks.user_deletion_routine_task',
        # 'schedule': crontab(minute='*/5'),
        'schedule': crontab(hour=0, minute=0, day_of_month='1'),
    },
}

# DOMAIN
DOMAIN_NAME = config("DOMAIN")

# SMS
SMS_URL = config("SMS_URL")
SMS_API_KEY = config("SMS_API_KEY")

# GOOGLE MAPS API
GOOGLE_MAPS_API_KEY = config("GOOGLE_MAPS_API_KEY")

# APP STORE DEFAULTS
APP_STORE_DEFAULT_PHONE = "+8801712345678"
APP_STORE_DEFAULT_OTP = "123456"

# provider commission
PROVIDER_COMMISSION = 0.01

# provider commission
PLATFORM_CHARGE = 0.1

# location
LOCATION_RADIUS = config("LOCATION_RADIUS", default=1)

# session
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 1800
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True

# log file location
LOG_DIR = config("LOG_LOCATION")

