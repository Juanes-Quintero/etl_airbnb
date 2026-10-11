"""
logger_config.py - Módulo centralizado de manejo de Logs

Este módulo configura el sistema de logging para todo el proceso ETL.
Genera un archivo de log por cada ejecución con el formato:
    logs/log_YYYYMMDD_HHMM.txt

Cada mensaje de log incluye:
    - Fecha y hora del evento
    - Nombre del módulo que lo generó
    - Nivel del mensaje (INFO, WARNING, ERROR)
    - Descripción clara del evento

Autor: [Nombres del grupo]
Fecha: Octubre 2026
"""

import logging
import os
from datetime import datetime


def get_logger(module_name):
    """
    Crea y configura un logger reutilizable para cualquier módulo del proyecto.

    El logger escribe los mensajes tanto en un archivo de texto (dentro
    de la carpeta logs/) como en la consola, para que el usuario pueda
    ver el progreso en tiempo real.

    Args:
        module_name (str): Nombre del módulo que solicita el logger.
                           Generalmente se pasa __name__.

    Returns:
        logging.Logger: Instancia del logger configurada y lista para usar.
    """
    # Directorio de logs en la raíz del proyecto
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Nombre del archivo con formato: log_YYYYMMDD_HHMM.txt
    current_time = datetime.now().strftime("%Y%m%d_%H%M")
    log_file = os.path.join(log_dir, f"log_{current_time}.txt")

    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)

    # Evitar duplicar handlers si el logger ya fue configurado
    if not logger.handlers:
        # Formato del mensaje: fecha - módulo - nivel - mensaje
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Handler para archivo de texto
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)

        # Handler para consola (muestra los mensajes en pantalla)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger
