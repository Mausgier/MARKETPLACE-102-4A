"""Configuración del módulo de carrito de compras."""

from django.apps import AppConfig


class CarritoAppConfig(AppConfig):
    """Registra el módulo funcional sin efectos secundarios al iniciar Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "carrito_app"
    verbose_name = "Carrito de compras"
