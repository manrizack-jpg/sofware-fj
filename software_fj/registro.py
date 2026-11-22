"""Configuración del archivo de logs (eventos y errores).

El sistema no usa base de datos: el único archivo que se escribe es el log.
"""
import logging
from pathlib import Path

NOMBRE_LOGGER = "software_fj"
FORMATO = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def configurar_logging(ruta_log="logs/software_fj.log", *, nivel=logging.DEBUG,
                       consola=False, sobrescribir=False):
    """Crea (o reconfigura) el logger principal y devuelve su ruta.

    ruta_log:     archivo donde se escriben los eventos.
    sobrescribir: True borra el contenido anterior; False agrega al final.
    consola:      True muestra además los logs por pantalla.
    """
    ruta = Path(ruta_log)
    ruta.parent.mkdir(parents=True, exist_ok=True)  # crea la carpeta logs/

    logger = logging.getLogger(NOMBRE_LOGGER)
    logger.setLevel(nivel)
    logger.propagate = False

    # Se cierran y quitan los manejadores previos para no duplicar líneas
    for manejador in list(logger.handlers):
        manejador.close()
        logger.removeHandler(manejador)

    formato = logging.Formatter(FORMATO)
    archivo = logging.FileHandler(ruta, mode="w" if sobrescribir else "a",
                                  encoding="utf-8")
    archivo.setFormatter(formato)
    logger.addHandler(archivo)

    if consola:
        pantalla = logging.StreamHandler()
        pantalla.setFormatter(formato)
        logger.addHandler(pantalla)
    return ruta


def obtener_logger(nombre):
    """Devuelve un logger hijo (software_fj.<nombre>)."""
    return logging.getLogger(f"{NOMBRE_LOGGER}.{nombre}")
