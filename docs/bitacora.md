# Bitácora de decisiones

Registro de las decisiones de datos, limpieza, arquitectura y modelado. Cada entrada indica el problema, las opciones consideradas y el motivo de la elección. Agregar las nuevas entradas al final.

| # | Fecha | Etapa | Problema | Opciones consideradas | Decisión y motivo |
|---|---|---|---|---|---|
| 1 | 2026-11-21 | Extracción | La descarga original (límite de 50.000) solo cubría el 1 y 2 de enero de 2025 | Mantener la muestra; descargar todo el periodo | Descargar todo: el objetivo 3 necesita meses y días de la semana |
| 2 | 2026-11-21 | Extracción | 14,8 millones de registros de todas las clases en 2025–2026 | Todas las clases; solo BUS; incluir abril de 2026 | Solo BUS, enero 2025–marzo 2026: alcance del estudio; abril estaba incompleto |
| 3 | 2026-11-21 | Extracción | La paginación por offset dejó de responder a los 3 millones de filas | Aumentar el tiempo de espera; paginar mes a mes | Mes a mes, con conteo oficial por mes: robusto y validado contra la fuente |
| 4 | 2026-11-22 | Calidad | Diciembre de 2025 con solo 6.043 registros | Excluirlo; conservarlo marcado | Conservarlo en la base, marcado como incompleto y sin interpretarlo |
| 5 | 2026-11-22 | Enriquecimiento | 2.071 rutas para calcular con OSRM en cada ejecución | Recalcular siempre; caché | Caché en `datos/distancias_rutas.csv`: reproducible y rápido |
| 6 | 2026-11-22 | Limpieza | Pasajeros nulos | Imputar 0; excluir | Excluir: imputar 0 crearía viajes vacíos artificiales (0 casos) |
| 7 | 2026-11-22 | Limpieza | 6.123 registros sin coordenadas | Distancia promedio; excluir | Excluir: imputar inventaría emisiones (0,11 %) |
| 8 | 2026-11-22 | Limpieza | La capacidad ignoraba el número de buses del registro | 40 por registro; 40 × buses | 40 × buses: un registro con 3 despachos son 3 buses |
| 9 | 2026-11-22 | Limpieza | 102.555 registros con más pasajeros que puestos | Recortar sin aviso; excluir todos; regla en dos niveles | Dos niveles: excluir > 50 por bus y conservar 41–50 topados en 100 %, para no sesgar hacia la subocupación |
| 10 | 2026-11-23 | Limpieza | Rutas a más de 1.000 km con patrón de ruta corta (municipios homónimos) | Ignorar; corregir códigos; excluir con regla general | Excluir 11 rutas (180.311 registros) con regla general; corregir requiere validación con las terminales |
| 11 | 2026-11-22 | Limpieza | 655.812 duplicados exactos | Eliminar; conservar | Conservar: sin identificador único pueden ser despachos distintos |
| 12 | 2026-11-22 | Limpieza | Regla fija para un registro atípico de Villavicencio | Mantenerla; reglas generales | Reglas generales; los viajes vacíos se conservan porque son el fenómeno estudiado |
| 13 | 2026-11-22 | Carga | `to_sql` por defecto tardaría horas con 5 millones de filas | Por lotes; COPY de PostgreSQL | COPY más copia en parquet para el análisis y Colab |
| 14 | 2026-11-22 | Arquitectura | El documento decía SQL Server y Pentaho | Migrar a esas herramientas; documentar lo implementado | Documentar PostgreSQL en Docker y Python, que es lo implementado y reproducible |
| 15 | 2026-11-22 | Análisis | Leer 5 millones de filas desde PostgreSQL es lento | PostgreSQL; parquet | Parquet para EDA y modelado; PostgreSQL para el modelo en estrella |
| 16 | 2026-11-22 | Indicadores | La intensidad se calculaba como promedio de cocientes | Promedio de cocientes; total sobre total | Total sobre total: el promedio excluía los viajes vacíos |
| 17 | 2026-11-22 | Visualización | Gráficas con 5 millones de puntos | Todos los puntos; muestra con semilla | Muestras aleatorias de 50.000 y 100.000 con semilla 42 |
| 18 | 2026-11-23 | Evaluación | Dependencia del supuesto de 40 puestos | Aceptarlo; análisis de sensibilidad | Sensibilidad con 45 puestos: la conclusión se mantiene (exceso 140,8 %) |
| 19 | 2026-11-23 | Calidad | El último día de cada mes llega truncado desde octubre de 2025 | Ignorar; excluir del modelado | Excluir como objetivo en la Fase 5 con regla general (< 50 % de la mediana móvil y no festivo) |
| 20 | 2026-11-23 | Seguridad | Credenciales escritas en el código | Mantener; archivo `.env` | Archivo `.env` fuera de git, con `.env.example` |
| 21 | 2026-11-23 | Modelado | 5,3 millones de registros para 11 modelos con Optuna | Todos los registros; agregar por ruta y día | Ruta × día, 100 rutas regulares de mayor demanda |
| 22 | 2026-11-23 | Modelado | La validación temporal por filas mezcla fechas | Por filas; por fechas | `TimeSeriesSplit` sobre fechas únicas |
| 23 | 2026-11-23 | Modelado | Costo cuadrático de SVR y KNN | Todos los datos; submuestra | Submuestra de 10.000 filas, documentada |
| 24 | 2026-11-23 | Modelo dimensional | Origen y destino usan la misma tabla de municipios | Dos tablas; dimensión de rol | Dimensión de rol con vistas `dim_origen` y `dim_destino` |
| 25 | 2026-11-24 | Evaluación | Posible doble conteo de buses en tránsito | Ignorarlo; sensibilidad con solo despachos de origen | Sensibilidad: exceso de 104,7 % con solo origen; la conclusión se mantiene |
| 26 | 2026-11-24 | Modelado | Elección del mejor modelo entre 11 candidatos | Menor error en prueba; menor RMSE medio en validación cruzada | RMSE medio en `TimeSeriesSplit` (Random Forest, 371,7 ± 84,3): el conjunto de prueba solo se usa para el informe final, no para elegir (`fase5_07_comparacion_modelos.csv`) |
| 27 | 2026-11-24 | Modelado | Valor de las variables de ingeniería (rezagos, medias móviles, calendario) | Solo variables base; base más ingeniería | Conservar la ingeniería: la ablación baja el RMSE de prueba de 394,9 a 305,0 con el mismo modelo (`fase5_09_ablacion.csv`) |
| 28 | 2026-11-24 | Tablero | El `.pbix` de 80 MB no se puede revisar ni comparar en git | `.pbix` binario; proyecto `.pbip` (TMDL y PBIR en texto) | `.pbip` en `dashboard/`, sin la caché de datos (`.gitignore`); se abre con Power BI Desktop y se actualiza desde PostgreSQL |
| 29 | 2026-11-24 | Tablero | Medida `Pasajeros` con el mismo nombre que la columna `pasajeros` | Renombrar la columna; renombrar la medida | Renombrar la medida a `Total pasajeros`: la columna viene del modelo en estrella y la usan los cuadernos |
