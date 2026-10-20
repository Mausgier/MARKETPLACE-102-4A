"""Rutas privadas de confirmación y consulta de órdenes."""

from django.urls import path
from . import views

app_name = "ordenes"
urlpatterns = [
    path("", views.mis_ordenes, name="lista"),
    path("confirmar/", views.confirmar, name="confirmar"),
    path("<uuid:pk>/", views.detalle, name="detalle"),
]
