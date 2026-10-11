"""
main.py - Script principal (orquestador) del proceso ETL

Este archivo coordina la ejecución secuencial de las tres fases
del proceso ETL:
    1. Extracción: Conexión a MongoDB y carga de colecciones.
    2. Transformación: Limpieza, normalización y derivación de datos.
    3. Carga: Inserción en SQLite y exportación a Excel.

Para ejecutar el proceso completo:
    python src/main.py

Autor: [Nombres del grupo]
Fecha: Octubre 2026
"""

import os
import sys

# Agregar la raíz del proyecto al path para que Python
# encuentre correctamente el paquete 'src'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.extraccion import Extraccion
from src.transformacion import Transformacion
from src.carga import Carga
from src.logger_config import get_logger

logger = get_logger(__name__)


def main():
    """
    Función principal que orquesta todo el proceso ETL.

    Flujo de ejecución:
        1. Se conecta a MongoDB y extrae las 3 colecciones.
        2. Se aplican las transformaciones definidas en la clase Transformacion.
        3. Se cargan los datos limpios en SQLite y se exportan a Excel.
        4. Se registra cada paso en el sistema de logs.
    """
    logger.info("=" * 60)
    logger.info("INICIANDO PROCESO ETL - AIRBNB BOGOTÁ")
    logger.info("=" * 60)

    # =========================================================
    # FASE 1: EXTRACCIÓN
    # Conexión a MongoDB y carga de colecciones en DataFrames
    # =========================================================
    extraccion = Extraccion(db_name='airbnb_bogota')
    try:
        extraccion.conectar()
        df_listings = extraccion.extraer_coleccion('listings')
        df_reviews = extraccion.extraer_coleccion('reviews')
        df_calendar = extraccion.extraer_coleccion('calendar')
    finally:
        extraccion.cerrar_conexion()

    # Validamos que se hayan extraído datos
    if df_listings.empty and df_reviews.empty and df_calendar.empty:
        logger.error("No se extrajeron datos. Verifica que MongoDB esté corriendo "
                      "y que la BD 'airbnb_bogota' tenga las colecciones cargadas.")
        return

    # =========================================================
    # FASE 2: TRANSFORMACIÓN
    # Limpieza, normalización y derivación de variables
    # =========================================================
    transformador = Transformacion(df_listings, df_reviews, df_calendar)
    df_list_clean, df_rev_clean, df_cal_clean = transformador.ejecutar_transformaciones()

    # =========================================================
    # FASE 3: CARGA
    # Inserción en SQLite y exportación a Excel
    # =========================================================
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'airbnb_analitica.db')
    export_dir = os.path.join(base_dir, 'data')

    carga = Carga(db_path, export_dir)
    try:
        carga.conectar()

        # Cargar cada colección transformada a SQLite y exportar a Excel
        carga.cargar_a_sqlite('listings', df_list_clean)
        carga.exportar_a_excel('listings_transformado.xlsx', df_list_clean)

        carga.cargar_a_sqlite('reviews', df_rev_clean)
        carga.exportar_a_excel('reviews_transformado.xlsx', df_rev_clean)

        carga.cargar_a_sqlite('calendar', df_cal_clean)
        carga.exportar_a_excel('calendar_transformado.xlsx', df_cal_clean)
    finally:
        carga.cerrar_conexion()

    logger.info("=" * 60)
    logger.info("PROCESO ETL FINALIZADO CON ÉXITO")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
