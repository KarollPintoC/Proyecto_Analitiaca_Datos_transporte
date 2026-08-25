---
trigger: always_on
description: Reglas estrictas, objetivos y restricciones para la Tesis de Movilidad Intermunicipal y CO2.
---

# Reglas y Objetivos del Proyecto (Tesis Especialización)

## 1. El Objetivo Supremo del Agente
El rol central del agente no es construir un software web o transaccional, sino desarrollar un **flujo de datos analítico (ETL -> EDA -> Modelado)** que permita validar las hipótesis de investigación sobre la **subocupación sistemática** en el transporte intermunicipal en Colombia. Se deben estructurar los datos para que el usuario responda a la pregunta rectora:
*"¿De qué manera la subocupación sistemática y la rigidez logística influyen en el incremento de la huella de carbono del sector transporte intermunicipal de pasajeros en las terminales terrestres de Colombia durante el periodo 2025-2026?"*

## 2. Restricciones Académicas y Tecnológicas (Obligatorias)
1. **Cero Datos Simulados:** Está estrictamente prohibido simular, inventar o generar con aleatoriedad (`random`) datos operativos, espaciales o ambientales. Toda inferencia debe basarse en catálogos oficiales (DIVIPOLA, Datos Abiertos, UPME) o usar la API de *Open Source Routing Machine (OSRM)* para distancias y enrutamientos. Si los datos faltan, el agente debe proponer una estrategia matemática, cruzamiento (joins) o geoespacial de homologación.
2. **Eficiencia en Big Data (Cuidado de APIs):** Para cálculos iterativos sobre miles de despachos (ej. API OSRM), estás obligado a usar técnicas de **Pares Únicos (Rutas Únicas)** agrupando orígenes y destinos (ej. `groupby`). Prohibido ejecutar peticiones HTTP masivas de forma individual para evitar colapsos por cuotas (Rate Limit).
3. **Manejo Riguroso de CO2 y Fórmulas:** Todos los KPIs de impacto, tales como Trabajo Útil (`pax_km`), Factor de Ocupación y Emisiones Brutas/Por Pasajero (`CO2e`), deben obedecer estrictamente las fórmulas dictadas en `.agents/docs/objetivos.md`.
4. **Idempotencia y Tolerancia a Fallos:** Todos los Jupyter Notebooks o scripts Python desarrollados deben ser idempotentes (poder ejecutarse múltiples veces sin corromper esquemas o duplicar datos en la base de datos PostgreSQL, usando `if_exists='replace'` o limpiezas previas). Deben incluir *fallbacks* lógicos (ej. si OSRM no halla la ruta por topografía, aplicar inmediatamente la distancia geodésica de Haversine * 1.3).
5. **Lenguaje Formal y Español Académico:** Todos los commits de Git, documentos Markdown y comentarios de código deben redactarse en español formal y técnico (ej. "tara", "hiperfrecuencia logística", "huella de carbono equivalente", "subocupación").

## 3. Manejo de Documentación y Contexto
Toda la documentación base de negocio reside ahora en la carpeta de este agente (`.agents/docs/`). Ante cualquier duda de negocio o matemática, el agente debe leer imperativamente:
- `.agents/docs/objetivos.md` (Diccionario de fórmulas, variables y pregunta rectora).
- `.agents/docs/guia.md` (Metodología paso a paso).
- `.agents/docs/CONTEXTO.md` (Arquitectura del stack, Docker y estado actual).
