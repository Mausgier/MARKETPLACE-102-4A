"""Liberación explícita; en despliegue requiere programación periódica externa."""

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError
from ordenes_app.services import expirar_ordenes


class Command(BaseCommand):
    """Expira órdenes pendientes vencidas sin duplicar liberaciones."""

    help = "Expira órdenes vencidas y libera sus reservas. Repetir es seguro."

    def handle(self, *args, **options):
        """Informa el resultado sin divulgar SQL ni datos personales."""
        try:
            cantidad = expirar_ordenes()
        except (DatabaseError, ValidationError) as error:
            raise CommandError("No se completó la expiración. Revisa la integridad y reintenta.") from error
        self.stdout.write(self.style.SUCCESS(f"Órdenes expiradas: {cantidad}."))
