# Cuantificación del Impacto Ambiental Derivado de la Subocupación Logística Intermunicipal

**Reporte Técnico de Fase 3**

El presente informe detalla el modelado matemático aplicado para cuantificar el impacto ambiental generado por la rigidez estructural (hiperfrecuencia) en la cadena de transporte terrestre automotor de pasajeros en Colombia.

---

## 1. Fundamentación Metodológica y Homologación de Combustión

Debido a las limitaciones inherentes al _dataset_ oficial del Ministerio de Transporte (ausencia de especificación de tren motriz), la metodología emplea una **homologación logística conservadora**. Se asume que el 100% de la flota categorizada como "BUS" (vehículos de alta capacidad: 30-40 plazas) opera mediante motores de combustión interna a base de **Diésel (ACPM)**.

### Saneamiento de Anomalías Administrativas (Outliers)

Durante el pre-procesamiento estadístico, se detectó un evento anómalo de severidad extrema en el corredor _Villavicencio ➔ Bogotá D.C._ (registro de múltiples vehículos pesados despachados simultáneamente con $0$ pasajeros). A efectos de preservar la integridad del modelo y prevenir asimetrías causadas por divisiones sobre cero o sesgos de ineficiencia irreal, este clúster fue purgado bajo la categoría metodológica de **"Despacho Técnico o Reposicionamiento de Flota"**.

---

## 2. Ecuaciones del Modelado Ambiental (Estándar UPME)

La transformación del Trabajo Útil Logístico (expresado en pasajero-kilómetro o $pax\_km$) hacia una métrica de impacto ambiental ($CO_2e$) se desarrolló integrando las constantes de ingeniería estipuladas por la Unidad de Planeación Minero Energética (UPME).

- **Rendimiento Operativo Asumido ($R$):** $10 \text{ km} / \text{galón}$
- **Factor de Emisión UPME ($F_e$):** $10.15 \text{ kg } CO_2e / \text{galón de Diésel}$

Las ecuaciones implementadas en el _DataFrame_ para cada vector de despacho $i$ son:

$$ \text{Consumo Galones}_{i} = \frac{\text{Distancia}_{i}}{R} $$

$$ \text{Emisión Bruta Total}_{i} = \text{Consumo Galones}_{i} \times F_e $$

El **KPI de Ineficiencia Ambiental**, que representa la huella de carbono asimilada por cada pasajero de forma individual, se define como:

$$ KPI*{i} \left( \frac{kg \text{ } CO_2e}{pax_km} \right) = \frac{\text{Emisión Bruta Total}*{i}}{\text{Pasajeros}_{i} \times \text{Distancia}_{i}} $$

---

## 3. Contraste Analítico: Simulación del "Peso Muerto"

Para aislar y cuantificar exclusivamente el volumen de contaminación generado por la subocupación (sillas vacías), el modelo matemático evaluó paralelamente la operación empírica contra una simulación estocástica de **Eficiencia Logística**, donde la constante de pasajeros se fijó en el **80% de la capacidad nominal del vehículo**.

### Resultados del Modelado Comparativo

| Métrica Analizada                | Escenario Logístico Ideal (80% Capacidad)     | Escenario Real Observado (Subocupado)         |
| :------------------------------- | :-------------------------------------------- | :-------------------------------------------- |
| **Factor de Ocupación Promedio** | $80.00\%$                                     | $43.11\%$                                     |
| **KPI Ambiental Promedio**       | $0.0317 \text{ kg } CO_2e \text{ / } pax\_km$ | $0.1098 \text{ kg } CO_2e \text{ / } pax\_km$ |
| **Varianza de Contaminación**    | Base de Control                               | $\Delta \textbf{+ 246.11 \%}$                 |

### Conclusión Central de Investigación

La evidencia extraída del modelo matemático confirma empíricamente la hipótesis rectora: **La hiperfrecuencia logística y la incapacidad de consolidación de demanda elevan la huella de carbono individual en un $246.11\%$**. El modelo demuestra que el peso muerto derivado de despachar flotas pesadas sin un umbral de ocupación sostenible penaliza severamente la sostenibilidad ambiental del transporte intermunicipal colombiano.
