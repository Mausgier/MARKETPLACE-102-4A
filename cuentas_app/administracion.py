"""Autorización administrativa y cambios acotados de estado, sin efectos comerciales."""

from django.contrib.auth import SESSION_KEY
from django.contrib.sessions.models import Session
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Usuario


def exigir_administrador(usuario):
    """
    Exige privilegios efectivos; la preferencia comercial no concede autorización.

    https://docs.djangoproject.com/en/5.2/topics/auth/default/#permissions-and-authorization
    """
    if not (
        usuario.is_authenticated and usuario.is_active and usuario.is_staff
        and usuario.has_perm("cuentas_app.change_usuario")
    ):
        raise PermissionDenied("No tienes autorización para administrar cuentas.")


def cuentas_administrables(*, administrador):
    """Consulta solo los campos de identificación y estado necesarios para el listado."""
    exigir_administrador(administrador)
    return Usuario.objects.only(
        "pk", "first_name", "last_name", "email", "is_active", "is_staff", "is_superuser",
    ).order_by("email", "pk")


def _invalidar_sesiones(usuario_id):
    """
    Elimina únicamente las sesiones vigentes de la cuenta suspendida.

    El proyecto usa sesiones en base de datos. Así la reactivación posterior no
    reutiliza sus cookies anteriores. No se modifican contraseñas ni sus hashes.
    Un cambio futuro a otro motor de sesiones requiere adaptar esta revocación.
    https://docs.djangoproject.com/en/5.2/topics/http/sessions/#using-sessions-out-of-views
    """
    claves = []
    for sesion in Session.objects.filter(expire_date__gt=timezone.now()).iterator():
        if str(sesion.get_decoded().get(SESSION_KEY)) == str(usuario_id):
            claves.append(sesion.session_key)
    if claves:
        Session.objects.filter(session_key__in=claves).delete()


@transaction.atomic
def cambiar_estado_cuenta(*, administrador, usuario_id, activar):
    """Cambia exclusivamente is_active tras comprobar permisos y proteger administradores."""
    # Releer impide reutilizar permisos o flags cacheados de una instancia antigua.
    if not administrador.is_authenticated:
        raise PermissionDenied("Debes iniciar sesión.")
    actor = get_object_or_404(Usuario, pk=administrador.pk)
    exigir_administrador(actor)
    cuenta = get_object_or_404(Usuario, pk=usuario_id)
    if not activar:
        if cuenta.pk == actor.pk:
            raise ValidationError("No puedes suspender tu propia cuenta.")
        if cuenta.is_staff or cuenta.is_superuser:
            raise ValidationError("Las cuentas administrativas están protegidas contra suspensión desde esta función.")
        # La condición protege también una cuenta promovida entre lectura y escritura.
        cambiadas = Usuario.objects.filter(
            pk=cuenta.pk, is_staff=False, is_superuser=False,
        ).update(is_active=False)
        if not cambiadas:
            raise ValidationError("La cuenta cambió de privilegios. Actualiza el listado.")
        _invalidar_sesiones(cuenta.pk)
    else:
        Usuario.objects.filter(pk=cuenta.pk).update(is_active=True)
    # Ningún precio, permiso, contraseña, publicación, orden o reserva se sobrescribe.
