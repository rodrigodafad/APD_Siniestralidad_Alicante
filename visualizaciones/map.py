import json
import folium
import rdflib
import pandas as pd
from pyproj import Transformer
from SPARQLWrapper import SPARQLWrapper, JSON
import branca.colormap as cm
import os
import random

# --- CONFIGURACIÓN ---
ARCHIVO_RDF = "accidentes_cv_graph.ttl"
ARCHIVO_GEOJSON = "municipios_cv.geojson"
ARCHIVO_PUNTOS = "accidentes_exactos.csv" 
ARCHIVO_SALIDA = "mapa_alicante_final_sincronizado.html"
CENTRO_MAPA = [38.3452, -0.4810]

print("--- GENERADOR DE MAPA FINAL (CONTADORES SINCRONIZADOS) ---\n")

# 1. CARGAR Y REPARAR GEOJSON
if not os.path.exists(ARCHIVO_GEOJSON):
    print(f"❌ Falta {ARCHIVO_GEOJSON}"); exit()
with open(ARCHIVO_GEOJSON, "r", encoding="utf-8") as f: geo_data = json.load(f)

transformer = Transformer.from_crs("EPSG:25830", "EPSG:4326", always_xy=True)
def transformar_poly(coords):
    if isinstance(coords[0][0], (float, int)): return [list(transformer.transform(x, y)) for x, y in coords]
    else: return [transformar_poly(c) for c in coords]
todos_ines = []
for feature in geo_data['features']:
    feature['geometry']['coordinates'] = transformar_poly(feature['geometry']['coordinates'])
    if 'MUNIINE' in feature['properties']: todos_ines.append(feature['properties']['MUNIINE'].zfill(5))

# 2. CONSULTAR WIKIDATA
print("2. Consultando datos demográficos...")
ids_str = ' '.join([f'"{ine}"' for ine in todos_ines])
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setQuery(f"""
SELECT ?ine (SAMPLE(?pop) as ?poblacion) (SAMPLE(?area) as ?superficie) (SAMPLE(?img) as ?imagen)
WHERE {{
  VALUES ?ine {{ {ids_str} }}
  ?item wdt:P772 ?ine .
  OPTIONAL {{ ?item wdt:P1082 ?pop . }}
  OPTIONAL {{ ?item wdt:P2046 ?area . }}
  OPTIONAL {{ ?item wdt:P18 ?img . }}
}}
GROUP BY ?ine
""")
sparql.setReturnFormat(JSON)
try: wd_results = sparql.query().convert()
except: wd_results = {"results": {"bindings": []}}

datos_wd = {}
for res in wd_results["results"]["bindings"]:
    ine = res["ine"]["value"]
    area_fmt = "?"
    if "superficie" in res:
        try:
            val = float(res['superficie']['value'])
            if val > 10000: val = val / 1_000_000
            area_fmt = f"{val:.1f}"
        except: pass
    datos_wd[ine] = {
        "poblacion": res["poblacion"]["value"] if "poblacion" in res else "N/D",
        "area": area_fmt,
        "imagen": res["imagen"]["value"] if "imagen" in res else "https://upload.wikimedia.org/wikipedia/commons/1/14/No_Image_Available.jpg"
    }

# 3. CÁLCULO DE ACCIDENTES (LÓGICA CORREGIDA)
print("3. Calculando estadísticas...")

# A) TOTALES (Desde RDF) - Esto no cambia, es el universo total
g = rdflib.Graph(); g.parse(ARCHIVO_RDF, format="turtle")
q_map = """PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT ?wikidata_id WHERE { ?s <http://schema.org/location> ?loc . ?loc owl:sameAs ?wikidata_id . }"""
wd_ids_rdf = [str(r.wikidata_id).split('/')[-1] for r in g.query(q_map)]
uniq_wd = list(set(wd_ids_rdf))
if uniq_wd:
    sp2 = SPARQLWrapper("https://query.wikidata.org/sparql")
    sp2.setQuery(f"SELECT ?item ?ine WHERE {{ VALUES ?item {{ {' '.join(['wd:'+w for w in uniq_wd])} }} ?item wdt:P772 ?ine . }}")
    sp2.setReturnFormat(JSON)
    try: map_wd_ine = {r["item"]["value"].split("/")[-1]: r["ine"]["value"].zfill(5) for r in sp2.query().convert()["results"]["bindings"]}
    except: map_wd_ine = {}
else: map_wd_ine = {}
ines_total = [map_wd_ine.get(wd) for wd in wd_ids_rdf if wd in map_wd_ine]
df_total = pd.Series(ines_total).value_counts()

# B) DIBUJADOS (Desde CSV) - AQUÍ ESTÁ LA CORRECCIÓN
if os.path.exists(ARCHIVO_PUNTOS):
    df_pts = pd.read_csv(ARCHIVO_PUNTOS)
    
    # 1. Mapeamos INE
    df_pts['ine'] = df_pts['wd_id'].map(map_wd_ine)
    
    # 2. LIMPIEZA CRÍTICA: Eliminamos filas que no se van a poder dibujar
    # (Si no tienen lat/lon o no tienen INE válido, las borramos AHORA del conteo)
    df_dibujables = df_pts.dropna(subset=['lat', 'lon', 'ine'])
    
    # 3. Contamos solo las supervivientes
    df_dibujados = df_dibujables['ine'].value_counts()
    
    # Usaremos df_dibujables para el bucle de pintado, asegurando coincidencia 1:1
else:
    df_dibujables = pd.DataFrame()
    df_dibujados = pd.Series()

# 4. RENDERIZAR MAPA
print("4. Generando mapa...")
m = folium.Map(location=CENTRO_MAPA, zoom_start=9, tiles="cartodbpositron")
colormap = cm.LinearColormap(colors=['#FFEDA0', '#E31A1C'], vmin=0, vmax=df_total.max() if not df_total.empty else 10)
colormap.caption = "Total Accidentes Registrados"
colormap.add_to(m)

for feature in geo_data['features']:
    props = feature['properties']
    if 'MUNIINE' in props:
        ine = props['MUNIINE'].zfill(5)
        
        totales = int(df_total.get(ine, 0))
        dibujados = int(df_dibujados.get(ine, 0)) # Este número ahora es exacto
        info = datos_wd.get(ine, {"poblacion": "N/D", "area": "-", "imagen": ""})

        props['TOTAL_ACC'] = totales
        props['RESUMEN'] = f"{totales} ({dibujados} visibles)"
        
        html = f"""
        <div style="font-family:Arial; width:220px;">
            <h4 style="margin:0 0 10px 0; color:#2c3e50;">{props['NOMBRE']}</h4>
            <div style="width:100%; height:120px; background-color:#eee; margin-bottom:10px; border-radius:4px; overflow:hidden;">
                <img src="{info['imagen']}" style="width:100%; height:100%; object-fit:cover;" onerror="this.src='https://upload.wikimedia.org/wikipedia/commons/1/14/No_Image_Available.jpg'">
            </div>
            <table style="width:100%; font-size:13px; border-collapse:collapse;">
                <tr style="border-bottom:1px solid #ddd;">
                    <td style="padding:4px;">⚠️ <b>Accidentes:</b></td>
                    <td style="text-align:right;">
                        <span style="color:#e74c3c; font-weight:bold;">{totales}</span>
                        <span style="color:#7f8c8d; font-size:11px;"> ({dibujados} en mapa)</span>
                    </td>
                </tr>
                <tr style="border-bottom:1px solid #ddd;">
                    <td style="padding:4px;">👥 <b>Población:</b></td>
                    <td style="text-align:right;">{info['poblacion']}</td>
                </tr>
                <tr>
                    <td style="padding:4px;">📏 <b>Área:</b></td>
                    <td style="text-align:right;">{info['area']} km²</td>
                </tr>
            </table>
        </div>
        """
        props['html_info'] = html

# Capa Municipios
folium.GeoJson(
    geo_data,
    name="Municipios",
    style_function=lambda x: {'fillColor': colormap(x['properties']['TOTAL_ACC']), 'color': 'gray', 'weight': 0.5, 'fillOpacity': 0.6},
    highlight_function=lambda x: {'weight': 2, 'color': 'black'},
    tooltip=folium.GeoJsonTooltip(fields=['NOMBRE', 'RESUMEN'], aliases=['Municipio:', 'Accidentes:']),
    popup=folium.GeoJsonPopup(fields=['html_info'], labels=False)
).add_to(m)

# Capa Puntos (Usamos df_dibujables que ya está filtrado)
fg = folium.FeatureGroup(name="Puntos Exactos")
for _, row in df_dibujables.iterrows():
    # Ya no hace falta try-except porque filtramos los NaNs antes
    lat = float(row['lat']) + random.uniform(-0.0001, 0.0001)
    lon = float(row['lon']) + random.uniform(-0.0001, 0.0001)
    
    gravedad = str(row['gravedad'])
    if gravedad in ["Mortal", "Fallecido"]:
        c = "black"
    elif gravedad == "Leve":
        c = "#f1c40f" # Amarillo
    else:
        c = "#e74c3c" # Rojo
        
    folium.CircleMarker([lat, lon], radius=4, color=c, fill=True, fill_opacity=1, weight=0.5, popup=row['direccion_orig']).add_to(fg)

fg.add_to(m)

folium.LayerControl().add_to(m)
m.save(ARCHIVO_SALIDA)
print(f"✅ ¡MAPA SINCRONIZADO! Abre: {ARCHIVO_SALIDA}")
