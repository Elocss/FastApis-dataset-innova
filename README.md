# Observatorio de Indicadores Regionales: Argentina, Uruguay y Chile
## Pipeline ETL con FastAPI, Ministerios Oficiales, ILOSTAT y CEPALSTAT

Este repositorio contiene la arquitectura integral de ingesta, depuración de datos, generación de datasets listos para producción y el diagnóstico analítico de **5 sectores estratégicos** y ocupaciones normalizadas en Argentina, Uruguay y Chile.

---

## 1. Mapeo Formal de Fuentes Oficiales Gubernamentales

Para garantizar la máxima validez y trazabilidad institucional, el catálogo de ocupaciones cita datos de los **Ministerios de Trabajo**, **Ministerios de Educación** e **Institutos de Estadística** de los tres países. Estos organismos se incluyen como **referencias de trazabilidad**, no como fuentes de datos integradas en vivo en el pipeline.

| País | Ministerio / Secretaría de Trabajo | Ministerio / Sistema de Educación | Instituto de Estadística | Organismos Internacionales |
|:---|:---|:---|:---|:---|
| **🇦🇷 Argentina** | **Secretaría de Trabajo, Empleo y Seguridad Social** (OEDE / SIPA) | **Secretaría de Educación** (DiNIECE / Relevamiento Anual) | **INDEC** (EPH) | **ILOSTAT (OIT)** [...] |
| **🇺🇾 Uruguay** | **MTSS - Ministerio de Trabajo y Seguridad Social** (DINAE / BPS) | **MEC - Ministerio de Educación y Cultura** & **ANEP** (DIEE / Monitor Educativo) | **INE Uruguay** (E[...] |
| **🇨🇱 Chile** | **Mintrab - Ministerio del Trabajo y Previsión Social** (SENCE / Observatorio Laboral) | **Mineduc - Ministerio de Educación** (Centro de Estudios CEM / SIES) | **INE Chil[...] |

### Alcance de Fuentes de Datos Consumidas

El pipeline obtiene datos en vivo desde:
- **ILOSTAT (OIT)**: API SDMX con series de respaldo automático en caso de falla
- **CEPALSTAT**: Snapshot curado (sin llamadas HTTP en tiempo real)

Los ministerios e institutos estadísticos nacionales se citan únicamente como atribución en el catálogo de ocupaciones y como referencia institucional de trazabilidad, pero **no son consultados directamente en ningún punto del código del pipeline**.

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

## 3. Calidad y Trazabilidad de los Datos

### Semántica del Campo `fuente_oficial`

El campo `fuente_oficial` en los CSV de salida indica la procedencia de cada fila de datos. Su significado exacto es:

| Valor | Significado | Características |
|:---|:---|:---|
| **ILOSTAT** | Datos obtenidos en vivo desde la API SDMX de la OIT (International Labour Organization) | Consulta en tiempo real; si falla, cae automáticamente a serie respaldo hardcodeada en `etl/ilostat_client.py` |
| **ILOSTAT_FALLBACK** | Serie respaldo utilizada cuando la consulta en vivo a ILOSTAT falló | Valores predeterminados y curados; permite continuidad operativa sin datos en vivo |
| **CEPALSTAT** | Snapshot estático curado de CEPALSTAT (Comisión Económica para América Latina) | No es una consulta en vivo; es un archivo o datos preprocesados sin llamadas HTTP en tiempo real |

### Implications for Data Consumers

- **Filas con `ILOSTAT`:** Potencialmente en vivo; reflejan la situación más reciente (sujeta a latencia de API).
- **Filas con `ILOSTAT_FALLBACK`:** Datos de respaldo; indican que hubo un fallo en la ingesta en vivo.
- **Filas con `CEPALSTAT`:** Snapshot estático; reflejan una fotografía curada en un momento del tiempo, no evoluciona con nuevas consultas.

Sin esta documentación, los consumidores de los CSV no tienen forma de saber qué filas son en vivo y cuáles son de respaldo o snapshot estático, lo que afecta directamente la interpretación de tendencias y confiabilidad de análisis.

---

## 4. Catálogo de Ocupaciones: 5 Sectores y 20 Ocupaciones Clave

El catálogo completo de ocupaciones normalizadas está disponible a través de múltiples canales para garantizar que siempre accedas a la versión más actualizada:

### Acceso al Catálogo en Vivo

- **📊 Descarga CSV:** `GET /api/v1/ocupaciones/descargar`
  - Descarga la tabla completa de 20 ocupaciones en formato CSV

- **🔍 Exploración interactiva:** Accede a **Swagger UI** en `http://127.0.0.1:8000/docs`
  - Ver esquema de datos en tiempo real
  - Probar endpoints directamente
  - Inspeccionar respuestas JSON

- **📁 Catálogo consolidado regional:** `GET /api/v1/consolidado/descargar`
  - Obtén datasets consolidados por país y sector

### Matriz de Ocupaciones

**Estructura:** 5 Sectores × 4 Ocupaciones = 20 roles estratégicos

| Sector | Ocupaciones |
|:---|:---|
| **Tecnología** | Desarrollador de Software, Ingeniero de Datos/ML, Especialista en Ciberseguridad, Arquitecto Cloud/DevOps |
| **Salud** | Médico General/Especialista, Profesional de Enfermería, Bioquímico/Farmacéutico, Técnico en Diagnóstico |
| **Energía** | Ingeniero en Energías Renovables, Ingeniero de Petróleo/Gas/Minería, Técnico en Redes Eléctricas, Auditor en Eficiencia Energética |
| **Turismo** | Administrador de Servicios Hoteleros, Guía de Ecoturismo, Coordinador de Turismo Digital, Chef Ejecutivo |
| **Economía del Conocimiento** | Diseñador UX/UI, Consultor en Transformación Digital, Científico en Biotecnología/AgTech, Analista Financiero Cuantitativo |

**Nota:** La tabla anterior es una síntesis visual. Para detalles completos (CIUO-08, niveles de demanda, crecimiento anual, habilidades específicas), consulta el endpoint `/api/v1/ocupaciones/descargar` o la interfaz Swagger.

---

## 5. Preguntas Estratégicas y Diagnóstico del Mercado Laboral

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
Existe un **desacople estructural (*skills mismatch*)**. Las ofertas formativas tradicionales tardan en actualizarse, mientras el mercado exige habilidades prácticas y certificaciones ágiles. La[...]

### 6. ¿Qué nuevas brechas de habilidades (*skills gaps*) están apareciendo?
Brecha de alfabetización en Inteligencia Artificial (*AI Literacy Gap*), falta de cultura de datos en mandos medios (*data-driven gap*) y demanda de seniority práctico frente al conocimiento pur[...]

### 7. ¿Qué tendencias pueden anticiparse?
Interconexión de plataformas vía APIs directas (FastAPI a Power BI), auge de micro-credenciales y bootcamps, y consolidación del Cono Sur como polo preferencial de *nearshoring* para mercados g[...]

---

## 6. Instrucciones de Ejecución

```powershell
# Iniciar la API localmente
uvicorn main:app --reload --port 8000
```
* **Swagger UI:** `http://127.0.0.1:8000/docs`
* **Descargar CSV Ocupaciones (5 sectores / 20 ocupaciones):** `GET /api/v1/ocupaciones/descargar`
* **Descargar CSV Consolidado Regional:** `GET /api/v1/consolidado/descargar`
