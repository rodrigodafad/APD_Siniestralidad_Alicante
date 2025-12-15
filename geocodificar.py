import rdflib
import pandas as pd
from geopy.geocoders import ArcGIS
from geopy.distance import geodesic # Para medir distancias
from SPARQLWrapper import SPARQLWrapper, JSON
from tqdm import tqdm
import re
import time

# --- CONFIGURACIÓN ---
ARCHIVO_RDF = "accidentes_cv_graph.ttl"
ARCHIVO_SALIDA = "accidentes_exactos.csv"
UMBRAL_SCORE = 75      # Confianza mínima de ArcGIS (0-100)
RADIO_CONFIANZA = 15   # Km máximos desde el centro del pueblo para aceptarlo

print(f"--- GEOCODIFICADO (Score > {UMBRAL_SCORE} | Radio < {RADIO_CONFIANZA}km) ---\n")

# 1. CARGAR RDF
print("1. Leyendo archivo RDF...")
g = rdflib.Graph()
try:
    g.parse(ARCHIVO_RDF, format="turtle")
except Exception as e:
    print(f"❌ Error RDF: {e}")
    exit()

query = """
PREFIX ex: <http://proyecto-accidentes.ua.es/resource/>
PREFIX schema1: <http://schema.org/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?accidente ?gravedad ?direccion ?wikidata_id
WHERE {
    ?accidente a schema1:Event ;
               ex:gravedad ?gravedad ;
               schema1:location ?lugar .
    
    ?lugar schema1:address ?direccion ;
           owl:sameAs ?wikidata_id .
}
"""
results = g.query(query)

accidentes = []
municipios_ids = set()

for r in results:
    wd_id = str(r.wikidata_id).split('/')[-1]
    accidentes.append({
        "id": str(r.accidente).split('/')[-1],
        "gravedad": str(r.gravedad),
        "direccion": str(r.direccion),
        "wd_id": wd_id
    })
    municipios_ids.add(wd_id)

print(f"   -> {len(accidentes)} accidentes totales.")

# 2. PRE-CARGA WIKIDATA (Necesaria para el 'Círculo de Confianza')
print(f"2. Obteniendo centros de municipios (Para validar distancias)...")
cache_centros = {} # { 'Q123': (lat, lon) }
cache_nombres = {} # { 'Q123': 'Agost' }

lista_ids = list(municipios_ids)
CHUNK_SIZE = 50 

for i in range(0, len(lista_ids), CHUNK_SIZE):
    chunk = lista_ids[i:i+CHUNK_SIZE]
    ids_str = " ".join([f"wd:{wd}" for wd in chunk])
    
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    q = f"""
    SELECT ?item ?itemLabel ?coords WHERE {{
      VALUES ?item {{ {ids_str} }}
      ?item wdt:P625 ?coords .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],es". }}
    }}
    """
    sparql.setQuery(q)
    sparql.setReturnFormat(JSON)
    try:
        res = sparql.query().convert()
        for r in res["results"]["bindings"]:
            wd = r["item"]["value"].split("/")[-1]
            wkt = r["coords"]["value"]
            lon, lat = wkt.replace("Point(", "").replace(")", "").split(" ")
            cache_centros[wd] = (float(lat), float(lon))
            if "itemLabel" in r: cache_nombres[wd] = r["itemLabel"]["value"]
    except: pass

# -------------------------------------------------------------------------
# FUNCIONES DE FILTRADO
# -------------------------------------------------------------------------

def es_direccion_potable(direccion):
    """Filtro Sintáctico: ¿Parece una dirección útil?"""
    d = direccion.upper().strip()
    
    # 1. Filtro 'No Inventariada'
    if "NO INVENTARIADA" in d: return False
    
    # 2. Filtro KM 0 (Falso positivo muy común)
    # Detecta "KM 0" o "KM 00" pero deja pasar "KM 0.5" o "KM 0,5"
    if re.search(r'KM\s+0+(?![.,]\d)', d): return False
    
    # 3. Debe tener números
    if not re.search(r'\d', d): return False
    
    # 4. Prefijos Válidos
    patron_carretera = r'^(CV|N|A|AP|CS|V|EL|RM|MU)[\s-]?\d+'
    patron_urbano = r'^(CALLE|C/|CARRER|AV|AVDA|AVENIDA|AVINGUDA|PLAZA|PLAÇA|CAMINO|CAMI|CTRA|CARRETERA|PARTIDA|POLIGONO)'
    
    if re.match(patron_carretera, d): return True
    if re.match(patron_urbano, d): return True
    
    return False

# 3. PROCESO DE GEOCODIFICACIÓN
print("3. Ejecutando Geocodificación Estricta...")
geolocator = ArcGIS()
resultados = []
stats = {"descartados_sintaxis": 0, "descartados_score": 0, "descartados_distancia": 0, "exito": 0}

for acc in tqdm(accidentes):
    direccion = acc['direccion'].strip()
    wd_id = acc['wd_id']
    
    # --- FILTRO 1: SINTAXIS ---
    if not es_direccion_potable(direccion):
        stats["descartados_sintaxis"] += 1
        continue
        
    nombre_pueblo = cache_nombres.get(wd_id, "Alicante")
    direccion_limpia = direccion.replace("KM", "km").replace(",", "")
    busqueda = f"{direccion_limpia}, {nombre_pueblo}, España"
    
    try:
        location = geolocator.geocode(busqueda, timeout=2)
        
        if location:
            # --- FILTRO 2: SCORE DE ARCGIS ---
            # location.raw contiene el JSON de respuesta. 'Score' suele ser de 0 a 100.
            score = location.raw.get('score', 0)
            if score < UMBRAL_SCORE:
                stats["descartados_score"] += 1
                continue
                
            # --- FILTRO 3: CÍRCULO DE CONFIANZA ---
            # Si ArcGIS dice que está en Cuenca, pero el pueblo es Agost... fuera.
            lat_arcgis, lon_arcgis = location.latitude, location.longitude
            
            if wd_id in cache_centros:
                centro_pueblo = cache_centros[wd_id]
                distancia = geodesic((lat_arcgis, lon_arcgis), centro_pueblo).km
                
                if distancia > RADIO_CONFIANZA:
                    stats["descartados_distancia"] += 1
                    continue
            
            # --- ACEPTADO ---
            resultados.append({
                "id": acc['id'],
                "gravedad": acc['gravedad'],
                "direccion_orig": direccion,
                "lat": lat_arcgis,
                "lon": lon_arcgis,
                "wd_id": wd_id,
                "score": score
            })
            stats["exito"] += 1
            
    except:
        pass # Error de conexión

# 4. GUARDAR
df_final = pd.DataFrame(resultados)
df_final.to_csv(ARCHIVO_SALIDA, index=False)

print(f"\n✅ PROCESO FINALIZADO.")
print(f"   📊 ESTADÍSTICAS DE CALIDAD:")
print(f"   - Total Accidentes: {len(accidentes)}")
print(f"   - 🗑️ Basura Sintáctica (KM 0, Sin números): {stats['descartados_sintaxis']}")
print(f"   - 🎯 Descartados por Baja Precisión (<{UMBRAL_SCORE}%): {stats['descartados_score']}")
print(f"   - 🌍 Descartados por Lejanía (>{RADIO_CONFIANZA}km): {stats['descartados_distancia']}")
print(f"   - ⭐ PUNTOS VÁLIDOS FINALES: {stats['exito']}")
print(f"   -> Archivo guardado: {ARCHIVO_SALIDA}")