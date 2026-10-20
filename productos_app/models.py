"""Entidades del catálogo propuestas en la Sumativa N.° 2."""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Categoria(models.Model):
    """Normaliza las categorías seleccionables para evitar valores libres inválidos."""

    nombre = models.CharField("Nombre", max_length=80, unique=True)

    class Meta:
        """Presenta las categorías en orden alfabético."""

        ordering = ("nombre",)
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        """Devuelve la etiqueta utilizada por el selector de categorías."""
        return self.nombre


class Producto(models.Model):
    """Describe el artículo, separando sus características de la oferta comercial."""

    nombre = models.CharField("Nombre", max_length=150)
    descripcion = models.TextField("Descripción", max_length=5000)
    # PROTECT impide eliminar una categoría que todavía describe productos.
    # https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.PROTECT
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="productos",
        verbose_name="Categoría",
    )

    class Meta:
        """Ordena los datos descriptivos del catálogo."""

        ordering = ("nombre", "pk")

    def __str__(self):
        """Identifica el producto mediante su nombre descriptivo."""
        return self.nombre


class Publicacion(models.Model):
    """
    Representa la oferta de un producto por un único vendedor, conforme a RN-03.

    https://docs.djangoproject.com/en/5.2/ref/models/fields/#decimalfield
    https://docs.djangoproject.com/en/5.2/ref/models/constraints/#checkconstraint
    """

    class Estado(models.TextChoices):
        """Distingue ofertas activas y retiradas para su futura gestión."""

        ACTIVA = "activa", "Activa"
        RETIRADA = "retirada", "Retirada"

    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, related_name="publicaciones",
    )
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="publicaciones",
    )
    # El importe utiliza decimales exactos, sin convertirlo a punto flotante.
    precio = models.DecimalField(
        "Precio", max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    # El modelo admite cero para el agotamiento futuro; el alta exige al menos uno.
    stock_disponible = models.PositiveIntegerField(
        "Unidades disponibles", validators=[MaxValueValidator(2147483647)],
    )
    # Preparación estructural del UML: RF-04 no crea ni vence reservas temporales.
    stock_reservado = models.PositiveIntegerField(default=0, editable=False)
    estado = models.CharField(
        max_length=10, choices=Estado.choices, default=Estado.ACTIVA,
        editable=False,
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Refuerza los límites de negocio también en la base de datos."""

        ordering = ("-fecha_creacion", "-pk")
        verbose_name = "Publicación"
        verbose_name_plural = "Publicaciones"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(precio__gt=0),
                name="publicacion_precio_positivo",
            ),
            models.CheckConstraint(
                condition=models.Q(stock_disponible__gte=0),
                name="publicacion_stock_disponible_no_negativo",
            ),
            models.CheckConstraint(
                condition=models.Q(stock_reservado__gte=0),
                name="publicacion_stock_reservado_no_negativo",
            ),
            models.CheckConstraint(
                condition=models.Q(estado__in=["activa", "retirada"]),
                name="publicacion_estado_valido",
            ),
        ]

    def __str__(self):
        """Identifica la oferta sin revelar datos privados del vendedor."""
        return f"{self.producto.nombre} (publicación {self.pk})"
