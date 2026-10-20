"""Rutas sin identificadores de usuario o carrito aportados por el cliente."""

from django.urls import path

from . import views

app_name = "carrito"

urlpatterns = [
    path("", views.ver_carrito, name="ver"),
    path("agregar/<int:publicacion_id>/", views.agregar, name="agregar"),
    path("linea/<int:item_id>/actualizar/", views.actualizar, name="actualizar"),
    path("linea/<int:item_id>/eliminar/", views.eliminar, name="eliminar"),
]
