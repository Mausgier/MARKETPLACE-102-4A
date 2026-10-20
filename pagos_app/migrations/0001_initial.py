"""Incorpora intentos de pago sin convertir ni modificar registros anteriores."""

import django.db.models.deletion
import django.db.models.functions.math
import django.utils.timezone
import pagos_app.models
import uuid
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):
    """Crea una tabla con referencias e invariantes para RF-19.1."""

    initial = True

    dependencies = [
        ('ordenes_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IntentoPago',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('clave_idempotencia', models.UUIDField(editable=False, unique=True)),
                ('referencia_comercial', models.CharField(default=pagos_app.models.generar_referencia_comercial, editable=False, max_length=26, unique=True)),
                ('proveedor', models.SlugField(blank=True, default='', max_length=40)),
                ('ambiente', models.CharField(choices=[('pruebas', 'Pruebas'), ('produccion', 'Producción')], default='pruebas', max_length=10)),
                ('monto', models.DecimalField(decimal_places=0, max_digits=15)),
                ('moneda', models.CharField(default='CLP', editable=False, max_length=3)),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('aprobado', 'Aprobado'), ('rechazado', 'Rechazado'), ('cancelado', 'Cancelado')], default='pendiente', max_length=10)),
                ('verificacion', models.CharField(choices=[('pendiente', 'Sin verificar'), ('requiere_consulta', 'Requiere consulta externa'), ('confirmada', 'Resultado verificado')], default='pendiente', max_length=20)),
                ('referencia_externa', models.CharField(blank=True, max_length=128, null=True)),
                ('creado_en', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('verificado_en', models.DateTimeField(blank=True, null=True)),
                ('orden', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='intentos_pago', to='ordenes_app.ordencompra')),
            ],
            options={
                'ordering': ('-creado_en', '-pk'),
                'indexes': [models.Index(fields=['estado', 'verificacion'], name='pago_por_verificar')],
                'constraints': [models.UniqueConstraint(fields=('proveedor', 'ambiente', 'referencia_externa'), name='pago_referencia_externa_unica'), models.UniqueConstraint(condition=models.Q(('estado', 'aprobado')), fields=('orden',), name='pago_un_aprobado_por_orden'), models.CheckConstraint(condition=models.Q(('monto', django.db.models.functions.math.Floor('monto')), ('monto__gt', 0), ('monto__lte', Decimal('999999999999999'))), name='pago_monto_clp_entero'), models.CheckConstraint(condition=models.Q(('moneda', 'CLP')), name='pago_moneda_clp'), models.CheckConstraint(condition=models.Q(('estado__in', ['pendiente', 'aprobado', 'rechazado', 'cancelado'])), name='pago_estado_valido'), models.CheckConstraint(condition=models.Q(('ambiente__in', ['pruebas', 'produccion'])), name='pago_ambiente_valido'), models.CheckConstraint(condition=models.Q(models.Q(('estado', 'pendiente'), ('verificacion__in', ['pendiente', 'requiere_consulta']), ('verificado_en__isnull', True)), models.Q(('referencia_externa__isnull', False), ('verificacion', 'confirmada'), ('verificado_en__isnull', False), models.Q(('proveedor', ''), _negated=True), models.Q(('referencia_externa', ''), _negated=True)), _connector='OR'), name='pago_resultado_verificable'), models.CheckConstraint(condition=models.Q(('referencia_externa__isnull', True), models.Q(models.Q(('proveedor', ''), _negated=True), models.Q(('referencia_externa', ''), _negated=True)), _connector='OR'), name='pago_referencia_con_proveedor')],
            },
        ),
    ]
