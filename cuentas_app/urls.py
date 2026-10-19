"""
Define las rutas de la gestión de cuentas implementada.

https://docs.djangoproject.com/en/5.2/topics/http/urls/#url-namespaces
"""

from django.urls import path

from . import views

app_name = "cuentas"

urlpatterns = [
    path("registro/", views.registro_usuario, name="registro"),
]
