"""Rutas públicas y de administración propia de publicaciones."""

from django.urls import path

from . import views, views_administracion

app_name = "productos"

urlpatterns = [
    path("", views.publicaciones_recientes, name="recientes"),
    path("administracion/", views_administracion.listado_publicaciones, name="administrar_publicaciones"),
    path("administracion/<int:pk>/", views_administracion.detalle_administrativo, name="detalle_administrativo"),
    path("administracion/<int:pk>/retirar/", views_administracion.retirar_administrativamente, name="retiro_administrativo"),
    path("publicar/", views.publicar_producto, name="publicar"),
    path("mis-publicaciones/", views.mis_publicaciones, name="mis_publicaciones"),
    path("<int:pk>/editar/", views.modificar_publicacion, name="editar"),
    path("<int:pk>/retirar/", views.eliminar_publicacion, name="retirar"),
    path("<int:pk>/", views.detalle_publicacion, name="detalle"),
]
