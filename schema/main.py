import pandas as pd
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD, RDFS, OWL
import warnings

warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

df_hechos = pd.read_excel("dim_clima/hecho_accidente.xls")
df_ubi = pd.read_excel("dim_clima/dim_ubicacion.xls", dtype={'COD_MUNICIPIO': str}) 
df_tipo = pd.read_excel("dim_clima/dim_tipo_accidente.xls")
df_via = pd.read_excel("dim_clima/dim_via.xls")
df_clima = pd.read_excel("dim_clima/dim_clima.xls")
df_tipo_senalizacion = pd.read_excel("dim_clima/dim_prioridad_senalizacion.xls")

# --- 2. UNIFICACIÓN (JOIN) ---
print("Unificando tablas...")
df_full = df_hechos.merge(df_ubi, on="ID_ACCIDENTE") \
                    .merge(df_tipo, on="ID_ACCIDENTE") \
                    .merge(df_via, on="ID_ACCIDENTE") \
                    .merge(df_clima, on="ID_ACCIDENTE") \
                    .merge(df_tipo_senalizacion, on="ID_ACCIDENTE")


print(f"Total de accidentes a procesar: {len(df_full)}")
print("Columnas: ", df_full.columns)

# --- 3. DICCIONARIO WIKIDATA (DESDE CSV) ---
print("Cargando diccionario de municipios desde 'municipios_alicante.csv'...")

mapa_wikidata = {}

df_wiki = pd.read_csv("municipios_alicante.csv", dtype={'codigoINE': str})

for index, row in df_wiki.iterrows():
    # 1. Obtener el Q-ID limpiando la URL
    # Viene así: http://www.wikidata.org/entity/Q11959
    # Hacemos split por '/' y nos quedamos el último trozo -> Q11959
    url_completa = str(row['municipio'])
    q_id = url_completa.split('/')[-1]
    
    # 2. Normalizar el Código INE a 5 dígitos
    # Si viene "3014", lo convierte a "03014"
    cod_ine = str(row['codigoINE'])

    # 3. Guardar en el diccionario
    mapa_wikidata[cod_ine] = q_id


g = Graph()


SCHEMA = Namespace("http://schema.org/")
EX = Namespace("http://proyecto-accidentes.ua.es/resource/")
WD = Namespace("http://www.wikidata.org/entity/")

g.bind("schema", SCHEMA)
g.bind("ex", EX)
g.bind("owl", OWL)
g.bind("wd", WD)

# 1. Métricas de víctimas
for prop in ["fallecidos", "heridosGraves", "heridosLeves"]:
    g.add((EX[prop], RDF.type, RDF.Property))
    g.add((EX[prop], RDFS.domain, SCHEMA.Event))
    g.add((EX[prop], RDFS.range, XSD.integer))

# 2. Factores ambientales y de la vía
props_texto = [
    "clima", "iluminacion", "estadoFirme", "trazado", 
    "zona", "niebla", "viento", "titularidad", "tipoVia",
    "controlTrafico" # Aquí unificaremos las señales
]

for prop in props_texto:
    g.add((EX[prop], RDF.type, RDF.Property))
    g.add((EX[prop], RDFS.domain, SCHEMA.Event))
    g.add((EX[prop], RDFS.range, XSD.string))

# --- 5. GENERACIÓN DE TRIPLETAS ---
print("Generando grafo RDF...")
contador = 0
for index, row in df_full.iterrows():
    acc_id = str(row['ID_ACCIDENTE'])
    
    # === A. EL EVENTO (ACCIDENTE) ===
    uri_evento = EX[f"accidente_{acc_id}"]
    g.add((uri_evento, RDF.type, SCHEMA.Event))
    
    # 1. Nombre limpio (sin espacios extra)
    nombre_accidente = f"Accidente: {str(row['TIPO_ACCIDENTE']).strip()}"
    g.add((uri_evento, SCHEMA.name, Literal(nombre_accidente)))
    
    # 2. Descripción completa
    clima = str(row['CONDICION_METEO']).strip() if pd.notna(row['CONDICION_METEO']) else "Desconocido"
    via_nombre = str(row['CARRETERA']).strip() if pd.notna(row['CARRETERA']) else "Vía sin nombre"
    desc = f"Accidente en {via_nombre} con clima {clima}."
    g.add((uri_evento, SCHEMA.description, Literal(desc)))
    
    # 3. Fecha ISO (Estrategia día 01)
    try:
        anyo = int(row['ANYO'])
        mes = int(row['MES'])
        hora = int(row['HORA'])
        # Formato YYYY-MM-DDTHH:MM:SS (Asumimos día 1)
        fecha_iso = f"{anyo}-{mes:02d}-01T{hora:02d}:00:00"
        g.add((uri_evento, SCHEMA.startDate, Literal(fecha_iso, datatype=XSD.dateTime)))
    except (ValueError, TypeError):
        pass # Si faltan datos de tiempo, saltamos la fecha

    
    gravedad = "Leve"
    if row['TOTAL_MU24H'] > 0:
        gravedad = "Mortal"
    elif row['TOTAL_HG24H'] > 0:
        gravedad = "Grave"
    g.add((uri_evento, EX.gravedad, Literal(gravedad)))
    
    if pd.notna(row['CONDICION_ILUMINACION']):
        g.add((uri_evento, EX.iluminacion, Literal(str(row['CONDICION_ILUMINACION']).strip())))
    
    if pd.notna(row['TITULARIDAD_VIA']):
        g.add((uri_evento, EX.tipoVia, Literal(str(row['TITULARIDAD_VIA']).strip())))
        
    # Para el RIDGELINE PLOT (Tiempo desagregado)
    if pd.notna(row['HORA']):
        try:
            g.add((uri_evento, EX.hora, Literal(int(row['HORA']), datatype=XSD.integer)))
        except: pass
        
    if pd.notna(row['DIA']): # Lunes, Martes...
        g.add((uri_evento, EX.diaSemana, Literal(str(row['DIA']).strip())))
    
    if pd.notna(row['MES']):
        try:
            g.add((uri_evento, EX.mes, Literal(int(row['MES']), datatype=XSD.integer)))
        except: pass

    # [MÉTRICAS]
    muertos = int(row['TOTAL_MU24H']) if pd.notna(row['TOTAL_MU24H']) else 0
    graves = int(row['TOTAL_HG24H']) if pd.notna(row['TOTAL_HG24H']) else 0
    leves = int(row['TOTAL_HL24H']) if pd.notna(row['TOTAL_HL24H']) else 0

    if muertos > 0: g.add((uri_evento, EX.fallecidos, Literal(muertos, datatype=XSD.integer)))
    if graves > 0:  g.add((uri_evento, EX.heridosGraves, Literal(graves, datatype=XSD.integer)))
    if leves > 0:   g.add((uri_evento, EX.heridosLeves, Literal(leves, datatype=XSD.integer)))

    # [ENTORNO Y VÍA] Mapeo directo si existe el dato
    mappings = {
        'CONDICION_METEO': EX.clima,
        'CONDICION_ILUMINACION': EX.iluminacion,
        'CONDICION_FIRME': EX.estadoFirme,
        'TRAZADO_PLANTA': EX.trazado,
        'ZONA': EX.zona,
        'CONDICION_NIEBLA': EX.niebla,
        'CONDICION_VIENTO': EX.viento
    }

    for columna, propiedad_rdf in mappings.items():
        if pd.notna(row[columna]):
            valor_limpio = str(row[columna]).strip()
            # Filtramos valores "desconocidos" o vacíos si quieres
            if valor_limpio and valor_limpio.upper() != "SIN ESPECIFICAR": 
                g.add((uri_evento, propiedad_rdf, Literal(valor_limpio)))

    # [SEÑALIZACIÓN] Lógica especial: Agrupar prioridades
    # Si hay semáforo, stop o agente, lo metemos en 'ex:controlTrafico'
    control = []
    if str(row['PRIORI_SEMAFORO']) == "Sí": control.append("Semáforo")
    if str(row['PRIORI_AGENTE']) == "Sí": control.append("Agente")
    if str(row['PRIORI_HORIZ_STOP']) == "Sí" or str(row['PRIORI_VERT_STOP']) == "Sí": control.append("Stop")
    
    if control:
        # Crea un string tipo "Semáforo, Stop"
        g.add((uri_evento, EX.controlTrafico, Literal(", ".join(control))))
    # === C. EL LUGAR (UBICACIÓN) ===
    uri_lugar = EX[f"lugar_{acc_id}"]
    g.add((uri_lugar, RDF.type, SCHEMA.Place))
    
    # Conexión Evento -> Lugar
    g.add((uri_evento, SCHEMA.location, uri_lugar))
    
    # Dirección Física
    km_str = f", KM {row['KM']}" if pd.notna(row['KM']) else ""
    direccion_completa = f"{via_nombre}{km_str}"
    g.add((uri_lugar, SCHEMA.address, Literal(direccion_completa)))
    
    
    cod_ine = str(row['COD_MUNICIPIO']).split('.')[0]
    

    if cod_ine in mapa_wikidata:
        wd_id = mapa_wikidata[cod_ine]
        g.add((uri_lugar, OWL.sameAs, URIRef(WD + wd_id)))
    else:
        if cod_ine == "00000": # Ignoramos los ceros que ya sabemos que son error
            contador +=1

# --- 6. EXPORTAR RESULTADO ---
archivo_salida = "accidentes_cv_graph.ttl"
g.serialize(destination=archivo_salida, format="turtle")
print(f"Aviso, hay un total de {contador} accidentes sin codigo INE")
print(f"¡ÉXITO! Se ha generado el archivo: {archivo_salida}")