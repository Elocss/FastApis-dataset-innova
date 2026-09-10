from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import FileResponse, JSONResponse
import os
import pandas as pd
import asyncio
from typing import Optional, List, Dict

from etl.ilostat_client import fetch_ilostat_data, PAISES_INFO
from etl.cepalstat_client import fetch_cepalstat_data
from etl.cleaner import depurar_y_estructurar, exportar_csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

app = FastAPI(
    title="Innova Data Platform - Pipeline Regional (Uruguay, Chile, Argentina)",
    description="API para la ingesta desde ILOSTAT y CEPALSTAT, depuración de calidad de datos y generación de CSVs listos para producción.",
    version="1.0.0"
)

@app.get("/", tags=["General"])
def read_root():
    return {
        "proyecto": "Innova Lab - Observatorio Regional de Indicadores",
        "paises_soportados": ["URY (Uruguay)", "CHL (Chile)", "ARG (Argentina)"],
        "fuentes_oficiales": ["ILOSTAT - OIT", "CEPALSTAT"],
        "documentacion_swagger": "/docs",
        "status": "online"
    }

# --------------------------------------------------------------------------
# ENDPOINTS POR PAÍS: URUGUAY, CHILE, ARGENTINA
# --------------------------------------------------------------------------
@app.get("/api/v1/paises/{pais}/procesar", tags=["Ingesta y Depuración por País"])
async def procesar_pais(
    pais: str = Path(..., description="Código ISO3 del país: URY, CHL o ARG")
):
    """
    Ejecuta la ingesta desde ILOSTAT y CEPALSTAT, aplica el pipeline de limpieza
    y genera el archivo CSV de producción para el país indicado.
    """
    pais_iso = pais.upper()
    if pais_iso not in PAISES_INFO:
        raise HTTPException(status_code=400, detail=f"País '{pais}' no soportado. Use URY, CHL o ARG.")
        
    nombre_pais = PAISES_INFO[pais_iso]["nombre"]
    
    # 1. Ingesta concurrente de ambas fuentes
    datos_ilo, datos_cepal = await asyncio.gather(
        fetch_ilostat_data(pais_iso),
        fetch_cepalstat_data(pais_iso)
    )
    
    datos_totales = datos_ilo + datos_cepal
    
    # 2. Pipeline de calidad y depuración
    df_depurado = depurar_y_estructurar(datos_totales)
    
    # 3. Guardado en carpeta processed
    nombre_archivo = f"dataset_{nombre_pais.lower()}_produccion.csv"
    ruta_csv = os.path.join(PROCESSED_DIR, nombre_archivo)
    exportar_csv(df_depurado, ruta_csv)
    
    return {
        "status": "Completado con éxito",
        "pais": nombre_pais,
        "codigo_iso3": pais_iso,
        "archivo_guardado": nombre_archivo,
        "ruta_absoluta": ruta_csv,
        "total_registros": len(df_depurado),
        "dimensiones": df_depurado["dimension"].unique().tolist(),
        "indicadores_depurados": df_depurado["indicador_nombre"].unique().tolist(),
        "rango_anios": f"{df_depurado['anio'].min()} - {df_depurado['anio'].max()}"
    }

@app.get("/api/v1/paises/{pais}/descargar", tags=["Descargas CSV"])
async def descargar_csv_pais(
    pais: str = Path(..., description="Código ISO3: URY, CHL o ARG")
):
    """
    Descarga el archivo CSV depurado y listo para producción del país seleccionado.
    """
    pais_iso = pais.upper()
    if pais_iso not in PAISES_INFO:
        raise HTTPException(status_code=400, detail="País no soportado.")
        
    nombre_pais = PAISES_INFO[pais_iso]["nombre"]
    nombre_archivo = f"dataset_{nombre_pais.lower()}_produccion.csv"
    ruta_csv = os.path.join(PROCESSED_DIR, nombre_archivo)
    
    # Si no existe aún el archivo, lo generamos automáticamente
    if not os.path.exists(ruta_csv):
        await procesar_pais(pais_iso)
        
    return FileResponse(
        path=ruta_csv,
        filename=nombre_archivo,
        media_type="text/csv"
    )

# --------------------------------------------------------------------------
# PIPELINE CONSOLIDADO REGIONAL (LOS 3 PAÍSES)
# --------------------------------------------------------------------------
@app.get("/api/v1/consolidado/procesar", tags=["Consolidado Regional"])
async def procesar_consolidado_regional():
    """
    Procesa Uruguay, Chile y Argentina en paralelo, unifica la taxonomía
    y genera el dataset consolidado regional.
    """
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
    
    # También generamos los individuales
    for pais_iso in ["URY", "CHL", "ARG"]:
        nom = PAISES_INFO[pais_iso]["nombre"]
        sub_df = df_consolidado[df_consolidado["pais_codigo_iso3"] == pais_iso]
        exportar_csv(sub_df, os.path.join(PROCESSED_DIR, f"dataset_{nom.lower()}_produccion.csv"))
        
    return {
        "status": "Pipeline regional completado",
        "archivo_generado": "dataset_consolidado_regional.csv",
        "total_filas_consolidadas": len(df_consolidado),
        "paises_procesados": df_consolidado["pais_nombre"].unique().tolist(),
        "resumen_por_pais": df_consolidado.groupby("pais_nombre").size().to_dict()
    }

@app.get("/api/v1/consolidado/descargar", tags=["Descargas CSV"])
async def descargar_consolidado_csv():
    """
    Descarga el dataset consolidado con los datos depurados de Uruguay, Chile y Argentina.
    """
    ruta_consolidado = os.path.join(PROCESSED_DIR, "dataset_consolidado_regional.csv")
    if not os.path.exists(ruta_consolidado):
        await procesar_consolidado_regional()
        
    return FileResponse(
        path=ruta_consolidado,
        filename="dataset_consolidado_regional.csv",
        media_type="text/csv"
    )

# --------------------------------------------------------------------------
# INFORME Y RESUMEN EJECUTIVO (METADATOS PARA DOCUMENTAR)
# --------------------------------------------------------------------------
@app.get("/api/v1/informe-metadatos", tags=["Documentación y Reportes"])
def obtener_informe_metadatos():
    """
    Entrega el reporte formal de metadatos, fuentes, indicadores y cobertura temporal.
    """
    return {
        "titulo": "Informe Técnico de Extracción y Depuración de Indicadores Regionales",
        "paises": {
            "Uruguay": {"iso3": "URY", "fuentes": ["ILOSTAT", "CEPALSTAT"], "enfoque": "Fase 1 Inicial"},
            "Chile": {"iso3": "CHL", "fuentes": ["ILOSTAT", "CEPALSTAT"], "enfoque": "Fase 2 Comparativa"},
            "Argentina": {"iso3": "ARG", "fuentes": ["ILOSTAT", "CEPALSTAT"], "enfoque": "Fase 3 Validada"}
        },
        "dimensiones_cubiertas": [
            "Actividad Económica (PIB Real, Inflación)",
            "Mercado Laboral (Desempleo, Ocupación, Salarios)",
            "Educación (Conclusión Secundaria, Gasto % PIB)",
            "Población (Población Total)"
        ],
        "estandares_aplicados": [
            "ISO 3166-1 alfa-3 para códigos de país",
            "Codificación UTF-8 con BOM (utf-8-sig) para compatibilidad internacional",
            "Tratamiento estricto de valores nulos y duplicados",
            "Tipado numérico estándar para carga en data warehouses / BI"
        ]
    }
