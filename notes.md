#####
1. database gis
2. daphne
3. rest
4. swagger
5. debug
6. cors
7. simplejwt
8. channels


celery -A core.celery beat --loglevel=info
celery -A core worker --loglevel=info


python3 manage.py migrate --database=location


users = User.objects.using('users').all()







########
GDAL_LIBRARY_PATH="/opt/homebrew/opt/gdal/lib/libgdal.dylib"
GEOS_LIBRARY_PATH = '/opt/homebrew/opt/geos/lib/libgeos_c.dylib'



#########
# settings.py

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'django.contrib.gis',


    'users',
    'msg',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',

    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Your Project API',
    'DESCRIPTION': 'Your project description',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # OTHER SETTINGS
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'chatrtc.urls'

WSGI_APPLICATION = 'chatrtc.wsgi.application'
ASGI_APPLICATION = 'chatrtc.asgi.application'

DATABASES = {
   'default': {
       'ENGINE': 'django.contrib.gis.db.backends.postgis',
       'NAME': 'postgres',
       'USER': 'postgres',
       'PASSWORD': '',
       'HOST': 'localhost',
       'PORT': '5432',
   }
}

STATIC_URL = 'static/'
STATICFILES_DIR = [os.path.join(BASE_DIR, "static")]

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

GDAL_LIBRARY_PATH = config("GDAL_LIBRARY_PATH")
GEOS_LIBRARY_PATH = config("GEOS_LIBRARY_PATH")

#####
# libraries
GEOS, GDAL GeoIP, PROJ.4, postgis
https://realpython.com/location-based-app-with-geodjango-tutorial/

