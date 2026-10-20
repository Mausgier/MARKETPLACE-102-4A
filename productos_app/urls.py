"""Rutas públicas y de administración propia de publicaciones."""

from django.urls import path

from . import views

app_name = "productos"

urlpatterns = [
    path("", views.publicaciones_recientes, name="recientes"),
    path("publicar/", views.publicar_producto, name="publicar"),
    path("mis-publicaciones/", views.mis_publicaciones, name="mis_publicaciones"),
    path("<int:pk>/editar/", views.modificar_publicacion, name="editar"),
    path("<int:pk>/retirar/", views.eliminar_publicacion, name="retirar"),
    path("<int:pk>/", views.detalle_publicacion, name="detalle"),
]
