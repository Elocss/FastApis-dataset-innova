import numpy as np
import pandas as pd
import os
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
CONSOLIDATED_FILE = os.path.join(PROCESSED_DIR, "dataset_consolidado_regional.csv")

# --------------------------------------------------------------------------
# 1. CONFIGURACIÓN METODOLÓGICA POR DEFECTO DEL ÍNDICE SINTÉTICO (IDELR)
# --------------------------------------------------------------------------
# Mapeo de alias para compatibilidad total de nombres de variables
INDICADORES_ALIAS = {
    "Tasa de Desocupación Total (% Fuerza de Trabajo)": "Tasa de Desocupación Total",
    "Tasa de Desocupación Total": "Tasa de Desocupación Total",
    "Tasa de Ocupación / Empleo": "Tasa de Ocupación",
    "Tasa de Ocupación": "Tasa de Ocupación",
    "Índice de Salario Medio Real (Base 2018=100)": "Índice de Salario Real",
    "Índice de Salario Real": "Índice de Salario Real",
    "Variación Anual del PIB Real": "Variación Anual del PIB Real",
    "Tasa de Finalización de Educación Secundaria": "Tasa de Finalización de Educación Secundaria",
    "Gasto Público en Educación (% del PIB)": "Gasto Público en Educación (% del PIB)",
    "Inflación Anual (IPC acumulado)": "Inflación Anual (IPC acumulado)",
    "Población Total": "Población Total"
}

DEFAULT_VARIABLES_CONFIG: Dict[str, Dict[str, Any]] = {
    "Variación Anual del PIB Real": {
        "dimension": "Economía",
        "peso": 0.25,
        "polaridad": "positiva",
        "min_teorico": -12.0,
        "max_teorico": 15.0,
        "descripcion": "Crecimiento del Producto Interno Bruto a precios constantes"
    },
    "Índice de Salario Real": {
        "dimension": "Salarios",
        "peso": 0.25,
        "polaridad": "positiva",
        "min_teorico": 60.0,
        "max_teorico": 120.0,
        "descripcion": "Poder adquisitivo de los salarios deflactado por IPC"
    },
    "Tasa de Ocupación": {
        "dimension": "Empleo",
        "peso": 0.20,
        "polaridad": "positiva",
        "min_teorico": 30.0,
        "max_teorico": 65.0,
        "descripcion": "Proporción de la población ocupada sobre la población total"
    },
    "Tasa de Finalización de Educación Secundaria": {
        "dimension": "Educación",
        "peso": 0.15,
        "polaridad": "positiva",
        "min_teorico": 40.0,
        "max_teorico": 90.0,
        "descripcion": "Tasa de graduación de nivel secundario/medio superior"
    },
    "Tasa de Desocupación Total": {
        "dimension": "Empleo",
        "peso": 0.15,
        "polaridad": "negativa",
        "min_teorico": 3.0,
        "max_teorico": 15.0,
        "descripcion": "Población desocupada en relación a la fuerza de trabajo activa"
    }
}

# --------------------------------------------------------------------------
# 2. MODELOS PYDANTIC PARA FastAPI
# --------------------------------------------------------------------------
class VariableCustomConfig(BaseModel):
    indicador_nombre: str = Field(..., example="Variación Anual del PIB Real")
    peso: float = Field(..., ge=0.0, le=1.0, example=0.25)
    polaridad: Optional[str] = Field("positiva", example="positiva")
    min_teorico: Optional[float] = Field(None, example=-12.0)
    max_teorico: Optional[float] = Field(None, example=15.0)

class CustomWeightsRequest(BaseModel):
    variables: List[VariableCustomConfig]
    tolerancia_epsilon: Optional[float] = Field(1.0, description="Umbral porcentual de estabilidad en % (default: 1.0%)")
    pais: Optional[str] = Field(None, description="Filtro opcional de país (ARG, CHL, URY)")
    anio_inicio: Optional[int] = Field(None, description="Año inicial (ej. 2018)")
    anio_fin: Optional[int] = Field(None, description="Año final (ej. 2024)")

# --------------------------------------------------------------------------
# 3. FUNCIONES DE NORMALIZACIÓN Y CÁLCULO FUNCIONAL
# --------------------------------------------------------------------------
def normalizar_valor(valor: float, min_val: float, max_val: float, polaridad: str = "positiva") -> float:
    """
    Normalización funcional Min-Max acotada en [0, 100].
    
    Para variables positivas:
        x_norm = ((x - min) / (max - min)) * 100
    Para variables negativas (inversas):
        x_norm = ((max - x) / (max - min)) * 100
    """
    if max_val == min_val:
        return 50.0
    val_clamped = max(min(valor, max_val), min_val)
    if polaridad.lower() == "positiva":
        return ((val_clamped - min_val) / (max_val - min_val)) * 100.0
    else:
        return ((max_val - val_clamped) / (max_val - min_val)) * 100.0

def clasificar_tendencia(delta_pct: Optional[float], epsilon: float = 1.0) -> str:
    """
    Clasificador formal de dinámicas temporales con banda muerta epsilon.
    """
    if delta_pct is None or pd.isna(delta_pct):
        return "BASE"
    if delta_pct > epsilon:
        return "CRECIMIENTO"
    elif delta_pct < -epsilon:
        return "DISMINUCION"
    else:
        return "ESTABILIDAD"

def calcular_indice_sintetico_panel(
    df: Optional[pd.DataFrame] = None,
    config: Optional[Dict[str, Dict[str, Any]]] = None,
    epsilon: float = 1.0,
    pais_filtro: Optional[str] = None,
    anio_inicio: Optional[int] = None,
    anio_fin: Optional[int] = None
) -> pd.DataFrame:
    """
    Aplica el cálculo funcional del índice sintético y clasifica la serie temporal histórica.
    """
    if df is None:
        if not os.path.exists(CONSOLIDATED_FILE):
            raise FileNotFoundError(f"No se encontró el dataset consolidado en {CONSOLIDATED_FILE}")
        df = pd.read_csv(CONSOLIDATED_FILE, encoding="utf-8-sig")

    if config is None:
        config = DEFAULT_VARIABLES_CONFIG

    # Validar o reescalar pesos para que la suma sea 1.0
    suma_pesos = sum(cfg["peso"] for cfg in config.values())
    if suma_pesos <= 0:
        raise ValueError("La suma de ponderaciones debe ser mayor a 0.")
    
    # Filtrar país y años si fueron provistos
    df_calc = df.copy()
    if pais_filtro:
        df_calc = df_calc[df_calc["pais_codigo_iso3"].str.upper() == pais_filtro.strip().upper()]
    if anio_inicio:
        df_calc = df_calc[df_calc["anio"] >= anio_inicio]
    if anio_fin:
        df_calc = df_calc[df_calc["anio"] <= anio_fin]

    # Calcular min y max empíricos si no están definidos
    for var_nom, cfg in config.items():
        sub_var = df_calc[df_calc["indicador_nombre"].map(lambda x: INDICADORES_ALIAS.get(x, x)) == var_nom]
        if not sub_var.empty:
            if cfg.get("min_teorico") is None:
                cfg["min_teorico"] = float(sub_var["valor"].min())
            if cfg.get("max_teorico") is None:
                cfg["max_teorico"] = float(sub_var["valor"].max())

    # Agrupación por País y Año para el cálculo vectorial
    filas_resultados = []
    grupos = df_calc.groupby(["pais_codigo_iso3", "anio"])

    for (pais_iso, anio), grupo in grupos:
        pais_nom = grupo["pais_nombre"].iloc[0]
        componentes_desglose = {}
        indice_acumulado = 0.0
        peso_efectivo_total = 0.0

        for _, fila in grupo.iterrows():
            indicador = INDICADORES_ALIAS.get(fila["indicador_nombre"], fila["indicador_nombre"])
            if indicador in config:
                cfg = config[indicador]
                val_real = float(fila["valor"])
                val_norm = normalizar_valor(
                    val_real,
                    cfg["min_teorico"],
                    cfg["max_teorico"],
                    cfg.get("polaridad", "positiva")
                )
                peso_norm = cfg["peso"] / suma_pesos
                contribucion = val_norm * peso_norm
                
                indice_acumulado += contribucion
                peso_efectivo_total += peso_norm
                
                componentes_desglose[indicador] = {
                    "valor_original": val_real,
                    "unidad": fila.get("unidad_medida", ""),
                    "valor_normalizado_100": round(val_norm, 2),
                    "peso_asignado": round(peso_norm, 4),
                    "contribucion_al_indice": round(contribucion, 2)
                }

        if peso_efectivo_total > 0:
            # Reajuste armónico por cobertura de datos en el año
            indice_final = (indice_acumulado / peso_efectivo_total)
            filas_resultados.append({
                "pais_codigo_iso3": pais_iso,
                "pais_nombre": pais_nom,
                "anio": int(anio),
                "indice_sintetico": round(indice_final, 2),
                "cobertura_variables_pct": round(peso_efectivo_total * 100, 1),
                "desglose_variables": componentes_desglose
            })

    df_res = pd.DataFrame(filas_resultados)
    if df_res.empty:
        return df_res

    # Ordenar cronológicamente por país y año
    df_res = df_res.sort_values(by=["pais_codigo_iso3", "anio"]).reset_index(drop=True)

    # Cálculo de dinámicas interanuales
    df_res["indice_previo"] = df_res.groupby("pais_codigo_iso3")["indice_sintetico"].shift(1)
    df_res["delta_absoluto"] = (df_res["indice_sintetico"] - df_res["indice_previo"]).round(2)
    df_res["variacion_interanual_pct"] = (
        (df_res["delta_absoluto"] / df_res["indice_previo"]) * 100.0
    ).round(2)

    # Identificación de tendencia
    df_res["tendencia"] = df_res["variacion_interanual_pct"].apply(
        lambda x: clasificar_tendencia(x, epsilon=epsilon)
    )

    # Iconografía y diagnóstico pedagógico
    icon_map = {
        "BASE": "⚪",
        "CRECIMIENTO": "🟢",
        "ESTABILIDAD": "🟡",
        "DISMINUCION": "🔴"
    }
    df_res["tendencia_icono"] = df_res["tendencia"].map(icon_map)

    # Reemplazar NaN por None para compatibilidad estricta con JSON
    df_res = df_res.replace({np.nan: None})

    return df_res

def generar_resumen_ejecutivo_paises(df_tendencias: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Genera un diagnóstico ejecutivo por país con indicadores de tendencia estructural.
    """
    resumen = []
    for pais_iso, sub_df in df_tendencias.groupby("pais_codigo_iso3"):
        sub_df = sub_df.sort_values(by="anio")
        primer_registro = sub_df.iloc[0]
        ultimo_registro = sub_df.iloc[-1]
        
        # Cálculo de pendiente OLS (Ordinary Least Squares) para ver tendencia global
        anios = sub_df["anio"].values
        indices = sub_df["indice_sintetico"].values
        if len(anios) > 1:
            pendiente, _ = np.polyfit(anios, indices, 1)
        else:
            pendiente = 0.0

        resumen.append({
            "pais_codigo_iso3": pais_iso,
            "pais_nombre": ultimo_registro["pais_nombre"],
            "periodo_analizado": f"{primer_registro['anio']} - {ultimo_registro['anio']}",
            "indice_inicial": float(primer_registro["indice_sintetico"]),
            "indice_actual_2024": float(ultimo_registro["indice_sintetico"]),
            "variacion_total_periodo_pct": round(
                ((ultimo_registro["indice_sintetico"] - primer_registro["indice_sintetico"]) / primer_registro["indice_sintetico"]) * 100.0, 2
            ),
            "pendiente_anual_promedio": round(float(pendiente), 3),
            "estado_actual_2024": ultimo_registro["tendencia"],
            "icono_actual": ultimo_registro["tendencia_icono"],
            "distribucion_tendencias": sub_df["tendencia"].value_counts().to_dict()
        })
    
    return sorted(resumen, key=lambda x: x["indice_actual_2024"], reverse=True)
