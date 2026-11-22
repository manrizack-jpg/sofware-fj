"""Sistema de gestión: administra clientes, servicios y reservas en listas.

No usa bases de datos; toda la información vive en objetos y listas.
El método ``ejecutar`` garantiza que ningún error detenga la aplicación.
"""
from dataclasses import dataclass
from typing import Any, Optional

from .cliente import Cliente
from .excepciones import (ErrorSoftwareFJ, ErrorInesperadoError,
                          ParametroFaltanteError, RegistroDuplicadoError,
                          RegistroNoEncontradoError)
from .registro import obtener_logger
from .reserva import Reserva
from .servicios import ServicioBase


@dataclass
class ResultadoOperacion:
    """Resultado de una operación ejecutada de forma segura."""
    exito: bool
    descripcion: str
    valor: Any = None
    error: Optional[str] = None


class SistemaGestion:
    """Núcleo de Software FJ."""

    def __init__(self):
        self._clientes = []    # lista interna de Cliente
        self._servicios = []   # lista interna de ServicioBase
        self._reservas = []    # lista interna de Reserva
        self._operaciones = 0
        self._log = obtener_logger("gestor")

    # ---- consultas (devuelven copias para proteger la encapsulación) ----
    @property
    def clientes(self):
        return tuple(self._clientes)

    @property
    def servicios(self):
        return tuple(self._servicios)

    @property
    def reservas(self):
        return tuple(self._reservas)

    def _buscar(self, lista, identificador, tipo):
        """Busca por id; lanza error si falta el parámetro o no existe."""
        if identificador is None or not str(identificador).strip():
            raise ParametroFaltanteError(f"Falta el identificador de {tipo}")
        for elemento in lista:
            if elemento.id == str(identificador).strip():
                return elemento
        raise RegistroNoEncontradoError(f"No existe {tipo} con id '{identificador}'")

    # ---- registros ------------------------------------------------------
    def registrar_cliente(self, identificador, nombre, documento, correo, telefono):
        cliente = Cliente(identificador, nombre, documento, correo, telefono)
        for existente in self._clientes:
            if existente.id == cliente.id or existente.documento == cliente.documento:
                raise RegistroDuplicadoError("El cliente ya está registrado",
                                             detalle=f"id/doc: {cliente.id}/{cliente.documento}")
        self._clientes.append(cliente)
        return cliente

    def registrar_servicio(self, servicio):
        if not isinstance(servicio, ServicioBase):
            raise ParametroFaltanteError("Se esperaba un objeto Servicio")
        if any(s.id == servicio.id for s in self._servicios):
            raise RegistroDuplicadoError("El servicio ya está registrado",
                                         detalle=servicio.id)
        self._servicios.append(servicio)
        return servicio

    def crear_reserva(self, id_reserva, id_cliente, id_servicio, horas, **opciones):
        cliente = self._buscar(self._clientes, id_cliente, "cliente")
        servicio = self._buscar(self._servicios, id_servicio, "servicio")
        if any(r.id == str(id_reserva).strip() for r in self._reservas):
            raise RegistroDuplicadoError("La reserva ya existe", detalle=str(id_reserva))
        reserva = Reserva(id_reserva, cliente, servicio, horas, **opciones)
        self._reservas.append(reserva)
        return reserva

    def confirmar_reserva(self, id_reserva):
        self._buscar(self._reservas, id_reserva, "reserva").confirmar()

    def cancelar_reserva(self, id_reserva, motivo="Solicitud del cliente"):
        self._buscar(self._reservas, id_reserva, "reserva").cancelar(motivo)

    def procesar_reserva(self, id_reserva):
        return self._buscar(self._reservas, id_reserva, "reserva").procesar()

    # ---- ejecución segura ---------------------------------------------
    def ejecutar(self, descripcion, funcion, *args, **kwargs):
        """Ejecuta una operación sin que un error detenga el sistema.

        try/except (errores propios y errores inesperados) / else / finally.
        """
        resultado = None
        try:
            valor = funcion(*args, **kwargs)
        except ErrorSoftwareFJ as error:
            # Error controlado del dominio
            self._log.error("%s | FALLÓ | %s", descripcion, error)
            if error.__cause__ is not None:  # encadenamiento: causa original
                self._log.error("   causa original: %r", error.__cause__)
            resultado = ResultadoOperacion(False, descripcion, error=str(error))
        except Exception as error:  # noqa: BLE001 - se captura todo a propósito
            # Error no previsto: se envuelve y se registra con traza completa
            envuelto = ErrorInesperadoError("Error no previsto durante la operación",
                                            detalle=repr(error))
            envuelto.__cause__ = error
            self._log.critical("%s | ERROR INESPERADO | %s", descripcion, envuelto,
                               exc_info=True)
            resultado = ResultadoOperacion(False, descripcion, error=str(envuelto))
        else:
            self._log.info("%s | OK", descripcion)
            resultado = ResultadoOperacion(True, descripcion, valor=valor)
        finally:
            self._operaciones += 1
            self._log.debug("Operación #%d finalizada", self._operaciones)
        return resultado

    def resumen(self):
        """Contadores generales del sistema."""
        return {"clientes": len(self._clientes), "servicios": len(self._servicios),
                "reservas": len(self._reservas), "operaciones": self._operaciones}
