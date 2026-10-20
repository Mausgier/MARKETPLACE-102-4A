"""
Define las rutas de la gestión de cuentas implementada.

https://docs.djangoproject.com/en/5.2/topics/http/urls/#url-namespaces
"""

from django.urls import path

from . import views, views_administracion

app_name = "cuentas"

urlpatterns = [
    path("", views.inicio_cuenta, name="inicio"),
    path("perfil/", views.perfil_usuario, name="perfil"),
    path("administracion/usuarios/", views_administracion.listado_usuarios, name="administrar_usuarios"),
    path("administracion/usuarios/<int:usuario_id>/suspender/", views_administracion.suspender_usuario, name="suspender_usuario"),
    path("administracion/usuarios/<int:usuario_id>/reactivar/", views_administracion.reactivar_usuario, name="reactivar_usuario"),
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
