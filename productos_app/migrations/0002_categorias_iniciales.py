"""Carga categorías reproducibles sin depender de la base de desarrollo."""

from django.db import migrations


def cargar_categorias(apps, schema_editor):
    """
    Incorpora categorías iniciales utilizando el modelo histórico de la migración.

    https://docs.djangoproject.com/en/5.2/topics/migrations/#data-migrations
    """
    categoria = apps.get_model("productos_app", "Categoria")
    conexion = schema_editor.connection.alias
    for nombre in ("Tecnología", "Hogar", "Moda", "Libros", "Deportes", "Otros"):
        categoria.objects.using(conexion).get_or_create(nombre=nombre)


class Migration(migrations.Migration):
    """Añade categorías; la operación inversa no elimina datos utilizados."""

    dependencies = [("productos_app", "0001_initial")]

    operations = [
        migrations.RunPython(cargar_categorias, migrations.RunPython.noop),
    ]
