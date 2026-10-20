"""Catálogo público paginado y administración autenticada de publicaciones propias."""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import DatabaseError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_safe

from .forms import BusquedaProductosForm, EdicionPublicacionForm, PublicacionForm
from .models import Publicacion
from .services import (
    crear_publicacion, editar_publicacion, obtener_publicacion_propia,
    retirar_publicacion,
)

logger = logging.getLogger(__name__)


def publicaciones_disponibles():
    """Comparte entre catálogo y detalle la condición de disponibilidad pública."""
    # Las retiradas y las activas sin existencias quedan fuera de ambas consultas.
    # select_related evita consultas adicionales por cada tarjeta o detalle.
    # https://docs.djangoproject.com/en/5.2/ref/models/querysets/#select-related
    return Publicacion.objects.filter(
        estado=Publicacion.Estado.ACTIVA, stock_disponible__gt=0,
    ).select_related("producto__categoria", "vendedor").order_by(
        "-fecha_creacion", "-pk",
    )


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
    """
    Busca y pagina las ofertas disponibles sin exigir una sesión autenticada.

    Conserva el nombre previo para mantener compatibles las rutas de RF-04 y RF-05.
    https://docs.djangoproject.com/en/5.2/topics/pagination/#using-paginator-in-a-view-function
    https://docs.djangoproject.com/en/5.2/ref/paginator/#django.core.paginator.Paginator.get_page
    https://docs.djangoproject.com/en/5.2/topics/db/queries/#complex-lookups-with-q-objects
    """
    formulario_busqueda = BusquedaProductosForm(request.GET)
    publicaciones = publicaciones_disponibles()
    termino = ""
    if formulario_busqueda.is_valid():
        termino = formulario_busqueda.cleaned_data["q"]
        if termino:
            # Se busca la frase completa en cualquiera de los dos campos mediante
            # parámetros del ORM. No se interpreta SQL ni se separan palabras.
            # icontains conserva la semántica de mayúsculas de la base utilizada;
            # SQLite tiene limitaciones para caracteres no ASCII.
            publicaciones = publicaciones.filter(
                Q(producto__nombre__icontains=termino)
                | Q(producto__descripcion__icontains=termino)
            )
    else:
        # No ejecutar una búsqueda inválida ni presentarla como catálogo general.
        publicaciones = publicaciones.none()
    # El desempate por pk da un orden definido incluso con fechas coincidentes.
    # La búsqueda se aplica antes de paginar: el conteo incluye solo coincidencias.
    paginador = Paginator(publicaciones, 12)
    # get_page resuelve texto o ausencia como primera página, y fuera de rango
    # como última página; también admite un catálogo vacío sin lanzar una excepción.
    pagina = paginador.get_page(request.GET.get("page"))
    return render(
        request, "productos_app/recientes.html",
        {
            "publicaciones": pagina, "pagina": pagina,
            "formulario_busqueda": formulario_busqueda, "termino": termino,
        },
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
