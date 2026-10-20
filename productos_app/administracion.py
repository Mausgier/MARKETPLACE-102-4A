"""Autorización administrativa y supervisión de publicaciones de todos los vendedores."""

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import Publicacion
from .services import _retirar_sin_reservas


def exigir_administrador_publicaciones(usuario):
    """
    Exige privilegios sobre publicaciones, independientes de los permisos de cuentas.

    https://docs.djangoproject.com/en/5.2/topics/auth/default/#permissions-and-authorization
    """
    if not (
        usuario.is_authenticated and usuario.is_active and usuario.is_staff
        and usuario.has_perm("productos_app.change_publicacion")
    ):
        raise PermissionDenied("No tienes autorización para administrar publicaciones.")


def publicaciones_administrables(*, administrador):
    """Incluye todos los estados con relaciones necesarias, sin cargar hashes del vendedor."""
    exigir_administrador_publicaciones(administrador)
    return Publicacion.objects.select_related("producto__categoria", "vendedor").only(
        "pk", "producto__nombre", "producto__descripcion", "producto__categoria__nombre",
        "vendedor__id", "vendedor__first_name", "vendedor__last_name", "vendedor__email",
        "precio", "stock_disponible", "stock_reservado", "estado", "fecha_creacion",
    ).order_by("-fecha_creacion", "-pk")


@transaction.atomic
def retirar_publicacion_administrativamente(*, administrador, pk):
    """Revalida privilegios y retira solo la oferta seleccionada, sin alterar inventario."""
    if not administrador.is_authenticated:
        raise PermissionDenied("Debes iniciar sesión.")
    # Nueva instancia para no reutilizar permisos cacheados o atributos antiguos.
    actor = get_object_or_404(get_user_model(), pk=administrador.pk)
    publicacion = get_object_or_404(publicaciones_administrables(administrador=actor), pk=pk)
    _retirar_sin_reservas(publicacion)
