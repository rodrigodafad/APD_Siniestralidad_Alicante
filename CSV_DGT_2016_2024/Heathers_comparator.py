import pandas as pd
import os

def leer_header(ruta):
    ext = ruta.lower().split(".")[-1]

    if ext == "csv":
        df = pd.read_csv(ruta, nrows=0)
    elif ext in ["xls", "xlsx"]:
        df = pd.read_excel(ruta, nrows=0)
    else:
        raise ValueError("Formato no soportado: " + ruta)

    return list(df.columns)

def comparar_headers(lista_rutas):
    headers = {os.path.basename(r): leer_header(r) for r in lista_rutas}

    print("\n=== HEADERS DETECTADOS ===")
    for nombre, h in headers.items():
        print(f"{nombre}: {h}")
    print()

    print("=== COMPARACIONES ===")
    nombres = list(headers.keys())

    for i in range(len(nombres)):
        for j in range(i + 1, len(nombres)):
            f1, f2 = nombres[i], nombres[j]
            h1, h2 = headers[f1], headers[f2]

            if h1 == h2:
                print(f"[OK] {f1} y {f2} tienen EL MISMO header.")
            else:
                print(f"[X] {f1} y {f2} tienen headers DIFERENTES.")
                print(f"   - Solo en {f1}: {set(h1) - set(h2)}")
                print(f"   - Solo en {f2}: {set(h2) - set(h1)}")
                print(f"   - Orden diferente: {h1 != h2}")
            print()

# === USO ===

rutas = [
    r"C:/Users/Guives/OneDrive/universidad/3º AÑO/ADQUISICIÓN Y PREPARACIÓN DE DATOS/Practica Cuatrimestre/CSV_DGT/TABLA_ACCIDENTES_24.xlsx",
    r"C:/Users/Guives/OneDrive/universidad/3º AÑO/ADQUISICIÓN Y PREPARACIÓN DE DATOS/Practica Cuatrimestre/CSV_DGT/TABLA_ACCIDENTES_23.xlsx",
    r"C:/Users/Guives/OneDrive/universidad/3º AÑO/ADQUISICIÓN Y PREPARACIÓN DE DATOS/Practica Cuatrimestre/CSV_DGT/TABLA_ACCIDENTES_22.xlsx",
    r"C:/Users/Guives/OneDrive/universidad/3º AÑO/ADQUISICIÓN Y PREPARACIÓN DE DATOS/Practica Cuatrimestre/CSV_DGT/TABLA_ACCIDENTES_21.xlsx",
    r"C:/Users/Guives/OneDrive/universidad/3º AÑO/ADQUISICIÓN Y PREPARACIÓN DE DATOS/Practica Cuatrimestre/CSV_DGT/TABLA_ACCIDENTES_20.xlsx",
    r"C:/Users/Guives/OneDrive/universidad/3º AÑO/ADQUISICIÓN Y PREPARACIÓN DE DATOS/Practica Cuatrimestre/CSV_DGT/TABLA_ACCIDENTES_19.xlsx",
    r"C:/Users/Guives/OneDrive/universidad/3º AÑO/ADQUISICIÓN Y PREPARACIÓN DE DATOS/Practica Cuatrimestre/CSV_DGT/TABLA_ACCIDENTES_18.xlsx",
    r"C:/Users/Guives/OneDrive/universidad/3º AÑO/ADQUISICIÓN Y PREPARACIÓN DE DATOS/Practica Cuatrimestre/CSV_DGT/TABLA_ACCIDENTES_17.xlsx",
    r"C:/Users/Guives/OneDrive/universidad/3º AÑO/ADQUISICIÓN Y PREPARACIÓN DE DATOS/Practica Cuatrimestre/CSV_DGT/TABLA_ACCIDENTES_16.xlsx",
]

comparar_headers(rutas)
