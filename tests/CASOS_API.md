# Casos de prueba de la API

Este documento describe dos casos funcionales y de integración para validar la API de `DataAnalyst`. El contrato estructurado equivalente está en [casos_api.json](casos_api.json).

## Preparación

1. Instalar dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Iniciar la API:

```powershell
uvicorn main:app --reload --port 8000
```

La URL base utilizada es `http://127.0.0.1:8000`.

## API-FUNC-001: catálogo filtrado

**Tipo:** funcional  
**Objetivo:** comprobar que `sector` y `pais` se apliquen simultáneamente.

### Ejecución

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/v1/ocupaciones/catalogo?sector=Tecnolog%C3%ADa&pais=ARG" `
  -Method Get
```

### Resultado esperado

- HTTP `200`.
- La respuesta es un arreglo JSON de `4` elementos.
- Todos los elementos tienen `pais_codigo_iso3` igual a `ARG`.
- Todos los elementos tienen `sector` igual a `Tecnología`.
- Cada elemento incluye `ocupacion_id`, `ocupacion_nombre`, `codigo_ciuo08_oit`, `nivel_demanda` y `habilidades_clave`.

## API-INT-001: consolidado regional

**Tipo:** integración  
**Objetivo:** comprobar el flujo conjunto de extracción, depuración, generación de CSV y descarga.

Este caso puede consultar ILOSTAT. Si ILOSTAT no responde, el cliente utiliza la serie local de respaldo, por lo que la prueba sigue siendo reproducible, aunque la procedencia de algunos registros puede variar.

### Paso 1: procesar

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/v1/consolidado/procesar" `
  -Method Get
```

### Resultado esperado del paso 1

- HTTP `200`.
- `status` es `Pipeline regional completado`.
- `paises_procesados` contiene `Argentina`, `Chile` y `Uruguay`.
- `total_filas_consolidadas` es mayor que `0`.
- Se generan estos archivos:
  - `data/processed/dataset_consolidado_regional.csv`
  - `data/processed/dataset_argentina_produccion.csv`
  - `data/processed/dataset_chile_produccion.csv`
  - `data/processed/dataset_uruguay_produccion.csv`

### Paso 2: descargar

```powershell
$response = Invoke-WebRequest `
  -Uri "http://127.0.0.1:8000/api/v1/consolidado/descargar" `
  -Method Get

$response.StatusCode
$response.Headers["Content-Type"]
$response.Content.Substring(0, 80)
```

### Resultado esperado del paso 2

- HTTP `200`.
- `Content-Type` comienza por `text/csv`.
- El contenido contiene las columnas canónicas `pais_codigo_iso3`, `pais_nombre`, `dimension` e `indicador_nombre`.

## Nota

Estos casos están expresados como especificación funcional y todavía no incluyen un runner automático. Pueden convertirse posteriormente en pruebas `pytest` usando `fastapi.testclient.TestClient`, sustituyendo las llamadas externas a ILOSTAT por mocks para evitar dependencia de red.
