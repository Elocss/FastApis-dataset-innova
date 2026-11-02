import unittest
from fastapi.testclient import TestClient

from main import app
from etl.data_science import (
    calcular_brechas_habilidades_sectoriales,
    evaluar_comparativa_laboral_educativa,
    generar_sistema_alertas_tempranas,
    generar_reporte_integral_data_science,
    HABILIDADES_EMERGENTES_CATALOGO,
    OFERTA_EDUCATIVA_OFICIAL_REGIONAL,
    REGLAS_DETECCION_CONFIG
)

class TestDataScienceEngine(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    # -------------------------------------------------------------
    # 1. CATALOGOS Y CONFIGURACION DE REGLAS
    # -------------------------------------------------------------
    def test_catalogos_configurados(self):
        self.assertEqual(len(HABILIDADES_EMERGENTES_CATALOGO), 20)
        self.assertEqual(len(OFERTA_EDUCATIVA_OFICIAL_REGIONAL), 3)  # ARG, CHL, URY
        self.assertEqual(len(OFERTA_EDUCATIVA_OFICIAL_REGIONAL["ARG"]), 5)  # 5 sectores por país
        self.assertIn("R1_VARIACION_DEMANDA_EXTREMA", REGLAS_DETECCION_CONFIG)
        self.assertIn("R2_VOLATILIDAD_INDICE_IDELR", REGLAS_DETECCION_CONFIG)
        self.assertIn("R3_MISMATCH_EDUCATIVO_CRITICO", REGLAS_DETECCION_CONFIG)
        self.assertIn("R4_HABILIDADES_EMERGENTES_CRITICAS", REGLAS_DETECCION_CONFIG)

    # -------------------------------------------------------------
    # 2. CALCULOS MATEMATICOS DE BRECHA DE HABILIDADES
    # -------------------------------------------------------------
    def test_calcular_brechas_habilidades_sectoriales(self):
        brechas = calcular_brechas_habilidades_sectoriales()
        self.assertEqual(len(brechas), 60)  # 20 ocupaciones * 3 paises

        for b in brechas:
            self.assertIn(b["pais_codigo_iso3"], ["ARG", "CHL", "URY"])
            self.assertTrue(0.0 <= b["score_brecha_talento_100"] <= 100.0)
            self.assertIn("diagnostico_brecha", b)
            self.assertIsInstance(b["habilidades_emergentes_2026"], list)
            self.assertGreater(len(b["habilidades_emergentes_2026"]), 0)
            self.assertIn("velocidad_obsolescencia", b)

    # -------------------------------------------------------------
    # 3. COMPARATIVA LABORAL VS EDUCATIVO (COEFICIENTE CCE)
    # -------------------------------------------------------------
    def test_evaluar_comparativa_laboral_educativa(self):
        comparativa = evaluar_comparativa_laboral_educativa()
        self.assertEqual(len(comparativa), 15)  # 5 sectores * 3 paises

        for comp in comparativa:
            cce = comp["coeficiente_cobertura_educativa_cce"]
            self.assertGreater(cce, 0.0)
            self.assertIn("diagnostico_descalce", comp)
            self.assertIn(comp["estado_alerta"], ["CRITICA", "ALERTA", "ESTABLE", "ATENCION"])
            self.assertIn("fuentes_oficiales_cruzadas", comp)

    # -------------------------------------------------------------
    # 4. SISTEMA DE ALERTAS TEMPRANAS
    # -------------------------------------------------------------
    def test_generar_sistema_alertas_tempranas(self):
        sistema = generar_sistema_alertas_tempranas()
        self.assertIn("total_alertas_activas", sistema)
        self.assertIn("resumen_por_severidad", sistema)
        self.assertIn("reglas_activas", sistema)
        self.assertIn("alertas", sistema)

        total_esperado = (
            sistema["resumen_por_severidad"]["CRITICAS"] +
            sistema["resumen_por_severidad"]["ALTAS"] +
            sistema["resumen_por_severidad"]["MODERADAS"]
        )
        self.assertEqual(sistema["total_alertas_activas"], total_esperado)
        self.assertGreater(sistema["total_alertas_activas"], 0)

    # -------------------------------------------------------------
    # 5. REPORTE INTEGRAL DATA SCIENCE
    # -------------------------------------------------------------
    def test_generar_reporte_integral_data_science(self):
        reporte = generar_reporte_integral_data_science()
        self.assertIn("titulo", reporte)
        self.assertIn("region", reporte)
        self.assertIn("resumen_ejecutivo", reporte)
        self.assertIn("top_ocupaciones_con_mayor_brecha", reporte)
        self.assertIn("alertas_recientes", reporte)
        self.assertEqual(len(reporte["top_ocupaciones_con_mayor_brecha"]), 8)

    # -------------------------------------------------------------
    # 6. ENDPOINTS FASTAPI (HTTP GET)
    # -------------------------------------------------------------
    def test_endpoints_data_science_http(self):
        # 1. Brechas
        r1 = self.client.get("/api/v1/ds/brechas-habilidades?pais=ARG")
        self.assertEqual(r1.status_code, 200)
        data1 = r1.json()
        self.assertEqual(data1["status"], "success")
        self.assertEqual(data1["total_ocupaciones_analizadas"], 20)

        # 2. Reglas
        r2 = self.client.get("/api/v1/ds/reglas-deteccion")
        self.assertEqual(r2.status_code, 200)
        data2 = r2.json()
        self.assertEqual(data2["status"], "success")
        self.assertIn("R1_VARIACION_DEMANDA_EXTREMA", data2["reglas_deteccion_variaciones"])

        # 3. Alertas
        r3 = self.client.get("/api/v1/ds/alertas-tendencias?severidad=CRITICA")
        self.assertEqual(r3.status_code, 200)
        data3 = r3.json()
        self.assertIn("alertas", data3)
        for a in data3["alertas"]:
            self.assertEqual(a["severidad"], "CRITICA")

        # 4. Comparativa Educativa
        r4 = self.client.get("/api/v1/ds/comparativa-educativo-laboral?pais=ARG")
        self.assertEqual(r4.status_code, 200)
        data4 = r4.json()
        self.assertEqual(data4["status"], "success")
        self.assertEqual(len(data4["comparativa_educativo_laboral"]), 5)  # 5 sectores en ARG

        # 5. Reporte Integral
        r5 = self.client.get("/api/v1/ds/reporte-integral")
        self.assertEqual(r5.status_code, 200)
        data5 = r5.json()
        self.assertIn("resumen_ejecutivo", data5)
        self.assertEqual(data5["region"], "Cono Sur (Argentina, Chile, Uruguay)")

if __name__ == "__main__":
    unittest.main()
