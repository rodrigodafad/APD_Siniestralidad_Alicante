# 🚗 Análisis de Siniestralidad Vial en Alicante (2016-2024)

**Asignatura:** Adquisición y preparación de datos (UA)
**Autores:** Stanislav Gatin, Alejandro García, Guillermo García, Rodrigo Gavilán.

## 📋 Descripción
Proyecto de análisis de datos para identificar patrones de letalidad en accidentes de tráfico. Se procesan microdatos de la DGT, se enriquecen con fuentes externas (Wikidata, GVA) y se generan visualizaciones geoespaciales y de flujo.

## 📂 Contenido del Repositorio

### Scripts de Procesamiento
* **`geocodificar.py`**: Limpieza y georreferenciación. Filtra direcciones inválidas y utiliza la API de ArcGIS para validar coordenadas (score > 75).
* **`sankey.py`**: Procesa el grafo RDF y genera el **texto plano** formateado para crear el diagrama de flujo en [SankeyMATIC](https://sankeymatic.com/).
* **`map.py`**: Genera un mapa interactivo en formato HTML. Cruza los puntos geocodificados con los polígonos municipales y datos de Wikidata.

### Datos
* **`municipios_cv.geojson`**: Archivo con los perímetros fronterizos de los municipios. Fuente original: *Dades Obertes Generalitat Valenciana*.

## 📊 Visualizaciones
1.  **Mapa Híbrido (`.html`):** Visualización generada por `map.py` que combina coropletas (densidad de accidentes por municipio) con marcadores de "puntos negros" exactos.
2.  **Diagrama de Sankey:** Flujo de causalidad (Tipo Accidente $\to$ Gravedad) generado en SankeyMATIC a partir del output de `sankey.py`.

## 🛠️ Requisitos
```bash
pip install pandas rdflib folium geopy SPARQLWrapper
