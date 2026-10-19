from django.apps import AppConfig


class CuentasAppConfig(AppConfig):
    """
    Define la configuración de la aplicación encargada de gestionar las cuentas de los usuarios.
    https://docs.djangoproject.com/en/5.2/ref/applications/#django.apps.AppConfig
    """

    # Este atributo define a qué aplicación se aplica la configuración.
    # https://docs.djangoproject.com/en/5.2/ref/applications/#django.apps.AppConfig.name
    name = "cuentas_app"

    # Nombre legible para el usuario de la aplicación.
    # https://docs.djangoproject.com/en/5.2/ref/applications/#django.apps.AppConfig.verbose_name
    verbose_name = "Cuentas"

    # El tipo de clave primaria implícita que se debe añadir a los modelos de esta aplicación.
    # https://docs.djangoproject.com/en/5.2/ref/applications/#django.apps.AppConfig.default_auto_field
    default_auto_field = "django.db.models.BigAutoField"
