import pdfplumber
import pandas as pd
from pathlib import Path
import re

def extraer_departamentos(pdf_path: str, output_csv: str):
    print(f"Leyendo el archivo: {pdf_path}...")
    
    todos_los_datos = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for num_pagina, pagina in enumerate(pdf.pages, start=1):
            texto = pagina.extract_text()
            if texto:
                lineas = texto.split('\n')
                for linea in lineas:
                    # Ignorar línea de encabezado o vacías
                    if "departamento" in linea.lower() or not linea.strip():
                        continue
                    
                    # El formato es "Nombre del Departamento 123"
                    # Usamos regex para atrapar todo hasta el último número
                    match = re.search(r'^(.*?)(\d+)$', linea.strip())
                    if match:
                        departamento = match.group(1).strip()
                        codigo = match.group(2).strip()
                        
                        todos_los_datos.append({
                            "departamento": departamento,
                            "codigo_departamento": codigo
                        })
                            
    # Crear el DataFrame
    df = pd.DataFrame(todos_los_datos)
    
    print(f"✅ Se extrajeron {len(df)} departamentos con éxito.")
    
    # Exportar a CSV
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"📂 Archivo CSV generado en: {output_csv}")
    
    return df

if __name__ == "__main__":
    archivo_pdf = "base/Fuente.xlsx - Table001 (Page 1).pdf"
    archivo_salida = "base/departamentos_extraidos.csv"
    
    if Path(archivo_pdf).exists():
        df_deptos = extraer_departamentos(archivo_pdf, archivo_salida)
        
        print("\nVista previa de los primeros 5 registros:")
        print(df_deptos.head())
    else:
        print(f"❌ ¡Error! No se encontró el archivo en la ruta: {archivo_pdf}")
