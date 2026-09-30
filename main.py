from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import FileResponse
import os
import time
import pandas as pd
import asyncio
from typing import Optional, List, Dict

from etl.ilostat_client import fetch_ilostat_data, PAISES_INFO
from etl.cepalstat_client import fetch_cepalstat_data
from etl.ocupaciones_client import obtener_dataset_ocupaciones_sectores
from etl.cleaner import depurar_y_estructurar, exportar_csv
from etl.analytics import (
    DEFAULT_VARIABLES_CONFIG,
    CustomWeightsRequest,
    calcular_indice_sintetico_panel,
    generar_resumen_ejecutivo_paises
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

CACHE_MAX_AGE_SECONDS = 24 * 60 * 60
pipeline_lock = asyncio.Lock()

app = FastAPI(
    title="Innova Data Platform - Observatorio Regional (Argentina, Uruguay, Chile)",
    description="API para la ingesta desde ILOSTAT, CEPALSTAT y fuentes gubernamentales de 5 Sectores y 20 Ocupaciones estratégicas con motor analítico de tendencias e índices compuestos.",
    version="1.2.0"
)

@app.get("/", tags=["General"])
def read_root():
    return {
        "proyecto": "Innova Lab - Observatorio de Indicadores y Ocupaciones Regionales",
        "paises_soportados": ["ARG (Argentina)", "URY (Uruguay)", "CHL (Chile)"],
        "sectores_analizados": ["Tecnología", "Salud", "Energía", "Turismo", "Economía del Conocimiento"],
        "total_ocupaciones_estudiadas": 20,
        "fuentes_oficiales": [
            "ILOSTAT - OIT (Estándar CIUO-08)",
            "CEPALSTAT",
            "INDEC / Sec. Economía del Conocimiento (Argentina)",
            "INE / MIEM / CUTI (Uruguay)",
            "INE / SENCE / Min. Energía (Chile)"
        ],
        "documentacion_swagger": "/docs",
        "status": "online"
    }

# --------------------------------------------------------------------------
# 1. ENDPOINTS DE INDICADORES SOCIOECONÓMICOS POR PAÍS
# --------------------------------------------------------------------------
def archivo_necesita_actualizacion(ruta_archivo: str) -> bool:
    if not os.path.exists(ruta_archivo):
        return True
    return time.time() - os.path.getmtime(ruta_archivo) > CACHE_MAX_AGE_SECONDS

def fuentes_de_registros(registros: List[Dict]) -> List[str]:
    return sorted({registro["fuente_oficial"] for registro in registros if registro.get("fuente_oficial")})

async def _procesar_pais(pais_iso: str) -> Dict:
    nombre_pais = PAISES_INFO[pais_iso]["nombre"]

    datos_ilo, datos_cepal = await asyncio.gather(
        fetch_ilostat_data(pais_iso),
        fetch_cepalstat_data(pais_iso)
    )

    datos_totales = datos_ilo + datos_cepal
    df_depurado = depurar_y_estructurar(datos_totales)

    nombre_archivo = f"dataset_{nombre_pais.lower()}_produccion.csv"
    ruta_csv = os.path.join(PROCESSED_DIR, nombre_archivo)
    exportar_csv(df_depurado, ruta_csv)

    return {
        "status": "Completado con éxito",
        "pais": nombre_pais,
        "codigo_iso3": pais_iso,
        "archivo_guardado": nombre_archivo,
        "total_registros": len(df_depurado),
        "fuentes_oficiales": fuentes_de_registros(datos_totales)
    }

@app.get("/api/v1/paises/{pais}/procesar", tags=["Indicadores Socioeconómicos"])
async def procesar_pais(
    pais: str = Path(..., description="Código ISO3 del país: URY, CHL o ARG")
):
    pais_iso = pais.upper()
    if pais_iso not in PAISES_INFO:
        raise HTTPException(status_code=400, detail=f"País '{pais}' no soportado. Use URY, CHL o ARG.")

    async with pipeline_lock:
        return await _procesar_pais(pais_iso)

@app.get("/api/v1/paises/{pais}/descargar", tags=["Indicadores Socioeconómicos"])
async def descargar_csv_pais(
    pais: str = Path(..., description="Código ISO3: URY, CHL o ARG")
):
    pais_iso = pais.upper()
    if pais_iso not in PAISES_INFO:
        raise HTTPException(status_code=400, detail="País no soportado.")

    nombre_pais = PAISES_INFO[pais_iso]["nombre"]
    nombre_archivo = f"dataset_{nombre_pais.lower()}_produccion.csv"
    ruta_csv = os.path.join(PROCESSED_DIR, nombre_archivo)

    if archivo_necesita_actualizacion(ruta_csv):
        async with pipeline_lock:
            if archivo_necesita_actualizacion(ruta_csv):
                await _procesar_pais(pais_iso)

    return FileResponse(path=ruta_csv, filename=nombre_archivo, media_type="text/csv")

# --------------------------------------------------------------------------
# 2. ENDPOINTS CONSOLIDADOS REGIONALES
# --------------------------------------------------------------------------
async def _procesar_consolidado_regional() -> Dict:
    tareas = [
        asyncio.gather(fetch_ilostat_data(p), fetch_cepalstat_data(p))
        for p in ["URY", "CHL", "ARG"]
    ]
    resultados = await asyncio.gather(*tareas)

    todos_los_datos = []
    for datos_ilo, datos_cepal in resultados:
        todos_los_datos.extend(datos_ilo)
        todos_los_datos.extend(datos_cepal)

    df_consolidado = depurar_y_estructurar(todos_los_datos)

    ruta_consolidado = os.path.join(PROCESSED_DIR, "dataset_consolidado_regional.csv")
    exportar_csv(df_consolidado, ruta_consolidado)

    for pais_iso in ["URY", "CHL", "ARG"]:
        nom = PAISES_INFO[pais_iso]["nombre"]
        sub_df = df_consolidado[df_consolidado["pais_codigo_iso3"] == pais_iso]
        exportar_csv(sub_df, os.path.join(PROCESSED_DIR, f"dataset_{nom.lower()}_produccion.csv"))

    return {
        "status": "Pipeline regional completado",
        "archivo_generado": "dataset_consolidado_regional.csv",
        "total_filas_consolidadas": len(df_consolidado),
        "paises_procesados": df_consolidado["pais_nombre"].unique().tolist(),
        "fuentes_oficiales": fuentes_de_registros(todos_los_datos)
    }

@app.get("/api/v1/consolidado/procesar", tags=["Consolidado Regional"])
async def procesar_consolidado_regional():
    async with pipeline_lock:
        return await _procesar_consolidado_regional()

@app.get("/api/v1/consolidado/descargar", tags=["Consolidado Regional"])
async def descargar_consolidado_csv():
    ruta_consolidado = os.path.join(PROCESSED_DIR, "dataset_consolidado_regional.csv")
    if archivo_necesita_actualizacion(ruta_consolidado):
        async with pipeline_lock:
            if archivo_necesita_actualizacion(ruta_consolidado):
                await _procesar_consolidado_regional()

    return FileResponse(path=ruta_consolidado, filename="dataset_consolidado_regional.csv", media_type="text/csv")

# --------------------------------------------------------------------------
# 3. ENDPOINTS: 5 SECTORES Y 20 OCUPACIONES ESTRATÉGICAS
# --------------------------------------------------------------------------
def _generar_ocupaciones_sectores() -> Dict:
    datos = obtener_dataset_ocupaciones_sectores()
    df = pd.DataFrame(datos)

    ruta_archivo = os.path.join(PROCESSED_DIR, "dataset_ocupaciones_sectores_produccion.csv")
    exportar_csv(df, ruta_archivo)

    return {
        "status": "Dataset de ocupaciones generado con éxito",
        "archivo_generado": "dataset_ocupaciones_sectores_produccion.csv",
        "total_filas": len(df),
        "sectores": df["sector"].unique().tolist(),
        "total_ocupaciones_unicas": df["ocupacion_nombre"].nunique(),
        "paises": df["pais_nombre"].unique().tolist()
    }

@app.get("/api/v1/ocupaciones/procesar", tags=["Sectores y Ocupaciones"])
async def procesar_ocupaciones_sectores():
    async with pipeline_lock:
        return _generar_ocupaciones_sectores()

@app.get("/api/v1/ocupaciones/descargar", tags=["Sectores y Ocupaciones"])
def descargar_ocupaciones_csv():
    ruta_archivo = os.path.join(PROCESSED_DIR, "dataset_ocupaciones_sectores_produccion.csv")
    if archivo_necesita_actualizacion(ruta_archivo):
        async with pipeline_lock:
            if archivo_necesita_actualizacion(ruta_archivo):
                _generar_ocupaciones_sectores()

    return FileResponse(
        path=ruta_archivo,
        filename="dataset_ocupaciones_sectores_produccion.csv",
        media_type="text/csv"
    )

@app.get("/api/v1/ocupaciones/catalogo", tags=["Sectores y Ocupaciones"])
def catalogo_ocupaciones(
    sector: Optional[str] = Query(None, description="Filtrar por sector: Tecnología, Salud, Energía, Turismo, Economía del Conocimiento"),
    pais: Optional[str] = Query(None, description="Filtrar por país: URY, CHL o ARG")
):
    datos = obtener_dataset_ocupaciones_sectores()
    df = pd.DataFrame(datos)

    if sector:
        df = df[df["sector"].str.lower() == sector.strip().lower()]
    if pais:
        df = df[df["pais_codigo_iso3"].str.lower() == pais.strip().lower()]

    return df.to_dict(orient="records")

# --------------------------------------------------------------------------
# 4. ENDPOINTS: CÁLCULO DE ÍNDICE SINTÉTICO, DINÁMICA TEMPORAL Y TENDENCIAS
# --------------------------------------------------------------------------
@app.get("/api/v1/analytics/configuracion-ponderaciones", tags=["Analytics & Índices Sintéticos"])
def obtener_configuracion_ponderaciones():
    """
    Retorna el modelo metodológico de variables, ponderaciones, dimensiones y polaridades
    utilizadas para el cálculo del Índice de Desarrollo Económico-Laboral Regional.
    """
    return {
        "indice_nombre": "Índice de Desarrollo Económico-Laboral Regional (IDELR)",
        "metodologia": "Normalización Min-Max [0, 100] + Agregación Lineal Ponderada",
        "variables_configuradas": DEFAULT_VARIABLES_CONFIG,
        "restriccion_pesos": "La suma de ponderaciones equivale a 1.0 (100%)"
    }

@app.get("/api/v1/analytics/indice-sintetico", tags=["Analytics & Índices Sintéticos"])
def consultar_indice_sintetico(
    pais: Optional[str] = Query(None, description="Filtrar por código ISO3: ARG, CHL o URY"),
    anio_inicio: Optional[int] = Query(2018, description="Año de inicio de la serie temporal (recomendado 2018)"),
    anio_fin: Optional[int] = Query(2024, description="Año final de la serie temporal"),
    tolerancia_epsilon: float = Query(1.0, description="Umbral de tolerancia (%) para clasificar ESTABILIDAD vs CRECIMIENTO/DISMINUCIÓN")
):
    """
    Calcula de manera funcional el índice sintético y su evolución histórica,
    identificando la tasa de variación interanual y la tendencia (Crecimiento, Estabilidad, Disminución).
    """
    df_res = calcular_indice_sintetico_panel(
        epsilon=tolerancia_epsilon,
        pais_filtro=pais,
        anio_inicio=anio_inicio,
        anio_fin=anio_fin
    )
    return {
        "total_registros_calculados": len(df_res),
        "parametros_aplicados": {
            "pais_filtro": pais,
            "periodo": f"{anio_inicio or 'Min'} - {anio_fin or 'Max'}",
            "tolerancia_epsilon_pct": tolerancia_epsilon
        },
        "serie_historica": df_res.to_dict(orient="records")
    }

@app.post("/api/v1/analytics/indice-sintetico/custom", tags=["Analytics & Índices Sintéticos"])
def calcular_indice_sintetico_personalizado(payload: CustomWeightsRequest):
    """
    Permite a los usuarios y dashboards definir dinámicamente un vector de variables y ponderaciones personalizadas.
    """
    custom_cfg = {}
    for var in payload.variables:
        custom_cfg[var.indicador_nombre] = {
            "peso": var.peso,
            "polaridad": var.polaridad or "positiva",
            "min_teorico": var.min_teorico,
            "max_teorico": var.max_teorico
        }
    
    df_res = calcular_indice_sintetico_panel(
        config=custom_cfg,
        epsilon=payload.tolerancia_epsilon or 1.0,
        pais_filtro=payload.pais,
        anio_inicio=payload.anio_inicio,
        anio_fin=payload.anio_fin
    )
    return {
        "mensaje": "Índice personalizado calculado con éxito",
        "variables_evaluadas": list(custom_cfg.keys()),
        "serie_historica": df_res.to_dict(orient="records")
    }

@app.get("/api/v1/analytics/tendencias/resumen-ejecutivo", tags=["Analytics & Índices Sintéticos"])
def resumen_ejecutivo_tendencias(
    anio_inicio: Optional[int] = Query(2018, description="Año inicial para el análisis de tendencia"),
    tolerancia_epsilon: float = Query(1.0, description="Umbral de estabilidad porcentual")
):
    """
    Genera un diagnóstico comparativo por país con pendientes de regresión OLS,
    variación acumulada total y estado actual de tendencia.
    """
    df_res = calcular_indice_sintetico_panel(
        epsilon=tolerancia_epsilon,
        anio_inicio=anio_inicio
    )
    resumen = generar_resumen_ejecutivo_paises(df_res)
    return {
        "titulo": "Diagnóstico Ejecutivo de Tendencias Regionales (Argentina, Chile, Uruguay)",
        "diagnostico_paises": resumen
    }

@app.get("/api/v1/analytics/descargar", tags=["Analytics & Índices Sintéticos"])
def descargar_analitica_csv(
    anio_inicio: Optional[int] = Query(2018, description="Año inicial")
):
    """
    Genera y descarga el CSV analítico con el índice sintético y las clasificaciones de tendencia
    listo para su ingesta en Power BI, Tableau o Excel.
    """
    df_res = calcular_indice_sintetico_panel(anio_inicio=anio_inicio)
    
    df_export = df_res[[
        "pais_codigo_iso3", "pais_nombre", "anio", 
        "indice_sintetico", "indice_previo", "delta_absoluto", 
        "variacion_interanual_pct", "tendencia"
    ]].copy()
    
    ruta_export = os.path.join(PROCESSED_DIR, "dataset_analitico_indice_tendencias.csv")
    exportar_csv(df_export, ruta_export)
    
    return FileResponse(
        path=ruta_export,
        filename="dataset_analitico_indice_tendencias.csv",
        media_type="text/csv"
    )
