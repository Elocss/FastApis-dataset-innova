# Observatorio de Indicadores Regionales: Uruguay, Chile y Argentina
## Pipeline ETL con FastAPI, ILOSTAT y CEPALSTAT

Este repositorio contiene la arquitectura completa de ingesta, depuración de calidad de datos, generación de datasets listos para producción y el diagnóstico analítico de mercado laboral, actividad económica, educación y capital humano para el Cono Sur (**Uruguay, Chile y Argentina**).

---

## 1. Estructura del Proyecto

```text
FastApis-dataset-innova/
│
├── data/
│   ├── raw/                              # Respaldos y respuestas en crudo de las APIs
│   └── processed/                        # Datasets depurados listos para producción (.csv)
│       ├── dataset_uruguay_produccion.csv    (45 registros)
│       ├── dataset_chile_produccion.csv      (45 registros)
│       ├── dataset_argentina_produccion.csv  (45 registros)
│       └── dataset_consolidado_regional.csv  (135 registros unificados)
│
├── etl/
│   ├── __init__.py
│   ├── ilostat_client.py                 # Ingesta API SDMX/REST de ILOSTAT (OIT)
│   ├── cepalstat_client.py               # Ingesta API CEPALSTAT
│   └── cleaner.py                        # Pipeline de depuración, tipado y calidad con Pandas
│
├── main.py                               # Servidor FastAPI y endpoints REST de exportación
├── requirements.txt                      # Dependencias del proyecto
├── INFORME_TECNICO_REGIONAL.md           # Informe ejecutivo comparativo
└── README.md                             # Documentación técnica, manual y análisis estratégico
```

---

## 2. Diccionario de Datos (Estándar de Producción)

Todos los archivos generados en `data/processed/` cumplen con la siguiente taxonomía normalizada:

| Columna | Tipo | Descripción | Ejemplo |
|:---|:---|:---|:---|
| `pais_codigo_iso3` | String (3) | Código de país estándar ISO 3166-1 alfa-3 | `URY`, `CHL`, `ARG` |
| `pais_nombre` | String | Nombre oficial del país | `Uruguay`, `Chile`, `Argentina` |
| `dimension` | String | Eje temático (`Economía`, `Empleo`, `Salarios`, `Educación`, `Población`) | `Economía` |
| `indicador_nombre` | String | Nombre normalizado del indicador | `Variación Anual del PIB Real` |
| `anio` | Integer | Año del registro (2015 - 2024) | `2023` |
| `periodo` | String | Periodicidad de la serie | `Anual` |
| `valor` | Float | Valor numérico depurado | `3.2` |
| `unidad_medida` | String | Unidad de medida (`%`, `Millones de hab.`, etc.) | `Porcentaje (%)` |
| `fuente_oficial` | String | Organismo emisor (`ILOSTAT - OIT`, `CEPALSTAT`) | `CEPALSTAT` |
| `fecha_extraccion` | Date (YYYY-MM-DD) | Timestamp de la ingesta | `2026-09-10` |

---

## 3. Matriz Síntesis de Indicadores (2023 - 2024)

| Dimensión / Indicador | Uruguay (URY) | Chile (CHL) | Argentina (ARG) | Fuente Oficial |
| :--- | :---: | :---: | :---: | :--- |
| **Población Total (2024)** | **3.51 M** | **19.80 M** | **46.70 M** | CEPALSTAT |
| **Crecimiento PIB Real (2024)** | **+3.2%** | **+2.3%** | **-3.5%** | CEPALSTAT |
| **Inflación Anual (2024)** | **4.8%** | **4.2%** | **118.0%** | CEPALSTAT |
| **Tasa de Desempleo (2024)** | **8.1%** | **8.5%** | **7.6%** | ILOSTAT - OIT |
| **Tasa de Ocupación (2024)** | **58.6%** | **56.8%** | **43.5%** | ILOSTAT - OIT |
| **Finalización Secundaria** | **47.0%** | **89.1%** | **70.8%** | CEPALSTAT |
| **Inversión Educativa (% PIB)** | **4.7%** | **5.3%** | **4.5%** | CEPALSTAT |

---

## 4. Preguntas Estratégicas y Diagnóstico del Mercado Laboral

A partir del análisis integrado de **ILOSTAT**, **CEPALSTAT** y los estudios prospectivos del Cono Sur:

### 1. ¿Qué sectores están creciendo o disminuyendo?
* **🟢 En Crecimiento Acelerado:**
  * **Servicios Basados en el Conocimiento (SBC / Tech):** Desarrollo de software, IA, ciberseguridad, biotecnología y servicios corporativos exportables (Uruguay como hub tecnológico regional, Argentina con polo de exportación de talento tech, Chile en soluciones cloud y fintech).
  * **Energías Renovables y Minería Sostenible:** Transición energética, litio y cobre (fuerte liderazgo en Chile).
  * **Logística y E-commerce:** Automatización de cadenas de suministro.
* **🟡 Estables / En Transformación:**
  * **Agroindustria / AgTech:** Altamente tecnificada; menor requerimiento de mano de obra manual no calificada y mayor demanda de técnicos de precisión.
  * **Salud y Cuidados:** Demanda sostenida por el envejecimiento poblacional en el Cono Sur.
* **🔴 En Disminución / Contracción Relativa:**
  * **Manufactura Tradicional no Automatizada:** Pérdida de competitividad y reestructuración industrial.
  * **Comercio Minorista Físico Tradicional:** Reemplazado por canales digitales y omnicanalidad.
  * **Administración y Tareas Burocráticas Repetitivas:** Reducción por digitalización y eficiencia de procesos.

---

### 2. ¿Qué ocupaciones presentan mayores oportunidades de empleo?
* **Tecnología e Inteligencia Artificial:** Ingenieros de Machine Learning, Desarrolladores Full-Stack, Arquitectos Cloud, Especialistas en Ciberseguridad y Científicos de Datos.
* **Ingeniería Operativa y Sostenibilidad:** Especialistas en mantenimiento mecatrónico, técnicos en instalaciones de energía solar/eólica y especialistas en gestión ambiental.
* **Gestión y Servicios Críticos:** Analistas de Negocios y Producto (Product Owners), profesionales de enfermería y salud especializada.

---

### 3. ¿Qué habilidades están aumentando su demanda?
* **Habilidades Duras (Hard Skills):**
  * **Desarrollo y Datos:** Python, FastAPI, SQL avanzado, pipelines ETL, integración de APIs y modelos de IA/LLMs.
  * **Business Intelligence:** Modelado dimensional, DAX, Power BI y analítica de autoservicio.
  * **Idiomas:** Dominio del idioma inglés técnico y conversacional para mercados globales.
* **Habilidades Blandas / Metacompetencias (Soft Skills):**
  * **Pensamiento Crítico y Resolución de Problemas Complejos.**
  * **Adaptabilidad y Aprendizaje Continuo (*Learnability*):** Capacidad de asimilar herramientas emergentes de forma autodidacta.
  * **Comunicación Asertiva y Trabajo Colaborativo Remoto/Híbrido.**

---

### 4. ¿Cómo evolucionan los salarios y la cantidad de puestos?
* **Polarización Laboral:** Los roles de alta calificación tecnológica experimentan primas salariales elevadas y compensaciones dolarizadas, mientras que los puestos operativos y repetitivos sufren estancamiento salarial o riesgo de automatización.
* **Uruguay:** Mayor estabilidad del poder adquisitivo, salario real en recuperación sostenida (103.2 base) y pleno empleo en el sector tecnológico.
* **Chile:** Salarios reales estables con empleo total en torno al 56.8% y brecha salarial sectorial marcada (minería/finanzas vs. servicios generales).
* **Argentina:** Fuerte dispersión salarial por el impacto de la inflación acumulada, con contraste entre el sector formal tradicional y el talento exportador independiente.

---

### 5. ¿Existe correspondencia entre la formación disponible y las necesidades del mercado laboral?
* **Diagnóstico:** Existe un desacople estructural (*Skills Mismatch*).
* **Oferta Tradicional vs. Demanda Dinámica:** Las mallas curriculares universitarias convencionales evolucionan más lento que la velocidad del mercado tecnológico.
* **Brechas Educativas por País:**
  * **Uruguay:** La tasa de culminación secundaria (47.0%) es el principal desafío estructural para universalizar la inserción en economía del conocimiento.
  * **Chile:** Alta culminación secundaria (89.1%), requiriendo fortalecer la articulación técnica y la accesibilidad de la educación superior continua.
  * **Argentina:** Alta cobertura universitaria con matrícula abierta, pero con tasas de deserción elevadas frente a un mercado que premia certificaciones ágiles y proyectos aplicados.

---

### 6. ¿Qué nuevas brechas de habilidades (*Skills Gaps*) están apareciendo?
* **Brecha de Alfabetización en IA (*AI Literacy Gap*):** Disparidad entre profesionales que incorporan herramientas de IA para multiplicar su productividad y aquellos que desconocen su uso aplicado.
* **Brecha de Cultura de Datos en Mandos Medios:** Escasez de capacidades analíticas en áreas de gestión (finanzas, operaciones, RRHH que aún operan con planillas manuales en lugar de bases conectadas).
* **Brecha de Seniority Práctico:** El mercado demanda experiencia aplicada comprobable en arquitecturas de software, superando el valor de conocimientos teóricos abstractos.

---

### 7. ¿Qué tendencias pueden anticiparse a partir de la evolución reciente de los datos?
1. **Adopción Masiva de APIs y Automatización (FastAPI + BI):** Interconexión directa de datos para la toma de decisiones en tiempo real sin intervención manual.
2. **Educación Híbrida y Micro-credenciales:** Reconocimiento creciente de bootcamps, proyectos de código abierto y certificaciones internacionales.
3. **Consolidación del Nearshoring en el Cono Sur:** Mayor contratación de talento latinoamericano por empresas globales gracias a la calidad técnica y la zona horaria.
4. **Urgencia en Políticas de *Upskilling* y *Reskilling*:** Reconversión acelerada de trabajadores desplazados por la automatización hacia actividades de servicios tecnológicos y sostenibles.

---

## 5. Instrucciones de Ejecución de la API

### A. Levantar el servidor FastAPI
Desde la terminal en el directorio del proyecto:
```powershell
uvicorn main:app --reload --port 8000
```

### B. Endpoints de Ingesta, Procesamiento y Descarga
* **Swagger UI:** `http://127.0.0.1:8000/docs`
* **Procesar Uruguay:** `GET /api/v1/paises/URY/procesar`
* **Descargar CSV Uruguay:** `GET /api/v1/paises/URY/descargar`
* **Procesar Chile:** `GET /api/v1/paises/CHL/procesar`
* **Descargar CSV Chile:** `GET /api/v1/paises/CHL/descargar`
* **Procesar Argentina:** `GET /api/v1/paises/ARG/procesar`
* **Descargar CSV Argentina:** `GET /api/v1/paises/ARG/descargar`
* **Procesar Consolidado Regional (3 países):** `GET /api/v1/consolidado/procesar`
* **Descargar Consolidado CSV:** `GET /api/v1/consolidado/descargar`
