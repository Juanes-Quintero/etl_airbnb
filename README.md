# ETL Airbnb Bogotá

Este proyecto implementa un proceso ETL (Extracción, Transformación y Carga) automatizado en Python para los datasets de Airbnb de Bogotá, Distrito Capital, Colombia. 

## Objetivo
Aplicar conceptos de Extracción, Transformación y Carga (ETL) sobre los datasets de Airbnb (`listings`, `reviews` y `calendar`) almacenados en una base de datos MongoDB local, preparándolos para su posterior análisis en Inteligencia de Negocios. El proyecto incluye análisis exploratorio (EDA), limpieza de datos, manejo centralizado de logs, y carga final a SQLite y Excel.

## Integrantes del Grupo y Responsabilidades
* **[Juan Esteban Quintero Acosta / 1000763396]** - Responsabilidad: Desarrollé el ejercicio de manera individual 
*
## Estructura del Repositorio
```text
etl_airbnb/
│
├── src/
│   ├── extraccion.py       # Conexión y extracción desde MongoDB (Documentado)
│   ├── transformacion.py   # Limpieza, normalización y derivación de campos (Documentado)
│   ├── carga.py            # Carga a SQLite, validación y exportación a XLSX (Documentado)
│   ├── main.py             # Script orquestador del ETL
│   └── logger_config.py    # Configuración centralizada de logs
├── notebooks/
│   └── exploracion_airbnb.ipynb  # Jupyter Notebook con el EDA completo (Correlaciones, Agrupaciones)
├── logs/                   # Carpeta donde se generan automáticamente los archivos de log
├── data/                   # Carpeta de salida para SQLite DB y Excel .xlsx
├── README.md               # Este archivo
└── requirements.txt        # Dependencias del proyecto
```

## Instrucciones de Instalación y Ejecución

### 1. Preparación de la Base de Datos (MongoDB)
Para que el proyecto funcione, debes tener instalado **MongoDB** ejecutándose localmente (puerto 27017).
Deberás importar los datasets fuente (`listings.csv`, `reviews.csv`, `calendar.csv`) en una base de datos llamada `airbnb_bogota`. 
Ejemplo usando `mongoimport` desde la terminal:
```bash
mongoimport --db airbnb_bogota --collection listings --type csv --headerline --file listings.csv
mongoimport --db airbnb_bogota --collection reviews --type csv --headerline --file reviews.csv
mongoimport --db airbnb_bogota --collection calendar --type csv --headerline --file calendar.csv
```

### 2. Creación del entorno virtual e instalación de dependencias
Abre una terminal en la raíz del proyecto y ejecuta los siguientes comandos para crear un entorno aislado e instalar las librerías necesarias:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

*Nota: Si estás en Windows y las políticas de seguridad (App Control) bloquean el entorno virtual, puedes saltarte el paso del `venv` e instalar los requerimientos directamente en tu Python global con `pip install -r requirements.txt`.*

### 3. Ejecución del Proceso ETL
Para ejecutar de forma automatizada todo el pipeline (Extracción, Transformación y Carga), ejecuta el orquestador:
```bash
python src/main.py
```

### 4. Ejemplo de Ejecución (Salida de Logs)
El sistema registrará todo el proceso en la consola y generará un archivo en la carpeta `logs/`. Verás un flujo similar a este:
```text
[INFO] === INICIANDO PROCESO ETL - AIRBNB BOGOTÁ ===
[INFO] Conexión exitosa a MongoDB en localhost:27017, BD: airbnb_bogota
[INFO] Colección 'listings' extraída exitosamente. Registros encontrados: 19187
[INFO] Iniciando limpieza de nulos y duplicados.
[INFO] Precios categorizados en Listings: Económico, Medio, Alto.
[INFO] Tabla 'listings' cargada en SQLite. Registros insertados: 19187
[INFO] Verificación exitosa: la tabla 'listings' tiene 19187 registros (coincide con el DataFrame).
[INFO] PROCESO ETL FINALIZADO CON ÉXITO
```
