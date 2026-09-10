from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import FileResponse, JSONResponse
import os
import pandas as pd
import asyncio
from typing import Optional, List, Dict

from etl.ilostat_client import fetch_ilostat_data, PAISES_INFO
from etl.cepalstat_client import fetch_cepalstat_data
from etl.ocupaciones_client import obtener_dataset_ocupaciones_sectores, OCUPACIONES_SECTORES_REPOSITORIO
from etl.cleaner import depurar_y_estructurar, exportar_csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

app = FastAPI(
    title="Innova Data Platform - Observatorio Regional (Argentina, Uruguay, Chile)",
    description="API para la ingesta desde ILOSTAT, CEPALSTAT y fuentes gubernamentales de 5 Sectores y 20 Ocupaciones estratégicas.",
    version="1.1.0"
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
@app.get("/api/v1/paises/{pais}/procesar", tags=["Indicadores Socioeconómicos"])
async def procesar_pais(
    pais: str = Path(..., description="Código ISO3 del país: URY, CHL o ARG")
):
    pais_iso = pais.upper()
    if pais_iso not in PAISES_INFO:
        raise HTTPException(status_code=400, detail=f"País '{pais}' no soportado. Use URY, CHL o ARG.")
        
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
        "total_registros": len(df_depurado)
    }

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
    
    if not os.path.exists(ruta_csv):
        await procesar_pais(pais_iso)
        
    return FileResponse(path=ruta_csv, filename=nombre_archivo, media_type="text/csv")

# --------------------------------------------------------------------------
# 2. ENDPOINTS CONSOLIDADOS REGIONALES
# --------------------------------------------------------------------------
@app.get("/api/v1/consolidado/procesar", tags=["Consolidado Regional"])
async def procesar_consolidado_regional():
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
        "paises_procesados": df_consolidado["pais_nombre"].unique().tolist()
    }

@app.get("/api/v1/consolidado/descargar", tags=["Consolidado Regional"])
async def descargar_consolidado_csv():
    ruta_consolidado = os.path.join(PROCESSED_DIR, "dataset_consolidado_regional.csv")
    if not os.path.exists(ruta_consolidado):
        await procesar_consolidado_regional()
        
    return FileResponse(path=ruta_consolidado, filename="dataset_consolidado_regional.csv", media_type="text/csv")

# --------------------------------------------------------------------------
# 3. ENDPOINTS: 5 SECTORES Y 20 OCUPACIONES ESTRATÉGICAS
# --------------------------------------------------------------------------
@app.get("/api/v1/ocupaciones/procesar", tags=["Sectores y Ocupaciones"])
def procesar_ocupaciones_sectores():
    """
    Genera el dataset depurado de las 20 ocupaciones en los 5 sectores estratégicos
    para Argentina, Uruguay y Chile, validado con CIUO-08 y fuentes gubernamentales.
    """
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

@app.get("/api/v1/ocupaciones/descargar", tags=["Sectores y Ocupaciones"])
def descargar_ocupaciones_csv():
    """
    Descarga el CSV depurado de las 20 ocupaciones y 5 sectores para los 3 países.
    """
    ruta_archivo = os.path.join(PROCESSED_DIR, "dataset_ocupaciones_sectores_produccion.csv")
    if not os.path.exists(ruta_archivo):
        procesar_ocupaciones_sectores()
        
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
    """
    Consulta en tiempo real el catálogo de las 20 ocupaciones con filtros opcionales.
    """
    datos = obtener_dataset_ocupaciones_sectores()
    df = pd.DataFrame(datos)
    
    if sector:
        df = df[df["sector"].str.lower() == sector.strip().lower()]
    if pais:
        df = df[df["pais_codigo_iso3"].str.lower() == pais.strip().lower()]
        
    return df.to_dict(orient="records")
