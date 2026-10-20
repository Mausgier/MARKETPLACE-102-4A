"""Supervisión privada y retiro POST de publicaciones sin modificar rutas de vendedores."""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import DatabaseError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST, require_safe

from .administracion import (
    exigir_administrador_publicaciones, publicaciones_administrables,
    retirar_publicacion_administrativamente,
)

logger = logging.getLogger(__name__)


@never_cache
@login_required
@require_safe
def listado_publicaciones(request):
    """Pagina todas las publicaciones, incluidas las retiradas o sin unidades libres."""
    pagina = Paginator(publicaciones_administrables(administrador=request.user), 20).get_page(
        request.GET.get("page"),
    )
    return render(request, "productos_app/administracion_lista.html", {"pagina": pagina})


@never_cache
@login_required
@require_safe
def detalle_administrativo(request, pk):
    """Consulta una publicación sin depender de su disponibilidad en el catálogo."""
    publicacion = get_object_or_404(
        publicaciones_administrables(administrador=request.user), pk=pk,
    )
    return render(request, "productos_app/administracion_detalle.html", {
        "publicacion": publicacion,
    })


@never_cache
@login_required
@require_POST
def retirar_administrativamente(request, pk):
    """Retira con CSRF, mensajes comprensibles y redirección fija tras el POST."""
    exigir_administrador_publicaciones(request.user)
    try:
        retirar_publicacion_administrativamente(administrador=request.user, pk=pk)
    except ValidationError as error:
        messages.error(request, " ".join(error.messages))
    except DatabaseError:
        logger.exception("No se pudo completar el retiro administrativo de una publicación.")
        messages.error(request, "No pudimos retirar la publicación. Actualiza la página e inténtalo nuevamente.")
    else:
        messages.success(request, "La publicación seleccionada quedó retirada del catálogo.")
    return redirect("productos:detalle_administrativo", pk=pk)
