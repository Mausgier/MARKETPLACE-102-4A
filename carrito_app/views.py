"""Vistas privadas del carrito con cambios POST y redirecciones fijas."""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST, require_safe

from .forms import CantidadCarritoForm
from .services import (
    actualizar_articulo, agregar_articulo, consultar_carrito, eliminar_articulo,
    validar_cuenta,
)

logger = logging.getLogger(__name__)


@never_cache
@login_required
@require_safe
def ver_carrito(request):
    """Muestra exclusivamente las selecciones de la cuenta de la sesión."""
    resumen = consultar_carrito(usuario=request.user)
    lineas = [{
        "item": item,
        "formulario": CantidadCarritoForm(
            initial={"cantidad": item.cantidad},
            auto_id=f"linea_{item.pk}_%s",
        ),
    } for item in resumen.pop("items")]
    return render(request, "carrito_app/carrito.html", {
        **resumen, "lineas": lineas,
    })


def _procesar_cambio(request, operacion, *, mensaje, **identificadores):
    """Valida cantidades y comunica errores seguros utilizando POST/Redirect/GET."""
    validar_cuenta(request.user)
    if operacion != eliminar_articulo:
        formulario = CantidadCarritoForm(request.POST)
        if not formulario.is_valid():
            messages.error(request, " ".join(formulario.errors["cantidad"]))
            return redirect("carrito:ver")
        identificadores["cantidad"] = formulario.cleaned_data["cantidad"]
    try:
        operacion(usuario=request.user, **identificadores)
    except ValidationError as error:
        messages.error(request, " ".join(error.messages))
    except DatabaseError:
        # La transacción terminó antes de informar el error; no divulgar SQL o datos.
        logger.exception("No se pudo guardar una operación del carrito.")
        messages.error(
            request, "No pudimos guardar el cambio. Actualiza el carrito "
            "e inténtalo nuevamente.",
        )
    else:
        messages.success(request, mensaje)
    return redirect("carrito:ver")


@never_cache
@login_required
@require_POST
def agregar(request, publicacion_id):
    """Añade unidades de la publicación indicada a la cuenta autenticada."""
    return _procesar_cambio(
        request, agregar_articulo, publicacion_id=publicacion_id,
        mensaje="Artículo añadido al carrito. Si ya existía, se sumaron las unidades.",
    )


@never_cache
@login_required
@require_POST
def actualizar(request, item_id):
    """Actualiza una línea propia tras volver a comprobar sus existencias."""
    return _procesar_cambio(
        request, actualizar_articulo, item_id=item_id,
        mensaje="Cantidad actualizada correctamente.",
    )


@never_cache
@login_required
@require_POST
def eliminar(request, item_id):
    """Retira una línea propia; GET nunca elimina selecciones."""
    return _procesar_cambio(
        request, eliminar_articulo, item_id=item_id,
        mensaje="Artículo eliminado del carrito.",
    )
