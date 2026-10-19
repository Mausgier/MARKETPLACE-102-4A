"""
Define las rutas de la gestión de cuentas implementada.

https://docs.djangoproject.com/en/5.2/topics/http/urls/#url-namespaces
"""

from django.urls import path

from . import views

app_name = "cuentas"

urlpatterns = [
    path("", views.inicio_cuenta, name="inicio"),
    path("registro/", views.registro_usuario, name="registro"),
    path(
        "iniciar-sesion/",
        views.InicioSesionView.as_view(),
        name="iniciar_sesion",
    ),
    path(
        "cerrar-sesion/",
        views.CierreSesionView.as_view(),
        name="cerrar_sesion",
    ),
]
