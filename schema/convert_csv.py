import pandas as pd

df_hechos = pd.read_excel("dim_clima/hecho_accidente.xls")
df_ubi = pd.read_excel("dim_clima/dim_ubicacion.xls",dtype={'COD_MUNICIPIO': str})
df_tipo = pd.read_excel("dim_clima/dim_tipo_accidente.xls")
df_via = pd.read_excel("dim_clima/dim_via.xls")
df_clima = pd.read_excel("dim_clima/dim_clima.xls")
df_tipo_senalizacion = pd.read_excel("dim_clima/dim_prioridad_senalizacion.xls")
df_tiempo_via = pd.read_excel("dim_clima/tiempo_via.xls")

folder_path = "dim_clima_csv"

df_hechos.to_csv(f"{folder_path}/hecho_accidente.csv", index=False, encoding='utf-8')
df_ubi.to_csv(f"{folder_path}/dim_ubicacion.csv", index=False, encoding='utf-8')
df_tipo.to_csv(f"{folder_path}/dim_tipo_accidente.csv", index=False, encoding='utf-8')
df_via.to_csv(f"{folder_path}/dim_via.csv", index=False, encoding='utf-8')
df_clima.to_csv(f"{folder_path}/dim_clima.csv", index=False, encoding='utf-8')
df_tipo_senalizacion.to_csv(f"{folder_path}/dim_prioridad_senalizacion.csv", index=False, encoding='utf-8')
df_tiempo_via.to_csv(f"{folder_path}/tiempo_via.csv", index=False, encoding='utf-8')

print(f"Todos los archivos han sido convertidos y guardados en la carpeta '{folder_path}'")
