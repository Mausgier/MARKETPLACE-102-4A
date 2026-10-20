"""Configuración del módulo de órdenes."""

from django.apps import AppConfig


class OrdenesAppConfig(AppConfig):
    """Registra las entidades y comandos de RF-10."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "ordenes_app"
