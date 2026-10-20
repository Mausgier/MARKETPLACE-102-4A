"""Contrato abstracto: no contiene SDK, cliente HTTP, credenciales o implementaciones."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class SolicitudPago:
    """Datos mínimos de una futura solicitud, derivados exclusivamente del servidor."""

    intento_id: UUID
    referencia_comercial: str
    clave_idempotencia: UUID
    monto: Decimal
    moneda: str


@dataclass(frozen=True)
class TransaccionIniciada:
    """Una referencia creada no es prueba de aprobación financiera."""

    referencia_externa: str
    url_pago: str


@dataclass(frozen=True)
class ResultadoVerificado:
    """Contrato de respuesta futura; su construcción aislada no demuestra autenticidad."""

    referencia_externa: str
    referencia_comercial: str
    monto: Decimal
    moneda: str
    estado: str


class ProveedorPago(ABC):
    """
    Puerto para adaptadores futuros de prueba, sin seleccionar una pasarela.

    Cada implementación deberá autenticar comunicaciones HTTPS, comprobar comercio,
    ambiente, referencias, monto y moneda. Nunca confiará en el retorno del comprador.
    No debe ejecutarse red dentro de transacciones largas de base de datos.
    """

    @abstractmethod
    def iniciar(self, solicitud: SolicitudPago) -> TransaccionIniciada:
        """Define la futura creación externa; RF-19.1 no implementa esta operación."""
        raise NotImplementedError

    @abstractmethod
    def consultar(self, referencia_externa: str) -> ResultadoVerificado:
        """Define la verificación servidor-servidor, nunca una respuesta del navegador."""
        raise NotImplementedError
