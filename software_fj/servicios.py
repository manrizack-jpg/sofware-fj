"""Servicios de Software FJ: clase abstracta y tres servicios especializados.

Se aplican herencia, polimorfismo (cada servicio sobrescribe describir,
validar_parametros y el cálculo del costo base) y sobrecarga de métodos
mediante parámetros opcionales y variantes nombradas.
"""
from abc import ABC, abstractmethod

from .base import EntidadBase
from .excepciones import (CalculoInconsistenteError, ParametroFaltanteError,
                          ParametroInvalidoError, ServicioInvalidoError)

IVA_DEFECTO = 0.19  # impuesto por defecto (19 %)


class ServicioBase(EntidadBase, ABC):
    """Clase abstracta Servicio: define lo que todo servicio debe ofrecer."""

    TIPO = "Servicio"
    HORAS_MAXIMAS = 8  # cada subclase puede cambiarlo

    def __init__(self, identificador, nombre, tarifa_hora, disponible=True):
        super().__init__(identificador)
        if nombre is None or not str(nombre).strip():
            raise ParametroFaltanteError("El servicio requiere un nombre")
        # bool es subclase de int: se descarta explícitamente
        if isinstance(tarifa_hora, bool) or not isinstance(tarifa_hora, (int, float)):
            raise ServicioInvalidoError("La tarifa debe ser numérica",
                                        detalle=repr(tarifa_hora))
        if tarifa_hora <= 0:
            raise ServicioInvalidoError("La tarifa por hora debe ser mayor que 0",
                                        detalle=str(tarifa_hora))
        self._nombre = str(nombre).strip()
        self._tarifa_hora = float(tarifa_hora)
        self._disponible = bool(disponible)

    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa_hora(self):
        return self._tarifa_hora

    @property
    def disponible(self):
        return self._disponible

    def marcar_disponible(self, estado):
        """Cambia la disponibilidad del servicio."""
        self._disponible = bool(estado)

    # ---- validación común --------------------------------------------
    def validar_horas(self, horas):
        """Valida la duración en horas (común a todos los servicios)."""
        if horas is None:
            raise ParametroFaltanteError("Falta la duración (horas)")
        if isinstance(horas, bool) or not isinstance(horas, (int, float)):
            raise ParametroInvalidoError("La duración debe ser numérica",
                                         detalle=repr(horas))
        if not 0 < horas <= self.HORAS_MAXIMAS:
            raise ParametroInvalidoError(
                f"Duración fuera de rango para {self.TIPO}",
                detalle=f"permitido: 0 < horas <= {self.HORAS_MAXIMAS}")

    @staticmethod
    def _verificar_opciones(opciones, permitidas):
        """Rechaza opciones que el servicio no reconoce."""
        extra = set(opciones) - set(permitidas)
        if extra:
            raise ParametroInvalidoError("Opciones no soportadas",
                                         detalle=", ".join(sorted(extra)))

    # ---- métodos abstractos (polimorfismo) ----------------------------
    @abstractmethod
    def validar_parametros(self, horas, **opciones):
        """Valida duración y opciones propias del servicio."""

    @abstractmethod
    def _costo_base(self, horas, **opciones):
        """Costo sin impuestos ni descuentos (lo define cada servicio)."""

    @abstractmethod
    def describir(self):
        """Descripción del servicio."""

    # ---- métodos sobrecargados ----------------------------------------
    def calcular_costo(self, horas, impuesto=IVA_DEFECTO, descuento=0.0, **opciones):
        """Costo final del servicio. Variantes de uso (sobrecarga):

        calcular_costo(horas)                        -> con IVA por defecto
        calcular_costo(horas, impuesto)              -> con impuesto propio
        calcular_costo(horas, impuesto, descuento)   -> con impuesto y descuento
        """
        self.validar_parametros(horas, **opciones)
        if not 0 <= impuesto <= 1:
            raise CalculoInconsistenteError("Impuesto fuera de rango",
                                            detalle=f"{impuesto} (debe ser 0 a 1)")
        if not 0 <= descuento < 1:
            raise CalculoInconsistenteError("Descuento fuera de rango",
                                            detalle=f"{descuento} (debe ser 0 a <1)")
        base = self._costo_base(horas, **opciones)
        total = base * (1 - descuento) * (1 + impuesto)
        if total <= 0:
            raise CalculoInconsistenteError("El costo calculado no es positivo")
        return round(total, 2)

    def costo_sin_impuesto(self, horas, **opciones):
        """Variante: costo sin IVA."""
        return self.calcular_costo(horas, impuesto=0.0, **opciones)

    def costo_con_descuento(self, horas, descuento, **opciones):
        """Variante: costo con IVA por defecto y un descuento."""
        return self.calcular_costo(horas, IVA_DEFECTO, descuento, **opciones)


class SalaReserva(ServicioBase):
    """Reserva de salas (con capacidad y proyector opcional)."""

    TIPO = "Sala"
    HORAS_MAXIMAS = 8
    CARGO_PROYECTOR = 10_000  # por hora

    def __init__(self, identificador, nombre, tarifa_hora, capacidad,
                 proyector=False, disponible=True):
        super().__init__(identificador, nombre, tarifa_hora, disponible)
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad < 1:
            raise ServicioInvalidoError("Capacidad inválida", detalle=repr(capacidad))
        self._capacidad = capacidad
        self._proyector = bool(proyector)

    @property
    def capacidad(self):
        return self._capacidad

    def validar_parametros(self, horas, **opciones):
        self.validar_horas(horas)
        self._verificar_opciones(opciones, ["asistentes"])
        asistentes = opciones.get("asistentes", 1)
        if isinstance(asistentes, bool) or not isinstance(asistentes, int) or asistentes < 1:
            raise ParametroInvalidoError("Número de asistentes inválido",
                                         detalle=repr(asistentes))
        if asistentes > self._capacidad:
            raise ParametroInvalidoError(
                "Los asistentes superan la capacidad de la sala",
                detalle=f"{asistentes} > {self._capacidad}")

    def _costo_base(self, horas, **opciones):
        extra = self.CARGO_PROYECTOR if self._proyector else 0
        return (self._tarifa_hora + extra) * horas

    def describir(self):
        proy = "con proyector" if self._proyector else "sin proyector"
        return (f"Sala {self.id} '{self.nombre}' | capacidad {self._capacidad} | "
                f"{proy} | ${self._tarifa_hora:,.0f}/h")


class AlquilerEquipo(ServicioBase):
    """Alquiler de equipos (portátiles, proyectores, etc.) por unidades."""

    TIPO = "Equipo"
    HORAS_MAXIMAS = 72

    def __init__(self, identificador, nombre, tarifa_hora, tipo_equipo,
                 unidades_disponibles, disponible=True):
        super().__init__(identificador, nombre, tarifa_hora, disponible)
        if not tipo_equipo or not str(tipo_equipo).strip():
            raise ParametroFaltanteError("Falta el tipo de equipo")
        if (isinstance(unidades_disponibles, bool)
                or not isinstance(unidades_disponibles, int) or unidades_disponibles < 0):
            raise ServicioInvalidoError("Unidades disponibles inválidas",
                                        detalle=repr(unidades_disponibles))
        self._tipo_equipo = str(tipo_equipo).strip()
        self._unidades = unidades_disponibles

    def validar_parametros(self, horas, **opciones):
        self.validar_horas(horas)
        self._verificar_opciones(opciones, ["unidades"])
        unidades = opciones.get("unidades", 1)
        if isinstance(unidades, bool) or not isinstance(unidades, int) or unidades < 1:
            raise ParametroInvalidoError("Cantidad de unidades inválida",
                                         detalle=repr(unidades))
        if unidades > self._unidades:
            raise ParametroInvalidoError(
                "No hay suficientes unidades disponibles",
                detalle=f"{unidades} > {self._unidades}")

    def _costo_base(self, horas, **opciones):
        return self._tarifa_hora * horas * opciones.get("unidades", 1)

    def describir(self):
        return (f"Equipo {self.id} '{self.nombre}' | {self._tipo_equipo} | "
                f"{self._unidades} unidades | ${self._tarifa_hora:,.0f}/h por unidad")


class AsesoriaEspecializada(ServicioBase):
    """Asesoría con un especialista junior o senior (virtual o presencial)."""

    TIPO = "Asesoría"
    HORAS_MAXIMAS = 6
    MULTIPLICADOR = {"junior": 1.0, "senior": 1.5}
    RECARGO_PRESENCIAL = 20_000  # valor fijo por sesión

    def __init__(self, identificador, nombre, tarifa_hora, especialidad,
                 nivel="junior", disponible=True):
        super().__init__(identificador, nombre, tarifa_hora, disponible)
        if not especialidad or not str(especialidad).strip():
            raise ParametroFaltanteError("Falta la especialidad")
        nivel = str(nivel).strip().lower()
        if nivel not in self.MULTIPLICADOR:
            raise ServicioInvalidoError("Nivel de asesor inválido",
                                        detalle="use 'junior' o 'senior'")
        self._especialidad = str(especialidad).strip()
        self._nivel = nivel

    def validar_parametros(self, horas, **opciones):
        self.validar_horas(horas)
        self._verificar_opciones(opciones, ["modalidad"])
        modalidad = opciones.get("modalidad", "virtual")
        if modalidad not in ("virtual", "presencial"):
            raise ParametroInvalidoError("Modalidad inválida",
                                         detalle="use 'virtual' o 'presencial'")

    def _costo_base(self, horas, **opciones):
        base = self._tarifa_hora * self.MULTIPLICADOR[self._nivel] * horas
        if opciones.get("modalidad") == "presencial":
            base += self.RECARGO_PRESENCIAL
        return base

    def describir(self):
        return (f"Asesoría {self.id} '{self.nombre}' | {self._especialidad} "
                f"({self._nivel}) | ${self._tarifa_hora:,.0f}/h")
