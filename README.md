# Analítica de Movilidad Intermunicipal y Emisiones de CO2 en Colombia

Proyecto de la **Especialización en Analítica de Datos**.

El proyecto mide la subocupación de los buses intermunicipales en Colombia y su impacto ambiental: cuántas emisiones de CO₂e se generan por pasajero-kilómetro y cuántas se habrían evitado si los buses viajaran al 80 % de su capacidad.

## Datos

| Fuente | Uso |
|---|---|
| [Despachos de terminales de transporte](https://www.datos.gov.co/resource/eh75-8ah6) (datos.gov.co, Ministerio de Transporte) | Despachos de **BUS** de enero de 2025 a marzo de 2026 (5,530,364 registros) |
| [Catálogo DIVIPOLA con coordenadas](https://www.datos.gov.co/resource/gdxc-w37w) (datos.gov.co) | Latitud y longitud de cada municipio |
| `base/Codigos_municipios_2007.pdf` y `base/Fuente.xlsx - Table001 (Page 1).pdf` | Nombres oficiales de municipios y departamentos (convertidos a CSV en `datos/`) |
| [OSRM](http://project-osrm.org/) (API pública) | Distancia por carretera de cada ruta; si falla, distancia geodésica × 1.3 |
| Factores UPME | Rendimiento de 10 km/galón y 10.15 kg CO₂e por galón de diésel |

## Fases

| Notebook | Qué hace | Salidas principales |
|---|---|---|
| `notebooks/Fase1_ETL.ipynb` | Descarga los despachos mes a mes, valida cada mes contra el conteo de la API, cruza con DIVIPOLA, calcula distancias, aplica la limpieza documentada y carga a PostgreSQL | `datos/despachos_enriquecidos.parquet`, tabla `despachos_enriquecidos` en PostgreSQL, `results/tables/validacion_*.csv`, `limpieza_antes_despues.csv` |
| `notebooks/Fase2_EDA.ipynb` | Análisis exploratorio con Polars: ocupación por ruta, terminal, hora, día, mes, festivos y distancia; correlaciones de Spearman | `results/figures/fig_eda_*.png`, `results/tables/eda_*.csv` |
| `notebooks/Fase3_Modelado_Ambiental.ipynb` | Modelo de emisiones UPME, comparación entre la operación real y un escenario ideal al 80 % de ocupación, y sensibilidad a la capacidad del bus | `datos/fase3_dataset_emisiones.parquet`, `results/figures/fig_f3_*.png`, `results/tables/fase3_*.csv` |

Las cifras de los informes se leen de `results/tables/`; ninguna se escribe a mano.

### Limpieza de Fase 1

Cada paso registra cuántos registros entran y salen en `results/tables/limpieza_antes_despues.csv`. Resumen:

- Se excluyen 6,123 registros con origen o destino sin coordenadas.
- Se excluyen 180,311 registros de 11 rutas con codificación geográfica inconsistente (detalle en `rutas_codificacion_inconsistente.csv`).
- Se excluyen 10,075 registros con ocupación mayor al 125 %. Los que están entre 101 % y 125 % se conservan con la ocupación topada en 100 %.
- Se conservan los duplicados exactos y los viajes con 0 pasajeros, porque la fuente no tiene un identificador único y los viajes vacíos emiten CO₂e.

Quedan **5,333,855 registros**. Los totales coinciden entre el dataset limpio, PostgreSQL y el parquet (`validacion_totales_carga.csv`).

## Resultados principales

Fuente: `results/tables/fase3_01_kpi_linea_base.csv` y `fase3_04_sensibilidad_capacidad.csv` (bus de 40 puestos).

| Indicador | Valor |
|---|---|
| Buses despachados | 5,497,543 |
| Pasajeros | 68,978,580 |
| Ocupación promedio | 31.4 % |
| Viajes vacíos | 8.9 % de los registros |
| Emisiones totales | 1,580,459 t CO₂e |
| Intensidad real | 0.0679 kg CO₂e por pasajero-km |
| Intensidad con 80 % de ocupación | 0.0317 kg CO₂e por pasajero-km |
| Exceso sobre el escenario ideal | +114 % |
| Emisiones evitables | 841,986 t CO₂e |

Si se asume un bus de 45 puestos, la ocupación baja a 27.9 % y el exceso sube a +141 %. La conclusión se mantiene con cualquiera de las dos capacidades.

El reporte técnico completo está en `reporte_fase3_conclusiones.md` (y en PDF).

## Estructura

```
├── base/                 PDF fuente de municipios y departamentos, notebook original
├── datos/
│   ├── raw/              Descargas mensuales de la API (no se sube a git)
│   ├── *_extraidos.csv   Catálogos de municipios y departamentos
│   ├── distancias_rutas.csv          Caché de distancias OSRM por ruta
│   ├── despachos_enriquecidos.parquet   Salida de Fase 1
│   └── fase3_dataset_emisiones.parquet  Salida de Fase 3
├── notebooks/            Fase 1, 2 y 3
├── results/
│   ├── figures/          Gráficas de Fase 2 y 3
│   └── tables/           Tablas de validación, limpieza, EDA y KPI
├── scripts/              Extracción de los catálogos desde los PDF (pdfplumber)
├── run_phase3.py         Script de apoyo de la versión anterior de Fase 3
├── docker-compose.yml    PostgreSQL 15 y JupyterLab
├── Makefile              Comandos de Docker
└── .env.example          Plantilla de credenciales locales
```

`.agents/` contiene un servidor MCP y documentos de contexto que se usaron como apoyo de IA durante el desarrollo.

## Cómo ejecutarlo

Requisitos: [uv](https://github.com/astral-sh/uv) y [Docker Desktop](https://www.docker.com/).

1. Crea el archivo de credenciales locales y ajusta los valores:
   ```bash
   cp .env.example .env
   ```
2. Instala las dependencias:
   ```bash
   uv sync
   ```
3. Levanta PostgreSQL (puerto 5433) y JupyterLab (puerto 8888):
   ```bash
   make up
   ```
4. Ejecuta los notebooks en orden: Fase 1, Fase 2 y Fase 3. Desde la terminal:
   ```bash
   cd notebooks
   uv run jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 Fase1_ETL.ipynb
   uv run jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 Fase2_EDA.ipynb
   uv run jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 Fase3_Modelado_Ambiental.ipynb
   ```

Otros comandos: `make psql` abre una consola de PostgreSQL, `make jupyter` muestra el enlace y el token, y `make clean` borra los contenedores y la base de datos.

### Notas sobre la ejecución

- **Fase 1 depende de la API de datos.gov.co.** Pide el conteo de cada mes antes de usar o descargar los datos, aunque el mes ya esté en `datos/raw/`. Si la API está lenta, la celda reintenta y se puede volver a ejecutar: retoma donde iba. La celda 3 solo es un diagnóstico de volumen y no la usan las demás.
- **Los parquet se regeneran con Fase 1 y Fase 3.** Cada uno pesa unos 80 MB. GitHub acepta archivos de hasta 100 MB, así que si crecen habrá que dejar de subirlos (o usar Git LFS) y regenerarlos localmente.
- **Distancias:** `datos/distancias_rutas.csv` guarda las distancias ya calculadas; OSRM solo se consulta para rutas nuevas.
