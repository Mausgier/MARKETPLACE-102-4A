"""Rutas de creación y consulta mínima de publicaciones."""

from django.urls import path

from . import views

app_name = "productos"

urlpatterns = [
    path("", views.publicaciones_recientes, name="recientes"),
    path("publicar/", views.publicar_producto, name="publicar"),
    path("<int:pk>/", views.detalle_publicacion, name="detalle"),
]
