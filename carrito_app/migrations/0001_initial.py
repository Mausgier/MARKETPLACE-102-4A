"""Crea las tablas del carrito y sus restricciones sin alterar datos anteriores."""

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """Incorpora el carrito persistente mediante una migración aditiva."""

    initial = True

    dependencies = [
        ('productos_app', '0002_categorias_iniciales'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Carrito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='carrito', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ItemCarrito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(2147483647)])),
                ('carrito', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='carrito_app.carrito')),
                ('publicacion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items_carrito', to='productos_app.publicacion')),
            ],
            options={
                'ordering': ('pk',),
                'constraints': [models.UniqueConstraint(fields=('carrito', 'publicacion'), name='item_carrito_oferta_unica'), models.CheckConstraint(condition=models.Q(('cantidad__gte', 1), ('cantidad__lte', 2147483647)), name='item_carrito_cantidad_valida')],
            },
        ),
    ]
