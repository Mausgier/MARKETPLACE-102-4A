"""Consulta pública mínima y administración autenticada de publicaciones propias."""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_safe

from .forms import EdicionPublicacionForm, PublicacionForm
from .models import Publicacion
from .services import (
    crear_publicacion, editar_publicacion, obtener_publicacion_propia,
    retirar_publicacion,
)

logger = logging.getLogger(__name__)


def publicaciones_disponibles():
    """Obtiene ofertas activas con unidades disponibles y sus relaciones descriptivas."""
    # select_related evita consultas adicionales por cada tarjeta o detalle.
    # https://docs.djangoproject.com/en/5.2/ref/models/querysets/#select-related
    return Publicacion.objects.filter(
        estado=Publicacion.Estado.ACTIVA, stock_disponible__gt=0,
    ).select_related("producto__categoria", "vendedor")


@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def publicar_producto(request):
    """
    Recibe los datos del artículo y utiliza la sesión para establecer su propietario.

    https://docs.djangoproject.com/en/5.2/topics/forms/#the-view
    """
    formulario = PublicacionForm(
        request.POST if request.method == "POST" else None
    )
    if request.method == "POST" and formulario.is_valid():
        try:
            publicacion = crear_publicacion(
                vendedor=request.user, **formulario.cleaned_data
            )
        except ValidationError as error:
            # Solo muestra detalles de campos públicos; oculta identificadores internos.
            if hasattr(error, "message_dict"):
                for campo, errores in error.message_dict.items():
                    if campo in formulario.fields:
                        for mensaje in errores:
                            formulario.add_error(campo, mensaje)
                    else:
                        formulario.add_error(None, "Revisa los datos e inténtalo nuevamente.")
            else:
                formulario.add_error(None, "Revisa los datos e inténtalo nuevamente.")
        except DatabaseError:
            # La transacción ya se revirtió; no se presentan detalles de la base al usuario.
            logger.exception("No se pudo completar la creación de una publicación.")
            formulario.add_error(
                None, "No pudimos guardar la publicación. Inténtalo nuevamente."
            )
        else:
            messages.success(request, "Tu publicación se creó correctamente.")
            return redirect("productos:detalle", pk=publicacion.pk)

    return render(
        request, "productos_app/publicar.html", {"formulario": formulario}
    )


@require_safe
def publicaciones_recientes(request):
    """Muestra hasta veinte ofertas recientes; el catálogo completo queda para RF-06."""
    return render(
        request, "productos_app/recientes.html",
        {"publicaciones": publicaciones_disponibles()[:20]},
    )


@require_safe
def detalle_publicacion(request, pk):
    """Permite consultar públicamente una oferta disponible sin exponer datos privados."""
    publicacion = get_object_or_404(publicaciones_disponibles(), pk=pk)
    return render(
        request, "productos_app/detalle.html", {"publicacion": publicacion}
    )


@never_cache
@login_required
@require_safe
def mis_publicaciones(request):
    """Muestra todas las ofertas propias, incluidas las retiradas y sin existencias."""
    publicaciones = Publicacion.objects.filter(vendedor=request.user).select_related(
        "producto__categoria",
    )
    return render(request, "productos_app/mis_publicaciones.html", {
        "publicaciones": publicaciones,
    })


@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def modificar_publicacion(request, pk):
    """Valida la propiedad en lectura y escritura; nunca recibe un vendedor del cliente."""
    publicacion = obtener_publicacion_propia(vendedor=request.user, pk=pk)
    formulario = EdicionPublicacionForm(
        request.POST if request.method == "POST" else None,
        publicacion=publicacion,
    )
    if request.method == "POST" and formulario.is_valid():
        try:
            editar_publicacion(vendedor=request.user, pk=pk, **formulario.cleaned_data)
        except ValidationError:
            formulario.add_error(
                None, "No se pudo guardar. Revisa los datos y comprueba "
                "que la publicación siga activa.",
            )
        except DatabaseError:
            logger.exception("No se pudo completar la edición de una publicación.")
            formulario.add_error(
                None, "No pudimos guardar los cambios. Inténtalo nuevamente."
            )
        else:
            messages.success(
                request, "Los cambios de tu publicación se guardaron correctamente."
            )
            return redirect("productos:mis_publicaciones")
    return render(request, "productos_app/editar.html", {
        "publicacion": publicacion, "formulario": formulario,
    })


@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def eliminar_publicacion(request, pk):
    """Presenta la confirmación por GET y ejecuta el retiro lógico solo mediante POST."""
    publicacion = obtener_publicacion_propia(vendedor=request.user, pk=pk)
    error = None
    if request.method == "POST":
        try:
            retirar_publicacion(vendedor=request.user, pk=pk)
        except ValidationError as excepcion:
            error = excepcion.messages[0]
        except DatabaseError:
            logger.exception("No se pudo completar el retiro de una publicación.")
            error = "No pudimos retirar la publicación. Inténtalo nuevamente."
        else:
            messages.success(
                request, "Tu publicación fue retirada de los artículos disponibles."
            )
            return redirect("productos:mis_publicaciones")
    return render(request, "productos_app/retirar.html", {
        "publicacion": publicacion, "error": error,
    })
