# Observatorio de Indicadores Regionales: Argentina, Uruguay y Chile
## Pipeline ETL con FastAPI, Ministerios Oficiales, ILOSTAT y CEPALSTAT

Este repositorio contiene la arquitectura integral de ingesta, depuración de datos, generación de datasets listos para producción y el diagnóstico analítico de **5 sectores estratégicos** y **20 ocupaciones clave** para el Cono Sur (**Argentina, Uruguay y Chile**).

---

## 1. Mapeo Formal de Fuentes Oficiales Gubernamentales

Para garantizar la máxima validez y trazabilidad institucional, el pipeline integra datos de los **Ministerios de Trabajo**, **Ministerios de Educación** y los **Institutos de Estadística** de cada país, armonizados bajo los estándares de **ILOSTAT** y **CEPALSTAT**:

| País | Ministerio / Secretaría de Trabajo | Ministerio / Sistema de Educación | Instituto de Estadística | Organismos Internacionales |
|:---|:---|:---|:---|:---|
| **🇦🇷 Argentina** | **Secretaría de Trabajo, Empleo y Seguridad Social** (OEDE / SIPA) | **Secretaría de Educación** (DiNIECE / Relevamiento Anual) | **INDEC** (EPH) | **ILOSTAT (OIT)** & **CEPALSTAT** |
| **🇺🇾 Uruguay** | **MTSS - Ministerio de Trabajo y Seguridad Social** (DINAE / BPS) | **MEC - Ministerio de Educación y Cultura** & **ANEP** (DIEE / Monitor Educativo) | **INE Uruguay** (ECH) | **ILOSTAT (OIT)** & **CEPALSTAT** |
| **🇨🇱 Chile** | **Mintrab - Ministerio del Trabajo y Previsión Social** (SENCE / Observatorio Laboral) | **Mineduc - Ministerio de Educación** (Centro de Estudios CEM / SIES) | **INE Chile** (ENE) | **ILOSTAT (OIT)** & **CEPALSTAT** |

---

## 2. Alcance del Proyecto

* **3 Países:** Argentina (ARG), Uruguay (URY) y Chile (CHL).
* **5 Sectores Estratégicos:**
  1. **Tecnología**
  2. **Salud**
  3. **Energía**
  4. **Turismo**
  5. **Economía del Conocimiento**
* **20 Ocupaciones Normalizadas:** Clasificadas según el estándar internacional **CIUO-08 (ISCO-08)** de la OIT.

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

### 1. ¿Qué sectores están creciendo o disminuyendo?
* **🟢 Crecimiento Acelerado:** Tecnología y Servicios Basados en el Conocimiento (SBC), Energías Renovables / Minería de Transición (Litio/Cobre) y TravelTech/Logística.
* **🟡 Estables / En Transformación:** Agroindustria / AgTech (menor mano de obra manual, mayor demanda técnica) y Servicios de Salud/Cuidado.
* **🔴 En Contracción Relativa:** Manufactura tradicional no automatizada, comercio minorista tradicional y tareas administrativas burocráticas repetitivas.

### 2. ¿Qué ocupaciones presentan mayores oportunidades de empleo?
Ingenieros de Datos / IA, Desarrolladores Full-Stack, Arquitectos Cloud, Ingenieros en Energías Renovables, Consultores de Transformación Digital y Enfermeros/as de Cuidados Críticos.

### 3. ¿Qué habilidades están aumentando su demanda?
* **Duras:** Python, FastAPI, modelado dimensional, DAX / Power BI, arquitecturas Cloud, integración de APIs de IA (LLMs) e inglés avanzado.
* **Blandas:** Pensamiento crítico, resolución de problemas complejos, adaptabilidad (*learnability*) y trabajo asíncrono.

### 4. ¿Cómo evolucionan los salarios y la cantidad de puestos?
Polarización del mercado laboral: alta prima salarial e ingresos dolarizados para talento tecnológico y de conocimiento; presión sobre puestos de tareas repetitivas frente a la automatización.

### 5. ¿Existe correspondencia entre la formación disponible y las necesidades del mercado?
Existe un **desacople estructural (*skills mismatch*)**. Las ofertas formativas tradicionales tardan en actualizarse, mientras el mercado exige habilidades prácticas y certificaciones ágiles. La culminación secundaria en Uruguay (47.0%) y la deserción universitaria en Argentina son cuellos de botella clave.

### 6. ¿Qué nuevas brechas de habilidades (*skills gaps*) están apareciendo?
Brecha de alfabetización en Inteligencia Artificial (*AI Literacy Gap*), falta de cultura de datos en mandos medios (*data-driven gap*) y demanda de seniority práctico frente al conocimiento puramente teórico.

### 7. ¿Qué tendencias pueden anticiparse?
Interconexión de plataformas vía APIs directas (FastAPI a Power BI), auge de micro-credenciales y bootcamps, y consolidación del Cono Sur como polo preferencial de *nearshoring* para mercados globales.

---

## 5. Informes Técnicos y de Homologación

* **[Informe de Mapeo de Variables Equivalentes (ARG, CHL, URY)](INFORME_MAPEO_VARIABLES_REGIONAL.md)**: Homologación metodológica de indicadores socioeconómicos, fuentes (INDEC, INE Chile, INE Uruguay, OIT, CEPAL) y equivalencias CIUO-08.
* **[Informe Técnico y Comparativo Regional](INFORME_TECNICO_REGIONAL.md)**: Síntesis macroeconómica comparada y análisis por país.

---

## 6. Instrucciones de Ejecución

```powershell
# Activar entorno e iniciar la API
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```
* **Swagger UI:** `http://127.0.0.1:8000/docs`
* **Descargar CSV Ocupaciones (5 sectores / 20 ocupaciones):** `GET /api/v1/ocupaciones/descargar`
* **Descargar CSV Consolidado Regional:** `GET /api/v1/consolidado/descargar`

