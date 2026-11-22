"""Clase abstracta que representa las entidades generales del sistema."""
from abc import ABC, abstractmethod
from datetime import datetime

from .excepciones import ParametroFaltanteError


class EntidadBase(ABC):
    """Toda entidad (cliente, servicio, reserva) tiene id y fecha de creación."""

    def __init__(self, identificador):
        # Un identificador vacío o None no es válido
        if identificador is None or not str(identificador).strip():
            raise ParametroFaltanteError("La entidad requiere un identificador")
        self._id = str(identificador).strip()  # atributo protegido
        self._creado_en = datetime.now()

    @property
    def id(self):
        """Identificador de solo lectura."""
        return self._id

    @property
    def creado_en(self):
        """Fecha y hora de creación (solo lectura)."""
        return self._creado_en

    @abstractmethod
    def describir(self):
        """Cada entidad concreta devuelve su descripción en texto."""

    def __str__(self):
        return self.describir()

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self._id}>"
