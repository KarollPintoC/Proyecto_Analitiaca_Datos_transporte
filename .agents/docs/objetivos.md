# Especificación Técnica y Analítica: Proyecto de Transporte Intermunicipal (2025-2026)
## Documento de Contexto y Diccionario de Datos para Agente de Desarrollo (Antigravity)

---

## 1. Contexto del Negocio y Problemática Operativa

El sector del transporte terrestre en Colombia es responsable de un alto consumo energético (aproximadamente el 44%) y es un emisor crítico de Gases de Efecto Invernadero (GEI). El Gobierno Nacional tiene la meta vinculante de reducir estas emisiones en un 51% para 2030 (Plan Nacional de Desarrollo 2022-2026). Sin embargo, el sector enfrenta una grave barrera operativa: la **subocupación sistemática**.

Actualmente, las terminales de transporte intermunicipal operan bajo una lógica de **hiperfrecuencia logística y oferta constante**. Las empresas priorizan mantener horarios de salida rígidos en lugar de consolidar pasajeros. Esto genera un efecto cascada negativo:
1. Buses de alta capacidad (30 a 40 puestos) viajan con muy pocos pasajeros (estimación del 75% de los despachos con 13 usuarios o menos).
2. El combustible diésel (responsable del 79% del transporte terrestre) se quema ineficientemente para mover el "peso muerto" (tara) del vehículo y no a los usuarios.
3. Se dispara la huella de carbono medida por pasajero-kilómetro, encareciendo los costos logísticos y ambientales.

### Objetivo del Agente (Lo que debes lograr)
El agente debe procesar registros históricos (2025-2026) para construir un diagnóstico empírico estructurado. No se debe crear un software transaccional, sino un flujo de datos (ETL -> EDA -> Modelado -> Dashboard BI).
Debes validar las siguientes premisas mediante análisis de datos:
* La ineficiencia operativa actúa como multiplicador de emisiones.
* La demanda de pasajeros está desincronizada de la oferta horaria.
* Es posible identificar un índice de predictibilidad en la demanda según variables temporales (días, meses, horas).

**Pregunta Rectora de Investigación a resolver mediante el análisis:**
*¿De qué manera la subocupación sistemática y la rigidez logística influyen en el incremento de la huella de carbono del sector transporte intermunicipal de pasajeros en las terminales terrestres de Colombia durante el periodo 2025-2026?*

---

## 2. Diccionario de Datos Requerido

Para ejecutar los procesos de transformación (ETL) y el Análisis Exploratorio de Datos (EDA), el agente debe estructurar, limpiar y cruzar los siguientes conjuntos de datos:

### A. Variables Operativas y de Demanda (Registros de Despacho Transaccional)
Datos provenientes de los sistemas de las terminales de transporte.
* **id_despacho:** Identificador único del viaje.
* **fecha_despacho:** Fecha exacta de la salida (YYYY-MM-DD). Fundamental para análisis de estacionalidad.
* **hora_despacho:** Hora de salida (HH:MM:SS). Clave para medir la hiperfrecuencia y rangos pico/valle.
* **pasajeros_reales:** Cantidad exacta de tiquetes vendidos/usuarios transportados en ese despacho.
* **frecuencia_ruta:** Número de vehículos despachados para la misma ruta en un bloque horario determinado.

### B. Variables del Vehículo (Flota y Capacidad)
Datos técnicos de los automotores asignados a los despachos.
* **id_vehiculo:** Placa o identificador del bus.
* **capacidad_instalada:** Número total de asientos disponibles. El filtro de negocio exige analizar vehículos de capacidad media y alta (30 a 40 puestos).
* **tipo_combustible:** Se debe filtrar estrictamente para vehículos propulsados por Diésel.
* **peso_tara_kg:** Peso muerto del vehículo vacío en kilogramos.

### C. Variables Geográficas y de Ruta
Datos de distancia para cálculos de eficiencia.
* **origen:** Municipio/Terminal de salida.
* **destino:** Municipio/Terminal de llegada.
* **distancia_km:** Longitud total de la ruta en kilómetros. Es el componente esencial para el cálculo del denominador logístico.

### D. Variables Ambientales y de Consumo
Factores para convertir la actividad física en huella ambiental.
* **consumo_combustible_gal:** Estimación de galones de diésel consumidos por el vehículo para la `distancia_km` dada.
* **factor_emision_diesel:** Coeficiente oficial (basado en estándares de la UPME / FECOC+ o MinAmbiente) que define los kg de CO2e emitidos por galón de diésel quemado.

---

## 3. Lógica Analítica y Fórmulas Clave (Instrucciones para el Agente)

Para responder a la pregunta de investigación, el agente deberá crear campos calculados utilizando la siguiente lógica de negocio:

1. **Cálculo del Factor de Ocupación (%)**
   `factor_ocupacion = (pasajeros_reales / capacidad_instalada) * 100`
   *Propósito:* Identificar el volumen exacto de capacidad ociosa por viaje.

2. **Cálculo de Trabajo Útil (Pasajeros-Kilómetro)**
   `pax_km = pasajeros_reales * distancia_km`
   *Propósito:* Métrica estándar en transporte para medir el trabajo logístico real realizado.

3. **Cálculo de la Huella de Carbono Bruta (CO2e total del viaje)**
   `emisiones_totales_co2e = consumo_combustible_gal * factor_emision_diesel`
   *Propósito:* Determinar el impacto ambiental absoluto de mover el vehículo del punto A al punto B.

4. **Cálculo del Indicador de Ineficiencia Ambiental (El KPI principal)**
   `emisiones_por_pax_km = emisiones_totales_co2e / pax_km`
   *Propósito:* Este indicador demostrará que a menor ocupación, el costo de carbono de transportar a un solo individuo se dispara, penalizando la ineficiencia logística.

## 4. Entregables Esperados del Agente
1. Scripts de extracción y limpieza de datos (Python/Pandas).
2. Modelos estadísticos y de correlación que crucen `hora_despacho` y `fecha_despacho` vs `factor_ocupacion`.
3. Base de datos estructurada lista para ser conectada a un entorno de Business Intelligence (Power BI) para la visualización del Dashboard final.
