"""Consultas privadas; distingue solicitudes de compra de compras efectivamente pagadas."""

from carrito_app.services import validar_cuenta

from .models import OrdenCompra


def compras_aprobadas_del_usuario(*, usuario):
    """
    Reserva el punto de integración del historial con los futuros pagos y pedidos.

    RF-11 parcial: todavía no existe evidencia de pagos aprobados en el modelo.
    No se infiere una compra desde la creación de una orden ni desde sus reservas.
    RF-19 deberá aportar la condición de aprobación y la fecha real de compra;
    los pedidos definitivos deberán aportar vendedores, estados y su cantidad.
    https://docs.djangoproject.com/en/5.2/ref/models/querysets/#none
    """
    validar_cuenta(usuario)
    # El conjunto vacío es deliberado: también excluye cualquier estado que se
    # incorpore en el futuro hasta que su integración se valide expresamente.
    return OrdenCompra.objects.filter(comprador=usuario).none()
