# Analítica de Movilidad Intermunicipal y Emisiones de CO2 en Colombia

Este proyecto es una iniciativa de especialización enfocada en el modelado estadístico y análisis geográfico del transporte intermunicipal en Colombia, para determinar la ineficiencia logística (tara / factor de subocupación) y su impacto ambiental (emisiones de CO₂ equivalentes per cápita).

## Características del Proyecto
1. **Infraestructura Contenerizada**: La orquestación local utiliza `Docker Compose` levantando automáticamente bases de datos relacionales y entornos analíticos interactivos.
2. **PostgreSQL Relacional**: Todos los datasets del gobierno abiertos procesados se persisten con rigor estructural.
3. **Automatización ETL & EDA**: Se extrae data de la API `datos.gov.co` utilizando librerías como Pandas, SQLAlchemy y herramientas visuales (Seaborn, Matplotlib).
4. **Calculo Avanzado OSRM**: El proyecto incluye un pipeline planificado para el enrutamiento geoespacial usando la API gratuita de Open Source Routing Machine, con la finalidad de trazar distancias reales por carretera en lugar de distancias planas.

## Estructura de Directorios
* `base/` y `datos/`: Almacena diccionarios de extracción estática (Códigos Municipales Históricos DIVIPOLA 2007) originados en formato PDF y convertidos a CSV.
* `notebooks/`: Entornos de Data Science de Jupyter para el procesamiento de Fases (Extracción, Limpieza, Enriquecimiento e Ingeniería de Características).
* `documentacion/`: Reglas de negocio y arquitecturas. Incluye la guía metodológica del proyecto.
* `.agents/`: Carpeta del servidor Model Context Protocol (MCP) que encapsula lógicas (Skills) para que IA genere analíticas de manera automatizada.

## Arranque Rápido
1. Requiere [uv](https://github.com/astral-sh/uv) instalado.
2. Requiere [Docker Desktop](https://www.docker.com/) levantado.
3. Puedes inicializar la infraestructura ejecutando el comando:
```bash
make up
```

## Estado Actual
- **Fase 1 (ETL):** Completada y profesionalizada (Limpieza, homologación de códigos DIVIPOLA).
- **Fase 2 y 3 (Pendientes):** Despliegue de lógica OSRM y Análisis Exploratorio de factores de ocupación.
