"""
Configuración de 'Django' para el proyecto 'config'.

Generado por 'django-admin startproject' utilizando 'Django 5.2.18'.

Para obtener más información sobre este archivo, visite:
https://docs.djangoproject.com/en/5.2/topics/settings/

Para consultar la lista completa de parámetros y sus valores, véase:
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv


# Crea rutas dentro del proyecto de la siguiente manera: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Carga la configuración local sin sustituir variables definidas en Windows.
# La ruta explícita evita depender del directorio de inicio del proceso.
# https://bbc2.github.io/python-dotenv/
load_dotenv(BASE_DIR / ".env", override=False, interpolate=False)

# La clave se obtiene del entorno; no se incluye una clave alternativa en el código.
# https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/#secret-key
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY.strip():
    raise ImproperlyConfigured(
        "Define DJANGO_SECRET_KEY en el entorno o en Codigo/.env; "
        "consulta Codigo/.env.example."
    )


# Un 'bool' que activa o desactiva el modo de depuración.
# https://docs.djangoproject.com/en/5.2/ref/settings/#debug
DEBUG = True


# Una lista de 'str' que representan los nombres de host o dominio a los que este sitio de 'Django' puede dar servicio.
# https://docs.djangoproject.com/en/5.2/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []


# Una lista de 'str' que designan todas las aplicaciones que están habilitadas dentro de esta instalación de 'Django'.
# https://docs.djangoproject.com/en/5.2/ref/settings/#installed-apps
INSTALLED_APPS = [

    # Aplicaciones predeterminadas de 'Django' y módulos del marketplace.
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Aplicación encargada de la gestión de cuentas de usuario.
    "cuentas_app.apps.CuentasAppConfig",
    "productos_app.apps.ProductosAppConfig",
    "carrito_app.apps.CarritoAppConfig",

]


# Una lista del 'middleware' que se puede utilizar.
# https://docs.djangoproject.com/en/5.2/ref/settings/#middleware
#
# El middleware es un marco de trabajo que permite intervenir en el procesamiento de solicitudes y respuestas de 'Django'.
# https://docs.djangoproject.com/en/5.2/topics/http/middleware/#middleware
MIDDLEWARE = [

    # Componentes predeterminados de 'Django' para procesar solicitudes y respuestas 'HTTP'.
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]


# Un 'str' que representa la ruta completa de importación en 'Python' hasta la raíz de 'URLconf'
# https://docs.djangoproject.com/en/5.2/ref/settings/#root-urlconf
ROOT_URLCONF = 'config.urls'


# Una lista que contiene la configuración de todos los motores de plantillas que se van a utilizar con 'Django'.
# https://docs.djangoproject.com/en/5.2/ref/settings/#templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# La ruta completa en 'Python' del objeto de la aplicación 'WSGI' que utilizan los servidores integrados de 'Django'.
# https://docs.djangoproject.com/en/5.2/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'


# Un diccionario que contiene la configuración de todas las bases de datos que se van a utilizar con 'Django'.
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# La lista de validadores que se utilizan para comprobar la seguridad de las contraseñas de los usuarios.
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
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


# Un 'str' que representa el código de idioma de esta instalación.
# https://docs.djangoproject.com/en/5.2/ref/settings/#language-code
# Presenta en español los errores y las ayudas integradas del registro.
LANGUAGE_CODE = 'es-cl'

# Un 'str' que representa la zona horaria de esta instalación.
# https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-TIME_ZONE
TIME_ZONE = 'UTC'


# Un 'bool' que especifica si debe activarse el sistema de traducción de 'Django'.
# https://docs.djangoproject.com/en/5.2/ref/settings/#use-i18n
USE_I18N = True


# Un 'bool' que especifica si las fechas y horas tendrán en cuenta la zona horaria de forma predeterminada o no.
# https://docs.djangoproject.com/en/5.2/ref/settings/#use-tz
USE_TZ = True


# Prefijo 'URL' utilizado para acceder a los archivos estáticos.
# https://docs.djangoproject.com/en/5.2/ref/settings/#static-url
#
# Los archivos estaticos corresponden a: Imagenes, 'JavaScript' o 'CSS'.
# https://docs.djangoproject.com/en/5.2/howto/static-files/#how-to-manage-static-files-e-g-images-javascript-css
STATIC_URL = 'static/'


# Tipo de campo de clave primaria predeterminado que se utilizará en los modelos que no tengan un campo con 'primary_key=True'.
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# El modelo que se debe utilizar para representar a un 'User'.
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-user-model
#
# En este caso, establecemos nuestro modelo personalizado, siguiendo la documentacion de 'Django'.
# https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#auth-custom-user
AUTH_USER_MODEL = "cuentas_app.Usuario"


# Rutas de acceso y destinos predeterminados; las vistas nativas validan next.
# https://docs.djangoproject.com/en/5.2/ref/settings/#login-url
LOGIN_URL = "cuentas:iniciar_sesion"
LOGIN_REDIRECT_URL = "cuentas:inicio"
LOGOUT_REDIRECT_URL = "cuentas:iniciar_sesion"

# Mantiene explícitas las protecciones de la cookie de sesión en desarrollo local.
# https://docs.djangoproject.com/en/5.2/ref/settings/#session-cookie-httponly
# https://docs.djangoproject.com/en/5.2/ref/settings/#session-cookie-samesite
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
