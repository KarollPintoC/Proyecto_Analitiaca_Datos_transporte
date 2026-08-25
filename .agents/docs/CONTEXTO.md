# Contexto del Proyecto: Analítica de Movilidad y Emisiones de CO2

Este archivo sirve como memoria y guía de contexto para el usuario y cualquier agente de Inteligencia Artificial que se integre al proyecto en iteraciones futuras. Contiene la arquitectura, objetivos y configuración actual del repositorio.

## 1. Objetivo Principal
El proyecto tiene como propósito realizar analítica de datos sobre **movilidad intermunicipal en Colombia** y calcular las **emisiones de CO₂ equivalentes**.
Se busca modelar el impacto ambiental (en kg de CO₂ emitidos por pasajero-kilómetro) tomando en consideración:
- La capacidad vehicular.
- El volumen de pasajeros transportados (Factor de Ocupación).
- La penalidad por la tara (despachos de vehículos con baja ocupación o vacíos).
- El uso de factores de emisión estándar para vehículos diésel (referencia UPME).

## 2. Infraestructura y Entorno
El proyecto está construido bajo una filosofía modular e infraestructura conteinerizada:

- **Gestor de Paquetes Python:** Se utiliza `uv` para gestionar el entorno virtual (`.venv`) en Python 3.10.9 y las dependencias (registradas en `pyproject.toml`).
- **Docker & Docker Compose:** Todo el despliegue analítico y de base de datos corre sobre Docker (orquestado vía `docker-compose.yml` y comandos centralizados en un `Makefile`).
  - **Servicio PostgreSQL:** Motor relacional (v15) para almacenar los datos limpios. (Puerto `5432`, DB: `movilidad`).
  - **Servicio JupyterLab:** Entorno interactivo de Data Science Notebook (con soporte de Python y R) para exploración. (Puerto `8888`, Token: `analitica2026`).

## 3. Arquitectura MCP (Model Context Protocol)
El entorno cuenta con un conjunto de **Skills** implementadas como un Servidor MCP para que los agentes de IA interactúen con el proyecto de forma autónoma.
Están programadas usando la API `mcp.server.Server` y configuradas a través del framework de customización de Antigravity IDE.

### Directorio de Agentes (`.agents/`)
- `mcp_server.py`: Contiene las siguientes Tools registradas:
  1. `skill_etl_datos_abiertos`: Extracción, Transformación y Carga (ETL) desde la API de Socrata (datos.gov.co) para el dataset de despachos (`eh75-8ah6`), filtrando años 2025/2026, motor diésel y capacidad 30-40 pasajeros.
  2. `skill_eda_ocupacion`: Análisis Exploratorio de Datos. Consulta PostgreSQL, genera métricas de subocupación y un mapa de calor (`heatmap_ocupacion.png`).
  3. `skill_calculo_emisiones_co2`: Procesa la analítica ambiental aplicando factores de emisión (UPME) y estimando el peso muerto (tara).
  4. `skill_despliegue_docker`: Genera programáticamente la infraestructura local (`docker-compose.yml`).
- `mcp_config.json`: Registra el servidor para auto-descubrimiento en Antigravity IDE.

## 4. Fuentes de Datos Base
Además del consumo de APIs dinámicas gubernamentales, el repositorio procesó y tradujo información catastral histórica:
- `/base/Codigos_municipios_2007.pdf` transformado a `/base/municipios_extraidos.csv` (1120 registros: `Codigo`, `Municipio`).
- `/base/Fuente.xlsx - Table001 (Page 1).pdf` transformado a `/base/departamentos_extraidos.csv` (33 registros: `departamento`, `codigo_departamento`).
Estos scripts de extracción se encuentran en la raíz del proyecto (`extraer_municipios.py` y `extraer_departamentos.py`) y utilizan `pdfplumber` y regex para extraer la tabla y limpiar la data.

## 5. Próximos Pasos (En cola de desarrollo)
- **Cálculo de Distancias OSRM:** Implementar un script de enrutamiento que consuma la API gratuita de Open Source Routing Machine (`router.project-osrm.org`) para calcular con alta precisión las distancias por carretera cruzando el dataset oficial de coordenadas de Colombia.
- **Análisis Exploratorio (EDA):** Realizar el modelado de ocupación, visualizando la "hiperfrecuencia logística" (viajes de vehículos pesados con baja ocupación o tara ineficiente).
- **Cálculo de Huella de Carbono:** Integrar el kilometraje real de OSRM con el factor de emisión para determinar los kg de CO₂ emitidos por pasajero-kilómetro en PostgreSQL.
