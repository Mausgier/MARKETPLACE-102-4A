"""Migración de RF-10 generada por Django: conserva los datos anteriores."""

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """Aplica cambios de estructura y restricciones para RF-10."""

    initial = True

    dependencies = [
        ('productos_app', '0003_publicacion_publicacion_reserva_no_supera_fisico'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OrdenCompra',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('clave_confirmacion', models.UUIDField(editable=False, unique=True)),
                ('creada_en', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('vence_en', models.DateTimeField()),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente de Pago'), ('expirada', 'Expirada')], default='pendiente', max_length=12)),
                ('total', models.DecimalField(decimal_places=2, max_digits=24)),
                ('comprador', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-creada_en', '-pk'),
            },
        ),
        migrations.CreateModel(
            name='DetalleOrden',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_producto', models.CharField(max_length=150)),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=12)),
                ('cantidad', models.PositiveIntegerField()),
                ('publicacion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='productos_app.publicacion')),
                ('vendedor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('orden', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='detalles', to='ordenes_app.ordencompra')),
            ],
            options={
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='ReservaStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('activa', 'Activa'), ('expirada', 'Expirada')], default='activa', max_length=10)),
                ('detalle', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='reserva', to='ordenes_app.detalleorden')),
            ],
        ),
        migrations.AddIndex(
            model_name='ordencompra',
            index=models.Index(fields=['estado', 'vence_en'], name='ordenes_por_vencer'),
        ),
        migrations.AddConstraint(
            model_name='ordencompra',
            constraint=models.CheckConstraint(condition=models.Q(('total__gt', 0)), name='orden_total_positivo'),
        ),
        migrations.AddConstraint(
            model_name='ordencompra',
            constraint=models.CheckConstraint(condition=models.Q(('vence_en__gt', models.F('creada_en'))), name='orden_vencimiento_posterior'),
        ),
        migrations.AddConstraint(
            model_name='ordencompra',
            constraint=models.CheckConstraint(condition=models.Q(('estado__in', ['pendiente', 'expirada'])), name='orden_estado_valido'),
        ),
        migrations.AddConstraint(
            model_name='detalleorden',
            constraint=models.UniqueConstraint(fields=('orden', 'publicacion'), name='orden_oferta_unica'),
        ),
        migrations.AddConstraint(
            model_name='detalleorden',
            constraint=models.CheckConstraint(condition=models.Q(('cantidad__gte', 1), ('cantidad__lte', 2147483647)), name='detalle_cantidad_valida'),
        ),
        migrations.AddConstraint(
            model_name='detalleorden',
            constraint=models.CheckConstraint(condition=models.Q(('precio_unitario__gt', 0)), name='detalle_precio_positivo'),
        ),
        migrations.AddConstraint(
            model_name='reservastock',
            constraint=models.CheckConstraint(condition=models.Q(('estado__in', ['activa', 'expirada'])), name='reserva_estado_valido'),
        ),
    ]
