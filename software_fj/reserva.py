"""Clase Reserva: integra cliente, servicio, duración y estado."""
from enum import Enum

from .base import EntidadBase
from .cliente import Cliente
from .excepciones import (CalculoInconsistenteError, OperacionNoPermitidaError,
                          ReservaInvalidaError, ServicioNoDisponibleError)
from .registro import obtener_logger
from .servicios import IVA_DEFECTO, ServicioBase

_log = obtener_logger("reserva")


class EstadoReserva(Enum):
    """Estados posibles de una reserva."""
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    PROCESADA = "PROCESADA"
    CANCELADA = "CANCELADA"


class Reserva(EntidadBase):
    """Reserva de un servicio por parte de un cliente."""

    def __init__(self, identificador, cliente, servicio, horas, *,
                 impuesto=IVA_DEFECTO, descuento=0.0, **opciones):
        super().__init__(identificador)
        # Validación de tipos: evita reservas con objetos incorrectos
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un Cliente válido")
        if not isinstance(servicio, ServicioBase):
            raise ReservaInvalidaError("La reserva requiere un Servicio válido")
        # El servicio debe estar disponible para poder reservarlo
        if not servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{servicio.nombre}' no está disponible",
                detalle=servicio.id)
        # Cada servicio valida sus propios parámetros (polimorfismo)
        servicio.validar_parametros(horas, **opciones)

        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas
        self._impuesto = impuesto
        self._descuento = descuento
        self._opciones = dict(opciones)
        self._estado = EstadoReserva.PENDIENTE
        self._costo_total = None

    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    @property
    def horas(self):
        return self._horas

    @property
    def estado(self):
        return self._estado

    @property
    def costo_total(self):
        return self._costo_total

    # ---- operaciones --------------------------------------------------
    def confirmar(self):
        """PENDIENTE -> CONFIRMADA (si el servicio sigue disponible)."""
        if self._estado is not EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                "Solo se puede confirmar una reserva pendiente",
                detalle=f"estado actual: {self._estado.value}")
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self._servicio.nombre}' ya no está disponible")
        self._estado = EstadoReserva.CONFIRMADA
        _log.info("Reserva %s confirmada", self.id)

    def cancelar(self, motivo="Sin motivo"):
        """Cancela la reserva si aún no fue procesada ni cancelada."""
        if self._estado in (EstadoReserva.CANCELADA, EstadoReserva.PROCESADA):
            raise OperacionNoPermitidaError(
                "La reserva no se puede cancelar",
                detalle=f"estado actual: {self._estado.value}")
        self._estado = EstadoReserva.CANCELADA
        _log.info("Reserva %s cancelada. Motivo: %s", self.id, motivo)

    def procesar(self):
        """CONFIRMADA -> PROCESADA, calculando el costo total.

        Usa try/except/else/finally y encadenamiento de excepciones
        (raise ... from ...).
        """
        if self._estado is not EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitidaError(
                "Solo se puede procesar una reserva confirmada",
                detalle=f"estado actual: {self._estado.value}")
        try:
            costo = self._servicio.calcular_costo(
                self._horas, self._impuesto, self._descuento, **self._opciones)
        except CalculoInconsistenteError as error:
            # Se conserva el error original como causa (__cause__)
            raise ReservaInvalidaError(
                f"No se pudo procesar la reserva {self.id}") from error
        else:
            # Solo se ejecuta si el cálculo salió bien
            self._costo_total = costo
            self._estado = EstadoReserva.PROCESADA
            _log.info("Reserva %s procesada. Total: $%s", self.id, f"{costo:,.2f}")
        finally:
            # Se ejecuta siempre, haya o no error
            _log.debug("Intento de procesamiento de la reserva %s finalizado", self.id)
        return costo

    def describir(self):
        total = f"${self._costo_total:,.2f}" if self._costo_total is not None else "pendiente"
        return (f"Reserva {self.id} | {self._cliente.nombre} -> "
                f"{self._servicio.nombre} | {self._horas} h | "
                f"{self._estado.value} | total {total}")
