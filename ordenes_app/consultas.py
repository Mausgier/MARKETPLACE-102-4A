"""Consultas privadas de compras y ventas, separadas de las solicitudes pendientes."""

from carrito_app.services import validar_cuenta

from .models import DetalleOrden, OrdenCompra


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


def ventas_del_usuario(*, usuario):
    """
    Prepara RF-12 sin interpretar detalles de órdenes como pedidos definitivos.

    Todavía no hay pagos aprobados ni pedidos por vendedor. Se reutiliza el vínculo
    histórico del detalle con su vendedor únicamente para delimitar esta consulta
    vacía, no como sustituto de un pedido ni como prueba de venta realizada.
    https://docs.djangoproject.com/en/5.2/ref/models/querysets/#none
    """
    validar_cuenta(usuario)
    # Integración pendiente: consultar los futuros pedidos del vendedor originados
    # en pagos aprobados, incluyendo cancelados y su reembolso cuando corresponda.
    # No excluir cancelados por estado ni mostrar aquí órdenes o reservas actuales.
    return DetalleOrden.objects.filter(vendedor=usuario).none()
