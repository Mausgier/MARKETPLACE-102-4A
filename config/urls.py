"""
Conecta las rutas del proyecto con las aplicaciones Django.

https://docs.djangoproject.com/en/5.2/topics/http/urls/#including-other-urlconfs
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

urlpatterns = [
    # La entrada principal dirige al registro disponible en esta etapa.
    path('', RedirectView.as_view(pattern_name='cuentas:registro', permanent=False)),
    path('cuentas/', include('cuentas_app.urls')),
    path('admin/', admin.site.urls),
]
