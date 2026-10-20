"""Migración de RF-10 generada por Django: conserva los datos anteriores."""

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """Aplica cambios de estructura y restricciones para RF-10."""

    dependencies = [
        ('productos_app', '0002_categorias_iniciales'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='publicacion',
            constraint=models.CheckConstraint(condition=models.Q(('stock_reservado__lte', models.F('stock_disponible'))), name='publicacion_reserva_no_supera_fisico'),
        ),
    ]
