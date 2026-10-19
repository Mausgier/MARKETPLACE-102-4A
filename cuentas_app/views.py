"""Vistas públicas de registro de cuentas del marketplace."""

from django.contrib import messages
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods

from .forms import RegistroUsuarioForm
from .models import Usuario


@sensitive_post_parameters("password1", "password2")
@require_http_methods(["GET", "POST"])
def registro_usuario(request):
    """
    Presenta el registro y crea una cuenta cuando sus datos son válidos.

    https://docs.djangoproject.com/en/5.2/topics/forms/#the-view
    https://docs.djangoproject.com/en/5.2/topics/db/transactions/#controlling-transactions-explicitly
    """
    # Conserva el POST vacío como formulario enviado para validar sus obligatorios.
    formulario = RegistroUsuarioForm(
        request.POST if request.method == "POST" else None
    )

    if request.method == "POST" and formulario.is_valid():
        try:
            with transaction.atomic():
                # UserCreationForm aplica el hash de contraseña antes del guardado.
                usuario = formulario.save(commit=False)

                # El registro público nunca otorga privilegios administrativos.
                # La preferencia comercial no interviene en estos permisos.
                usuario.is_staff = False
                usuario.is_superuser = False
                usuario.save()
        except IntegrityError:
            # Otra solicitud puede registrar el correo después de su validación.
            # Consulta fuera de atomic para que la transacción ya esté revertida.
            if Usuario.objects.filter(
                email__iexact=formulario.cleaned_data["email"]
            ).exists():
                formulario.add_error(
                    "email", RegistroUsuarioForm.MENSAJE_CORREO_DUPLICADO
                )
            else:
                # No oculta errores de integridad ajenos a un correo duplicado.
                raise
        else:
            messages.success(request, "Tu cuenta se creó correctamente.")
            # POST/Redirect/GET evita repetir el alta al actualizar la página.
            return redirect("cuentas:registro")

    return render(
        request,
        "cuentas_app/registro.html",
        {"formulario": formulario},
    )
