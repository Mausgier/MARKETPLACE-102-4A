"""Confirmación completa, reserva condicional y expiración idempotente de órdenes."""

import hashlib
import json
from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

from django.core import signing
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from carrito_app.models import ItemCarrito
from carrito_app.services import obtener_carrito_para_escritura, validar_cuenta
from productos_app.models import Publicacion

from .models import DetalleOrden, OrdenCompra, ReservaStock

SALT_CONFIRMACION = "ordenes.confirmar.v1"


def _items(usuario):
    """Carga una instantánea ordenada; las reservas se adquieren en este mismo orden."""
    return list(ItemCarrito.objects.filter(carrito__usuario=usuario).select_related(
        "publicacion__producto",
    ).order_by("publicacion_id"))


def _huella(items):
    """Detecta cambios de selección, nombre, vendedor o precio desde la vista previa."""
    datos = [(i.pk, i.publicacion_id, i.publicacion.vendedor_id,
              i.publicacion.producto.nombre, str(i.publicacion.precio), i.cantidad)
             for i in items]
    return hashlib.sha256(json.dumps(datos, ensure_ascii=False).encode()).hexdigest()


def _validar_items(items):
    """Rechaza el conjunto completo si una sola línea no puede reservarse."""
    if not items:
        raise ValidationError("El carrito está vacío.")
    for item in items:
        if type(item.cantidad) is not int or item.cantidad < 1:
            raise ValidationError("El carrito contiene una cantidad inválida.")
        if item.problema_disponibilidad:
            raise ValidationError("El carrito requiere ajustes: " + item.problema_disponibilidad)


def preparar_confirmacion(*, usuario):
    """Firma el resumen aceptable; no crea órdenes ni reservas al mostrarlo."""
    validar_cuenta(usuario)
    expirar_ordenes()
    items = _items(usuario)
    _validar_items(items)
    token = signing.dumps({
        "usuario": usuario.pk, "clave": str(uuid4()), "huella": _huella(items),
    }, salt=SALT_CONFIRMACION)
    return {"items": items, "total": sum((i.subtotal for i in items), Decimal("0.00")),
            "token": token}


def generar_orden(*, usuario, token):
    """Valida la firma y libera vencidas antes de iniciar la transacción de creación."""
    validar_cuenta(usuario)
    try:
        datos = signing.loads(token, salt=SALT_CONFIRMACION, max_age=900)
    except signing.BadSignature as error:
        raise ValidationError("La confirmación no es válida o venció. Revisa nuevamente el resumen.") from error
    if datos["usuario"] != usuario.pk:
        raise ValidationError("La confirmación no corresponde a esta cuenta.")
    expirar_ordenes()
    return _generar_atomicamente(usuario, datos)


@transaction.atomic
def _generar_atomicamente(usuario, datos):
    """
    Reserva todas las líneas o ninguna; vacía el carrito únicamente tras el éxito.

    La cabecera del carrito serializa sus confirmaciones. Las actualizaciones
    condicionales de cada oferta evitan sobreventa también sin bloqueo de filas
    en SQLite. Un error de contención revierte todo y permite reintentar la clave.
    https://docs.djangoproject.com/en/5.2/ref/models/expressions/#avoiding-race-conditions-using-f
    https://docs.djangoproject.com/en/5.2/topics/db/transactions/
    """
    carrito = obtener_carrito_para_escritura(usuario)
    existente = OrdenCompra.objects.filter(
        clave_confirmacion=datos["clave"], comprador=usuario,
    ).first()
    if existente:
        return existente
    items = _items(usuario)
    _validar_items(items)
    if _huella(items) != datos["huella"]:
        raise ValidationError("El carrito o sus precios cambiaron. Revisa nuevamente el resumen.")
    ahora = timezone.now()
    orden = OrdenCompra(
        comprador=usuario, clave_confirmacion=datos["clave"], creada_en=ahora,
        vence_en=ahora + timedelta(minutes=15),
        total=sum((i.subtotal for i in items), Decimal("0.00")),
    )
    orden.full_clean()
    orden.save()
    for item in items:
        oferta = item.publicacion
        reservada = Publicacion.objects.filter(
            pk=oferta.pk, estado=Publicacion.Estado.ACTIVA,
            precio=oferta.precio, producto_id=oferta.producto_id,
            stock_disponible__gte=F("stock_reservado") + item.cantidad,
        ).update(stock_reservado=F("stock_reservado") + item.cantidad)
        if not reservada:
            raise ValidationError("Cambió la disponibilidad o el precio. No se generó la orden; revisa el carrito.")
        detalle = DetalleOrden.objects.create(
            orden=orden, publicacion=oferta, vendedor_id=oferta.vendedor_id,
            nombre_producto=oferta.producto.nombre,
            precio_unitario=oferta.precio, cantidad=item.cantidad,
        )
        ReservaStock.objects.create(detalle=detalle)
    if timezone.now() >= orden.vence_en:
        raise ValidationError("La operación tardó demasiado. No se generó la orden; revisa el carrito.")
    ItemCarrito.objects.filter(carrito=carrito).delete()
    return orden


@transaction.atomic
def _expirar_una(pk, ahora):
    """La transición condicional adquiere el derecho exclusivo a liberar una orden."""
    cambiada = OrdenCompra.objects.filter(
        pk=pk, estado=OrdenCompra.Estado.PENDIENTE, vence_en__lte=ahora,
    ).update(estado=OrdenCompra.Estado.EXPIRADA)
    if not cambiada:
        return 0
    reservas = ReservaStock.objects.filter(
        detalle__orden_id=pk, estado=ReservaStock.Estado.ACTIVA,
    ).select_related("detalle").order_by("detalle__publicacion_id")
    for reserva in reservas:
        detalle = reserva.detalle
        liberada = Publicacion.objects.filter(
            pk=detalle.publicacion_id, stock_reservado__gte=detalle.cantidad,
        ).update(stock_reservado=F("stock_reservado") - detalle.cantidad)
        if not liberada:
            raise ValidationError("No se pudo liberar una reserva por inconsistencia de inventario.")
        reserva.estado = ReservaStock.Estado.EXPIRADA
        reserva.save(update_fields=["estado"])
    return 1


def expirar_ordenes():
    """Expira vencidas por orden, de forma repetible; no simula un programador automático."""
    ahora = timezone.now()
    ids = list(OrdenCompra.objects.filter(
        estado=OrdenCompra.Estado.PENDIENTE, vence_en__lte=ahora,
    ).order_by("pk").values_list("pk", flat=True))
    return sum(_expirar_una(pk, ahora) for pk in ids)
