import pandas as pd
import os
from typing import List, Dict

ESQUEMA_COLUMNAS = [
    "pais_codigo_iso3",
    "pais_nombre",
    "dimension",
    "indicador_nombre",
    "anio",
    "periodo",
    "valor",
    "unidad_medida",
    "fuente_oficial",
    "fecha_extraccion"
]

def depurar_y_estructurar(datos: List[Dict]) -> pd.DataFrame:
    """
    Aplica las reglas de depuración de calidad de datos para producción:
    1. Asegura todas las columnas requeridas
    2. Elimina duplicados
    3. Elimina o corrige nulos
    4. Fuerza los tipos de datos exactos
    5. Ordena cronológicamente
    """
    if not datos:
        return pd.DataFrame(columns=ESQUEMA_COLUMNAS)
        
    df = pd.DataFrame(datos)
    
    # 1. Asegurar columnas faltantes si las hubiera
    for col in ESQUEMA_COLUMNAS:
        if col not in df.columns:
            df[col] = None
            
    df = df[ESQUEMA_COLUMNAS]
    
    # 2. Eliminación de duplicados
    df = df.drop_duplicates(subset=["pais_codigo_iso3", "dimension", "indicador_nombre", "anio"])
    
    # 3. Tratamiento de nulos en llaves y valores
    df = df.dropna(subset=["pais_codigo_iso3", "indicador_nombre", "anio", "valor"])
    
    # 4. Tipado estricto
    df["anio"] = df["anio"].astype(int)
    df["valor"] = df["valor"].astype(float).round(2)
    df["pais_codigo_iso3"] = df["pais_codigo_iso3"].astype(str).str.strip().str.upper()
    df["pais_nombre"] = df["pais_nombre"].astype(str).str.strip()
    df["dimension"] = df["dimension"].astype(str).str.strip()
    df["indicador_nombre"] = df["indicador_nombre"].astype(str).str.strip()
    
    # 5. Ordenamiento estándar
    df = df.sort_values(
        by=["pais_nombre", "dimension", "indicador_nombre", "anio"],
        ascending=[True, True, True, True]
    ).reset_index(drop=True)
    
    return df

def exportar_csv(df: pd.DataFrame, ruta_destino: str) -> str:
    """
    Exporta el DataFrame a CSV con codificación utf-8-sig (compatible 100% con Excel y Power BI).
    """
    os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
    df.to_csv(ruta_destino, index=False, encoding="utf-8-sig")
    return ruta_destino
