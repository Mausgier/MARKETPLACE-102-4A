"""Vistas de registro, autenticación e inicio de cuenta del marketplace."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods

from .forms import InicioSesionForm, RegistroUsuarioForm
from .models import Usuario


@sensitive_post_parameters("password1", "password2")
@require_http_methods(["GET", "POST"])
def registro_usuario(request):
    """
    Presenta el registro y crea una cuenta cuando sus datos son válidos.

    https://docs.djangoproject.com/en/5.2/topics/forms/#the-view
    https://docs.djangoproject.com/en/5.2/topics/db/transactions/#controlling-transactions-explicitly
    """
    if request.user.is_authenticated:
        return redirect("cuentas:inicio")

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
            return redirect("cuentas:iniciar_sesion")

    return render(
        request,
        "cuentas_app/registro.html",
        {"formulario": formulario},
    )


class InicioSesionView(LoginView):
    """
    Delega el inicio de sesión, CSRF y las redirecciones seguras a Django.

    https://docs.djangoproject.com/en/5.2/topics/auth/default/#django.contrib.auth.views.LoginView
    """

    template_name = "cuentas_app/iniciar_sesion.html"
    authentication_form = InicioSesionForm
    # Mantiene el comportamiento nativo: un GET no redirige según la autenticación.
    # La plantilla ofrece volver al inicio cuando ya existe una sesión activa.
    redirect_authenticated_user = False


class CierreSesionView(LogoutView):
    """
    Finaliza la sesión mediante POST protegido con CSRF y confirma el resultado.

    https://docs.djangoproject.com/en/5.2/topics/auth/default/#django.contrib.auth.views.LogoutView
    """

    def get_redirect_url(self):
        """Ignora next para utilizar siempre el destino de cierre configurado."""
        return ""

    def post(self, request, *args, **kwargs):
        """Conserva la invalidación y las redirecciones seguras de LogoutView."""
        respuesta = super().post(request, *args, **kwargs)
        messages.success(request, "Cerraste sesión correctamente.")
        return respuesta


@never_cache
@login_required
def inicio_cuenta(request):
    """
    Presenta el inicio privado sin implementar todavía la gestión de perfil.

    https://docs.djangoproject.com/en/5.2/topics/auth/default/#the-login-required-decorator
    https://docs.djangoproject.com/en/5.2/topics/http/decorators/#caching
    """
    # RN-01: el acceso es común y no depende de la preferencia comercial.
    return render(request, "cuentas_app/inicio.html")
