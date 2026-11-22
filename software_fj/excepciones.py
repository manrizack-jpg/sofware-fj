"""Excepciones personalizadas del sistema Software FJ.

Todas heredan de ErrorSoftwareFJ, de modo que el sistema puede capturar
cualquier error propio con un único ``except ErrorSoftwareFJ`` y, a la vez,
distinguir cada situación con una clase específica.
"""


class ErrorSoftwareFJ(Exception):
    """Excepción base de la aplicación."""

    codigo = "SFJ-000"  # código corto que se escribe en el log

    def __init__(self, mensaje="Error en Software FJ", *, detalle=None):
        super().__init__(mensaje)  # guarda el mensaje en la excepción estándar
        self.mensaje = mensaje
        self.detalle = detalle  # información adicional opcional

    def __str__(self):
        base = f"[{self.codigo}] {self.mensaje}"
        return f"{base} ({self.detalle})" if self.detalle else base


class ValidacionError(ErrorSoftwareFJ):
    """Datos que no cumplen las reglas de validación."""
    codigo = "SFJ-100"


class ParametroFaltanteError(ValidacionError):
    """Se omitió un parámetro obligatorio (o llegó vacío / None)."""
    codigo = "SFJ-101"


class ClienteInvalidoError(ValidacionError):
    """Datos personales de un cliente inválidos."""
    codigo = "SFJ-102"


class ParametroInvalidoError(ValidacionError):
    """Parámetros de un servicio o de una reserva inválidos."""
    codigo = "SFJ-103"


class ServicioInvalidoError(ValidacionError):
    """Datos de un servicio inválidos (tarifa, nombre, capacidad...)."""
    codigo = "SFJ-104"


class RegistroDuplicadoError(ErrorSoftwareFJ):
    """Se intentó registrar algo que ya existe."""
    codigo = "SFJ-200"


class RegistroNoEncontradoError(ErrorSoftwareFJ):
    """No existe el cliente, servicio o reserva solicitado."""
    codigo = "SFJ-201"


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """El servicio existe pero no se puede reservar en este momento."""
    codigo = "SFJ-300"


class ReservaInvalidaError(ErrorSoftwareFJ):
    """La reserva no se pudo crear o procesar."""
    codigo = "SFJ-301"


class OperacionNoPermitidaError(ErrorSoftwareFJ):
    """La operación no es válida para el estado actual del objeto."""
    codigo = "SFJ-302"


class CalculoInconsistenteError(ErrorSoftwareFJ):
    """Un cálculo de costos produjo o recibió valores incoherentes."""
    codigo = "SFJ-400"


class ErrorInesperadoError(ErrorSoftwareFJ):
    """Envuelve errores no previstos (por ejemplo un ZeroDivisionError)."""
    codigo = "SFJ-999"
