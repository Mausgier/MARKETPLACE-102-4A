"""Selecciones persistentes y cálculos actuales; RF-09 nunca reserva stock."""

from decimal import Decimal

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from productos_app.models import Publicacion

from .models import Carrito, ItemCarrito


def validar_cuenta(usuario):
    """Exige cuenta activa, sin restringir la preferencia comercial de RN-01."""
    if not usuario.is_authenticated or not usuario.is_active:
        raise PermissionDenied("Debes iniciar sesión con una cuenta activa.")


def _carrito_para_escritura(usuario, *, crear=False):
    """
    Serializa las operaciones del carrito dentro de la transacción del servicio.

    Una escritura de la cabecera precede a la lectura y modificación de líneas.
    SQLite serializa escritores; MySQL/InnoDB bloquea la fila actualizada.
    No se depende de select_for_update, que no bloquea filas en SQLite.
    Ante contención, la base puede rechazar la operación: la vista pide reintentar.
    https://docs.djangoproject.com/en/5.2/ref/models/querysets/#select-for-update
    https://docs.djangoproject.com/en/5.2/topics/db/transactions/
    """
    validar_cuenta(usuario)
    if crear:
        carrito, _ = Carrito.objects.get_or_create(usuario=usuario)
    else:
        carrito = get_object_or_404(Carrito, usuario=usuario)
    Carrito.objects.filter(pk=carrito.pk, usuario=usuario).update(
        actualizado_en=timezone.now(),
    )
    return carrito


def _validar_cantidad(publicacion, cantidad):
    """Revalida disponibilidad y cantidad sin descontar ni reservar unidades."""
    if type(cantidad) is not int or not 1 <= cantidad <= 2147483647:
        raise ValidationError("La cantidad debe ser un entero positivo válido.")
    if publicacion.estado != Publicacion.Estado.ACTIVA:
        raise ValidationError("La publicación fue retirada y no puede añadirse o actualizarse.")
    if publicacion.stock_disponible == 0:
        raise ValidationError("El artículo no tiene existencias disponibles.")
    if cantidad > publicacion.stock_disponible:
        raise ValidationError(
            f"La cantidad total seleccionada supera las {publicacion.stock_disponible} "
            "unidades disponibles. Reduce la cantidad."
        )


@transaction.atomic
def agregar_articulo(*, usuario, publicacion_id, cantidad):
    """Suma unidades en una única línea propia, leyendo el stock vigente."""
    carrito = _carrito_para_escritura(usuario, crear=True)
    publicacion = get_object_or_404(Publicacion, pk=publicacion_id)
    item = ItemCarrito.objects.filter(
        carrito=carrito, publicacion=publicacion,
    ).first()
    # Validar también el incremento impide usar negativos para reducir una línea.
    _validar_cantidad(publicacion, cantidad)
    cantidad_total = cantidad + (item.cantidad if item else 0)
    _validar_cantidad(publicacion, cantidad_total)
    if item is None:
        item = ItemCarrito(carrito=carrito, publicacion=publicacion)
    item.cantidad = cantidad_total
    item.full_clean()
    item.save()


@transaction.atomic
def actualizar_articulo(*, usuario, item_id, cantidad):
    """Sustituye la cantidad solo de una línea perteneciente a la cuenta activa."""
    carrito = _carrito_para_escritura(usuario)
    item = get_object_or_404(
        ItemCarrito.objects.select_related("publicacion"),
        pk=item_id, carrito=carrito,
    )
    _validar_cantidad(item.publicacion, cantidad)
    item.cantidad = cantidad
    item.full_clean()
    item.save(update_fields=["cantidad"])


@transaction.atomic
def eliminar_articulo(*, usuario, item_id):
    """Elimina únicamente una selección propia, conservando producto y publicación."""
    carrito = _carrito_para_escritura(usuario)
    item = get_object_or_404(ItemCarrito, pk=item_id, carrito=carrito)
    item.delete()


def consultar_carrito(*, usuario):
    """Calcula el resumen actual sin crear carritos en GET ni almacenar importes."""
    validar_cuenta(usuario)
    items = list(ItemCarrito.objects.filter(
        carrito__usuario=usuario,
    ).select_related("publicacion__producto"))
    return {
        "items": items,
        "total": sum((item.subtotal for item in items), Decimal("0.00")),
        "hay_incidencias": any(item.problema_disponibilidad for item in items),
    }
