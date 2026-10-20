"""Carrito actual por cuenta y cantidades seleccionadas, sin importes históricos."""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from productos_app.models import Publicacion


class Carrito(models.Model):
    """Mantiene un único carrito actual por cuenta, independiente de la sesión."""

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="carrito",
    )
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Identifica el carrito sin divulgar datos personales."""
        return f"Carrito {self.pk}"


class ItemCarrito(models.Model):
    """
    Vincula una publicación al carrito; no guarda precio ni total redundantes.

    https://docs.djangoproject.com/en/5.2/ref/models/constraints/
    """

    carrito = models.ForeignKey(
        Carrito, on_delete=models.CASCADE, related_name="items",
    )
    # Retirar una oferta no debe borrar silenciosamente las selecciones existentes.
    publicacion = models.ForeignKey(
        Publicacion, on_delete=models.PROTECT, related_name="items_carrito",
    )
    cantidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(2147483647)],
    )

    class Meta:
        """Impide líneas duplicadas y cantidades fuera del intervalo permitido."""

        ordering = ("pk",)
        constraints = [
            models.UniqueConstraint(
                fields=["carrito", "publicacion"], name="item_carrito_oferta_unica",
            ),
            models.CheckConstraint(
                condition=models.Q(cantidad__gte=1, cantidad__lte=2147483647),
                name="item_carrito_cantidad_valida",
            ),
        ]

    @property
    def subtotal(self):
        """Calcula con Decimal el importe seleccionado al precio comercial actual."""
        return self.publicacion.precio * self.cantidad

    @property
    def problema_disponibilidad(self):
        """Evalúa la oferta actual sin cambiar la selección ni reservar existencias."""
        if self.publicacion.estado != Publicacion.Estado.ACTIVA:
            return "Publicación retirada. Elimina esta línea del carrito."
        if self.publicacion.unidades_libres == 0:
            return "Artículo sin existencias. Elimina la línea o espera su reposición."
        if self.cantidad > self.publicacion.unidades_libres:
            return (
                f"Solo hay {self.publicacion.unidades_libres} unidades disponibles. "
                "Reduce la cantidad o elimina la línea."
            )
        return ""

    def __str__(self):
        """Identifica una selección sin exponer al propietario."""
        return f"Línea {self.pk} del carrito {self.carrito_id}"
