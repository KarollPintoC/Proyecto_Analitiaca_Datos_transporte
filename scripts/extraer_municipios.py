import pdfplumber
import pandas as pd
from pathlib import Path

def extraer_municipios(pdf_path: str, output_csv: str):
    print(f"Leyendo el archivo: {pdf_path}...")
    
    # Lista para acumular los datos de todas las páginas
    todos_los_datos = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for num_pagina, pagina in enumerate(pdf.pages, start=1):
            # Extraer la tabla de la página actual
            tabla = pagina.extract_table()
            
            if tabla:
                for fila in tabla:
                    # Limpiar las celdas de saltos de línea (None check)
                    fila_limpia = [str(celda).strip().replace('\n', ' ') if celda else "" for celda in fila]
                    
                    # Asegurar que tenemos al menos dos columnas
                    if len(fila_limpia) >= 2:
                        codigo = fila_limpia[0]
                        municipio = fila_limpia[1]
                        
                        # Filtrar solo las filas cuyo código sea numérico
                        if codigo.isdigit():
                            todos_los_datos.append({"Codigo": codigo, "Municipio": municipio})
                            
    # Crear un DataFrame con pandas para estructurar los datos
    df = pd.DataFrame(todos_los_datos)
    
    print(f"✅ Se extrajeron {len(df)} municipios con éxito.")
    
    # Exportar el resultado a un archivo CSV
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"📂 Archivo CSV generado en: {output_csv}")
    
    return df

if __name__ == "__main__":
    # Rutas de entrada y salida
    archivo_pdf = "base/Codigos_municipios_2007.pdf"
    archivo_salida = "base/municipios_extraidos.csv"
    
    if Path(archivo_pdf).exists():
        df_municipios = extraer_municipios(archivo_pdf, archivo_salida)
        
        # Imprimir una muestra de los datos extraídos
        print("\nVista previa de los primeros 5 registros:")
        print(df_municipios.head())
    else:
        print(f"❌ ¡Error! No se encontró el archivo en la ruta: {archivo_pdf}")
