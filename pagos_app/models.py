"""Intentos y referencias financieras, sin aplicación comercial ni datos de tarjetas."""

import secrets
import uuid

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.db.models.functions import Floor
from django.utils import timezone

from .validaciones import MAXIMO_MONTO_CLP, validar_monto_clp


def generar_referencia_comercial():
    """Genera una referencia corta aleatoria, sin datos personales, única en la base."""
    return secrets.token_hex(13)


class IntentoPago(models.Model):
    """
    Representa un intento vinculado a una orden, no una compra ni un pago aplicado.

    https://docs.djangoproject.com/en/5.2/ref/models/constraints/
    """

    class Estado(models.TextChoices):
        """Conserva los cuatro resultados financieros exigidos por RF-19."""

        PENDIENTE = "pendiente", "Pendiente"
        APROBADO = "aprobado", "Aprobado"
        RECHAZADO = "rechazado", "Rechazado"
        CANCELADO = "cancelado", "Cancelado"

    class Verificacion(models.TextChoices):
        """Distingue falta de respuesta de un resultado confirmado externamente."""

        PENDIENTE = "pendiente", "Sin verificar"
        REQUIERE_CONSULTA = "requiere_consulta", "Requiere consulta externa"
        CONFIRMADA = "confirmada", "Resultado verificado"

    class Ambiente(models.TextChoices):
        """Identifica el contexto de una referencia sin habilitar esos entornos."""

        PRUEBAS = "pruebas", "Pruebas"
        PRODUCCION = "produccion", "Producción"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    orden = models.ForeignKey(
        "ordenes_app.OrdenCompra", on_delete=models.PROTECT, related_name="intentos_pago",
    )
    clave_idempotencia = models.UUIDField(unique=True, editable=False)
    referencia_comercial = models.CharField(
        max_length=26, unique=True, default=generar_referencia_comercial, editable=False,
    )
    # Vacío significa que aún no se eligió proveedor; Flow no se presupone seleccionado.
    proveedor = models.SlugField(max_length=40, blank=True, default="")
    ambiente = models.CharField(max_length=10, choices=Ambiente.choices, default=Ambiente.PRUEBAS)
    # El límite explícito evita depender de precisión decimal superior en SQLite.
    monto = models.DecimalField(max_digits=15, decimal_places=0)
    moneda = models.CharField(max_length=3, default="CLP", editable=False)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PENDIENTE)
    verificacion = models.CharField(
        max_length=20, choices=Verificacion.choices, default=Verificacion.PENDIENTE,
    )
    referencia_externa = models.CharField(max_length=128, null=True, blank=True)
    creado_en = models.DateTimeField(default=timezone.now, editable=False)
    actualizado_en = models.DateTimeField(auto_now=True)
    verificado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        """Refuerza referencias, dominio monetario y coherencia de resultados."""

        ordering = ("-creado_en", "-pk")
        indexes = [models.Index(fields=["estado", "verificacion"], name="pago_por_verificar")]
        constraints = [
            models.UniqueConstraint(
                fields=["proveedor", "ambiente", "referencia_externa"],
                name="pago_referencia_externa_unica",
            ),
            # SQLite aplica este índice parcial. MySQL exige otra garantía antes
            # de habilitarlo: esta restricción condicional no es portable a ese motor.
            models.UniqueConstraint(
                fields=["orden"], condition=models.Q(estado="aprobado"),
                name="pago_un_aprobado_por_orden",
            ),
            models.CheckConstraint(
                condition=models.Q(monto__gt=0, monto__lte=MAXIMO_MONTO_CLP, monto=Floor("monto")),
                name="pago_monto_clp_entero",
            ),
            models.CheckConstraint(condition=models.Q(moneda="CLP"), name="pago_moneda_clp"),
            models.CheckConstraint(
                condition=models.Q(estado__in=["pendiente", "aprobado", "rechazado", "cancelado"]),
                name="pago_estado_valido",
            ),
            models.CheckConstraint(
                condition=models.Q(ambiente__in=["pruebas", "produccion"]), name="pago_ambiente_valido",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(verificacion__in=["pendiente", "requiere_consulta"],
                             verificado_en__isnull=True, estado="pendiente")
                    | (models.Q(verificacion="confirmada", verificado_en__isnull=False,
                                referencia_externa__isnull=False)
                       & ~models.Q(proveedor="") & ~models.Q(referencia_externa=""))
                ), name="pago_resultado_verificable",
            ),
            models.CheckConstraint(
                condition=(models.Q(referencia_externa__isnull=True)
                           | (~models.Q(proveedor="") & ~models.Q(referencia_externa=""))),
                name="pago_referencia_con_proveedor",
            ),
        ]

    def clean_fields(self, exclude=None):
        """Valida antes de la conversión del campo para no aceptar float ni redondeos."""
        if not exclude or "monto" not in exclude:
            try:
                self.monto = validar_monto_clp(self.monto)
            except ValidationError as error:
                raise ValidationError({"monto": error.messages}) from error
        super().clean_fields(exclude=exclude)

    def clean(self):
        """Conserva correspondencia exacta con el total histórico de la orden."""
        super().clean()
        if self.referencia_externa == "":
            self.referencia_externa = None
        try:
            monto = validar_monto_clp(self.monto)
        except ValidationError:
            # clean_fields ya informa el importe inválido. No comparar valores
            # no finitos o mal formados con el total durante la validación conjunta.
            return
        if self.orden_id:
            try:
                total = self.orden.total
            except (ObjectDoesNotExist, ValidationError):
                # clean_fields informa la relación inválida, sin provocar una excepción
                # adicional al intentar consultar una orden que no existe.
                return
            if monto != total:
                raise ValidationError({"monto": "El monto debe coincidir exactamente con el total de la orden."})

    def save(self, *args, **kwargs):
        """
        Evita que el guardado ordinario convierta importes inválidos silenciosamente.

        La validación estructural no acredita una respuesta de pasarela. RF-19.1
        no ofrece ningún servicio para aprobar o aplicar pagos.
        https://docs.djangoproject.com/en/5.2/ref/models/instances/#validating-objects
        """
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Identifica el intento sin divulgar referencias externas o datos sensibles."""
        return f"Intento {self.pk} ({self.get_estado_display()})"
