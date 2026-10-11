"""
transformacion.py - Módulo de Transformación del proceso ETL

Este archivo contiene la clase Transformacion, encargada de limpiar,
normalizar y preparar los DataFrames extraídos de MongoDB para su
posterior carga en la base de datos analítica (SQLite) y exportación
a archivos Excel.

Las transformaciones aplicadas se basan en los hallazgos del Análisis
Exploratorio de Datos (EDA) documentado en el notebook
'exploracion_airbnb.ipynb'.

Autor: [Nombres del grupo]
Fecha: Octubre 2026
"""

import pandas as pd
from src.logger_config import get_logger

logger = get_logger(__name__)


class Transformacion:
    """
    Clase encargada de la fase de Transformación del proceso ETL.

    Responsabilidades:
        - Limpieza de valores nulos y registros duplicados.
        - Normalización de precios (eliminar símbolos $ y comas, convertir a numérico).
        - Conversión de fechas a formato estándar YYYY-MM-DD.
        - Derivación de variables temporales (año, mes, día, trimestre).
        - Categorización de precios por rangos (Económico, Medio, Alto).
        - Expansión o tratamiento de campos anidados (amenities).
        - Limpieza de caracteres Unicode no válidos (surrogates/emojis corruptos).
        - Generación de DataFrames limpios y listos para la carga.

    Atributos:
        df_listings (pd.DataFrame): Copia del DataFrame de listings para transformar.
        df_reviews (pd.DataFrame): Copia del DataFrame de reviews para transformar.
        df_calendar (pd.DataFrame): Copia del DataFrame de calendar para transformar.
    """

    def __init__(self, df_listings, df_reviews, df_calendar):
        """
        Inicializa la clase con copias de los DataFrames originales.

        Se trabaja sobre copias para no modificar los datos originales,
        lo cual es una buena práctica en procesos ETL.

        Args:
            df_listings (pd.DataFrame): DataFrame con los datos de listings.
            df_reviews (pd.DataFrame): DataFrame con los datos de reviews.
            df_calendar (pd.DataFrame): DataFrame con los datos de calendar.
        """
        self.df_listings = df_listings.copy()
        self.df_reviews = df_reviews.copy()
        self.df_calendar = df_calendar.copy()

    def limpiar_nulos_duplicados(self):
        """
        Elimina registros duplicados en las tres colecciones.

        Justificación (basada en el EDA):
            En el análisis exploratorio se detectó la presencia de registros
            duplicados en las colecciones, lo cual puede sesgar los resultados
            analíticos. Se aplica drop_duplicates() para garantizar la unicidad
            de los registros.

        Se registra en el log la cantidad de registros antes y después
        de la limpieza para cada colección.
        """
        logger.info("Iniciando limpieza de nulos y duplicados.")
        datasets = {
            "Listings": self.df_listings,
            "Reviews": self.df_reviews,
            "Calendar": self.df_calendar
        }
        for name, df in datasets.items():
            if not df.empty:
                inicial = len(df)
                df.drop_duplicates(inplace=True)
                eliminados = inicial - len(df)
                logger.info(f"[{name}] Registros iniciales: {inicial}, "
                            f"finales: {len(df)}, duplicados eliminados: {eliminados}")

    def normalizar_precios(self):
        """
        Normaliza los campos de precio eliminando símbolos y convirtiendo a numérico.

        Justificación (basada en el EDA):
            Los campos 'price' y 'adjusted_price' vienen como texto con
            el formato '$1,234.00'. Para poder hacer cálculos matemáticos
            (promedios, rangos, etc.) es necesario:
            1. Eliminar el símbolo de dólar ($)
            2. Eliminar las comas separadoras de miles (,)
            3. Convertir el texto resultante a un valor numérico (float)

        Se aplica tanto a Listings como a Calendar.
        """
        logger.info("Normalizando campos de precio (eliminando '$' y ',' y convirtiendo a numérico)...")

        # Normalización en Listings
        if not self.df_listings.empty and 'price' in self.df_listings.columns:
            self.df_listings['price'] = (self.df_listings['price']
                                         .astype(str)
                                         .str.replace(r'[\$,]', '', regex=True))
            self.df_listings['price'] = pd.to_numeric(self.df_listings['price'], errors='coerce')
            logger.info("Precios normalizados en Listings.")

        # Normalización en Calendar (price y adjusted_price)
        if not self.df_calendar.empty:
            for col in ['price', 'adjusted_price']:
                if col in self.df_calendar.columns:
                    self.df_calendar[col] = (self.df_calendar[col]
                                              .astype(str)
                                              .str.replace(r'[\$,]', '', regex=True))
                    self.df_calendar[col] = pd.to_numeric(self.df_calendar[col], errors='coerce')
            logger.info("Precios normalizados en Calendar (price y adjusted_price).")

    def convertir_fechas_y_derivar(self):
        """
        Convierte campos de fecha a formato estándar YYYY-MM-DD y
        deriva nuevas variables temporales.

        Justificación (basada en el EDA):
            Las fechas originales vienen como texto sin formato estándar.
            Se necesita convertirlas a tipo datetime para poder:
            1. Ordenar cronológicamente los datos.
            2. Extraer componentes temporales útiles para análisis de
               estacionalidad y tendencias.

        Variables derivadas en Calendar:
            - year: Año de la fecha.
            - month: Mes de la fecha (1-12).
            - day: Día del mes (1-31).
            - quarter: Trimestre del año (1-4).

        Se aplica también la conversión de fechas en Reviews.
        """
        logger.info("Convirtiendo fechas a formato YYYY-MM-DD y derivando variables temporales...")

        # Calendar: Conversión y derivación de variables
        if not self.df_calendar.empty and 'date' in self.df_calendar.columns:
            self.df_calendar['date'] = pd.to_datetime(self.df_calendar['date'], errors='coerce')
            self.df_calendar['year'] = self.df_calendar['date'].dt.year
            self.df_calendar['month'] = self.df_calendar['date'].dt.month
            self.df_calendar['day'] = self.df_calendar['date'].dt.day
            self.df_calendar['quarter'] = self.df_calendar['date'].dt.quarter
            self.df_calendar['date'] = self.df_calendar['date'].dt.strftime('%Y-%m-%d')
            logger.info("Fechas convertidas y variables derivadas en Calendar (year, month, day, quarter).")

        # Reviews: Solo conversión de formato
        if not self.df_reviews.empty and 'date' in self.df_reviews.columns:
            self.df_reviews['date'] = pd.to_datetime(
                self.df_reviews['date'], errors='coerce'
            ).dt.strftime('%Y-%m-%d')
            logger.info("Fechas convertidas en Reviews.")

    def categorizar_precios(self):
        """
        Categoriza los precios de los listings en rangos definidos.

        Justificación (basada en el EDA):
            En el análisis de outliers se detectaron valores extremos
            en la variable 'price'. Para facilitar el análisis de
            Inteligencia de Negocios, se crean categorías que agrupan
            los alojamientos según su nivel de precio:
            - Económico: $0 a $150,000
            - Medio: $150,001 a $350,000
            - Alto: Mayor a $350,000

        Se crea una nueva columna llamada 'price_category' en Listings.
        """
        if not self.df_listings.empty and 'price' in self.df_listings.columns:
            bins = [-1, 150000, 350000, float('inf')]
            labels = ['Económico', 'Medio', 'Alto']
            self.df_listings['price_category'] = pd.cut(
                self.df_listings['price'], bins=bins, labels=labels
            )
            logger.info("Precios categorizados en Listings: Económico, Medio, Alto.")

    def expandir_anidados(self):
        """
        Expande y limpia los campos anidados de la colección Listings.

        Justificación (basada en el EDA):
            La columna 'amenities' contiene listas de servicios en formato
            de texto (ej: '["Wifi", "Kitchen", "Pool"]'). Para facilitar
            su lectura y análisis, se convierten en cadenas de texto
            separadas por comas (ej: 'Wifi, Kitchen, Pool').
        """
        if not self.df_listings.empty and 'amenities' in self.df_listings.columns:
            self.df_listings['amenities'] = self.df_listings['amenities'].apply(
                lambda x: ', '.join(eval(x)) if isinstance(x, str) and x.startswith('[') else x
            )
            logger.info("Campo 'amenities' expandido en Listings (listas convertidas a texto).")

    def limpiar_surrogates(self):
        """
        Elimina caracteres Unicode no válidos (surrogates) de las columnas de texto.

        Justificación:
            Algunos registros de Listings contienen emojis o caracteres
            especiales mal codificados que impiden la exportación a
            SQLite y Excel. Se limpian codificando y decodificando
            en UTF-8 con la opción 'ignore' para descartar los
            caracteres problemáticos.
        """
        logger.info("Limpiando caracteres Unicode no válidos (surrogates) en Listings...")
        if not self.df_listings.empty:
            for col in self.df_listings.select_dtypes(include=['object']).columns:
                self.df_listings[col] = self.df_listings[col].apply(
                    lambda x: x.encode('utf-8', 'ignore').decode('utf-8') if isinstance(x, str) else x
                )
            logger.info("Caracteres no válidos eliminados exitosamente.")

    def ejecutar_transformaciones(self):
        """
        Ejecuta todas las transformaciones en orden secuencial.

        Orden de ejecución:
            1. Limpieza de duplicados
            2. Normalización de precios
            3. Conversión de fechas y derivación de variables
            4. Categorización de precios
            5. Expansión de campos anidados
            6. Limpieza de caracteres corruptos

        Returns:
            tuple: Tres DataFrames transformados (listings, reviews, calendar).

        Raises:
            Exception: Si ocurre un error durante alguna transformación.
        """
        logger.info("=" * 60)
        logger.info("INICIANDO PROCESO DE TRANSFORMACIÓN")
        logger.info("=" * 60)
        try:
            self.limpiar_nulos_duplicados()
            self.normalizar_precios()
            self.convertir_fechas_y_derivar()
            self.categorizar_precios()
            self.expandir_anidados()
            self.limpiar_surrogates()
            logger.info("=" * 60)
            logger.info("TRANSFORMACIÓN COMPLETADA CON ÉXITO")
            logger.info("=" * 60)
            return self.df_listings, self.df_reviews, self.df_calendar
        except Exception as e:
            logger.error(f"Error durante las transformaciones: {e}")
            raise
