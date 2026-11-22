"""Pruebas unitarias de Software FJ (ejecutar: python -m unittest -v)."""
import tempfile
import unittest
from pathlib import Path

from software_fj import (AlquilerEquipo, AsesoriaEspecializada, Cliente,
                         EstadoReserva, SalaReserva, SistemaGestion,
                         configurar_logging)
from software_fj.base import EntidadBase
from software_fj.excepciones import (CalculoInconsistenteError, ClienteInvalidoError,
                                     ErrorSoftwareFJ, OperacionNoPermitidaError,
                                     ParametroFaltanteError, ParametroInvalidoError,
                                     ReservaInvalidaError, ServicioInvalidoError,
                                     ServicioNoDisponibleError)
from software_fj.servicios import ServicioBase


class PruebasBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ruta_log = Path(self.tmp.name) / "prueba.log"
        configurar_logging(self.ruta_log, sobrescribir=True)
        self.s = SistemaGestion()
        self.s.registrar_cliente("C1", "Ana Gómez", "1012345678", "ana@correo.com", "3001234567")
        self.s.registrar_servicio(SalaReserva("S1", "Sala", 50_000, 10, proyector=True))
        self.s.registrar_servicio(AlquilerEquipo("E1", "Portátiles", 20_000, "Portátil", 5))
        self.s.registrar_servicio(AsesoriaEspecializada("A1", "Asesoría", 80_000, "Python", "senior"))

    def tearDown(self):
        # Cierra el archivo de log antes de borrar la carpeta temporal
        configurar_logging(Path(self.tmp.name) / "cierre.log")
        self.tmp.cleanup()


class PruebasCliente(PruebasBase):
    def test_cliente_valido_normaliza_datos(self):
        c = Cliente("X", "luis pérez", "123456", "LUIS@Correo.com", "3001112233")
        self.assertEqual(c.nombre, "Luis Pérez")
        self.assertEqual(c.correo, "luis@correo.com")

    def test_correo_invalido(self):
        with self.assertRaises(ClienteInvalidoError):
            Cliente("X", "Luis Pérez", "123456", "sin-arroba", "3001112233")

    def test_parametro_faltante(self):
        with self.assertRaises(ParametroFaltanteError):
            Cliente("X", None, "123456", "a@b.co", "3001112233")


class PruebasServicios(PruebasBase):
    def test_clase_abstracta_no_se_instancia(self):
        with self.assertRaises(TypeError):
            ServicioBase("X", "Y", 1000)
        with self.assertRaises(TypeError):
            EntidadBase("X")

    def test_polimorfismo_costos(self):
        sala, equipo, ase = self.s.servicios
        self.assertEqual(sala.calcular_costo(3), 214_200.00)
        self.assertEqual(equipo.calcular_costo(24, unidades=2), 1_142_400.00)
        self.assertEqual(ase.calcular_costo(2, modalidad="presencial"),
                         round((80_000 * 1.5 * 2 + 20_000) * 1.19, 2))

    def test_sobrecarga_variantes(self):
        sala = self.s.servicios[0]
        self.assertEqual(sala.costo_sin_impuesto(2), 120_000.0)
        self.assertEqual(sala.calcular_costo(2, 0.0, 0.5), 60_000.0)
        self.assertEqual(sala.costo_con_descuento(2, 0.5), round(60_000 * 1.19, 2))

    def test_tarifa_invalida(self):
        with self.assertRaises(ServicioInvalidoError):
            SalaReserva("S9", "Mala", -5, 4)

    def test_descuento_inconsistente(self):
        with self.assertRaises(CalculoInconsistenteError):
            self.s.servicios[0].calcular_costo(1, 0.19, 1.5)

    def test_opcion_desconocida(self):
        with self.assertRaises(ParametroInvalidoError):
            self.s.servicios[0].calcular_costo(1, color="rojo")


class PruebasReservas(PruebasBase):
    def test_flujo_completo(self):
        self.s.crear_reserva("R1", "C1", "S1", 3, asistentes=8)
        self.s.confirmar_reserva("R1")
        self.assertEqual(self.s.procesar_reserva("R1"), 214_200.00)
        self.assertIs(self.s.reservas[0].estado, EstadoReserva.PROCESADA)

    def test_servicio_no_disponible(self):
        self.s.servicios[1].marcar_disponible(False)
        with self.assertRaises(ServicioNoDisponibleError):
            self.s.crear_reserva("R2", "C1", "E1", 2)

    def test_cancelar_dos_veces(self):
        self.s.crear_reserva("R3", "C1", "S1", 1)
        self.s.cancelar_reserva("R3")
        with self.assertRaises(OperacionNoPermitidaError):
            self.s.cancelar_reserva("R3")

    def test_encadenamiento_de_excepciones(self):
        self.s.crear_reserva("R4", "C1", "S1", 1, descuento=1.5)
        self.s.confirmar_reserva("R4")
        with self.assertRaises(ReservaInvalidaError) as ctx:
            self.s.procesar_reserva("R4")
        self.assertIsInstance(ctx.exception.__cause__, CalculoInconsistenteError)


class PruebasEstabilidadYLog(PruebasBase):
    def test_ejecutar_no_detiene_el_sistema(self):
        r1 = self.s.ejecutar("error controlado", self.s.confirmar_reserva, "NO-EXISTE")
        r2 = self.s.ejecutar("error inesperado", lambda: 1 / 0)
        r3 = self.s.ejecutar("operación válida", self.s.crear_reserva, "R5", "C1", "S1", 1)
        self.assertFalse(r1.exito)
        self.assertFalse(r2.exito)
        self.assertTrue(r3.exito)

    def test_errores_quedan_en_el_log(self):
        self.s.ejecutar("fallo de prueba", self.s.confirmar_reserva, "NO-EXISTE")
        self.s.ejecutar("fallo inesperado", lambda: 1 / 0)
        texto = self.ruta_log.read_text(encoding="utf-8")
        self.assertIn("fallo de prueba | FALLÓ", texto)
        self.assertIn("CRITICAL", texto)
        self.assertIn("ZeroDivisionError", texto)

    def test_todo_error_propio_hereda_de_base(self):
        for exc in (ClienteInvalidoError, ReservaInvalidaError, CalculoInconsistenteError):
            self.assertTrue(issubclass(exc, ErrorSoftwareFJ))


if __name__ == "__main__":
    unittest.main()
