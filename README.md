# 🚗 Análisis de Siniestralidad Vial en Alicante (2016-2024)

**Asignatura:** Adquisición y preparación de datos (UA)
**Autores:** Stanislav Gatin, Alejandro García, Guillermo García, Rodrigo Gavilán.

## 📋 Descripción
Proyecto de análisis de datos para identificar patrones de letalidad en accidentes de tráfico. Se procesan microdatos de la DGT, se enriquecen con fuentes externas (Wikidata, GVA) y se generan visualizaciones geoespaciales y de flujo para la toma de decisiones.

## 📂 Contenido del Repositorio

### ⚙️ Scripts de Procesamiento
* **`geocodificar.py`**: Limpieza y georreferenciación. Filtra direcciones inválidas y utiliza la API de ArcGIS para validar coordenadas (score > 75).
* **`sankey.py`**: Procesa el grafo RDF y genera el **texto plano** formateado para crear los diagramas en [SankeyMATIC](https://sankeymatic.com/).
* **`map.py`**: Genera el mapa interactivo HTML cruzando puntos geocodificados con polígonos municipales y datos de Wikidata.

### 💾 Datos Fuente
* **`accidentes_cv_graph.ttl`**: Dataset transformado a Linked Data (RDF) con schema.org.
* **`municipios_cv.geojson`**: Perímetros municipales. Fuente: *Dades Obertes Generalitat Valenciana*.

### 📈 Visualizaciones (Resultados)
* **`mapa.html`**: Mapa interactivo híbrido (Coropletas + Puntos Exactos).
* **`flujo_completo.svg`**: Diagrama de Sankey global (Vía $\to$ Tipo $\to$ Hora $\to$ Gravedad).
* **`tipo_accidente-gravedad.svg`**: Diagrama específico relacionando la mecánica del accidente con la letalidad.
* **`tipo_via-gravedad.svg`**: Diagrama específico comparando siniestralidad en carreteras vs. zona urbana.

## 📊 Detalle de las Visualizaciones
1.  **Mapa Híbrido (`mapa.html`):** Generado por `map.py`. Permite explorar la densidad de accidentes por municipio y localizar tramos concretos de alta siniestralidad ("puntos negros") enriquecidos con datos demográficos.
2.  **Diagramas de Sankey (`.svg`):** Generados mediante *SankeyMATIC* con los datos extraídos por `sankey.py`.
    * El flujo completo permite ver la "historia" del accidente desde el entorno hasta la consecuencia.
    * Los diagramas específicos aíslan variables críticas para entender qué factores (tipo de vía o maniobra) aumentan la probabilidad de muerte o heridas graves.

## 🛠️ Requisitos
```bash
pip install pandas rdflib folium geopy SPARQLWrapper
