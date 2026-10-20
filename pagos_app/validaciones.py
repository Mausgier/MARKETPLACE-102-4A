"""Importes CLP exactos; nunca redondea ni convierte desde punto flotante."""

from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError

MAXIMO_MONTO_CLP = Decimal("999999999999999")


def validar_monto_clp(valor):
    """Devuelve un Decimal entero positivo, limitado explícitamente a quince dígitos."""
    if isinstance(valor, (float, bool)):
        raise ValidationError("El monto debe proporcionarse como Decimal, entero o texto decimal exacto.")
    try:
        monto = Decimal(valor)
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValidationError("El monto CLP no es válido.") from error
    if not monto.is_finite() or monto <= 0:
        raise ValidationError("El monto CLP debe ser positivo y finito.")
    if monto != monto.to_integral_value():
        raise ValidationError("CLP requiere unidades enteras. No se redondeará el importe de la orden.")
    if monto > MAXIMO_MONTO_CLP:
        raise ValidationError("El monto supera el límite de quince dígitos admitido en esta etapa.")
    return monto.to_integral_value()
