"""Operaciones transaccionales de alta, edición propia y retiro lógico de ofertas."""

from django.core.exceptions import PermissionDenied, ValidationError
from django.core.validators import MinValueValidator
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404

from .models import Producto, Publicacion


@transaction.atomic
def crear_publicacion(*, vendedor, nombre, descripcion, categoria, precio,
                      stock_disponible):
    """
    Crea producto y publicación como una única operación con datos ya validados.

    https://docs.djangoproject.com/en/5.2/topics/db/transactions/#controlling-transactions-explicitly
    https://docs.djangoproject.com/en/5.2/ref/models/instances/#django.db.models.Model.full_clean
    """
    if not vendedor.is_authenticated or not vendedor.is_active:
        raise PermissionDenied("Debes iniciar sesión con una cuenta activa.")

    # RN-01: cualquier cuenta activa puede vender, sin comprobar su preferencia.
    MinValueValidator(1)(stock_disponible)
    producto = Producto(
        nombre=nombre, descripcion=descripcion, categoria=categoria,
    )
    producto.full_clean()
    producto.save()

    # El propietario y los valores internos se determinan exclusivamente aquí.
    publicacion = Publicacion(
        producto=producto, vendedor=vendedor, precio=precio,
        stock_disponible=stock_disponible, stock_reservado=0,
        estado=Publicacion.Estado.ACTIVA,
    )
    publicacion.full_clean()
    publicacion.save()
    return publicacion


def obtener_publicacion_propia(*, vendedor, pk):
    """Restringe la consulta por propietario, incluso si se conoce un identificador ajeno."""
    if not vendedor.is_authenticated or not vendedor.is_active:
        raise PermissionDenied("Debes iniciar sesión con una cuenta activa.")
    return get_object_or_404(
        Publicacion.objects.select_related("producto__categoria").filter(
            vendedor=vendedor,
        ), pk=pk,
    )


@transaction.atomic
def editar_publicacion(*, vendedor, pk, nombre, descripcion, categoria, precio,
                       stock_disponible):
    """Valida y guarda únicamente campos comerciales permitidos de una oferta propia."""
    publicacion = obtener_publicacion_propia(vendedor=vendedor, pk=pk)
    if publicacion.estado != Publicacion.Estado.ACTIVA:
        raise ValidationError("Una publicación retirada no puede modificarse.")

    producto = publicacion.producto
    cambio_descriptivo = (
        producto.nombre != nombre or producto.descripcion != descripcion
        or producto.categoria_id != categoria.pk
    )
    if cambio_descriptivo:
        # El diseño admite varias publicaciones por producto: no alterar otras ofertas.
        if producto.publicaciones.exclude(pk=pk).exists():
            producto = Producto()
        producto.nombre = nombre
        producto.descripcion = descripcion
        producto.categoria = categoria
        producto.full_clean()
        producto.save()

    publicacion.producto = producto
    publicacion.precio = precio
    publicacion.stock_disponible = stock_disponible
    publicacion.full_clean()
    # La condición se evalúa en la escritura: no reducir el físico bajo reservas
    # creadas simultáneamente ni reactivar una oferta retirada mientras se editaba.
    actualizada = Publicacion.objects.filter(
        pk=pk, vendedor=vendedor, estado=Publicacion.Estado.ACTIVA,
        stock_reservado__lte=stock_disponible,
    ).update(producto=producto, precio=publicacion.precio, stock_disponible=stock_disponible)
    if not actualizada:
        raise ValidationError("No se puede reducir el stock físico bajo las unidades reservadas.")
    return publicacion


@transaction.atomic
def retirar_publicacion(*, vendedor, pk):
    """Retira sin borrar la oferta ni sus relaciones comerciales; repetir es inocuo."""
    publicacion = obtener_publicacion_propia(vendedor=vendedor, pk=pk)
    if publicacion.estado == Publicacion.Estado.RETIRADA:
        return
    # Salvaguarda para futuros procesos: RF-05 no libera ni administra reservas.
    # La condición se comprueba en la escritura, sin sobrescribir otros campos.
    actualizadas = Publicacion.objects.filter(
        pk=pk, vendedor=vendedor, estado=Publicacion.Estado.ACTIVA,
        stock_reservado=0,
    ).update(estado=Publicacion.Estado.RETIRADA)
    if not actualizadas:
        raise ValidationError(
            "No se puede retirar la publicación mientras tenga unidades reservadas "
            "o su estado haya cambiado. Actualiza la página e inténtalo nuevamente."
        )
