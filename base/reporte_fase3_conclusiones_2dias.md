# Cuantificación del Impacto Ambiental Derivado de la Subocupación Logística Intermunicipal

**Reporte Técnico de Fase 3**

Este informe presenta el modelo con el que se cuantifica el impacto ambiental de la subocupación de los buses intermunicipales en Colombia. Cubre los despachos de enero de 2025 a marzo de 2026. Todas las cifras provienen de `notebooks/Fase3_Modelado_Ambiental.ipynb` y de las tablas en `results/tables/`.

---

## 1. Datos y supuestos

### Homologación del combustible

El dataset oficial del Ministerio de Transporte no especifica el tipo de motor. Por eso se adopta una **homologación conservadora**: el 100 % de la flota clasificada como "BUS" (vehículos de alta capacidad, 30 a 40 puestos) se asume con motor de combustión a **diésel (ACPM)**.

### Depuración del dataset (Fase 1)

De los 5,530,364 registros descargados quedan **5,333,855** tras la limpieza. El detalle de cada paso está en `results/tables/limpieza_antes_despues.csv`:

- Se excluyen 6,123 registros con origen o destino sin coordenadas, porque su distancia no es calculable.
- Se excluyen 180,311 registros de 11 rutas con codificación geográfica inconsistente. Son rutas de más de 400 km, sin viajes de regreso y con 10 pasajeros por bus o menos; el patrón corresponde a destinos codificados como un municipio homónimo de otro departamento (por ejemplo, Candelaria, Valle, codificada como Candelaria, Atlántico).
- Se excluyen 10,075 registros con ocupación mayor al 125 %, que no es físicamente plausible. Los registros entre 101 % y 125 % se conservan con la ocupación topada en 100 %.
- Se conservan los 472,317 viajes con 0 pasajeros (8.9 %), porque emiten CO₂e sin transportar pasajeros, que es el fenómeno estudiado.

Los totales coinciden entre el dataset limpio, PostgreSQL y el archivo parquet (`validacion_totales_carga.csv`).

---

## 2. Ecuaciones del modelo ambiental (estándar UPME)

Las emisiones se calculan con las constantes de la Unidad de Planeación Minero Energética (UPME):

- **Rendimiento del bus ($R$):** $10$ km/galón
- **Factor de emisión ($F_e$):** $10.15$ kg CO₂e por galón de diésel
- **Capacidad por bus ($C$):** $40$ puestos (con sensibilidad a $45$ en la sección 4)

Para cada registro $i$, con distancia $d_i$, $b_i$ buses despachados y $p_i$ pasajeros:

$$ \text{Consumo}_i = \frac{d_i}{R} \times b_i \qquad \text{Emisiones}_i = \text{Consumo}_i \times F_e $$

La **intensidad de emisión** se calcula como total sobre total, para incluir los viajes con 0 pasajeros. Un promedio de los cocientes de cada viaje los excluiría por división por cero, y son justamente los más ineficientes:

$$ I_{\text{real}} = \frac{\sum_i \text{Emisiones}_i}{\sum_i p_i \, d_i} \quad \left[\frac{\text{kg CO}_2\text{e}}{\text{pasajero-km}}\right] $$

---

## 3. Contraste entre la operación real y el escenario ideal

Para aislar el efecto de las sillas vacías, la operación observada se compara con un **escenario ideal** en el que los mismos buses viajan al **80 % de su capacidad** (32 pasajeros por bus). Es un cálculo determinístico: las emisiones son las mismas y solo cambian los pasajeros-km transportados.

$$ I_{\text{ideal}} = \frac{F_e}{R \times 0.8\,C} = \frac{10.15}{10 \times 32} = 0.0317 $$

### Resultados (bus de 40 puestos)

| Indicador                          | Escenario ideal (80 %) | Operación real         |
| :--------------------------------- | :--------------------- | :--------------------- |
| **Ocupación**                      | 80.0 %                 | 31.4 %                 |
| **Intensidad de emisión**          | 0.0317 kg CO₂e/pax-km  | 0.0679 kg CO₂e/pax-km  |
| **Exceso sobre el escenario ideal** | Base de control        | **+114.0 %**           |

Otros indicadores del periodo (`fase3_01_kpi_linea_base.csv`):

- **Buses despachados:** 5,497,543, con 68,978,580 pasajeros.
- **Registros en ocupación crítica (menos de 35 %):** 61.7 %.
- **Emisiones totales:** 1,580,459 t CO₂e.
- **Emisiones evitables con una ocupación del 80 %:** 841,986 t CO₂e, el 53.3 % del total, equivalentes a 82,954,276 galones de diésel.

La brecha frente al escenario ideal se mantiene en todos los meses: la intensidad real oscila entre 0.059 y 0.076 kg CO₂e/pax-km (`fase3_02_kpi_mensual.csv`). Diciembre de 2025 se excluye de esta lectura porque la fuente tiene datos incompletos para ese mes. Una brecha estable indica un problema estructural de programación de despachos, no estacional.

---

## 4. Sensibilidad a la capacidad del bus

En Fase 1 aparecieron registros con hasta 50 pasajeros por bus, lo que sugiere que parte de la flota tiene más de 40 puestos. Por eso se recalculan los indicadores con 45 puestos (`fase3_04_sensibilidad_capacidad.csv`):

| Indicador                   | 40 puestos | 45 puestos |
| :-------------------------- | :--------- | :--------- |
| Ocupación                   | 31.4 %     | 27.9 %     |
| Intensidad ideal            | 0.0317     | 0.0282     |
| Exceso sobre el ideal       | +114.0 %   | +140.8 %   |
| Emisiones evitables (t CO₂e) | 841,986    | 924,038    |

Con más puestos por bus la subocupación es mayor. El supuesto de 40 puestos es, por tanto, conservador.

---

## 5. Rutas prioritarias

Las 10 rutas con más emisiones evitables concentran el **21.6 %** del total evitable, entre 2,050 rutas (`fase3_03_rutas_emisiones_evitables.csv`). Encabezan la lista Bogotá – Cali (3.4 %), Bogotá – Cúcuta (2.7 %) y Bogotá – Sogamoso (2.4 %). Consolidar despachos en esos corredores capturaría una parte relevante del beneficio ambiental.

---

## Conclusión

Los resultados confirman la hipótesis del proyecto. Con una ocupación promedio de 31.4 %, la huella de carbono por pasajero-kilómetro del transporte intermunicipal en bus es **114 % mayor** que la de una operación consolidada al 80 % de ocupación. Eso equivale a **841,986 t CO₂e evitables** en quince meses, el 53 % de las emisiones del periodo. La conclusión se mantiene, y se refuerza, si se asume una capacidad de 45 puestos. La brecha es estable a lo largo de los meses, lo que apunta a la programación de despachos como causa estructural.
