"""
Conecta las rutas del proyecto con las aplicaciones Django.

https://docs.djangoproject.com/en/5.2/topics/http/urls/#including-other-urlconfs
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

urlpatterns = [
    # El inicio de cuenta conduce al acceso cuando no existe una sesión autenticada.
    path('', RedirectView.as_view(pattern_name='cuentas:inicio', permanent=False)),
    path('cuentas/', include('cuentas_app.urls')),
    path('articulos/', include('productos_app.urls')),
    path('carrito/', include('carrito_app.urls')),
    path('ordenes/', include('ordenes_app.urls')),
    path('admin/', admin.site.urls),
]
