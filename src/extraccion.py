"""
extraccion.py - Módulo de Extracción del proceso ETL

Este archivo contiene la clase Extraccion, encargada de conectarse a la
base de datos MongoDB local y extraer las colecciones de Airbnb (Listings,
Reviews y Calendar) en DataFrames de pandas para su posterior análisis
y transformación.

Autor: [Nombres del grupo]
Fecha: Octubre 2026
"""

import pandas as pd
from pymongo import MongoClient
from src.logger_config import get_logger

logger = get_logger(__name__)


class Extraccion:
    """
    Clase encargada de la fase de Extracción del proceso ETL.

    Responsabilidades:
        - Establecer conexión con la base de datos MongoDB local.
        - Consultar cada colección (listings, reviews, calendar).
        - Cargar los datos en DataFrames de pandas.
        - Registrar en el log la conexión realizada y la cantidad de
          registros extraídos por colección.

    Atributos:
        host (str): Dirección del servidor MongoDB (por defecto 'localhost').
        port (int): Puerto de conexión a MongoDB (por defecto 27017).
        db_name (str): Nombre de la base de datos a consultar.
        client: Instancia del cliente de conexión a MongoDB.
        db: Referencia a la base de datos seleccionada.
    """

    def __init__(self, host='localhost', port=27017, db_name='airbnb_bogota'):
        """
        Inicializa los parámetros de conexión a MongoDB.

        Args:
            host (str): Dirección del servidor. Por defecto 'localhost'.
            port (int): Puerto del servidor. Por defecto 27017.
            db_name (str): Nombre de la base de datos. Por defecto 'airbnb_bogota'.
        """
        self.host = host
        self.port = port
        self.db_name = db_name
        self.client = None
        self.db = None

    def conectar(self):
        """
        Establece la conexión con MongoDB.

        Crea una instancia de MongoClient y selecciona la base de datos
        indicada en el atributo db_name. Registra en el log si la conexión
        fue exitosa o si ocurrió un error.

        Raises:
            Exception: Si no se puede establecer la conexión.
        """
        try:
            self.client = MongoClient(self.host, self.port)
            self.db = self.client[self.db_name]
            # Verificamos que la conexión esté activa consultando el servidor
            self.client.server_info()
            logger.info(f"Conexión exitosa a MongoDB en {self.host}:{self.port}, BD: {self.db_name}")
        except Exception as e:
            logger.error(f"Error al conectar a MongoDB: {e}")
            raise

    def extraer_coleccion(self, nombre_coleccion):
        """
        Consulta una colección específica de MongoDB y la carga en un DataFrame.

        Convierte todos los documentos de la colección en una lista de
        diccionarios y luego en un DataFrame de pandas. El campo '_id'
        (ObjectId de MongoDB) se convierte a string para evitar problemas
        de compatibilidad en las etapas posteriores.

        Args:
            nombre_coleccion (str): Nombre de la colección a extraer
                                     (ej. 'listings', 'reviews', 'calendar').

        Returns:
            pd.DataFrame: DataFrame con los datos de la colección.
                          Retorna un DataFrame vacío si ocurre un error.
        """
        try:
            coleccion = self.db[nombre_coleccion]
            # Extraemos todos los documentos del cursor y los convertimos a lista
            datos = list(coleccion.find())
            df = pd.DataFrame(datos)

            # Convertimos el ObjectId de MongoDB a string para compatibilidad
            if '_id' in df.columns:
                df['_id'] = df['_id'].astype(str)

            logger.info(f"Colección '{nombre_coleccion}' extraída exitosamente. "
                        f"Registros encontrados: {len(df)}, Columnas: {len(df.columns)}")
            return df
        except Exception as e:
            logger.error(f"Error al extraer la colección '{nombre_coleccion}': {e}")
            return pd.DataFrame()

    def cerrar_conexion(self):
        """
        Cierra la conexión con MongoDB de forma segura.

        Es importante cerrar la conexión al finalizar la extracción
        para liberar los recursos del servidor.
        """
        if self.client:
            self.client.close()
            logger.info("Conexión a MongoDB cerrada exitosamente.")
