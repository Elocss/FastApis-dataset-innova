# 📌 Definiciones Técnicas y Criterios de Aceptación — Casos de Carga (QA)
**Proyecto:** Innova Data Platform / Observatorio Regional (`Innova Lab`)  
**Repositorio:** `https://github.com/Elocss/FastApis-dataset-innova.git`  
**Módulos Involucrados:** `etl/cleaner.py`, `main.py`, Pipeline de Ingesta, Dataset Consolidado Regional  
**Fecha de Aprobación:** Octubre 2026  
**Estado:** Aprobado / Listo para Matriz de Pruebas  

---

## 🚀 Resumen Ejecutivo de Aprobaciones

| Caso QA | Título | Estado | Definición Aprobada y Enlace Técnico |
|---|---|---|---|
| **LOAD-006** | Duplicados en Carga Manual | **APROBADO** | Clave natural de unicidad: `(pais_codigo_iso3, dimension, indicador_nombre, anio, periodo, unidad_medida, fuente_oficial)`. En el mismo archivo se toma la última versión; en base de datos/data lakehouse se aplica política idempotente `UPSERT / MERGE`. |
| **LOAD-009** | Cobertura del Dataset (135 / 45) | **APROBADO** | Confirmado. El archivo `data/processed/dataset_consolidado_regional.csv` contiene exactamente 135 registros: **3 Países Piloto (ARG, CHL, URY) × 45 registros** por país (5 métricas macro/laborales × 3 sectores/dimensiones × 3 períodos temporales). |
| **LOAD-010** | Estructura de Carga Manual | **APROBADO** | Contrato de entrada de 8 campos en Backend, validaciones sincrónicas (`HTTP 422`) y transformación directa al esquema común `ESQUEMA_COLUMNAS` de `etl/cleaner.py`. |
| **LOAD-011** | Deduplicación del ETL (`cleaner.py`) | **APROBADO** | La regla implementada en `cleaner.py` (`pais_codigo_iso3 + dimension + indicador_nombre + anio + periodo + unidad_medida + fuente_oficial`) es la regla canónica oficial y esperada. |
| **LOAD-012** | Registros Válidos y Descartados | **APROBADO** | Distinción formal: Rechazos sincrónicos de entrada (`HTTP 422` por nulos o tipo de dato) vs descarte por deduplicación (`drop_duplicates` en ETL) vs derivación a cuarentena por inconsistencia de catálogo o rango. |

---

## 1. LOAD-006 — Duplicados en Carga Manual

### A. Identificación del Registro Duplicado
Un registro se identifica como duplicado si comparte exactamente los 7 atributos de su clave natural:
$$\text{Clave} = (\text{country\_code}, \text{sector/occupation}, \text{metric\_name}, \text{year}, \text{period}, \text{unit}, \text{source})$$

### B. Criterio de Tratamiento Durante la Carga
1. **Detección dentro del mismo lote/archivo subido:**
   * **Valores idénticos:** Se descarta la fila redundante de forma automática conservando una única ocurrencia.
   * **Valores diferentes:** Se adopta el **último registro cronológico** del archivo/lote y se emite un `Warning` de auditoría indicando: `"Registro sobreescrito por actualización en la misma carga"`.
2. **Detección al consolidar contra el Data Lakehouse / Base de Datos:**
   * Se ejecuta una operación idempotente **`UPSERT` (o `MERGE`)** que actualiza el valor y la marca temporal de extracción/actualización sin duplicar filas.

---

## 2. LOAD-009 — Cobertura del Dataset (45 por País / 135 en Total)

### A. Qué contiene el CSV compartido y a qué dataset corresponde
El archivo `data/processed/dataset_consolidado_regional.csv` (y sus fuentes individuales `dataset_argentina_produccion.csv`, `dataset_chile_produccion.csv` y `dataset_uruguay_produccion.csv`) corresponde al **Golden Dataset de Control y Línea Base Regional** de la plataforma.

### B. Desglose exacto de los 135 registros:
El alcance regional comprende **3 Países Piloto**:
$$\text{Total Regional: } 3 \text{ países} \times 45 \text{ registros/país} = 135 \text{ registros}$$

* 🇦🇷 **Argentina (ARG):** 45 registros
* 🇨🇱 **Chile (CHL):** 45 registros
* 🇺🇾 **Uruguay (URY):** 45 registros

### C. Cobertura Matricial (por qué 45 registros):
Cada país cubre una cuadrícula uniforme sin nulos para calcular el **Índice Sintético Regional (IDELR)** y el **Índice Compuesto de Oportunidad Laboral (ICOL)**:
$$\text{Matriz por País: } 5 \text{ Indicadores Base} \times 3 \text{ Dimensiones / Sectores Clave} \times 3 \text{ Ventanas Temporales} = 45 \text{ registros}$$

QA puede verificar en cualquier momento con la instrucción:
```powershell
Import-Csv "data/processed/dataset_consolidado_regional.csv" | Group-Object pais_codigo_iso3 | Select-Object Name, Count
# Salida esperada: ARG = 45, CHL = 45, URY = 45 (Total = 135)
```

---

## 3. LOAD-010 — Estructura de la Carga Manual

### A. Estructura que recibe el Backend (Contrato de Entrada - 8 Campos)
```json
{
  "country_code": "ARG",
  "sector_id": "SEC-01",
  "occupation_id": "OCC-2512",
  "metric_name": "Tasa de Desocupación Total",
  "metric_value": "7.7",
  "period": "2023",
  "source_name": "INDEC / EPH",
  "data_type": "percentage"
}
```

### B. Validaciones Sincrónicas en Backend (Nivel 1)
1. **Presencia:** No se admiten valores `null` o cadenas vacías en campos requeridos.
2. **País:** Debe pertenecer a los códigos ISO-3 permitidos (`ARG`, `CHL`, `URY` o catálogo habilitado).
3. **Parseo Numérico:** `metric_value` debe poder convertirse a número flotante. Cadenas tipo `"sin dato"`, `"s/d"` o con caracteres alfabéticos son rechazadas.
4. **Formato Período:** Admite año (`2023`), año-trimestre (`2023-Q2`) o año-mes (`2023-06`).

*Respuesta ante fallo:* **`HTTP 422 Unprocessable Entity`** detallando fila y causa.

### C. Adaptación a la Estructura Común de Data (`etl/cleaner.py`)
El pipeline transforma los 8 campos de entrada al `ESQUEMA_COLUMNAS` estándar de producción:

| Campo Origen (Backend) | Transformación / Normalización | Campo Canónico ETL (`cleaner.py`) | Tipo en ETL |
|---|---|---|---|
| `country_code` | `UPPER`, `TRIM`, resolución contra `PAISES_INFO` | `pais_codigo_iso3` | `str` (ISO-3) |
| (Derivado de `country_code`) | Búsqueda en catálogo institucional | `pais_nombre` | `str` |
| `sector_id` / `occupation_id` | Concatenación o mapeo de dimensión temática | `dimension` | `str` |
| `metric_name` | Homologación con `INDICADORES_ALIAS` | `indicador_nombre` | `str` |
| `period` | Extracción de componente anual | `anio` | `int` |
| `period` | Normalización de granularidad (`ANUAL`, `Q1`, `M06`) | `periodo` | `str` |
| `metric_value` | Casteo a flotante redondeado a 2 decimales | `valor` | `float` |
| `data_type` | Homologación (`percentage`, `currency`, `count`) | `unidad_medida` | `str` |
| `source_name` | Limpieza y validación de fuente oficial | `fuente_oficial` | `str` |
| (Metadata) | Generación automática `NOW()` en UTC | `fecha_extraccion` | `str` (ISO-8601) |

---

## 4. LOAD-011 — Deduplicación del ETL (`cleaner.py`)

### A. Regla Exacta en Código (`cleaner.py` líneas 40-43)
```python
df = df.drop_duplicates(subset=[
    "pais_codigo_iso3", 
    "dimension", 
    "indicador_nombre", 
    "anio",
    "periodo", 
    "unidad_medida", 
    "fuente_oficial"
])
```

### B. Dictamen Técnico para QA
**CONFIRMADO: La regla implementada en `cleaner.py` es la esperada y aprobada.**  
*Justificación:* Cada uno de los 7 campos es estrictamente necesario para fijar la unicidad de una métrica:
1. `pais_codigo_iso3`: Alcance geográfico.
2. `dimension`: Segmento sectorial o laboral.
3. `indicador_nombre`: Fenómeno macro o laboral observado.
4. `anio`: Coordenada temporal macro.
5. `periodo`: Granularidad intra-anual (evita que un dato trimestral colisione con el anual consolidado).
6. `unidad_medida`: Evita mezclar mediciones absolutas con porcentuales.
7. `fuente_oficial`: Permite distinguir mediciones oficiales paralelas si correspondiera.

---

## 5. LOAD-012 — Registros Válidos y Descartados

```
[Registro Recibido]
        │
        ├─► ¿Falla campo obligatorio o formato no numérico? 
        │     └─► [RECHAZO ENTRADA] (HTTP 422 - Sincrónico, no entra al pipeline)
        │
        ├─► ¿Es idéntico a otro registro del mismo lote en los 7 campos clave?
        │     └─► [DESCARTADO POR DEDUPLICACIÓN] (drop_duplicates en cleaner.py)
        │
        ├─► ¿Contiene valor con formato numérico pero fuera de rango lógico (ej: desempleo < 0)?
        │     └─► [CUARENTENA] (staging_quarantine con flag de auditoría)
        │
        └─► ¿Cumple validaciones y tipos correctos?
              └─► [VÁLIDO] (Persistido en dataset de producción)
```

### Matriz de Criterios:

| Etapa | Escenario | Estado QA | Acción Ejecutada |
|---|---|---|---|
| **Backend (Entrada)** | Falta `country_code`, `metric_name`, `metric_value` o `period`. | **Inválido** | **HTTP 422**: Rechazo antes de procesar. |
| **Backend (Entrada)** | `metric_value` no numérico (`"N/D"`, `"error"`, texto). | **Inválido** | **HTTP 422**: Rechazo con mensaje descriptivo. |
| **Backend (Entrada)** | `country_code` no alfanumérico o longitud distinta a 3. | **Inválido** | **HTTP 422**: Código de país inválido. |
| **ETL (Procesamiento)** | Registro completo con datos consistentes. | **VÁLIDO** | **Procesado y persistido** en `data/processed/`. |
| **ETL (Procesamiento)** | Fila exactamente redundante dentro del lote. | **Descartado** | **Deduplicado**: Se procesa una sola vez. |
| **ETL (Procesamiento)** | Clave de dimensión u ocupación no encontrada en catálogo. | **Cuarentena** | Se aísla con etiqueta `UNMAPPED_CATALOG` para revisión de Data. |
| **ETL (Procesamiento)** | `data_type == 'percentage'` con valor $< 0\%$ o $> 100\%$. | **Cuarentena** | Se aísla con etiqueta `OUTLIER_RANGE`. |

---
*Documento aprobado y sincronizado con el repositorio oficial.*
