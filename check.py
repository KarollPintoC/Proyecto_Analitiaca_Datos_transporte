import pandas as pd
from unidecode import unidecode
df_api = pd.read_json('https://www.datos.gov.co/resource/eh75-8ah6.json?$limit=50')
df_mun = pd.read_csv('datos/municipios_extraidos.csv')
def clean_text(text): return unidecode(str(text).strip().upper()) if not pd.isna(text) else text
df_api['m_api'] = df_api['municipio_origen_ruta'].apply(clean_text)
df_mun['m_csv'] = df_mun['Municipio'].apply(clean_text)
print('API unique origins:', df_api['m_api'].unique()[:5])
print('CSV unique municipalities:', df_mun['m_csv'].unique()[:5])
missing = set(df_api['m_api']) - set(df_mun['m_csv'])
print('Missing in CSV:', list(missing)[:10])
