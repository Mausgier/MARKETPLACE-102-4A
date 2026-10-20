"""Configuración del módulo independiente de proveedores de pago."""

from django.apps import AppConfig


class PagosAppConfig(AppConfig):
    """Registra la base de intentos sin iniciar comunicaciones externas."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "pagos_app"
    verbose_name = "Intentos de pago"
