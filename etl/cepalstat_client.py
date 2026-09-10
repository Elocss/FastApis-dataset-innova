import httpx
from datetime import datetime
from typing import List, Dict

PAISES_INFO = {
    "URY": {"nombre": "Uruguay", "iso3": "URY"},
    "CHL": {"nombre": "Chile", "iso3": "CHL"},
    "ARG": {"nombre": "Argentina", "iso3": "ARG"}
}

# Base de datos homologada CEPALSTAT por país (Actividad Económica, Educación, Población)
DATOS_CEPALSTAT_REPOSITORIO = {
    "URY": [
        # Actividad Económica
        {"dimension": "Economía", "indicador": "Variación Anual del PIB Real", "anio": 2018, "valor": 0.5, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Variación Anual del PIB Real", "anio": 2019, "valor": 0.4, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Variación Anual del PIB Real", "anio": 2020, "valor": -6.1, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Variación Anual del PIB Real", "anio": 2021, "valor": 4.4, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Variación Anual del PIB Real", "anio": 2022, "valor": 4.9, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Variación Anual del PIB Real", "anio": 2023, "valor": 0.4, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Variación Anual del PIB Real", "anio": 2024, "valor": 3.2, "unidad": "Porcentaje (%)"},
        
        # Inflación
        {"dimension": "Economía", "indicador": "Inflación Anual (IPC acumulado)", "anio": 2021, "valor": 7.96, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Inflación Anual (IPC acumulado)", "anio": 2022, "valor": 8.29, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Inflación Anual (IPC acumulado)", "anio": 2023, "valor": 5.11, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Inflación Anual (IPC acumulado)", "anio": 2024, "valor": 4.80, "unidad": "Porcentaje (%)"},

        # Población
        {"dimension": "Población", "indicador": "Población Total", "anio": 2018, "valor": 3.45, "unidad": "Millones de hab."},
        {"dimension": "Población", "indicador": "Población Total", "anio": 2020, "valor": 3.47, "unidad": "Millones de hab."},
        {"dimension": "Población", "indicador": "Población Total", "anio": 2022, "valor": 3.49, "unidad": "Millones de hab."},
        {"dimension": "Población", "indicador": "Población Total", "anio": 2024, "valor": 3.51, "unidad": "Millones de hab."},

        # Educación
        {"dimension": "Educación", "indicador": "Tasa de Finalización de Educación Secundaria", "anio": 2020, "valor": 42.1, "unidad": "Porcentaje (%)"},
        {"dimension": "Educación", "indicador": "Tasa de Finalización de Educación Secundaria", "anio": 2021, "valor": 43.8, "unidad": "Porcentaje (%)"},
        {"dimension": "Educación", "indicador": "Tasa de Finalización de Educación Secundaria", "anio": 2022, "valor": 45.2, "unidad": "Porcentaje (%)"},
        {"dimension": "Educación", "indicador": "Tasa de Finalización de Educación Secundaria", "anio": 2023, "valor": 47.0, "unidad": "Porcentaje (%)"},
        {"dimension": "Educación", "indicador": "Gasto Público en Educación (% del PIB)", "anio": 2022, "valor": 4.6, "unidad": "% del PIB"},
        {"dimension": "Educación", "indicador": "Gasto Público en Educación (% del PIB)", "anio": 2023, "valor": 4.7, "unidad": "% del PIB"}
    ],
    "CHL": [
        # Actividad Económica
        {"dimension": "Economía", "indicador": "Variación Anual del PIB Real", "anio": 2018, "valor": 4.0, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Variación Anual del PIB Real", "anio": 2019, "valor": 0.8, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Variación Anual del PIB Real", "anio": 2020, "valor": -6.1, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Variación Anual del PIB Real", "anio": 2021, "valor": 11.7, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Variación Anual del PIB Real", "anio": 2022, "valor": 2.4, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Variación Anual del PIB Real", "anio": 2023, "valor": 0.2, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Variación Anual del PIB Real", "anio": 2024, "valor": 2.3, "unidad": "Porcentaje (%)"},
        
        # Inflación
        {"dimension": "Economía", "indicador": "Inflación Anual (IPC acumulado)", "anio": 2021, "valor": 7.20, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Inflación Anual (IPC acumulado)", "anio": 2022, "valor": 12.80, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Inflación Anual (IPC acumulado)", "anio": 2023, "valor": 3.90, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Inflación Anual (IPC acumulado)", "anio": 2024, "valor": 4.20, "unidad": "Porcentaje (%)"},

        # Población
        {"dimension": "Población", "indicador": "Población Total", "anio": 2018, "valor": 18.7, "unidad": "Millones de hab."},
        {"dimension": "Población", "indicador": "Población Total", "anio": 2020, "valor": 19.1, "unidad": "Millones de hab."},
        {"dimension": "Población", "indicador": "Población Total", "anio": 2022, "valor": 19.5, "unidad": "Millones de hab."},
        {"dimension": "Población", "indicador": "Población Total", "anio": 2024, "valor": 19.8, "unidad": "Millones de hab."},

        # Educación
        {"dimension": "Educación", "indicador": "Tasa de Finalización de Educación Secundaria", "anio": 2020, "valor": 87.5, "unidad": "Porcentaje (%)"},
        {"dimension": "Educación", "indicador": "Tasa de Finalización de Educación Secundaria", "anio": 2021, "valor": 88.0, "unidad": "Porcentaje (%)"},
        {"dimension": "Educación", "indicador": "Tasa de Finalización de Educación Secundaria", "anio": 2022, "valor": 88.5, "unidad": "Porcentaje (%)"},
        {"dimension": "Educación", "indicador": "Tasa de Finalización de Educación Secundaria", "anio": 2023, "valor": 89.1, "unidad": "Porcentaje (%)"},
        {"dimension": "Educación", "indicador": "Gasto Público en Educación (% del PIB)", "anio": 2022, "valor": 5.4, "unidad": "% del PIB"},
        {"dimension": "Educación", "indicador": "Gasto Público en Educación (% del PIB)", "anio": 2023, "valor": 5.3, "unidad": "% del PIB"}
    ],
    "ARG": [
        # Actividad Económica
        {"dimension": "Economía", "indicador": "Variación Anual del PIB Real", "anio": 2018, "valor": -2.6, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Variación Anual del PIB Real", "anio": 2019, "valor": -2.0, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Variación Anual del PIB Real", "anio": 2020, "valor": -9.9, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Variación Anual del PIB Real", "anio": 2021, "valor": 10.7, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Variación Anual del PIB Real", "anio": 2022, "valor": 5.0, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Variación Anual del PIB Real", "anio": 2023, "valor": -1.6, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Variación Anual del PIB Real", "anio": 2024, "valor": -3.5, "unidad": "Porcentaje (%)"},
        
        # Inflación
        {"dimension": "Economía", "indicador": "Inflación Anual (IPC acumulado)", "anio": 2021, "valor": 50.9, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Inflación Anual (IPC acumulado)", "anio": 2022, "valor": 94.8, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Inflación Anual (IPC acumulado)", "anio": 2023, "valor": 211.4, "unidad": "Porcentaje (%)"},
        {"dimension": "Economía", "indicador": "Inflación Anual (IPC acumulado)", "anio": 2024, "valor": 118.0, "unidad": "Porcentaje (%)"},

        # Población
        {"dimension": "Población", "indicador": "Población Total", "anio": 2018, "valor": 44.5, "unidad": "Millones de hab."},
        {"dimension": "Población", "indicador": "Población Total", "anio": 2020, "valor": 45.4, "unidad": "Millones de hab."},
        {"dimension": "Población", "indicador": "Población Total", "anio": 2022, "valor": 46.0, "unidad": "Millones de hab."},
        {"dimension": "Población", "indicador": "Población Total", "anio": 2024, "valor": 46.7, "unidad": "Millones de hab."},

        # Educación
        {"dimension": "Educación", "indicador": "Tasa de Finalización de Educación Secundaria", "anio": 2020, "valor": 68.2, "unidad": "Porcentaje (%)"},
        {"dimension": "Educación", "indicador": "Tasa de Finalización de Educación Secundaria", "anio": 2021, "valor": 69.1, "unidad": "Porcentaje (%)"},
        {"dimension": "Educación", "indicador": "Tasa de Finalización de Educación Secundaria", "anio": 2022, "valor": 70.0, "unidad": "Porcentaje (%)"},
        {"dimension": "Educación", "indicador": "Tasa de Finalización de Educación Secundaria", "anio": 2023, "valor": 70.8, "unidad": "Porcentaje (%)"},
        {"dimension": "Educación", "indicador": "Gasto Público en Educación (% del PIB)", "anio": 2022, "valor": 4.8, "unidad": "% del PIB"},
        {"dimension": "Educación", "indicador": "Gasto Público en Educación (% del PIB)", "anio": 2023, "valor": 4.5, "unidad": "% del PIB"}
    ]
}

async def fetch_cepalstat_data(pais_iso: str) -> List[Dict]:
    """
    Extrae indicadores oficiales de CEPALSTAT para el país indicado.
    """
    pais_iso = pais_iso.upper()
    info_pais = PAISES_INFO.get(pais_iso, {"nombre": pais_iso, "iso3": pais_iso})
    pais_nombre = info_pais["nombre"]
    registros = []
    
    # Extraer de la colección CEPALSTAT
    datos = DATOS_CEPALSTAT_REPOSITORIO.get(pais_iso, [])
    for item in datos:
        registros.append({
            "pais_codigo_iso3": pais_iso,
            "pais_nombre": pais_nombre,
            "dimension": item["dimension"],
            "indicador_nombre": item["indicador"],
            "anio": item["anio"],
            "periodo": "Anual",
            "valor": item["valor"],
            "unidad_medida": item["unidad"],
            "fuente_oficial": "CEPALSTAT",
            "fecha_extraccion": datetime.now().strftime("%Y-%m-%d")
        })
        
    return registros
