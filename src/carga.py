"""
carga.py - Módulo de Carga del proceso ETL

Este archivo contiene la clase Carga, encargada de insertar los
DataFrames transformados en una base de datos SQLite y exportar
los resultados a archivos Excel (.xlsx).

Autor: [Nombres del grupo]
Fecha: Octubre 2026
"""

import sqlite3
import pandas as pd
import os
from src.logger_config import get_logger

logger = get_logger(__name__)


class Carga:
    """
    Clase encargada de la fase de Carga del proceso ETL.

    Responsabilidades:
        - Insertar los datos transformados en una base de datos SQLite.
        - Exportar los datos transformados a archivos Excel (.xlsx).
        - Verificar que los registros se hayan cargado correctamente.
        - Registrar en los logs los eventos principales del proceso.

    Atributos:
        db_path (str): Ruta del archivo de base de datos SQLite.
        export_dir (str): Directorio donde se guardarán los archivos Excel.
        conn: Objeto de conexión a la base de datos SQLite.
    """

    def __init__(self, db_path, export_dir):
        """
        Inicializa la clase con las rutas de destino.

        Args:
            db_path (str): Ruta completa del archivo SQLite a crear/usar.
            export_dir (str): Directorio donde se exportarán los archivos Excel.
        """
        self.db_path = db_path
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)
        self.conn = None

    def conectar(self):
        """
        Establece conexión con la base de datos SQLite.

        Si el archivo .db no existe, SQLite lo crea automáticamente.

        Raises:
            Exception: Si no se puede establecer la conexión.
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            logger.info(f"Conectado a SQLite en: {self.db_path}")
        except Exception as e:
            logger.error(f"Error al conectar con SQLite: {e}")
            raise

    def cargar_a_sqlite(self, nombre_tabla, df):
        """
        Inserta los datos del DataFrame en una tabla de SQLite.

        Utiliza el método to_sql de pandas con if_exists='replace'
        para reemplazar la tabla si ya existe, garantizando que los
        datos siempre estén actualizados.

        Después de la inserción, se realiza una verificación contando
        los registros en la tabla para confirmar que la carga fue correcta.

        Args:
            nombre_tabla (str): Nombre de la tabla destino en SQLite.
            df (pd.DataFrame): DataFrame con los datos a insertar.
        """
        try:
            if not df.empty:
                df.to_sql(nombre_tabla, self.conn, if_exists='replace', index=False)
                logger.info(f"Tabla '{nombre_tabla}' cargada en SQLite. "
                            f"Registros insertados: {len(df)}")

                # Verificación de carga: contamos los registros en la tabla
                cursor = self.conn.execute(f"SELECT COUNT(*) FROM {nombre_tabla}")
                count = cursor.fetchone()[0]
                if count == len(df):
                    logger.info(f"Verificación exitosa: la tabla '{nombre_tabla}' "
                                f"tiene {count} registros (coincide con el DataFrame).")
                else:
                    logger.warning(f"Verificación de '{nombre_tabla}': se esperaban "
                                   f"{len(df)} registros pero se encontraron {count}.")
        except Exception as e:
            logger.error(f"Error al cargar en SQLite la tabla '{nombre_tabla}': {e}")

    def exportar_a_excel(self, nombre_archivo, df):
        """
        Exporta un DataFrame a un archivo Excel (.xlsx).

        Si el DataFrame tiene más de 1,048,500 registros (límite de Excel),
        se exporta únicamente el primer millón de filas y se registra
        una advertencia en el log.

        Args:
            nombre_archivo (str): Nombre del archivo Excel de salida.
            df (pd.DataFrame): DataFrame con los datos a exportar.
        """
        path = os.path.join(self.export_dir, nombre_archivo)
        try:
            if not df.empty:
                df_export = df
                # Excel tiene un límite de 1,048,576 filas por hoja
                if len(df) > 1048500:
                    logger.warning(f"'{nombre_archivo}' tiene {len(df)} registros y "
                                   f"supera el límite de Excel (1,048,576). "
                                   f"Se exportará una muestra de 1,000,000 registros.")
                    df_export = df.head(1000000)
                df_export.to_excel(path, index=False, engine='openpyxl')
                logger.info(f"Datos exportados a Excel exitosamente en: {path} "
                            f"({len(df_export)} registros)")
        except Exception as e:
            logger.error(f"Error al exportar a Excel '{nombre_archivo}': {e}")

    def cerrar_conexion(self):
        """
        Cierra la conexión con la base de datos SQLite.

        Es importante cerrar la conexión al finalizar la carga
        para liberar los recursos y asegurar que los datos se
        escriban correctamente en el archivo .db.
        """
        if self.conn:
            self.conn.close()
            logger.info("Conexión a SQLite cerrada exitosamente.")
