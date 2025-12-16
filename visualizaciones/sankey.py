import rdflib
import pandas as pd

# --- CONFIGURACIÓN ---
ARCHIVO_RDF = "accidentes_cv_graph.ttl"
ARCHIVO_SALIDA = "sankey_evidencia_tipo_gravedad.txt"

# COLORES SEMÁNTICOS
COLORES = {
    # Causas (Tipos)
    "Atropello": "#C0392B",    # Rojo Oscuro (Alto Riesgo)
    "Salida Vía": "#D35400",   # Naranja Fuerte (Riesgo Medio-Alto)
    "Vuelco": "#E67E22",       # Naranja
    "Choque": "#8E44AD",       # Morado (Frecuente pero menos letal)
    "Otro": "#95A5A6",         # Gris

    # Consecuencias (Gravedad)
    "Ileso": "#2ECC71",        # Verde
    "Leve": "#F1C40F",         # Amarillo
    "Grave": "#E74C3C",        # Rojo
    "Mortal": "#000000"        # Negro (Luto)
}

print("--- GENERANDO EVIDENCIA 2: TIPO -> GRAVEDAD ---")

g = rdflib.Graph()
g.parse(ARCHIVO_RDF, format="turtle")

# 1. Consulta Directa
query = """
PREFIX ex: <http://proyecto-accidentes.ua.es/resource/>
PREFIX schema1: <http://schema.org/>

SELECT ?tipo ?nombre ?gravedad
WHERE {
    ?acc a schema1:Event .
    OPTIONAL { ?acc ex:tipoAccidente ?tipo . }
    OPTIONAL { ?acc schema1:name ?nombre . }
    OPTIONAL { ?acc ex:gravedad ?gravedad . }
}
"""
results = g.query(query)

data = []
for r in results:
    # Recuperar tipo si falta (usando el nombre)
    t = str(r.tipo) if r.tipo else (str(r.nombre).replace("Accidente: ", "") if r.nombre else "Otro")
    g_val = str(r.gravedad) if r.gravedad else "Leve"
    data.append({"tipo": t, "gravedad": g_val})

df = pd.DataFrame(data)

# 2. Limpieza y Agrupación
def limpiar_tipo(t):
    t = t.lower()
    if "atropello" in t or "peatón" in t: return "Atropello"
    if "salida" in t: return "Salida Vía"
    if "vuelco" in t: return "Vuelco"
    if "colisión" in t or "choque" in t or "alcance" in t or "múltiple" in t: return "Choque"
    return "Otro"

def limpiar_gravedad(g):
    g = g.lower()
    if "ileso" in g: return "Ileso"
    if "leve" in g: return "Leve"
    if "fallecido" in g or "mortal" in g: return "Mortal"
    return "Grave"

df['tipo'] = df['tipo'].apply(limpiar_tipo)
df['gravedad'] = df['gravedad'].apply(limpiar_gravedad)

# 3. Generar Texto Sankey
lines = ["// --- EVIDENCIA: MECÁNICA DEL ACCIDENTE ---", ""]

# Colores
for k, v in COLORES.items(): lines.append(f":{k} {v}")
lines.append("")

# Datos
flujo = df.groupby(['tipo', 'gravedad']).size().reset_index(name='count').sort_values('count', ascending=False)

for _, r in flujo.iterrows():
    lines.append(f"{r['tipo']} [{r['count']}] {r['gravedad']}")

with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"✅ HECHO. Archivo: {ARCHIVO_SALIDA}")
print("   -> Úsalo para demostrar qué accidentes son más letales en sankeymatic.com.")
