# 🚗 DGT Data Engineering Pipeline (2016-2024)

> **ETL Pipeline & Dimensional Modeling for Traffic Accident Analysis**
> *Proyecto de Ingeniería de Datos para la consolidación, limpieza y normalización de 9 años de microdatos de accidentes de tráfico en España (DGT).*

![Pentaho](https://img.shields.io/badge/Pentaho-Data_Integration-blue?style=for-the-badge&logo=pentaho) ![Excel](https://img.shields.io/badge/Microsoft_Excel-Streaming_API-green?style=for-the-badge&logo=microsoft-excel) ![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)

## 📋 Descripción del Proyecto

Este repositorio contiene el flujo de trabajo ETL desarrollado en **Pentaho Data Integration (PDI/Kettle)** para procesar datos históricos de accidentes de tráfico proporcionados por la DGT.

El objetivo principal es transformar archivos crudos y desnormalizados en un **Modelo Dimensional (Esquema de Estrella)** optimizado para herramientas de Business Intelligence, permitiendo el análisis de tendencias a largo plazo en la provincia de Alicante.

### 🎯 Objetivos Técnicos
* **Ingesta Masiva:** Procesamiento eficiente de archivos históricos anuales.
* **Limpieza de Datos:** Estandarización de columnas y filtrado geográfico ("Filter Early").
* **Enriquecimiento:** Generación de nuevas métricas (franjas horarias, clasificación de días).
* **Optimización:** Uso de técnicas *In-Memory* para cruces de diccionarios y *Streaming* para lectura de archivos pesados.

---

## 🏗️ Arquitectura del Flujo (Pipeline)

El proyecto se divide en tres componentes principales orquestados por un Job maestro.

### 1. 🔄 Flujo Principal: `Limpieza_Datos_DGT.ktr`
Es el núcleo del ETL. Realiza las siguientes operaciones:
* **Extracción (Extract):** Lectura de microdatos con **Apache POI Streaming** para evitar saturación de memoria RAM.
* **Transformación (Transform):**
    * *Filtrado:* Restricción a `PROVINCIA = 3` (Alicante).
    * *Binning:* Creación de categorías (`Madrugada/Mañana/Tarde/Noche`) y tipos de día (`Laborable/Fin de Semana`).
    * *Broadcasting:* División del flujo en 7 ramas paralelas.
    * *Lookups:* Decodificación de códigos numéricos usando un diccionario maestro cargado en memoria (Cache).
* **Carga (Load):** Generación de archivos Excel independientes para cada dimensión y tabla de hechos.

### 2. 🗜️ Compresor y Unificación: `csv_compressor.ktr`
Un flujo auxiliar diseñado para consolidar múltiples salidas parciales en archivos maestros unificados (`all_in_one`), facilitando la carga final en la herramienta de visualización.

### 3. 🤖 Orquestador: `Job.kjb`
Controla el ciclo de vida de la ejecución:
1.  **START:** Inicio del cronograma.
2.  **TRANSFORMATION:** Ejecuta la limpieza y lógica de negocio.
3.  **SUCCESS:** Validación y notificación de término exitoso.
