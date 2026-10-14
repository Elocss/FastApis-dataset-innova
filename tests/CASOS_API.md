# Casos de prueba de la API y Motor Analítico

Este documento describe los casos funcionales, de integración y analíticos para validar la API de `Innova Data Platform`.

## Preparación y Ejecución de la Suite Automática

1. Activar el entorno virtual:
```powershell
.\.venv\Scripts\Activate.ps1
```

2. Ejecutar la suite automatizada de pruebas unitarias y de integración:
```powershell
python -m unittest tests/test_analytics.py -v
```

3. Iniciar la API en desarrollo:
```powershell
uvicorn main:app --reload --port 8000
```
La URL base utilizada es `http://127.0.0.1:8000`.

---

## API-FUNC-001: Catálogo Filtrado de Ocupaciones

**Tipo:** Funcional  
**Objetivo:** Comprobar que los filtros de `sector` y `pais` se apliquen simultáneamente.

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/v1/ocupaciones/catalogo?sector=Tecnolog%C3%ADa&pais=ARG" `
  -Method Get
```

**Resultado esperado:**
- HTTP `200`.
- Arreglo JSON de `4` elementos con `pais_codigo_iso3 = "ARG"` y `sector = "Tecnología"`.

---

## API-INT-001: Pipeline Consolidado Regional

**Tipo:** Integración  
**Objetivo:** Comprobar extracción, depuración, consolidación y descarga del CSV regional.

```powershell
# Paso 1: Procesar
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/consolidado/procesar" -Method Get

# Paso 2: Descargar
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/consolidado/descargar" -Method Get
```

---

## API-ANL-001: Serie Histórica del Índice Macroeconómico (IDELR)

**Tipo:** Analítico / Funcional  
**Objetivo:** Validar el cálculo del IDELR, variación interanual y clasificación de tendencias con banda muerta ($\epsilon = 1.0\%$).

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/v1/analytics/indice-sintetico?pais=URY&anio_inicio=2018" `
  -Method Get
```

**Resultado esperado:**
- HTTP `200`.
- Registros con campos `indice_sintetico`, `delta_absoluto`, `variacion_interanual_pct`, `tendencia` (`CRECIMIENTO`, `ESTABILIDAD`, `DISMINUCION`) y `desglose_variables`.

---

## API-ANL-002: Ranking de Oportunidad de Ocupaciones (ICOL)

**Tipo:** Analítico / Funcional  
**Objetivo:** Validar el cálculo del score compuesto ICOL cruzando macroeconomía, demanda y crecimiento.

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/v1/analytics/ocupaciones/ranking?pais=CHL&sector=Energ%C3%ADa" `
  -Method Get
```

**Resultado esperado:**
- HTTP `200`.
- 4 ocupaciones del sector Energía en Chile ordenadas por `indice_oportunidad_icol`.
- Incluye `score_demanda_100`, `score_crecimiento_100`, `score_entorno_macro_100`, `ranking_pais` y `ranking_sector`.

---

## API-ANL-003: Matriz de Validación Cruzada (3 Países x 5 Sectores x 20 Ocupaciones)

**Tipo:** Control de Calidad Analítico  
**Objetivo:** Certificar las 60 combinaciones evaluadas, sin nulos y con scores acotados en $[0, 100]$.

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/v1/analytics/ocupaciones/validacion-cruzada" `
  -Method Get
```

**Resultado esperado:**
- HTTP `200`.
- `total_combinaciones_validadas = 60`.
- `invariante_rango_0_100 = true`.
- `integridad_sin_nulos = true`.
- Resúmenes agregados por sector y por país.

---

## Casos de Prueba de Carga y Pipeline (LOAD-006 a LOAD-012)

Para las especificaciones técnicas y criterios de aceptación acordados con el equipo de QA sobre:
- **LOAD-006:** Duplicados en carga manual y política `UPSERT`.
- **LOAD-009:** Cobertura de 135 registros (45 por país: ARG, CHL, URY) en `dataset_consolidado_regional.csv`.
- **LOAD-010:** Contrato de 8 campos de Backend y transformación a `ESQUEMA_COLUMNAS` de `cleaner.py`.
- **LOAD-011:** Regla de deduplicación canónica en `cleaner.py`.
- **LOAD-012:** Matriz de registros válidos, descartados y cuarentena.

Consulte el documento oficial: [DEFINICIONES_CASOS_CARGA_QA.md](../DEFINICIONES_CASOS_CARGA_QA.md).
