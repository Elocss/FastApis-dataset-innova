# Observatorio de Indicadores Regionales: Argentina, Uruguay y Chile
## Pipeline de datos con FastAPI, ILOSTAT y CEPALSTAT

Este repositorio contiene una API FastAPI para generar datasets regionales, depurar indicadores socioeconómicos y consultar un catálogo de **5 sectores estratégicos** y **20 ocupaciones clave** para el Cono Sur (**Argentina, Uruguay y Chile**).

### Estado actual de las fuentes

* **ILOSTAT:** se intenta consultar la API SDMX para la tasa de desocupación. Si la consulta falla o no devuelve datos, se utiliza una serie histórica local de respaldo.
* **CEPALSTAT:** los indicadores se generan desde un repositorio local homologado incluido en el código; actualmente no hay una consulta HTTP a CEPALSTAT.
* **Ocupaciones:** el catálogo de 20 ocupaciones y sus metadatos se encuentra definido localmente en `etl/ocupaciones_client.py`.
* Las instituciones nacionales mencionadas más adelante son fuentes de referencia del análisis, no conectores implementados por este repositorio.

---

## 1. Mapeo Formal de Fuentes Oficiales Gubernamentales

Las instituciones nacionales indicadas en esta sección son fuentes de referencia para la selección y contextualización de indicadores. La implementación actual consume ILOSTAT parcialmente y utiliza repositorios locales para CEPALSTAT y ocupaciones; no incluye conectores directos a cada organismo nacional.

| País | Ministerio / Secretaría de Trabajo | Ministerio / Sistema de Educación | Instituto de Estadística | Organismos Internacionales |
|:---|:---|:---|:---|:---|
| **Argentina** | **Secretaría de Trabajo, Empleo y Seguridad Social** (OEDE / SIPA) | **Secretaría de Educación** (DiNIECE / Relevamiento Anual) | **INDEC** (EPH) | **ILOSTAT (OIT)** y **CEPALSTAT** |
| **Uruguay** | **MTSS - Ministerio de Trabajo y Seguridad Social** (DINAE / BPS) | **MEC - Ministerio de Educación y Cultura** y **ANEP** (DIEE / Monitor Educativo) | **INE Uruguay** (ECH) | **ILOSTAT (OIT)** y **CEPALSTAT** |
| **Chile** | **Mintrab - Ministerio del Trabajo y Previsión Social** (SENCE / Observatorio Laboral) | **Mineduc - Ministerio de Educación** (Centro de Estudios CEM / SIES) | **INE Chile** (ENE) | **ILOSTAT (OIT)** y **CEPALSTAT** |

---

## 2. Alcance del Proyecto

* **3 Países:** Argentina (ARG), Uruguay (URY) y Chile (CHL).
* **5 Sectores Estratégicos:** Tecnología, Salud, Energía, Turismo y Economía del Conocimiento.
* **20 Ocupaciones Normalizadas:** clasificadas según el estándar internacional **CIUO-08 (ISCO-08)** de la OIT.

---

## 3. Matriz de los 5 Sectores y 20 Ocupaciones Clave

| Sector | ID | Ocupación | CIUO-08 | Nivel de Demanda | Crecimiento Anual Est. | Habilidades Clave |
|:---|:---|:---|:---:|:---:|:---:|:---|
| **Tecnología** | OCUP_01 | Desarrollador de Software y Aplicaciones | `2512` | Muy Alta | +18.5% | Python, FastAPI, React, SQL, Git |
| **Tecnología** | OCUP_02 | Ingeniero de Datos y Machine Learning | `2511` | Muy Alta | +24.0% | Pipelines ETL, PyTorch, Pandas, Power BI |
| **Tecnología** | OCUP_03 | Especialista en Ciberseguridad y Redes | `2529` | Alta | +15.2% | ISO 27001, Ethical Hacking, Cloud Security |
| **Tecnología** | OCUP_04 | Arquitecto Cloud y DevOps | `2522` | Muy Alta | +21.0% | Docker, Kubernetes, AWS/Azure, CI/CD |
| **Salud** | OCUP_05 | Médico General y Especialista | `2211` | Alta | +6.5% | Diagnóstico Clínico, Telemedicina, HCE |
| **Salud** | OCUP_06 | Profesional de Enfermería y Cuidados Críticos | `2221` | Muy Alta | +9.8% | Emergencias, Monitoreo Biomédico, Cuidados |
| **Salud** | OCUP_07 | Bioquímico y Farmacéutico Clínico | `2262` | Media-Alta | +7.2% | Ensayos Farmacológicos, Biología Molecular |
| **Salud** | OCUP_08 | Técnico en Diagnóstico por Imágenes | `3211` | Alta | +11.4% | Resonancia/Tomografía, Procesamiento de Imágenes |
| **Energía** | OCUP_09 | Ingeniero en Energías Renovables (Solar/Eólica) | `2149` | Muy Alta | +16.8% | Parques Eólicos/Solares, Simulación SCADA |
| **Energía** | OCUP_10 | Ingeniero de Petróleo, Gas y Minería de Transición | `2146` | Alta | +8.9% | Extracción No Convencional, Litio/Cobre |
| **Energía** | OCUP_11 | Técnico en Redes Eléctricas Inteligentes | `3113` | Alta | +12.0% | Telemetría, Media/Alta Tensión, Smart Grids |
| **Energía** | OCUP_12 | Auditor en Eficiencia Energética | `2149` | Media-Alta | +14.3% | ISO 50001, Huella de Carbono, Optimización |
| **Turismo** | OCUP_13 | Administrador de Servicios Hoteleros | `1411` | Media-Alta | +7.5% | Revenue Management, PMS Hoteleros, Idiomas |
| **Turismo** | OCUP_14 | Guía de Ecoturismo y Aventura | `5113` | Alta | +13.1% | Primeros Auxilios Remotos, Patrimonio, Idiomas |
| **Turismo** | OCUP_15 | Coordinador de Turismo Digital (TravelTech) | `3339` | Alta | +10.2% | Gestión Canales OTA, Marketing Turístico, CRM |
| **Turismo** | OCUP_16 | Chef Ejecutivo y Gestor Gastronómico | `3434` | Media-Alta | +6.8% | Cocina Regional de Autor, Costos, BPM/HACCP |
| **Economía del Conocimiento** | OCUP_17 | Diseñador UX/UI y Producto Digital | `2166` | Muy Alta | +17.4% | Figma, Design Systems, User Research |
| **Economía del Conocimiento** | OCUP_18 | Consultor en Transformación Digital | `2421` | Muy Alta | +15.9% | BPMN, Power BI, Scrum, Estrategia de Datos |
| **Economía del Conocimiento** | OCUP_19 | Científico en Biotecnología y AgTech | `2131` | Alta | +13.7% | Genómica Aplicada, Bioinformática, Fermentación |
| **Economía del Conocimiento** | OCUP_20 | Analista Financiero Cuantitativo / FinTech | `2413` | Muy Alta | +19.2% | Modelado Financiero, Python, AML, Pagos Digitales |

---

## 4. Preguntas Estratégicas y Diagnóstico del Mercado Laboral

Las conclusiones de esta sección son un diagnóstico interpretativo y no se calculan automáticamente desde la API. Para convertirlas en resultados reproducibles sería necesario documentar las fuentes, consultas y metodología de cada análisis.

### 1. ¿Qué sectores están creciendo o disminuyendo?
* **Crecimiento acelerado:** Tecnología y Servicios Basados en el Conocimiento (SBC), Energías Renovables / Minería de Transición (Litio/Cobre) y TravelTech/Logística.
* **Estables / En transformación:** Agroindustria / AgTech y Servicios de Salud/Cuidado.
* **En contracción relativa:** Manufactura tradicional no automatizada, comercio minorista tradicional y tareas administrativas repetitivas.

### 2. ¿Qué ocupaciones presentan mayores oportunidades de empleo?
Ingenieros de Datos / IA, Desarrolladores Full-Stack, Arquitectos Cloud, Ingenieros en Energías Renovables, Consultores de Transformación Digital y Enfermeros/as de Cuidados Críticos.

### 3. ¿Qué habilidades están aumentando su demanda?
* **Duras:** Python, FastAPI, modelado dimensional, DAX / Power BI, arquitecturas Cloud, integración de APIs de IA (LLMs) e inglés avanzado.
* **Blandas:** Pensamiento crítico, resolución de problemas complejos, adaptabilidad y trabajo asíncrono.

### 4. ¿Cómo evolucionan los salarios y la cantidad de puestos?
El dataset incluye un índice de salario real de referencia para los países, pero no calcula salarios dolarizados ni cantidad de puestos por ocupación. Esas conclusiones requieren fuentes y análisis adicionales.

### 5. ¿Existe correspondencia entre la formación disponible y las necesidades del mercado?
El informe plantea un desacople estructural (*skills mismatch*). Esta conclusión debe interpretarse como análisis cualitativo, ya que la API no compara ofertas formativas con vacantes laborales.

### 6. ¿Qué nuevas brechas de habilidades (*skills gaps*) están apareciendo?
Se identifican como hipótesis de análisis la brecha de alfabetización en Inteligencia Artificial, la falta de cultura de datos en mandos medios y la demanda de experiencia práctica.

### 7. ¿Qué tendencias pueden anticiparse?
El análisis plantea la interconexión de plataformas vía APIs, el auge de microcredenciales y la consolidación del Cono Sur como polo de *nearshoring*. Estas tendencias no son predicciones calculadas por el pipeline.

---

## 5. Instrucciones de Ejecución

### Instalación

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Inicio de la API

```powershell
uvicorn main:app --reload --port 8000
```

* **Swagger UI:** `http://127.0.0.1:8000/docs`

### Endpoints principales

* **Procesar y descargar indicadores de un país:**
  * `GET /api/v1/paises/{pais}/procesar`
  * `GET /api/v1/paises/{pais}/descargar`
* **Procesar y descargar el consolidado regional:**
  * `GET /api/v1/consolidado/procesar`
  * `GET /api/v1/consolidado/descargar`
* **Generar y descargar ocupaciones:**
  * `GET /api/v1/ocupaciones/procesar`
  * `GET /api/v1/ocupaciones/descargar`
* **Consultar el catálogo de ocupaciones:** `GET /api/v1/ocupaciones/catalogo`

En los endpoints de país, `{pais}` debe ser `ARG`, `URY` o `CHL`. El catálogo acepta los filtros opcionales `sector` y `pais`.

### Limitaciones y reproducibilidad

Los datasets de indicadores pueden variar según la respuesta de ILOSTAT. La tasa de desocupación puede provenir de la API o del respaldo local, mientras que los demás indicadores proceden de repositorios locales. Por ello, las cantidades de registros indicadas en el informe técnico son una referencia de la ejecución con el respaldo completo, no una garantía para todas las ejecuciones.

El campo `fecha_extraccion` se genera en cada ejecución y los archivos de `data/processed/` son productos generados, no una copia necesariamente actualizada de las fuentes.
