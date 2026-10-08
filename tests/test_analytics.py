import unittest
import pandas as pd
import numpy as np
from fastapi.testclient import TestClient

from main import app
from etl.analytics import (
    normalizar_valor,
    clasificar_tendencia,
    parse_tasa_crecimiento,
    calcular_indice_sintetico_panel,
    calcular_indice_oportunidad_laboral,
    generar_matriz_validacion_cruzada,
    DEFAULT_VARIABLES_CONFIG,
    DEFAULT_ICOL_WEIGHTS
)

class TestAnalyticsEngine(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    # -------------------------------------------------------------
    # 1. PRUEBAS DE NORMALIZACIÓN Y MATEMÁTICA ANALÍTICA
    # -------------------------------------------------------------
    def test_normalizar_valor_polaridad_positiva(self):
        # Valor en el punto medio
        res = normalizar_valor(valor=50.0, min_val=0.0, max_val=100.0, polaridad="positiva")
        self.assertEqual(res, 50.0)

        # Clamping superior
        res_clamp_sup = normalizar_valor(valor=120.0, min_val=0.0, max_val=100.0, polaridad="positiva")
        self.assertEqual(res_clamp_sup, 100.0)

        # Clamping inferior
        res_clamp_inf = normalizar_valor(valor=-10.0, min_val=0.0, max_val=100.0, polaridad="positiva")
        self.assertEqual(res_clamp_inf, 0.0)

    def test_normalizar_valor_polaridad_negativa(self):
        # Desocupación: mayor valor es peor score (0), menor valor es mejor score (100)
        res_min = normalizar_valor(valor=3.0, min_val=3.0, max_val=15.0, polaridad="negativa")
        self.assertEqual(res_min, 100.0)

        res_max = normalizar_valor(valor=15.0, min_val=3.0, max_val=15.0, polaridad="negativa")
        self.assertEqual(res_max, 0.0)

    def test_clasificar_tendencia_epsilon(self):
        self.assertEqual(clasificar_tendencia(None), "BASE")
        self.assertEqual(clasificar_tendencia(0.5, epsilon=1.0), "ESTABILIDAD")
        self.assertEqual(clasificar_tendencia(-0.8, epsilon=1.0), "ESTABILIDAD")
        self.assertEqual(clasificar_tendencia(2.5, epsilon=1.0), "CRECIMIENTO")
        self.assertEqual(clasificar_tendencia(-3.1, epsilon=1.0), "DISMINUCION")

    def test_parse_tasa_crecimiento(self):
        self.assertEqual(parse_tasa_crecimiento("+18.5% anual"), 18.5)
        self.assertEqual(parse_tasa_crecimiento("24.0%"), 24.0)
        self.assertEqual(parse_tasa_crecimiento(-5.2), -5.2)
        self.assertEqual(parse_tasa_crecimiento("sin dato"), 0.0)

    # -------------------------------------------------------------
    # 2. PRUEBAS DEL ÍNDICE SINTÉTICO MACROECONÓMICO (IDELR)
    # -------------------------------------------------------------
    def test_calcular_indice_sintetico_panel(self):
        df_res = calcular_indice_sintetico_panel()
        self.assertFalse(df_res.empty)
        self.assertIn("indice_sintetico", df_res.columns)
        self.assertIn("tendencia", df_res.columns)
        self.assertIn("desglose_variables", df_res.columns)

        # Invariante: el índice debe estar en [0, 100]
        self.assertTrue((df_res["indice_sintetico"] >= 0.0).all())
        self.assertTrue((df_res["indice_sintetico"] <= 100.0).all())

        # Los tres países deben estar presentes
        paises_presentes = set(df_res["pais_codigo_iso3"].unique())
        self.assertTrue({"ARG", "CHL", "URY"}.issubset(paises_presentes))

    # -------------------------------------------------------------
    # 3. PRUEBAS DEL ÍNDICE COMPUESTO DE OPORTUNIDAD LABORAL (ICOL)
    # -------------------------------------------------------------
    def test_calcular_indice_oportunidad_laboral_dimensiones(self):
        df_icol = calcular_indice_oportunidad_laboral()
        
        # 3 países x 20 ocupaciones = 60 filas
        self.assertEqual(len(df_icol), 60)
        self.assertEqual(df_icol["ocupacion_id"].nunique(), 20)
        self.assertEqual(df_icol["sector"].nunique(), 5)
        self.assertEqual(df_icol["pais_codigo_iso3"].nunique(), 3)

        # Invariante de rango [0, 100]
        self.assertTrue((df_icol["indice_oportunidad_icol"] >= 0.0).all())
        self.assertTrue((df_icol["indice_oportunidad_icol"] <= 100.0).all())

        # Integridad de rankings
        self.assertTrue((df_icol["ranking_regional"] >= 1).all())
        self.assertTrue((df_icol["ranking_pais"] >= 1).all())
        self.assertTrue((df_icol["ranking_sector"] >= 1).all())

    def test_matriz_validacion_cruzada_control_calidad(self):
        matriz = generar_matriz_validacion_cruzada()
        self.assertEqual(matriz["status"], "Validación exitosa")
        self.assertEqual(matriz["total_combinaciones_validadas"], 60)
        self.assertTrue(matriz["control_calidad"]["invariante_rango_0_100"])
        self.assertTrue(matriz["control_calidad"]["integridad_sin_nulos"])
        self.assertEqual(len(matriz["resumen_sectores"]), 5)
        self.assertEqual(len(matriz["resumen_paises"]), 3)

    # -------------------------------------------------------------
    # 4. PRUEBAS DE INTEGRACIÓN CON FASTAPI
    # -------------------------------------------------------------
    def test_api_ranking_ocupaciones(self):
        response = self.client.get("/api/v1/analytics/ocupaciones/ranking?pais=ARG&sector=Tecnolog%C3%ADa")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("ranking_ocupaciones", data)
        self.assertEqual(data["total_ocupaciones_evaluadas"], 4)
        for item in data["ranking_ocupaciones"]:
            self.assertEqual(item["pais_codigo_iso3"], "ARG")
            self.assertEqual(item["sector"], "Tecnología")

    def test_api_validacion_cruzada(self):
        response = self.client.get("/api/v1/analytics/ocupaciones/validacion-cruzada")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_combinaciones_validadas"], 60)
        self.assertTrue(data["control_calidad"]["invariante_rango_0_100"])

    def test_api_simulacion_custom_ocupaciones(self):
        payload = {
            "peso_macro_idelr": 0.20,
            "peso_demanda_mercado": 0.50,
            "peso_crecimiento_estimado": 0.30,
            "pais": "URY"
        }
        response = self.client.post("/api/v1/analytics/ocupaciones/custom", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_evaluadas"], 20)
        self.assertEqual(data["ponderaciones_utilizadas"]["peso_demanda_mercado"], 0.50)

if __name__ == "__main__":
    unittest.main()
