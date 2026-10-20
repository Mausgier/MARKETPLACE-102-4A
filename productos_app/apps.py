"""Configuración del módulo de productos y publicaciones."""

from django.apps import AppConfig


class ProductosAppConfig(AppConfig):
    """Agrupa productos, categorías y publicaciones sin acoplarlos a las cuentas."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "productos_app"
    verbose_name = "Productos y publicaciones"
