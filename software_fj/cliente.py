"""Clase Cliente con validaciones robustas y datos personales encapsulados."""
import re

from .base import EntidadBase
from .excepciones import ClienteInvalidoError, ParametroFaltanteError

PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' ]+$")


def _obligatorio(valor, campo):
    """Lanza ParametroFaltanteError si el valor es None o texto vacío."""
    if valor is None or not str(valor).strip():
        raise ParametroFaltanteError(f"Falta el campo obligatorio '{campo}'")
    return str(valor).strip()


class Cliente(EntidadBase):
    """Cliente de Software FJ. Los datos se validan en cada asignación."""

    def __init__(self, identificador, nombre, documento, correo, telefono):
        super().__init__(identificador)
        # Se asigna mediante las propiedades para reutilizar las validaciones
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        self.telefono = telefono

    # ---- nombre -------------------------------------------------------
    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        texto = _obligatorio(valor, "nombre")
        if len(texto) < 3 or not PATRON_NOMBRE.match(texto):
            raise ClienteInvalidoError("Nombre inválido",
                                       detalle="mínimo 3 letras, sin números")
        self._nombre = texto.title()

    # ---- documento ----------------------------------------------------
    @property
    def documento(self):
        return self._documento

    @documento.setter
    def documento(self, valor):
        texto = _obligatorio(valor, "documento")
        if not texto.isdigit() or not 6 <= len(texto) <= 12:
            raise ClienteInvalidoError("Documento inválido",
                                       detalle="solo dígitos, entre 6 y 12")
        self._documento = texto

    # ---- correo -------------------------------------------------------
    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        texto = _obligatorio(valor, "correo").lower()
        if not PATRON_CORREO.match(texto):
            raise ClienteInvalidoError("Correo electrónico inválido",
                                       detalle=texto)
        self._correo = texto

    # ---- teléfono -----------------------------------------------------
    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        texto = _obligatorio(valor, "teléfono")
        if not texto.isdigit() or not 7 <= len(texto) <= 10:
            raise ClienteInvalidoError("Teléfono inválido",
                                       detalle="solo dígitos, entre 7 y 10")
        self._telefono = texto

    def describir(self):
        return (f"Cliente {self.id}: {self.nombre} | doc. {self.documento} | "
                f"{self.correo} | tel. {self.telefono}")
