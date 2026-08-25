# Guía Detallada de Ejecución: Fases 1 a 3
**Proyecto:** Patrones De Movimiento Intermunicipal En Colombia: Clave Para La Rentabilidad, Eficiencia Energética Y Reducción De Emisiones.
**Fuente de Datos:** `https://www.datos.gov.co/resource/eh75-8ah6.csv`

Esta guía detalla el **Qué** (objetivo) y el **Cómo** (herramientas y scripts sugeridos) para ejecutar las tres primeras fases de tu proyecto.

---

## Fase 1: Levantamiento, Extracción y Estructuración (ETL)

### ¿Qué hay que hacer?
Debes capturar los datos brutos desde la plataforma de Datos Abiertos del gobierno, limpiarlos, aplicar tus reglas de negocio (filtrar años 2025-2026, buses a diésel de 30-40 puestos) y cargar la información limpia y estructurada en una base de datos relacional para su posterior análisis.

### ¿Cómo hacerlo?

**1. Preparación de la Base de Datos (SQL Server Express)**
Antes de extraer los datos, necesitas donde guardarlos.
*   Abre SQL Server Management Studio (SSMS).
*   Crea una base de datos: `CREATE DATABASE MovilidadIntermunicipal;`
*   Crea la tabla destino con los tipos de datos correctos. Ejemplo:
    ```sql
    CREATE TABLE Despachos (
        id_despacho INT IDENTITY(1,1) PRIMARY KEY,
        fecha_despacho DATE,
        hora_despacho TIME,
        municipio_origen VARCHAR(100),
        municipio_destino VARCHAR(100),
        empresa_transportadora VARCHAR(150),
        clase_vehiculo VARCHAR(50),
        nivel_servicio VARCHAR(50),
        capacidad_pasajeros INT,
        pasajeros_transportados INT
    );
    ```

**2. Proceso ETL con Pentaho Data Integration (Spoon)**
*   **Extracción (Input):** Utiliza el paso `CSV file input` y pega la URL de la API o carga el archivo descargado localmente. Configura el delimitador (usualmente coma `,`).
*   **Transformación (Steps):**
    *   Añade un paso `Filter Rows` para dejar solo: `capacidad_pasajeros >= 30 AND capacidad_pasajeros <= 40`.
    *   Añade otro `Filter Rows` para `combustible = 'Diésel'` (si la columna existe, de lo contrario asume la parametrización según las flotas o metadatos).
    *   Añade un `String operations` o `Replace in string` para limpiar espacios en blanco o normalizar los nombres de los municipios (ej. pasar todo a MAYÚSCULAS).
    *   Usa un `Select Values` para quedarte solo con las columnas pertinentes y renombrarlas si es necesario para que coincidan con tu tabla de SQL Server.
*   **Carga (Output):** Añade un paso `Table output`, configura tu conexión JDBC a SQL Server y mapea los campos transformados hacia la tabla `Despachos`.

---

## Fase 2: Análisis Exploratorio de Datos (EDA) y Diagnóstico

### ¿Qué hay que hacer?
Conectarte a la base de datos limpia y realizar estadística descriptiva. Tu objetivo principal aquí es demostrar matemáticamente la hipótesis de la **subocupación** y visualizar la "hiperfrecuencia logística" (buses saliendo a la misma hora con pocos pasajeros).

### ¿Cómo hacerlo?

**1. Configuración del Entorno (Python / Jupyter Notebook)**
*   Instala las librerías necesarias: `pip install pandas numpy matplotlib seaborn pyodbc`
*   Inicia Jupyter Notebook.

**2. Conexión y Carga de Datos (Script sugerido)**
```python
import pandas as pd
import pyodbc
import matplotlib.pyplot as plt
import seaborn as sns

# Conexión a SQL Server
conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                      'Server=TU_SERVIDOR\SQLEXPRESS;'
                      'Database=MovilidadIntermunicipal;'
                      'Trusted_Connection=yes;')

# Carga de datos
df = pd.read_sql("SELECT * FROM Despachos", conn)
```

**3. Creación de Métricas Clave**
Debes crear la variable principal del proyecto: El factor de ocupación.
```python
# Calcular factor de ocupación (porcentaje)
df['factor_ocupacion'] = (df['pasajeros_transportados'] / df['capacidad_pasajeros']) * 100

# Identificar subocupación (Ej: menor al 50%)
df['estado_ocupacion'] = df['factor_ocupacion'].apply(lambda x: 'Subocupado' if x < 50 else 'Óptimo')
```

**4. Visualización del Diagnóstico**
*   **Histograma de Ocupación:** `sns.histplot(df['factor_ocupacion'], bins=20)` te mostrará visualmente hacia dónde se sesgan los despachos (probablemente a la izquierda, indicando subocupación).
*   **Heatmap de Frecuencias:** Agrupa los datos por `hora_despacho` y `dia_semana` para identificar picos de salida de vehículos y cruzarlos con la cantidad promedio de pasajeros en esas mismas franjas.

---

## Fase 3: Modelado Estadístico y Comprensión Ambiental

### ¿Qué hay que hacer?
Traducir la ineficiencia logística (tara o peso muerto viajando vacío) en un impacto ambiental cuantificable (Huella de Carbono / Emisiones de CO2). Además, aplicar estadística en R (o continuar en Python) para ver si la demanda es predecible según variables de tiempo.

### ¿Cómo hacerlo?

**1. Modelado de Huella de Carbono (Matemática)**
Necesitas integrar un Factor de Emisión (FE). Asumiendo un FE hipotético de la UPME (ej. X kg de CO2 por galón de diésel o por kilómetro recorrido para buses de 40 pasajeros).
*   **Cálculo Exacto de Distancias (Opción A - OSRM API):** Para dotar al proyecto de mayor rigor académico y calcular las emisiones con alta precisión, se implementará un modelo programático basado en OpenStreetMap:
    1. **Extracción de Coordenadas:** Se cruzará el código DIVIPOLA de origen y destino con un catálogo gubernamental (dataset público) para extraer la `latitud` y `longitud` exacta de los municipios.
    2. **Pares Únicos:** Se identificarán las rutas únicas (ej. aislar 300 rutas distintas dentro de los 50,000 despachos) para optimizar el consumo de red.
    3. **Consumo OSRM:** Mediante peticiones HTTP a la API pública `http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false`, se obtendrá la distancia real de conducción por carretera en metros (que se convertirá a kilómetros).
    4. **Integración:** El kilometraje devuelto por la API alimentará de forma dinámica la variable `distancia_km` de los despachos analizados.
*   **Cálculo en Python/R:**
    ```python
    # Fórmula conceptual: CO2_Total = Distancia(km) * Factor_Emision_Vehiculo(kg CO2/km)
    # CO2_Por_Pasajero = CO2_Total / Pasajeros_Transportados
    
    fe_bus_diesel = 0.85 # kg CO2 por Km (Valor ejemplo, validar con UPME)
    
    df['emision_total_kg'] = df['distancia_km'] * fe_bus_diesel
    df['emision_por_pasajero_kg'] = df['emision_total_kg'] / df['pasajeros_transportados']
    ```
    *Aquí demostrarás que un bus subocupado dispara alarmantemente la emisión per cápita (por pasajero).*

**2. Estudio Estadístico de Temporalidad (RStudio)**
Si decides usar R como dice la propuesta para el modelado estadístico:
*   Exporta un subset limpio desde SQL Server o desde el mismo Python a un nuevo CSV.
*   En RStudio, importa los datos y usa regresiones o análisis de varianza (ANOVA).
    ```R
    library(ggplot2)
    library(dplyr)
    
    datos <- read.csv("subset_analisis.csv")
    
    # Análisis de correlación: ¿Afecta el día de la semana a la ocupación?
    # Convertir día a factor
    datos$dia_semana <- as.factor(datos$dia_semana)
    
    # Modelo lineal simple para evaluar predictibilidad
    modelo <- lm(pasajeros_transportados ~ dia_semana + hora_despacho, data=datos)
    summary(modelo)
    ```
    *El `summary(modelo)` te dirá (mediante el p-value) si el día y la hora son estadísticamente significativos para predecir cuántos pasajeros viajarán, lo cual es vital para sugerir la reestructuración de horarios.*
