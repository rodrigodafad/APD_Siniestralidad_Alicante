import os
import pandas as pd
archivo_ttl = "accidentes_cv_graph.ttl"
termino_busqueda = "accidente_"

csv_folder = "dim_clima_csv"
archivo = os.path.join(csv_folder, "dataset_final.csv")
loaded_df = pd.read_csv(archivo)
total_accidentes = len(loaded_df)

print(f"Analizando el archivo '{archivo_ttl}'...")

try:
    contador = 0
    lineas_leidas = 0
    
    with open(archivo_ttl, "r", encoding="utf-8") as f:
        for linea in f:
            lineas_leidas += 1
            # Contamos cuántas veces aparece el término en esta línea
            if termino_busqueda in linea:
                contador += linea.count(termino_busqueda)

    print("-" * 30)
    print(f"RESULTADO FINAL:")
    print(f"Total de líneas en el archivo: {lineas_leidas}")
    print(f"Apariciones de '{termino_busqueda}': {contador}")
    print(f"Total de accidentes esperados en el CSV: {total_accidentes}")
    print("-" * 30)

    if contador == total_accidentes:
        print("✅ ¡ÉXITO TOTAL! Todos los accidentes están en el archivo.")
        print("El problema anterior era solo que buscábamos la palabra equivocada ('schema:Event').")
    elif contador == 0:
        print("❌ El archivo está vacío o no se guardaron los nombres correctamente.")
    else:
        print(f"⚠️ Hay datos, pero no los 27110 esperados (faltan {27110 - contador}).")

except FileNotFoundError:
    print(f"Error: No encuentro el archivo '{archivo_ttl}'. Asegúrate de haber ejecutado el script de generación antes.")