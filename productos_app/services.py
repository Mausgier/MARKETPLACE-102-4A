"""Operaciones de negocio para crear ofertas sin registros parciales."""

from django.core.exceptions import PermissionDenied
from django.core.validators import MinValueValidator
from django.db import transaction

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
