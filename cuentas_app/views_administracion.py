"""Listado privado y operaciones POST de suspensión y reactivación de cuentas."""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import DatabaseError
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST, require_safe

from .administracion import (
    cambiar_estado_cuenta, cuentas_administrables, exigir_administrador,
)

logger = logging.getLogger(__name__)


@never_cache
@login_required
@require_safe
def listado_usuarios(request):
    """Lista cuentas sin cargar contraseñas; pagina todas con un orden estable."""
    pagina = Paginator(cuentas_administrables(administrador=request.user), 20).get_page(
        request.GET.get("page"),
    )
    return render(request, "cuentas_app/administracion_usuarios.html", {"pagina": pagina})


def _cambiar_estado(request, usuario_id, *, activar):
    """Aplica el estado fijado por la ruta, ignorando permisos y propietarios del POST."""
    exigir_administrador(request.user)
    try:
        cambiar_estado_cuenta(
            administrador=request.user, usuario_id=usuario_id, activar=activar,
        )
    except ValidationError as error:
        messages.error(request, " ".join(error.messages))
    except DatabaseError:
        logger.exception("No se pudo completar un cambio administrativo de estado.")
        messages.error(request, "No pudimos guardar el cambio. Actualiza el listado e inténtalo nuevamente.")
    else:
        messages.success(
            request, f"La cuenta seleccionada (ID {usuario_id}) fue "
            + ("reactivada correctamente." if activar else "suspendida correctamente."),
        )
    return redirect("cuentas:administrar_usuarios")


@never_cache
@login_required
@require_POST
def suspender_usuario(request, usuario_id):
    """Suspende únicamente por POST con CSRF; no acepta un estado desde el cliente."""
    return _cambiar_estado(request, usuario_id, activar=False)


@never_cache
@login_required
@require_POST
def reactivar_usuario(request, usuario_id):
    """Reactiva la cuenta seleccionada sin conceder o cambiar permisos."""
    return _cambiar_estado(request, usuario_id, activar=True)
