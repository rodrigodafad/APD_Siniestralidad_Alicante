# 🚗 Análisis de Siniestralidad Vial en Alicante (2016-2023)

**Asignatura:** Adquisición y preparación de datos (UA)
**Autores:** Stanislav Gatin, Alejandro García, Guillermo García, Rodrigo Gavilán.

## 📋 Descripción del Trabajo
Este proyecto analiza los accidentes de tráfico en la provincia de Alicante para identificar patrones de gravedad y puntos negros. Se ha realizado un proceso de ingestión de microdatos oficiales, limpieza, geocodificación y transformación a **Linked Data (RDF)** para su posterior visualización y enriquecimiento con datos demográficos externos.

## 📂 Contenido del Repositorio

### Código y Transformaciones
* `geocodificar.py`: Script de limpieza y georreferenciación utilizando la API de ArcGIS. Filtra direcciones inválidas y asegura la precisión espacial (radio < 15km).
* `sankey.py`: Generación de datos para el análisis de flujos (Tipo de Accidente $\to$ Gravedad) consultando el grafo RDF.
* `map.py`: Creación del mapa interactivo híbrido. Cruza los datos de accidentes con consultas SPARQL a Wikidata (población y superficie).

### Datos
* `accidentes_cv_graph.ttl`: Dataset final transformado a RDF utilizando el vocabulario **schema.org**.
* `municipios_cv.geojson`: Cartografía base para las visualizaciones espaciales.

## 📊 Visualizaciones Generadas
1.  **Mapa Híbrido:** Combina un mapa de coropletas (densidad de accidentes por municipio) con la ubicación exacta de los siniestros graves y mortales.
2.  **Diagrama de Sankey:** Visualiza la relación de causalidad entre la tipología del accidente (ej. Atropello, Salida de Vía) y la gravedad de las víctimas.

## 🛠️ Requisitos
```bash
pip install pandas rdflib folium geopy SPARQLWrapper
