"""Resumen previo y consultas privadas de las órdenes de la cuenta autenticada."""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_safe

from carrito_app.services import validar_cuenta

from .forms import ConfirmarOrdenForm
from .consultas import compras_aprobadas_del_usuario
from .models import OrdenCompra
from .services import expirar_ordenes, generar_orden, preparar_confirmacion

logger = logging.getLogger(__name__)


@never_cache
@login_required
@require_safe
def historial_compras(request):
    """
    Presenta RF-11 parcial sin convertir órdenes pendientes o vencidas en compras.

    No ejecuta mantenimiento de reservas ni acepta propietarios desde la URL.
    https://docs.djangoproject.com/en/5.2/topics/auth/default/#the-login-required-decorator
    """
    return render(request, "ordenes_app/historial.html", {
        "compras": compras_aprobadas_del_usuario(usuario=request.user),
    })


@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def confirmar(request):
    """GET presenta el resumen; solo POST con CSRF genera la orden completa."""
    validar_cuenta(request.user)
    try:
        if request.method == "POST":
            formulario = ConfirmarOrdenForm(request.POST)
            if not formulario.is_valid():
                raise ValidationError("La confirmación no es válida. Revisa el resumen.")
            orden = generar_orden(usuario=request.user, **formulario.cleaned_data)
            messages.success(request, "La orden fue registrada. Consulta su estado y vencimiento.")
            return redirect("ordenes:detalle", pk=orden.pk)
        resumen = preparar_confirmacion(usuario=request.user)
    except ValidationError as error:
        messages.error(request, " ".join(error.messages))
    except DatabaseError:
        logger.exception("No se pudo completar la confirmación de una orden.")
        messages.error(request, "No pudimos completar la operación. Revisa tus órdenes antes de reintentar la misma confirmación.")
    else:
        return render(request, "ordenes_app/confirmar.html", {
            **resumen, "formulario": ConfirmarOrdenForm(initial={"token": resumen["token"]}),
        })
    return redirect("carrito:ver")


def _actualizar_vencidas(request):
    """Intenta liberar vencimientos al consultar, sin exponer errores de almacenamiento."""
    try:
        expirar_ordenes()
    except (DatabaseError, ValidationError):
        logger.exception("No se pudieron actualizar los vencimientos.")
        messages.error(request, "No se pudieron actualizar los vencimientos. Una reserva vencida no es válida aunque aún figure pendiente.")


@never_cache
@login_required
@require_safe
def mis_ordenes(request):
    """Lista exclusivamente las órdenes propias; la expiración es mantenimiento explícito."""
    validar_cuenta(request.user)
    if request.method == "GET":
        _actualizar_vencidas(request)
    return render(request, "ordenes_app/lista.html", {
        "ordenes": OrdenCompra.objects.filter(comprador=request.user),
    })


@never_cache
@login_required
@require_safe
def detalle(request, pk):
    """La consulta por identificador siempre queda restringida al comprador actual."""
    validar_cuenta(request.user)
    orden = get_object_or_404(OrdenCompra, pk=pk, comprador=request.user)
    if request.method == "GET":
        _actualizar_vencidas(request)
        orden.refresh_from_db()
    return render(request, "ordenes_app/detalle.html", {
        "orden": orden, "detalles": orden.detalles.select_related("vendedor"),
    })
