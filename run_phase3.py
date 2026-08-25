import nbformat as nbf
import json
import polars as pl
from sqlalchemy import create_engine

# --- 1. MODIFICAR EL NOTEBOOK ---
with open('notebooks/Fase2_EDA.ipynb', 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

md_senior = """## 📌 Profundización Analítica: Detección de Anomalías e Hiperfrecuencia

En esta sección se exploran patrones ocultos en el comportamiento logístico a nivel nacional.

> [!WARNING]
> **Nota Metodológica sobre Anomalías:** Durante el análisis de canibalización logística se detectó un valor atípico extremo (Outlier) en la ruta *Villavicencio -> Bogotá D.C.* (10 despachos simultáneos a las 22:00 hrs con 0 pasajeros totales). Por rigor estadístico, este registro se asume como un posible **"despacho técnico" (reposicionamiento de flota sin fines comerciales)** o un error administrativo de registro en la terminal.
> Para evitar que este sesgo extremo corrompa el cálculo de la huella de carbono y los promedios globales, **se excluirá explícitamente del DataFrame antes de proceder a la Fase 3.**
"""

code_senior = """# 1. Filtro de Saneamiento Estadístico (Exclusión de Despachos Técnicos Extremos)
df_eda = df_eda.filter(
    ~((pl.col("nombre_origen") == "VILLAVICENCIO") & 
      (pl.col("nombre_destino") == "BOGOTA, D.C.") & 
      (pl.col("hora_despacho") == 22) & 
      (pl.col("pasajeros") == 0.0) & 
      (pl.col("despachos") >= 10))
)

display(Markdown("✅ **Saneamiento completado:** Se ha excluido el outlier de Villavicencio para no sesgar el modelo ambiental."))

# 2. Análisis de Peores Orígenes y Franjas
display(Markdown("### A. Identificación de Outliers (Ineficiencia Crítica Global)"))
terminales_stats = df_eda.group_by("nombre_origen").agg([
    pl.len().alias("Volumen de Viajes"),
    pl.col("factor_ocupacion").mean().round(2).alias("Ocupación Promedio (%)")
]).filter(pl.col("Volumen de Viajes") >= 50).sort("Ocupación Promedio (%)").head(3)

horas_stats = df_eda.group_by("hora_despacho").agg([
    pl.len().alias("Volumen de Viajes"),
    pl.col("factor_ocupacion").mean().round(2).alias("Ocupación Promedio (%)")
]).sort("Ocupación Promedio (%)").head(3)

display(Markdown("**Top 3 Peores Terminales de Origen (Costa Atlántica y Valle):**"))
display(terminales_stats)

display(Markdown("**Top 3 Peores Franjas Horarias (Horarios Madrugada):**"))
display(horas_stats)

# 3. Canibalización
display(Markdown("### B. Canibalización de Rutas (Hiperfrecuencia de Despachos)"))
df_canibal = df_eda.filter(pl.col("despachos") > 1).with_columns([
    ((pl.col("pasajeros") / (pl.col("capacidad_estimada") * pl.col("despachos"))) * 100).alias("ocupacion_bloque")
])
canibal_critico = df_canibal.filter(pl.col("ocupacion_bloque") < 35).height
display(Markdown(f"- Se detectaron **{canibal_critico} bloques horarios** en el país donde terminales despacharon múltiples buses simultáneos al mismo destino operando bajo ocupación crítica (<35%)."))

# 4. Correlación Temporal
display(Markdown("### C. Correlación Temporal (El día de mayor 'peso muerto')"))
dias_stats = df_eda.group_by("dia_semana").agg([
    pl.len().alias("Volumen de Viajes"),
    pl.col("factor_ocupacion").mean().round(2).alias("Ocupación Promedio (%)")
]).sort("Ocupación Promedio (%)")
display(dias_stats)
"""

# Insertar antes de la celda de visualización para que los datos gráficos tomen el DataFrame saneado
# Encontramos la celda que importa matplotlib y lo metemos justo antes
for i, cell in enumerate(nb.cells):
    if cell.cell_type == 'code' and 'import matplotlib.pyplot as plt' in cell.source:
        nb.cells.insert(i, nbf.v4.new_markdown_cell(md_senior))
        nb.cells.insert(i+1, nbf.v4.new_code_cell(code_senior))
        break
else:
    nb.cells.append(nbf.v4.new_markdown_cell(md_senior))
    nb.cells.append(nbf.v4.new_code_cell(code_senior))

with open('notebooks/Fase2_EDA.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Notebook actualizado con el deep-dive y la nota metodológica.")


# --- 2. CÁLCULOS FASE 3: MODELADO AMBIENTAL ---
db_url = 'postgresql://postgres:postgres@localhost:5432/movilidad'
engine = create_engine(db_url)
df = pl.read_database(query="SELECT * FROM despachos_enriquecidos;", connection=engine)

df = df.with_columns([
    pl.col("hora_despacho").cast(pl.Int32, strict=False),
    pl.col("pasajeros").cast(pl.Float64, strict=False).fill_null(0.0),
    pl.col("despachos").cast(pl.Int32, strict=False).fill_null(1)
])

# Filtro metodológico (Excluir outlier Villavicencio)
df = df.filter(
    ~((pl.col("nombre_origen") == "VILLAVICENCIO") & 
      (pl.col("nombre_destino") == "BOGOTA, D.C.") & 
      (pl.col("hora_despacho") == 22) & 
      (pl.col("pasajeros") == 0.0) & 
      (pl.col("despachos") >= 10))
)

# Cálculos UPME
Rendimiento_km_gal = 10.0
Factor_emision_diesel = 10.15

df = df.with_columns([
    ((pl.col("pasajeros") / pl.col("capacidad_estimada")) * 100).clip(upper_bound=100.0).alias("factor_ocupacion"),
    (pl.col("pasajeros") * pl.col("distancia_km")).alias("pax_km"),
    ((pl.col("distancia_km") / Rendimiento_km_gal) * Factor_emision_diesel).alias("emisiones_co2e")
])

df = df.with_columns(
    pl.when(pl.col("pax_km") > 0)
    .then(pl.col("emisiones_co2e") / pl.col("pax_km"))
    .otherwise(None)
    .alias("co2e_por_pax_km")
)

# Cálculo de la diferencia (Lo que contamina el peso muerto vs el escenario ideal)
# Escenario ideal: Bus viaja al 80% de ocupación.
df = df.with_columns([
    (pl.col("capacidad_estimada") * 0.8).alias("pasajeros_ideales")
])
df = df.with_columns([
    (pl.col("pasajeros_ideales") * pl.col("distancia_km")).alias("pax_km_ideal")
])
df = df.with_columns([
    (pl.col("emisiones_co2e") / pl.col("pax_km_ideal")).alias("co2e_pax_ideal")
])

# Resultados Fase 3
avg_co2_real = df.select(pl.col("co2e_por_pax_km").mean()).item()
avg_co2_ideal = df.select(pl.col("co2e_pax_ideal").mean()).item()
penalizacion_absoluta = avg_co2_real - avg_co2_ideal
penalizacion_porcentaje = (penalizacion_absoluta / avg_co2_ideal) * 100

print(f"\n--- IMPACTO AMBIENTAL FASE 3 ---")
print(f"Emisión Promedio Ideal (80% ocupado): {avg_co2_ideal:.4f} kg CO2e / pax-km")
print(f"Emisión Promedio Real (Subocupado): {avg_co2_real:.4f} kg CO2e / pax-km")
print(f"Incremento por 'Peso Muerto': +{penalizacion_absoluta:.4f} kg CO2e / pax-km ({penalizacion_porcentaje:.2f}%)")

