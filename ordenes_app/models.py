"""Registro histórico de la operación y ciclo de vida de sus reservas."""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class OrdenCompra(models.Model):
    """Conserva comprador, importe aceptado, vencimiento e identidad idempotente."""

    class Estado(models.TextChoices):
        """Estados implementados; la aprobación de pagos permanece fuera de RF-10."""

        PENDIENTE = "pendiente", "Pendiente de Pago"
        EXPIRADA = "expirada", "Expirada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comprador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    clave_confirmacion = models.UUIDField(unique=True, editable=False)
    creada_en = models.DateTimeField(default=timezone.now, editable=False)
    vence_en = models.DateTimeField()
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.PENDIENTE)
    total = models.DecimalField(max_digits=24, decimal_places=2)

    class Meta:
        """Ordena las consultas y refuerza importe, estado y vencimiento."""

        ordering = ("-creada_en", "-pk")
        constraints = [
            models.CheckConstraint(condition=models.Q(total__gt=0), name="orden_total_positivo"),
            models.CheckConstraint(condition=models.Q(vence_en__gt=models.F("creada_en")), name="orden_vencimiento_posterior"),
            models.CheckConstraint(condition=models.Q(estado__in=["pendiente", "expirada"]), name="orden_estado_valido"),
        ]
        indexes = [models.Index(fields=["estado", "vence_en"], name="ordenes_por_vencer")]

    @property
    def reserva_vigente(self):
        """No considera vigente una orden vencida aunque aún no se ejecute el comando."""
        return self.estado == self.Estado.PENDIENTE and timezone.now() < self.vence_en


class DetalleOrden(models.Model):
    """Congela nombre, vendedor, precio y cantidad, sin depender de ediciones futuras."""

    orden = models.ForeignKey(OrdenCompra, on_delete=models.PROTECT, related_name="detalles")
    publicacion = models.ForeignKey("productos_app.Publicacion", on_delete=models.PROTECT)
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    nombre_producto = models.CharField(max_length=150)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    cantidad = models.PositiveIntegerField()

    class Meta:
        """Evita detalles duplicados e importes o cantidades inválidos."""

        ordering = ("pk",)
        constraints = [
            models.UniqueConstraint(fields=["orden", "publicacion"], name="orden_oferta_unica"),
            models.CheckConstraint(condition=models.Q(cantidad__gte=1, cantidad__lte=2147483647), name="detalle_cantidad_valida"),
            models.CheckConstraint(condition=models.Q(precio_unitario__gt=0), name="detalle_precio_positivo"),
        ]

    @property
    def subtotal(self):
        """Calcula únicamente con los valores históricos de este detalle."""
        return self.precio_unitario * self.cantidad


class ReservaStock(models.Model):
    """Una reserva por detalle; cantidad y vencimiento se obtienen de su orden."""

    class Estado(models.TextChoices):
        """Distingue reservas activas y liberadas por expiración."""

        ACTIVA = "activa", "Activa"
        EXPIRADA = "expirada", "Expirada"

    detalle = models.OneToOneField(DetalleOrden, on_delete=models.PROTECT, related_name="reserva")
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.ACTIVA)

    class Meta:
        """Restringe los estados al ciclo de vida implementado."""

        constraints = [models.CheckConstraint(
            condition=models.Q(estado__in=["activa", "expirada"]), name="reserva_estado_valido",
        )]
