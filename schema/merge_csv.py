import pandas as pd

df_hechos = pd.read_csv("dim_clima_csv/hecho_accidente.csv")
df_ubi = pd.read_csv("dim_clima_csv/dim_ubicacion.csv",dtype={'COD_MUNICIPIO': str})
df_tipo = pd.read_csv("dim_clima_csv/dim_tipo_accidente.csv")
df_via = pd.read_csv("dim_clima_csv/dim_via.csv")
df_clima = pd.read_csv("dim_clima_csv/dim_clima.csv")
df_tipo_senalizacion = pd.read_csv("dim_clima_csv/dim_prioridad_senalizacion.csv")
df_tiempo_via = pd.read_csv("dim_clima_csv/tiempo_via.csv")


# Merge correcto usando los nombres reales
df_final = (
    df_hechos
        .merge(df_ubi, on="id", how="left")
        .merge(df_tipo, on="id", how="left")
        .merge(df_via, on="id", how="left")
        .merge(df_clima, on="id", how="left")
        .merge(df_tipo_senalizacion, on="id", how="left")
        .merge(df_tiempo_via, on="id", how="left")
)

df_final.to_csv("dim_clima_csv/dataset_final.csv", index=False)