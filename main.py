"""Simulación de Software FJ: 29 operaciones válidas e inválidas.

Ejecutar:  python main.py
Genera el archivo logs/software_fj.log con todos los eventos y errores.
"""
from pathlib import Path

from software_fj import (AlquilerEquipo, AsesoriaEspecializada, SalaReserva,
                         SistemaGestion, configurar_logging)

RUTA_LOG = Path(__file__).parent / "logs" / "software_fj.log"


def main():
    configurar_logging(RUTA_LOG, sobrescribir=True)  # log limpio en cada corrida
    s = SistemaGestion()
    resultados = []

    def op(descripcion, funcion, *args, **kwargs):
        """Ejecuta una operación, guarda y muestra su resultado."""
        r = s.ejecutar(descripcion, funcion, *args, **kwargs)
        resultados.append(r)
        marca = "[OK]   " if r.exito else "[ERROR]"
        extra = f" -> {r.error}" if not r.exito else ""
        print(f"{len(resultados):02d} {marca} {descripcion}{extra}")
        return r

    print("=== Software FJ: simulación de operaciones ===\n")

    # ---- Clientes (válidos e inválidos) ----
    op("Registrar cliente válido (Ana Gómez)", s.registrar_cliente,
       "CLI-001", "ana gómez", "1012345678", "ana@correo.com", "3001234567")
    op("Registrar cliente válido (Carlos Ruiz)", s.registrar_cliente,
       "CLI-002", "Carlos Ruiz", "79876543", "carlos.ruiz@empresa.co", "3109876543")
    op("Registrar cliente con correo inválido", s.registrar_cliente,
       "CLI-003", "Luis Pérez", "1098765432", "luis-correo", "3201112233")
    op("Registrar cliente con documento duplicado", s.registrar_cliente,
       "CLI-004", "Ana María", "1012345678", "ana2@correo.com", "3004445566")
    op("Registrar cliente sin nombre (parámetro faltante)", s.registrar_cliente,
       "CLI-005", None, "1055566677", "sin.nombre@correo.com", "3007778899")

    # ---- Servicios (válidos e inválidos) ----
    sala = SalaReserva("SAL-01", "Sala Innovación", 50_000, capacidad=10, proyector=True)
    equipo = AlquilerEquipo("EQ-01", "Portátiles Pro", 20_000, "Portátil", 5)
    asesoria = AsesoriaEspecializada("ASE-01", "Asesoría en Python", 80_000,
                                     "Programación", "senior")
    op("Registrar servicio: sala con proyector", s.registrar_servicio, sala)
    op("Registrar servicio: alquiler de equipos", s.registrar_servicio, equipo)
    op("Registrar servicio: asesoría senior", s.registrar_servicio, asesoria)
    op("Crear servicio con tarifa negativa", lambda: s.registrar_servicio(
        SalaReserva("SAL-02", "Sala Error", -100, capacidad=4)))

    # ---- Reservas ----
    op("Reserva válida de sala (Ana, 3 h, 8 asistentes)", s.crear_reserva,
       "RES-001", "CLI-001", "SAL-01", 3, asistentes=8)
    op("Confirmar reserva RES-001", s.confirmar_reserva, "RES-001")
    r = op("Procesar reserva RES-001 (IVA 19 %)", s.procesar_reserva, "RES-001")
    print(f"      costo total: ${r.valor:,.2f}")

    op("Reserva de equipos con descuento del 10 % (Carlos, 24 h, 2 unidades)",
       s.crear_reserva, "RES-002", "CLI-002", "EQ-01", 24, unidades=2, descuento=0.10)
    op("Confirmar reserva RES-002", s.confirmar_reserva, "RES-002")
    r = op("Procesar reserva RES-002", s.procesar_reserva, "RES-002")
    print(f"      costo total: ${r.valor:,.2f}")

    op("Reserva inválida: asistentes superan la capacidad", s.crear_reserva,
       "RES-003", "CLI-001", "SAL-01", 2, asistentes=25)
    op("Reserva inválida: duración de 0 horas", s.crear_reserva,
       "RES-004", "CLI-002", "ASE-01", 0)
    op("Reserva con cliente inexistente", s.crear_reserva,
       "RES-005", "CLI-999", "SAL-01", 2)
    op("Reserva con parámetro faltante (sin id de servicio)", s.crear_reserva,
       "RES-006", "CLI-001", None, 2)

    equipo.marcar_disponible(False)  # el servicio deja de estar disponible
    op("Reserva de servicio no disponible (equipos)", s.crear_reserva,
       "RES-007", "CLI-001", "EQ-01", 5)
    equipo.marcar_disponible(True)

    op("Reserva de asesoría presencial (Ana, 2 h)", s.crear_reserva,
       "RES-008", "CLI-001", "ASE-01", 2, modalidad="presencial")
    op("Cancelar reserva RES-008", s.cancelar_reserva, "RES-008", "Cambio de agenda")
    op("Cancelar de nuevo RES-008 (operación no permitida)", s.cancelar_reserva, "RES-008")
    op("Procesar RES-008 cancelada (operación no permitida)", s.procesar_reserva, "RES-008")

    # ---- Error de cálculo con encadenamiento de excepciones ----
    op("Reserva con descuento del 150 % (se detecta al procesar)", s.crear_reserva,
       "RES-009", "CLI-002", "SAL-01", 1, descuento=1.5)
    op("Confirmar RES-009", s.confirmar_reserva, "RES-009")
    op("Procesar RES-009 (error encadenado)", s.procesar_reserva, "RES-009")

    # ---- Error inesperado: el sistema sigue funcionando ----
    op("Operación con error inesperado (división por cero)", lambda: 10 / 0)
    op("Reserva final tras los errores (Carlos, asesoría virtual 1 h)", s.crear_reserva,
       "RES-010", "CLI-002", "ASE-01", 1)

    # ---- Resumen ----
    ok = sum(1 for x in resultados if x.exito)
    print("\n=== Resumen ===")
    print(f"Operaciones: {len(resultados)} | exitosas: {ok} | con error controlado: {len(resultados) - ok}")
    print(f"Estado del sistema: {s.resumen()}")
    print("\nReservas registradas:")
    for reserva in s.reservas:
        print(" -", reserva)
    print(f"\nEl sistema siguió estable. Log completo en: logs/software_fj.log")


if __name__ == "__main__":
    main()
