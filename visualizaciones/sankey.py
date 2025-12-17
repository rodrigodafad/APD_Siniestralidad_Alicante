import rdflib
import pandas as pd

# --- CONFIGURACIÓN ---
ARCHIVO_RDF = "accidentes_cv_graph.ttl"
ARCHIVO_SALIDA = "sankey_multietapa.txt"

# COLORES PARA EL DIAGRAMA (Opcional para SankeyMatic)
COLORES = {
    # Ubicación
    "Carretera": "#2E86C1", "Calle/Urbana": "#17A589",
    # Tipo Accidente
    "Colisión": "#D35400", "Salida Vía": "#8E44AD", "Atropello": "#C0392B", "Otros": "#7F8C8D",
    # Momento
    "Día": "#F1C40F", "Noche": "#2C3E50", "Crepúsculo": "#E67E22",
    # Gravedad
    "Leve": "#27AE60", "Grave": "#E67E22", "Mortal": "#C0392B"
}

print("--- GENERANDO SANKEY 4 ETAPAS: UBICACIÓN -> TIPO -> MOMENTO -> GRAVEDAD ---")

g = rdflib.Graph()
g.parse(ARCHIVO_RDF, format="turtle")

# 1. CONSULTA SPARQL EXTENDIDA
query = """
PREFIX ex: <http://proyecto-accidentes.ua.es/resource/>
PREFIX schema1: <http://schema.org/>

SELECT ?zona ?tipoNombre ?iluminacion ?gravedad
WHERE {
    ?acc a schema1:Event .
    OPTIONAL { ?acc ex:zona ?zona . }
    OPTIONAL { ?acc schema1:name ?tipoNombre . }
    OPTIONAL { ?acc ex:iluminacion ?iluminacion . }
    OPTIONAL { ?acc ex:gravedad ?gravedad . }
}
"""
results = g.query(query)

data = []
for r in results:
    data.append({
        "zona": str(r.zona) if r.zona else "Desconocida",
        "tipo": str(r.tipoNombre) if r.tipoNombre else "Otros",
        "luz": str(r.iluminacion) if r.iluminacion else "Desconocida",
        "gravedad": str(r.gravedad) if r.gravedad else "Leve"
    })

df = pd.DataFrame(data)

# 2. LÓGICA DE LIMPIEZA Y CATEGORIZACIÓN
def categorizar_ubicacion(z):
    z = z.lower()
    if "carretera" in z: return "Carretera"
    if "calle" in z or "zona urbana" in z: return "Calle/Urbana"
    return "Otras Zonas"

def categorizar_tipo(t):
    t = t.lower()
    if "atropello" in t: return "Atropello"
    if "salida" in t: return "Salida Vía"
    if any(x in t for x in ["frontal", "alcance", "lateral", "múltiple", "colisión"]): return "Colisión"
    return "Otros"

def categorizar_momento(l):
    l = l.lower()
    if "luz del día" in l: return "Día"
    if "noche" in l or "sin luz" in l: return "Noche"
    if "amanecer" in l or "atardecer" in l: return "Crepúsculo"
    return "Día" # Valor por defecto

def categorizar_gravedad(g):
    g = g.lower()
    if "leve" in g: return "Leve"
    if "grave" in g: return "Grave"
    if "mortal" in g or "fallecido" in g: return "Mortal"
    return "Leve"

# Aplicar limpieza
df['etapa1'] = df['zona'].apply(categorizar_ubicacion)
df['etapa2'] = df['tipo'].apply(categorizar_tipo)
df['etapa3'] = df['luz'].apply(categorizar_momento)
df['etapa4'] = df['gravedad'].apply(categorizar_gravedad)

# 3. GENERAR LÍNEAS DE FLUJO PARA SANKEYMATIC
# El truco es sumar los flujos de cada par de columnas consecutivas
lines = ["// --- DIAGRAMA DE FLUJO DE ACCIDENTES ---", ""]

# Añadir definición de colores
for nombre, color in COLORES.items():
    lines.append(f":{nombre} {color}")
lines.append("")

# Función auxiliar para agrupar pares de columnas
def obtener_flujos(df, col_origen, col_destino):
    agrupado = df.groupby([col_origen, col_destino]).size().reset_index(name='qty')
    return [f"{r[col_origen]} [{r['qty']}] {r[col_destino]}" for _, r in agrupado.iterrows() if r['qty'] > 0]

# Unir todos los flujos
lines.extend(obtener_flujos(df, 'etapa1', 'etapa2')) # Ubicación -> Tipo
lines.extend(obtener_flujos(df, 'etapa2', 'etapa3')) # Tipo -> Momento
lines.extend(obtener_flujos(df, 'etapa3', 'etapa4')) # Momento -> Gravedad

# 4. GUARDAR
with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"✅ Archivo generado para SankeyMatic: {ARCHIVO_SALIDA}")