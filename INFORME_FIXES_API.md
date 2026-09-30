# Informe de fixes y riesgos de la API

## Objetivo

Este documento registra las correcciones aplicadas a los riesgos funcionales y operativos detectados en la API de `DataAnalyst`. El objetivo es que el equipo pueda revisar los cambios, reproducirlos y decidir qué mejoras quedan para una siguiente iteración.

## Fixes aplicados

### 1. Renovación automática de archivos procesados

Los endpoints de descarga ya no consideran válido cualquier CSV existente. Un archivo se regenera cuando no existe o tiene más de 24 horas de antigüedad.

Afecta a:

- `/api/v1/paises/{pais}/descargar`
- `/api/v1/consolidado/descargar`
- `/api/v1/ocupaciones/descargar`

La ventana está centralizada en `CACHE_MAX_AGE_SECONDS` dentro de `main.py`.

### 2. Protección contra escrituras concurrentes

Los endpoints de procesamiento comparten `pipeline_lock`, un `asyncio.Lock` que evita que dos solicitudes escriban simultáneamente los mismos archivos procesados.

Esto reduce el riesgo de CSV incompletos o mezclados cuando se reciben solicitudes concurrentes.

### 3. Trazabilidad de las fuentes utilizadas

Las respuestas de procesamiento incluyen `fuentes_oficiales`. El consumidor puede distinguir si los datos provinieron de la API SDMX de ILOSTAT, del respaldo local de ILOSTAT o de CEPALSTAT.

La trazabilidad detallada por registro continúa disponible en el campo `fuente_oficial` del dataset.

### 4. Contrato de nombres alineado

Los indicadores de empleo generados por ILOSTAT ahora usan los nombres definidos en el informe de homologación:

- `Tasa de Desocupación Total`
- `Tasa de Ocupación`
- `Índice de Salario Real`

Los CSV existentes deben regenerarse para reflejar estos nombres.

### 5. Llave de ocupaciones corregida documentalmente

`codigo_ciuo08_oit` no se trata como identificador único, porque dos perfiles pueden compartir una clasificación CIUO-08. La llave recomendada para integrar ocupaciones es:

```text
pais_codigo_iso3 + ocupacion_id
```

CIUO-08 queda como campo de clasificación y comparación internacional.

## Verificación

Los casos funcionales y de integración están descritos en:

- [tests/CASOS_API.md](tests/CASOS_API.md)
- [tests/casos_api.json](tests/casos_api.json)

La validación estática de `main.py`, `etl/ilostat_client.py` y este informe no presenta errores de diagnóstico.

## Riesgos pendientes

Estos puntos no se modifican en esta iteración:

- Los endpoints `/procesar` siguen usando `GET` por compatibilidad con la API existente. Una versión futura debería migrarlos a `POST`.
- No se incorpora autenticación, autorización ni rate limiting.
- ILOSTAT continúa dependiendo de una respuesta externa y su contrato SDMX debe cubrirse con mocks y pruebas de integración controladas.
- El repositorio todavía no tiene un runner automático `pytest`.
- Los datos locales de respaldo requieren mantener una referencia de versión, fecha de actualización y fuente verificable.

## Recomendación de revisión

Antes de publicar la API fuera de un entorno interno:

1. Convertir los casos documentados en pruebas automatizadas.
2. Añadir autenticación y límites de uso.
3. Migrar el procesamiento a comandos `POST` o tareas asíncronas.
4. Versionar los datos de respaldo y sus metadatos.
