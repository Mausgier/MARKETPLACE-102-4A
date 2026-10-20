"""Registro técnico interno de intentos pendientes; no inicia ni aprueba pagos."""

from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from carrito_app.services import validar_cuenta
from ordenes_app.models import OrdenCompra

from .models import IntentoPago
from .validaciones import validar_monto_clp


@transaction.atomic
def registrar_intento_pendiente(*, usuario, orden_id, clave_idempotencia,
                               proveedor="", ambiente=IntentoPago.Ambiente.PRUEBAS):
    """
    Registra metadatos desde una orden propia sin escribir en ella ni en reservas.

    Reutiliza la clave de una misma solicitud; claves diferentes representan intentos
    distintos. Esta clave deberá generarse del lado del servidor al integrar la UI.
    https://docs.djangoproject.com/en/5.2/ref/models/querysets/#get-or-create
    """
    validar_cuenta(usuario)
    try:
        clave = UUID(str(clave_idempotencia))
    except (ValueError, TypeError, AttributeError) as error:
        raise ValidationError("La clave de idempotencia no es válida.") from error
    orden = get_object_or_404(OrdenCompra, pk=orden_id, comprador=usuario)
    monto = validar_monto_clp(orden.total)
    existente = IntentoPago.objects.filter(clave_idempotencia=clave).first()
    if existente:
        _comprobar_reutilizacion(existente, orden, monto, proveedor, ambiente)
        return existente
    if orden.estado != OrdenCompra.Estado.PENDIENTE or timezone.now() >= orden.vence_en:
        raise ValidationError("La orden debe estar pendiente y dentro de su plazo de reserva.")
    intento, _ = IntentoPago.objects.get_or_create(
        clave_idempotencia=clave,
        defaults={"orden": orden, "monto": monto, "proveedor": proveedor, "ambiente": ambiente},
    )
    _comprobar_reutilizacion(intento, orden, monto, proveedor, ambiente)
    return intento


def _comprobar_reutilizacion(intento, orden, monto, proveedor, ambiente):
    """No permite reutilizar una clave para otra operación o configuración."""
    if (intento.orden_id != orden.pk or intento.monto != monto
            or intento.proveedor != proveedor or intento.ambiente != ambiente):
        raise ValidationError("La clave de idempotencia ya corresponde a otra solicitud.")
