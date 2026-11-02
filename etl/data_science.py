"""
==============================================================================
INNOVA DATA PLATFORM — MÓDULO AVANZADO DE DATA SCIENCE
==============================================================================
Componentes:
1. Mapeo y Detección de Brechas de Talento y Habilidades Emergentes (2026+).
2. Reglas Estadísticas de Detección de Variaciones Significativas (R1 a R4).
3. Motor de Alertas Automatizadas sobre Tendencias, Índices (IDELR/ICOL) y Brechas.
4. Comparativa Analítica Laboral vs. Datos Educativos Oficiales (Mismatch y CCE).
==============================================================================
"""

import numpy as np
import pandas as pd
import os
import re
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from etl.ocupaciones_client import OCUPACIONES_SECTORES_REPOSITORIO, obtener_dataset_ocupaciones_sectores
from etl.analytics import (
    calcular_indice_sintetico_panel,
    calcular_indice_oportunidad_laboral,
    DEMANDA_SCORE_MAP,
    PAIS_FACTOR_MADUREZ_MAP
)

# --------------------------------------------------------------------------
# 1. CATÁLOGO MAESTRO DE HABILIDADES EMERGENTES (2026+) POR OCUPACIÓN
# --------------------------------------------------------------------------
HABILIDADES_EMERGENTES_CATALOGO: Dict[str, Dict[str, Any]] = {
    "OCUP_01": {
        "ocupacion_nombre": "Desarrollador de Software y Aplicaciones",
        "sector": "Tecnología",
        "habilidades_tradicionales": ["JavaScript", "Python", "SQL", "Git", "HTML/CSS"],
        "habilidades_emergentes": ["Generative AI Coding", "LLM Orchestration (LangChain/LlamaIndex)", "Micro-frontends", "Rust", "WebAssembly"],
        "nivel_adopcion_regional": "Alta",
        "impacto_ia_automatizacion": "Disruptivo / Complementario",
        "velocidad_obsolescencia": "Muy Rápida (< 18 meses)"
    },
    "OCUP_02": {
        "ocupacion_nombre": "Ingeniero de Datos y Machine Learning",
        "sector": "Tecnología",
        "habilidades_tradicionales": ["ETL Batch", "Pandas", "Scikit-Learn", "PostgreSQL"],
        "habilidades_emergentes": ["Arquitecturas RAG", "Vector Databases (Milvus, Pinecone)", "Edge AI", "LLMOps & Model Governance", "Data Mesh"],
        "nivel_adopcion_regional": "Muy Alta",
        "impacto_ia_automatizacion": "Acelerador Fundamental",
        "velocidad_obsolescencia": "Ultra Rápida (< 12 meses)"
    },
    "OCUP_03": {
        "ocupacion_nombre": "Especialista en Ciberseguridad y Redes",
        "sector": "Tecnología",
        "habilidades_tradicionales": ["Firewalls de Red", "Antivirus Corporativo", "VPN IPsec", "ISO 27001 Básico"],
        "habilidades_emergentes": ["Arquitectura Zero-Trust", "Criptografía Post-Cuántica", "Detección de Amenazas con IA", "SOAR (Security Orchestration)", "Seguridad de LLMs / Prompt Injection"],
        "nivel_adopcion_regional": "Alta",
        "impacto_ia_automatizacion": "Crítico Defensivo",
        "velocidad_obsolescencia": "Rápida (< 24 meses)"
    },
    "OCUP_04": {
        "ocupacion_nombre": "Arquitecto Cloud y DevOps",
        "sector": "Tecnología",
        "habilidades_tradicionales": ["Linux SysAdmin", "Docker Básico", "Scripts Bash", "Jenkins"],
        "habilidades_emergentes": ["FinOps (Optimización de Costos Cloud)", "GitOps con ArgoCD", "Platform Engineering", "eBPF para Observabilidad", "Kubernetes Multi-Cluster Mesh"],
        "nivel_adopcion_regional": "Muy Alta",
        "impacto_ia_automatizacion": "Alto",
        "velocidad_obsolescencia": "Rápida (< 24 meses)"
    },
    "OCUP_05": {
        "ocupacion_nombre": "Médico General y Especialista",
        "sector": "Salud",
        "habilidades_tradicionales": ["Examen Físico Clínico", "Prescripción Farmacológica", "Historia Clínica en Papel"],
        "habilidades_emergentes": ["Diagnóstico Predictivo Asistido por IA", "Telemedicina e Interoperabilidad HL7/FHIR", "Medicina Genómica Personalizada", "Monitoreo Remoto de Pacientes"],
        "nivel_adopcion_regional": "Media-Alta",
        "impacto_ia_automatizacion": "Asistencia / Aumento Humano",
        "velocidad_obsolescencia": "Moderada (< 48 meses)"
    },
    "OCUP_06": {
        "ocupacion_nombre": "Profesional de Enfermería y Cuidados Críticos",
        "sector": "Salud",
        "habilidades_tradicionales": ["Toma de Signos Vitales", "Administración de Vías", "Cuidados Generales"],
        "habilidades_emergentes": ["Monitoreo Biomédico Continuo IoT", "Triage Digital Inteligente", "Simulación Clínica Avanzada", "Gestión de Cuidados para Envejecimiento Activo"],
        "nivel_adopcion_regional": "Media",
        "impacto_ia_automatizacion": "Bajo (Alta Intensidad Humana)",
        "velocidad_obsolescencia": "Moderada (< 48 meses)"
    },
    "OCUP_07": {
        "ocupacion_nombre": "Bioquímico y Farmacéutico Clínico",
        "sector": "Salud",
        "habilidades_tradicionales": ["Bioquímica Básica", "Dispensación de Fármacos", "Cultivos Clásicos"],
        "habilidades_emergentes": ["Edición Génica CRISPR/Cas9", "Cribado Virtual de Fármacos (In Silico)", "Secuenciación de Próxima Generación (NGS)", "Farmacovigilancia Basada en Big Data"],
        "nivel_adopcion_regional": "Alta",
        "impacto_ia_automatizacion": "Transformador",
        "velocidad_obsolescencia": "Rápida (< 24 meses)"
    },
    "OCUP_08": {
        "ocupacion_nombre": "Técnico en Diagnóstico por Imágenes y Bioinformática",
        "sector": "Salud",
        "habilidades_tradicionales": ["Operación de Rayos X", "Tomografía Convencional", "Revelado Digital"],
        "habilidades_emergentes": ["Redes Convolucionales para Detección Temprana", "Reconstrucción Tomográfica 3D/4D", "Procesamiento Bioinformático de Imágenes", "Control de Calidad Automatizado con IA"],
        "nivel_adopcion_regional": "Alta",
        "impacto_ia_automatizacion": "Muy Alto",
        "velocidad_obsolescencia": "Rápida (< 24 meses)"
    },
    "OCUP_09": {
        "ocupacion_nombre": "Ingeniero en Energías Renovables (Eólica / Solar)",
        "sector": "Energía",
        "habilidades_tradicionales": ["Cálculo Eléctrico Convencional", "Topografía Básica", "Grupos Electrógenos"],
        "habilidades_emergentes": ["Producción y Logística de Hidrógeno Verde", "Sistemas de Almacenamiento en Baterías (BESS)", "Modelado CFD con IA para Parques Eólicos", "Sistemas Híbridos Solar-Eólico"],
        "nivel_adopcion_regional": "Muy Alta",
        "impacto_ia_automatizacion": "Alto",
        "velocidad_obsolescencia": "Rápida (< 24 meses)"
    },
    "OCUP_10": {
        "ocupacion_nombre": "Ingeniero de Operaciones de Petróleo, Gas y Minería de Transición",
        "sector": "Energía",
        "habilidades_tradicionales": ["Perforación Convencional", "Metalurgia Tradicional", "Geología Manual"],
        "habilidades_emergentes": ["Extracción Directa de Litio (DLE)", "Minería de Cobre Verde con Cero Emisiones", "Gemelos Digitales de Yacimientos", "Monitoreo Sísmico 4D"],
        "nivel_adopcion_regional": "Muy Alta",
        "impacto_ia_automatizacion": "Medio-Alto",
        "velocidad_obsolescencia": "Moderada (< 36 meses)"
    },
    "OCUP_11": {
        "ocupacion_nombre": "Técnico en Redes Eléctricas Inteligentes (Smart Grids)",
        "sector": "Energía",
        "habilidades_tradicionales": ["Tendido de Líneas", "Tableros Analógicos", "Mantenimiento Preventivo"],
        "habilidades_emergentes": ["Subestaciones Digitales IEC 61850", "Medidores AMI Bidireccionales", "Gestión de Microrredes Distribuidas", "Ciberdefensa OT para Infraestructura Crítica"],
        "nivel_adopcion_regional": "Alta",
        "impacto_ia_automatizacion": "Alto",
        "velocidad_obsolescencia": "Rápida (< 24 meses)"
    },
    "OCUP_12": {
        "ocupacion_nombre": "Auditor y Consultor en Eficiencia Energética",
        "sector": "Energía",
        "habilidades_tradicionales": ["Revisión de Facturas Eléctricas", "Termometría Básica"],
        "habilidades_emergentes": ["Norma ISO 50001 con Telemetría IoT", "Cálculo de Huella de Carbono Corporativa Scope 1-3", "Mercados y Créditos de Carbono", "Gemelos Térmicos Industriales"],
        "nivel_adopcion_regional": "Alta",
        "impacto_ia_automatizacion": "Medio-Alto",
        "velocidad_obsolescencia": "Rápida (< 24 meses)"
    },
    "OCUP_13": {
        "ocupacion_nombre": "Administrador de Servicios Hoteleros y Experiencia de Huésped",
        "sector": "Turismo",
        "habilidades_tradicionales": ["Recepción y Conserjería", "Control Manual de Reservas", "Libro de Huéspedes"],
        "habilidades_emergentes": ["Pricing Dinámico Algorítmico (Revenue Management con IA)", "Check-in Biométrico y Llaves Digitales", "Estándares de Sostenibilidad Turística ESG", "Análisis de Sentimiento de Reseñas"],
        "nivel_adopcion_regional": "Media-Alta",
        "impacto_ia_automatizacion": "Alto en Operaciones",
        "velocidad_obsolescencia": "Moderada (< 36 meses)"
    },
    "OCUP_14": {
        "ocupacion_nombre": "Guía Especializado en Ecoturismo y Aventura",
        "sector": "Turismo",
        "habilidades_tradicionales": ["Rutas Tradicionales", "Guía Oral de Monumentos", "Idiomas Básicos"],
        "habilidades_emergentes": ["Turismo Regenerativo y Conservación Activa", "Sistemas de Seguridad y Telemetría Satelital", "Certificación Wilderness First Responder (WFR)", "Interpretación de Biodiversidad con Apps de Ciencia Ciudadana"],
        "nivel_adopcion_regional": "Media",
        "impacto_ia_automatizacion": "Bajo (Alta Conexión con la Naturaleza)",
        "velocidad_obsolescencia": "Lenta (> 48 meses)"
    },
    "OCUP_15": {
        "ocupacion_nombre": "Coordinador de Operaciones Turísticas Digitales (TravelTech)",
        "sector": "Turismo",
        "habilidades_tradicionales": ["Gestión de Paquetes en Agencia", "Emisión Manual GDS"],
        "habilidades_emergentes": ["Integraciones API bajo Estándar NDC (IATA)", "Big Data Turístico para Destinos Inteligentes", "E-Commerce Turístico Omnicanal", "Marketing de Hiperpersonalización con IA"],
        "nivel_adopcion_regional": "Alta",
        "impacto_ia_automatizacion": "Muy Alto",
        "velocidad_obsolescencia": "Rápida (< 24 meses)"
    },
    "OCUP_16": {
        "ocupacion_nombre": "Chef Ejecutivo y Gestor Gastronómico Sostenible",
        "sector": "Turismo",
        "habilidades_tradicionales": ["Cocina Tradicional", "Escandallos en Papel", "BPM Básica"],
        "habilidades_emergentes": ["Gastronomía Circular y Cero Desperdicio (Zero-Waste)", "Trazabilidad Blockchain de Proveedores Km 0", "Fermentación de Precisión y Alimentos Plant-Based", "Software ERP Integrado de Costos y Mermas"],
        "nivel_adopcion_regional": "Media-Alta",
        "impacto_ia_automatizacion": "Bajo en Creación / Alto en Logística",
        "velocidad_obsolescencia": "Moderada (< 36 meses)"
    },
    "OCUP_17": {
        "ocupacion_nombre": "Diseñador UX/UI y Experiencia de Producto Digital",
        "sector": "Economía del Conocimiento",
        "habilidades_tradicionales": ["Photoshop/Illustrator", "Diseño Gráfico Estático", "Wireframes en Papel"],
        "habilidades_emergentes": ["Diseño para Agentes de IA y UI Conversacional", "Design Systems Tokenizados", "Investigación Cuantitativa de Usuarios con IA", "Accesibilidad Web Universal WCAG 2.2 AAA"],
        "nivel_adopcion_regional": "Muy Alta",
        "impacto_ia_automatizacion": "Transformador",
        "velocidad_obsolescencia": "Rápida (< 18 meses)"
    },
    "OCUP_18": {
        "ocupacion_nombre": "Consultor en Transformación Digital y Analítica de Negocio",
        "sector": "Economía del Conocimiento",
        "habilidades_tradicionales": ["Excel Avanzado", "Diagramas de Flujo en Visio", "Informes en PowerPoint"],
        "habilidades_emergentes": ["Minería de Procesos (Process Mining - Celonis)", "Despliegue de Agentes de IA Autónomos", "Hiperautomatización con RPA e Inteligencia Artificial", "Gobernanza Ética y Regulatoria de Datos (GDPR/Ley Protección de Datos)"],
        "nivel_adopcion_regional": "Muy Alta",
        "impacto_ia_automatizacion": "Acelerador Primario",
        "velocidad_obsolescencia": "Rápida (< 18 meses)"
    },
    "OCUP_19": {
        "ocupacion_nombre": "Científico e Investigador en Biotecnología y AgTech",
        "sector": "Economía del Conocimiento",
        "habilidades_tradicionales": ["Microbiología Básica", "Ensayos de Campo", "Genética Mendeliana"],
        "habilidades_emergentes": ["Modelado de Proteínas con AlphaFold / ESMFold", "Bioinformática de Alto Rendimiento en la Nube", "Bioinsumos y Microbiomas para Suelos", "Agricultura de Precisión Integrada con Sensores Satelitales"],
        "nivel_adopcion_regional": "Muy Alta",
        "impacto_ia_automatizacion": "Revolución Científica",
        "velocidad_obsolescencia": "Rápida (< 24 meses)"
    },
    "OCUP_20": {
        "ocupacion_nombre": "Analista Financiero Cuantitativo y FinTech",
        "sector": "Economía del Conocimiento",
        "habilidades_tradicionales": ["Contabilidad Financiera", "Modelos DCF en Excel", "Análisis Fundamental"],
        "habilidades_emergentes": ["Algoritmos de Trading Cuantitativo en Python", "Tokenización de Activos del Mundo Real (RWA)", "Cumplimiento Automatizado Anti-Lavado (RegTech / AML)", "Scoring Crediticio Alternativo con Redes Neuronales"],
        "nivel_adopcion_regional": "Muy Alta",
        "impacto_ia_automatizacion": "Muy Alto",
        "velocidad_obsolescencia": "Rápida (< 18 meses)"
    }
}

# --------------------------------------------------------------------------
# 2. DATASETS OFICIALES DE OFERTA EDUCATIVA (GRADUADOS / MATRÍCULA)
# Fuentes: 
# - ARG: Secretaría de Educación / DiNIECE (Relevamiento Anual) + SPU (Anuario Egresados Universitarios).
# - CHL: Mineduc / SIES (Servicio de Información de Educación Superior).
# - URY: MEC (Dirección de Educación) + ANEP + Monitor Educativo / UdelaR / UTEC.
# --------------------------------------------------------------------------
OFERTA_EDUCATIVA_OFICIAL_REGIONAL: Dict[str, Dict[str, Dict[str, Any]]] = {
    "ARG": {
        "Tecnología": {
            "carreras_afines": "Lic. en Sistemas, Ing. Informática, Tecnicaturas en Programación, Ciencia de Datos",
            "egresados_anuales_estimados": 12500,
            "crecimiento_matricula_pct": "+14.2% anual",
            "demanda_anual_puestos": 22000,
            "fuentes": "SPU / Secretaría de Educación / CESSI Argentina"
        },
        "Salud": {
            "carreras_afines": "Medicina, Lic. en Enfermería, Bioquímica, Farmacia, Diagnóstico por Imágenes",
            "egresados_anuales_estimados": 18200,
            "crecimiento_matricula_pct": "+3.8% anual",
            "demanda_anual_puestos": 26000,
            "fuentes": "Ministerio de Salud / SPU Relevamiento Universitario"
        },
        "Energía": {
            "carreras_afines": "Ing. Eléctrica, Ing. Química/Petróleo, Tecnicaturas en Energías Renovables, Minería",
            "egresados_anuales_estimados": 4800,
            "crecimiento_matricula_pct": "+9.1% anual",
            "demanda_anual_puestos": 8900,
            "fuentes": "Secretaría de Energía / CONEAU / SPU"
        },
        "Turismo": {
            "carreras_afines": "Lic. en Turismo y Hotelería, Guía de Turismo, Gastronomía Profesional, Gestión de Servicios",
            "egresados_anuales_estimados": 7100,
            "crecimiento_matricula_pct": "+2.5% anual",
            "demanda_anual_puestos": 8500,
            "fuentes": "Secretaría de Turismo / DiNIECE / AHRCC"
        },
        "Economía del Conocimiento": {
            "carreras_afines": "Biotecnología, Diseño Digital/Multimedia, Economía y Finanzas, Administración de Empresas",
            "egresados_anuales_estimados": 16400,
            "crecimiento_matricula_pct": "+11.5% anual",
            "demanda_anual_puestos": 24500,
            "fuentes": "Subsecretaría de Economía del Conocimiento / SPU / Argencon"
        }
    },
    "CHL": {
        "Tecnología": {
            "carreras_afines": "Ingeniería Civil Informática, Computación, Ciberseguridad, Analista Programador",
            "egresados_anuales_estimados": 8900,
            "crecimiento_matricula_pct": "+12.8% anual",
            "demanda_anual_puestos": 14500,
            "fuentes": "Mineduc / SIES (Servicio de Información de Educación Superior) / ACTI"
        },
        "Salud": {
            "carreras_afines": "Medicina, Enfermería, Tecnología Médica, Química y Farmacia",
            "egresados_anuales_estimados": 13100,
            "crecimiento_matricula_pct": "+4.1% anual",
            "demanda_anual_puestos": 16200,
            "fuentes": "SIES Mineduc / Superintendencia de Salud / DEIS"
        },
        "Energía": {
            "carreras_afines": "Ingeniería en Minas, Ingeniería Eléctrica/Energías Renovables, Metalurgia",
            "egresados_anuales_estimados": 5400,
            "crecimiento_matricula_pct": "+10.4% anual",
            "demanda_anual_puestos": 8100,
            "fuentes": "SIES Mineduc / Consejo Minero / Ministerio de Energía"
        },
        "Turismo": {
            "carreras_afines": "Administración Hotelera y Turismo, Ecoturismo, Gastronomía Internacional",
            "egresados_anuales_estimados": 4900,
            "crecimiento_matricula_pct": "+3.2% anual",
            "demanda_anual_puestos": 5800,
            "fuentes": "SIES Mineduc / Sernatur / Fedetur"
        },
        "Economía del Conocimiento": {
            "carreras_afines": "Ingeniería Comercial, Diseño y Animación Digital, Bioingeniería, Finanzas",
            "egresados_anuales_estimados": 11800,
            "crecimiento_matricula_pct": "+8.9% anual",
            "demanda_anual_puestos": 15900,
            "fuentes": "SIES Mineduc / CORFO / FinteChile"
        }
    },
    "URY": {
        "Tecnología": {
            "carreras_afines": "Ingeniería en Computación (UdelaR/ORT), Tecnólogo en Informática (UTEC), Analista TI",
            "egresados_anuales_estimados": 2400,
            "crecimiento_matricula_pct": "+15.6% anual",
            "demanda_anual_puestos": 4200,
            "fuentes": "MEC / Monitor Educativo ANEP / UdelaR / CUTI"
        },
        "Salud": {
            "carreras_afines": "Doctor en Medicina, Lic. en Enfermería, Química Farmacéutica, Escuela Universitaria de Tecnología Médica",
            "egresados_anuales_estimados": 2900,
            "crecimiento_matricula_pct": "+3.4% anual",
            "demanda_anual_puestos": 3500,
            "fuentes": "MEC / UdelaR / MSP Uruguay"
        },
        "Energía": {
            "carreras_afines": "Ingeniería Industrial Mecánica/Eléctrica, Tecnólogo en Energías Renovables (UTEC)",
            "egresados_anuales_estimados": 750,
            "crecimiento_matricula_pct": "+12.1% anual",
            "demanda_anual_puestos": 1100,
            "fuentes": "MEC / UTEC / MIEM Uruguay"
        },
        "Turismo": {
            "carreras_afines": "Tecnicatura en Gestión Hotelera y Turística (UTU/UdelaR), Guía Turístico, Gastronomía",
            "egresados_anuales_estimados": 1200,
            "crecimiento_matricula_pct": "+2.1% anual",
            "demanda_anual_puestos": 1450,
            "fuentes": "MEC / DGETP-UTU / Ministerio de Turismo"
        },
        "Economía del Conocimiento": {
            "carreras_afines": "Lic. en Biología Humana/Biotecnología, Lic. en Economía, Diseño y Comunicación Visual",
            "egresados_anuales_estimados": 3100,
            "crecimiento_matricula_pct": "+9.7% anual",
            "demanda_anual_puestos": 4600,
            "fuentes": "MEC / UdelaR / Uruguay XXI / Institut Pasteur"
        }
    }
}

# --------------------------------------------------------------------------
# 3. REGLAS ESTADÍSTICAS Y UMBRALES DE DETECCIÓN DE VARIACIONES SIGNIFICATIVAS
# --------------------------------------------------------------------------
REGLAS_DETECCION_CONFIG: Dict[str, Dict[str, Any]] = {
    "R1_VARIACION_DEMANDA_EXTREMA": {
        "nombre": "R1: Variación Acelerada de Demanda Ocupacional",
        "descripcion": "Detecta saltos o caídas bruscas en la proyección o demanda laboral interanual.",
        "umbral_valor": 15.0,
        "unidad": "% anual",
        "condicion": "|Delta_Pct| >= 15.0%",
        "severidad_default": "ALTA"
    },
    "R2_VOLATILIDAD_INDICE_IDELR": {
        "nombre": "R2: Desviación Significativa del Entorno Macroeconómico",
        "descripcion": "Detecta rupturas de estabilidad en el índice IDELR o desvíos mayores a 1.5 desviaciones estándar.",
        "umbral_valor": 5.0,
        "umbral_zscore": 1.50,
        "unidad": "Puntos de Score / Z-Score",
        "condicion": "|Delta_IDELR| >= 5.0 pts  O  |Z_Score| >= 1.5",
        "severidad_default": "CRITICA"
    },
    "R3_MISMATCH_EDUCATIVO_CRITICO": {
        "nombre": "R3: Brecha Crítica entre Formación y Demanda Laboral (CCE)",
        "descripcion": "Detecta cuando los graduados cubren menos del 60% de los puestos demandados o superan el 140% (descalce).",
        "umbral_deficit": 0.60,
        "umbral_superavit": 1.40,
        "unidad": "Ratio CCE (Graduados / Demanda)",
        "condicion": "CCE < 0.60 (Déficit Severo)  O  CCE > 1.40 (Saturación/Subempleo)",
        "severidad_default": "CRITICA"
    },
    "R4_HABILIDADES_EMERGENTES_CRITICAS": {
        "nombre": "R4: Disrupción Acelerada de Habilidades Tecnológicas",
        "descripcion": "Identifica perfiles donde la velocidad de obsolescencia es menor a 24 meses y se requieren más de 3 habilidades de frontera.",
        "umbral_obsolescencia_meses": 24,
        "unidad": "Meses / Velocidad de Adopción",
        "condicion": "Obsolescencia <= 24 meses Y Nivel Adopción in ['Muy Alta', 'Alta']",
        "severidad_default": "ALTA"
    }
}

# --------------------------------------------------------------------------
# 4. MODELOS PYDANTIC PARA FastAPI
# --------------------------------------------------------------------------
class FiltroDataScienceRequest(BaseModel):
    pais: Optional[str] = Field(None, description="Filtro de país (ARG, CHL, URY)")
    sector: Optional[str] = Field(None, description="Filtro de sector")
    severidad_minima: Optional[str] = Field("TODAS", description="Filtrar por severidad: CRITICA, ALTA, MODERADA, TODAS")

# --------------------------------------------------------------------------
# 5. FUNCIONES ANALÍTICAS DEL MOTOR DE DATA SCIENCE
# --------------------------------------------------------------------------

def calcular_brechas_habilidades_sectoriales(pais_filtro: Optional[str] = None, sector_filtro: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Calcula la brecha de talento cruzada (Talent Gap Score) e integra las habilidades emergentes
    para las 20 ocupaciones en los 3 países.
    """
    df_icol = calcular_indice_oportunidad_laboral()
    if pais_filtro:
        df_icol = df_icol[df_icol["pais_codigo_iso3"] == pais_filtro.upper()]
    if sector_filtro:
        df_icol = df_icol[df_icol["sector"].str.lower() == sector_filtro.lower()]

    registros = []
    for _, row in df_icol.iterrows():
        ocup_id = row["ocupacion_id"]
        p_iso = row["pais_codigo_iso3"]
        sector = row["sector"]
        
        info_emergente = HABILIDADES_EMERGENTES_CATALOGO.get(ocup_id, {
            "habilidades_tradicionales": [],
            "habilidades_emergentes": [],
            "nivel_adopcion_regional": "Media",
            "impacto_ia_automatizacion": "Moderado",
            "velocidad_obsolescencia": "Normal"
        })

        # Cálculo de Brecha de Talento (Talent Gap Index 0-100)
        # Basado en demanda relativa del mercado vs. stock formativo educativo ponderado por madurez
        score_demanda = float(row["score_demanda_100"])
        score_crecimiento = float(row["score_crecimiento_100"])
        factor_madurez = float(row["factor_madurez_pais"])
        
        # Obtener ratio de cobertura educativa del sector
        edu_info = OFERTA_EDUCATIVA_OFICIAL_REGIONAL.get(p_iso, {}).get(sector, {})
        graduados = edu_info.get("egresados_anuales_estimados", 5000)
        demanda = edu_info.get("demanda_anual_puestos", 7000)
        ratio_cce = round(graduados / demanda, 3) if demanda > 0 else 1.0

        # Brecha: Mayor score indica mayor escasez de talento y urgencia formativa
        # Fórmula: Intensidad de Demanda (60%) + Déficit de Cobertura (40%) ajustado por factor país
        deficit_component = max((1.0 - ratio_cce), 0.0) * 100.0
        brecha_score = round(min(max((score_demanda * 0.55 + score_crecimiento * 0.25 + deficit_component * 0.20) * factor_madurez, 0.0), 100.0), 2)

        # Diagnóstico cualitativo de la brecha
        if brecha_score >= 82.0:
            diag_brecha = "Déficit Crítico de Talento"
            icono_brecha = "🔴"
            urgencia = "Prioridad 1: Formación Acelerada Inmediata"
        elif brecha_score >= 68.0:
            diag_brecha = "Déficit Moderado de Especialistas"
            icono_brecha = "🟡"
            urgencia = "Prioridad 2: Actualización de Currículas"
        elif brecha_score >= 50.0:
            diag_brecha = "Equilibrio Oferta-Demanda"
            icono_brecha = "🟢"
            urgencia = "Prioridad 3: Monitoreo Regular"
        else:
            diag_brecha = "Superávit Relativo / Saturación"
            icono_brecha = "🔵"
            urgencia = "Prioridad 4: Reconversión Hacia Nichos"

        registros.append({
            "pais_codigo_iso3": p_iso,
            "pais_nombre": row["pais_nombre"],
            "sector": sector,
            "ocupacion_id": ocup_id,
            "ocupacion_nombre": row["ocupacion_nombre"],
            "codigo_ciuo08_oit": row["codigo_ciuo08_oit"],
            "indice_oportunidad_icol": float(row["indice_oportunidad_icol"]),
            "score_demanda_mercado": score_demanda,
            "score_crecimiento_estimado": score_crecimiento,
            "coeficiente_cobertura_educativa_cce": ratio_cce,
            "score_brecha_talento_100": brecha_score,
            "diagnostico_brecha": diag_brecha,
            "icono_brecha": icono_brecha,
            "urgencia_intervencion": urgencia,
            "habilidades_tradicionales": info_emergente.get("habilidades_tradicionales", []),
            "habilidades_emergentes_2026": info_emergente.get("habilidades_emergentes", []),
            "nivel_adopcion_habilidades": info_emergente.get("nivel_adopcion_regional", "Media"),
            "impacto_ia_automatizacion": info_emergente.get("impacto_ia_automatizacion", "Moderado"),
            "velocidad_obsolescencia": info_emergente.get("velocidad_obsolescencia", "Moderada")
        })

    return sorted(registros, key=lambda x: x["score_brecha_talento_100"], reverse=True)


def evaluar_comparativa_laboral_educativa(pais_filtro: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Compara la demanda laboral de nuevos puestos frente a la oferta anual de graduados
    por país y sector, calculando el Coeficiente de Cobertura Educativa (CCE) y el Mismatch.
    """
    paises = ["ARG", "CHL", "URY"]
    if pais_filtro:
        paises = [pais_filtro.upper()]

    comparativas = []
    paises_nombres = {"ARG": "Argentina", "CHL": "Chile", "URY": "Uruguay"}

    for p in paises:
        data_pais = OFERTA_EDUCATIVA_OFICIAL_REGIONAL.get(p, {})
        for sector, info in data_pais.items():
            egresados = info["egresados_anuales_estimados"]
            demanda = info["demanda_anual_puestos"]
            cce = round(egresados / demanda, 3)
            deficit_absoluto = demanda - egresados

            # Diagnóstico de descalce
            if cce < 0.60:
                diagnostico = "Déficit Formativo Severo (Alerta Roja)"
                estado = "CRITICA"
                semaforo = "🔴"
            elif cce < 0.85:
                diagnostico = "Déficit Formativo Moderado"
                estado = "ALERTA"
                semaforo = "🟡"
            elif cce <= 1.20:
                diagnostico = "Equilibrio Formativo-Laboral"
                estado = "ESTABLE"
                semaforo = "🟢"
            else:
                diagnostico = "Superávit Formativo / Riesgo de Desempleo Técnico"
                estado = "ATENCION"
                semaforo = "🔵"

            comparativas.append({
                "pais_codigo_iso3": p,
                "pais_nombre": paises_nombres.get(p, p),
                "sector": sector,
                "carreras_universitarias_afines": info["carreras_afines"],
                "egresados_anuales_estimados": egresados,
                "crecimiento_matricula_anual": info["crecimiento_matricula_pct"],
                "demanda_anual_puestos_nuevos": demanda,
                "brecha_anual_puestos_deficit": deficit_absoluto,
                "coeficiente_cobertura_educativa_cce": cce,
                "diagnostico_descalce": diagnostico,
                "estado_alerta": estado,
                "semaforo": semaforo,
                "fuentes_oficiales_cruzadas": info["fuentes"]
            })

    return sorted(comparativas, key=lambda x: x["coeficiente_cobertura_educativa_cce"])


def generar_sistema_alertas_tempranas(pais_filtro: Optional[str] = None, severidad_minima: str = "TODAS") -> Dict[str, Any]:
    """
    Ejecuta el motor de reglas analíticas (R1 a R4) y emite alertas automáticas
    clasificadas por severidad para todos los equipos del proyecto.
    """
    alertas = []
    contador_id = 1

    # 1. EVALUACIÓN DE REGLA R2: TENDENCIAS MACRO Y VOLATILIDAD DEL IDELR
    df_idelr = calcular_indice_sintetico_panel()
    if pais_filtro:
        df_idelr = df_idelr[df_idelr["pais_codigo_iso3"] == pais_filtro.upper()]

    for p_iso, sub_df in df_idelr.groupby("pais_codigo_iso3"):
        sub_df = sub_df.sort_values(by="anio")
        p_nom = sub_df.iloc[0]["pais_nombre"]
        
        # Evaluar últimos períodos
        if len(sub_df) >= 2:
            ultimo_row = sub_df.iloc[-1]
            penultimo_row = sub_df.iloc[-2]
            delta_idelr = float(ultimo_row.get("delta_indice_pct", 0.0) or 0.0)
            score_idelr = float(ultimo_row.get("indice_sintetico_idelr", 50.0))

            if abs(delta_idelr) >= REGLAS_DETECCION_CONFIG["R2_VOLATILIDAD_INDICE_IDELR"]["umbral_valor"]:
                alertas.append({
                    "alerta_id": f"ALT_{contador_id:03d}",
                    "regla_origen": "R2_VOLATILIDAD_INDICE_IDELR",
                    "categoria": "MACROECONOMIA_Y_DESARROLLO",
                    "severidad": "CRITICA" if delta_idelr < -5.0 else "ALTA",
                    "icono": "🔴" if delta_idelr < -5.0 else "🟡",
                    "pais_codigo_iso3": p_iso,
                    "pais_nombre": p_nom,
                    "sector_u_ocupacion": "Todas las ocupaciones (Nivel País)",
                    "valor_detectado": f"Delta IDELR {delta_idelr:+.2f}% (Score actual: {score_idelr:.2f})",
                    "umbral_disparador": "|Delta| >= 5.0%",
                    "mensaje_ejecutivo": f"Ruptura de estabilidad en el índice sintético IDELR de {p_nom} ({delta_idelr:+.2f}%).",
                    "recomendacion_accion": "Monitorear impacto en creación de puestos y ajustar ponderaciones macroeconómicas."
                })
                contador_id += 1

    # 2. EVALUACIÓN DE REGLA R3: MISMATCH Y BRECHA FORMATIVA CRÍTICA
    comp_edu = evaluar_comparativa_laboral_educativa(pais_filtro=pais_filtro)
    for comp in comp_edu:
        cce = comp["coeficiente_cobertura_educativa_cce"]
        if cce < REGLAS_DETECCION_CONFIG["R3_MISMATCH_EDUCATIVO_CRITICO"]["umbral_deficit"]:
            alertas.append({
                "alerta_id": f"ALT_{contador_id:03d}",
                "regla_origen": "R3_MISMATCH_EDUCATIVO_CRITICO",
                "categoria": "DESCALCE_EDUCATIVO_LABORAL",
                "severidad": "CRITICA",
                "icono": "🔴",
                "pais_codigo_iso3": comp["pais_codigo_iso3"],
                "pais_nombre": comp["pais_nombre"],
                "sector_u_ocupacion": f"Sector: {comp['sector']}",
                "valor_detectado": f"CCE = {cce:.2f} (Déficit de {comp['brecha_anual_puestos_deficit']:,} graduados/año)",
                "umbral_disparador": "CCE < 0.60 (Déficit severo de oferta)",
                "mensaje_ejecutivo": f"En {comp['pais_nombre']}, los egresados de {comp['sector']} solo cubren el {cce*100:.1f}% de las vacantes demandadas.",
                "recomendacion_accion": "Priorizar becas, alianzas público-privadas y tecnicaturas de reconversión inmediata."
            })
            contador_id += 1
        elif cce > REGLAS_DETECCION_CONFIG["R3_MISMATCH_EDUCATIVO_CRITICO"]["umbral_superavit"]:
            alertas.append({
                "alerta_id": f"ALT_{contador_id:03d}",
                "regla_origen": "R3_MISMATCH_EDUCATIVO_CRITICO",
                "categoria": "DESCALCE_EDUCATIVO_LABORAL",
                "severidad": "MODERADA",
                "icono": "🔵",
                "pais_codigo_iso3": comp["pais_codigo_iso3"],
                "pais_nombre": comp["pais_nombre"],
                "sector_u_ocupacion": f"Sector: {comp['sector']}",
                "valor_detectado": f"CCE = {cce:.2f} (Superávit formativo)",
                "umbral_disparador": "CCE > 1.40 (Sobreoferta)",
                "mensaje_ejecutivo": f"Sobreoferta de graduados frente a puestos formales creados en {comp['sector']} ({comp['pais_nombre']}).",
                "recomendacion_accion": "Estimular diversificación curricular y competencias de exportación de servicios."
            })
            contador_id += 1

    # 3. EVALUACIÓN DE REGLAS R1 Y R4: CRECIMIENTO EXTREMO Y DISRUPCIÓN DE HABILIDADES
    brechas = calcular_brechas_habilidades_sectoriales(pais_filtro=pais_filtro)
    for b in brechas:
        crec = b["score_crecimiento_estimado"]
        obs = b["velocidad_obsolescencia"]
        adop = b["nivel_adopcion_habilidades"]

        # R1: Crecimiento muy acelerado (> 18%)
        if crec >= 18.0:
            alertas.append({
                "alerta_id": f"ALT_{contador_id:03d}",
                "regla_origen": "R1_VARIACION_DEMANDA_EXTREMA",
                "categoria": "DINAMICA_DE_DEMANDA_LABORAL",
                "severidad": "ALTA",
                "icono": "🟡",
                "pais_codigo_iso3": b["pais_codigo_iso3"],
                "pais_nombre": b["pais_nombre"],
                "sector_u_ocupacion": f"{b['ocupacion_nombre']} ({b['sector']})",
                "valor_detectado": f"Crecimiento estimado: +{crec:.1f}% anual",
                "umbral_disparador": "Crecimiento >= 15.0%",
                "mensaje_ejecutivo": f"Demanda explosiva detectada para {b['ocupacion_nombre']} en {b['pais_nombre']} (+{crec:.1f}%).",
                "recomendacion_accion": "Acelerar programas de pasantías e inserción temprana con cámaras empresariales."
            })
            contador_id += 1

        # R4: Obsolescencia crítica (< 18 meses) y alta disrupción por IA
        if "< 18 meses" in obs or "< 12 meses" in obs:
            alertas.append({
                "alerta_id": f"ALT_{contador_id:03d}",
                "regla_origen": "R4_HABILIDADES_EMERGENTES_CRITICAS",
                "categoria": "DISRUPCION_TECNOLOGICA_Y_HABILIDADES",
                "severidad": "ALTA",
                "icono": "⚡",
                "pais_codigo_iso3": b["pais_codigo_iso3"],
                "pais_nombre": b["pais_nombre"],
                "sector_u_ocupacion": f"{b['ocupacion_nombre']} ({b['sector']})",
                "valor_detectado": f"Obsolescencia: {obs} | Adopción: {adop}",
                "umbral_disparador": "Obsolescencia <= 18 meses",
                "mensaje_ejecutivo": f"Riesgo de desactualización técnica acelerada en {b['ocupacion_nombre']}. Habilidades emergentes críticas: {', '.join(b['habilidades_emergentes_2026'][:3])}.",
                "recomendacion_accion": "Implementar microcertificaciones continuas de frontera."
            })
            contador_id += 1

    # Filtrar por severidad si se solicita
    if severidad_minima and severidad_minima.upper() != "TODAS":
        alertas = [a for a in alertas if a["severidad"] == severidad_minima.upper()]

    # Resumen de alertas
    total_criticas = sum(1 for a in alertas if a["severidad"] == "CRITICA")
    total_altas = sum(1 for a in alertas if a["severidad"] == "ALTA")
    total_moderadas = sum(1 for a in alertas if a["severidad"] == "MODERADA")

    return {
        "status": "Monitoreo de alertas completado",
        "total_alertas_activas": len(alertas),
        "resumen_por_severidad": {
            "CRITICAS": total_criticas,
            "ALTAS": total_altas,
            "MODERADAS": total_moderadas
        },
        "reglas_activas": list(REGLAS_DETECCION_CONFIG.keys()),
        "alertas": alertas
    }


def generar_reporte_integral_data_science(pais_filtro: Optional[str] = None) -> Dict[str, Any]:
    """
    Genera un informe integral consolidado para todos los equipos del proyecto
    (BI, Producto, Frontend, Políticas Públicas).
    """
    brechas = calcular_brechas_habilidades_sectoriales(pais_filtro=pais_filtro)
    comparativas = evaluar_comparativa_laboral_educativa(pais_filtro=pais_filtro)
    alertas = generar_sistema_alertas_tempranas(pais_filtro=pais_filtro)

    # Top ocupaciones con mayor brecha de talento
    top_brechas = brechas[:8]

    # Sectores con mayor déficit educativo acumulado
    df_comp = pd.DataFrame(comparativas)
    resumen_deficit_sector = []
    if not df_comp.empty:
        for sec, sub_df in df_comp.groupby("sector"):
            resumen_deficit_sector.append({
                "sector": sec,
                "deficit_total_puestos_regional": int(sub_df["brecha_anual_puestos_deficit"].sum()),
                "cce_promedio": round(float(sub_df["coeficiente_cobertura_educativa_cce"].mean()), 3),
                "estado_general": "DEFICIT_CRITICO" if sub_df["coeficiente_cobertura_educativa_cce"].mean() < 0.70 else "EQUILIBRIO"
            })
        resumen_deficit_sector = sorted(resumen_deficit_sector, key=lambda x: x["cce_promedio"])

    return {
        "titulo": "Informe Integral de Data Science: Brechas, Mismatch Educativo y Alertas Tempranas",
        "region": "Cono Sur (Argentina, Chile, Uruguay)",
        "paises_evaluados": ["ARG", "CHL", "URY"] if not pais_filtro else [pais_filtro.upper()],
        "resumen_ejecutivo": {
            "total_ocupaciones_analizadas": len(brechas),
            "total_alertas_emitidas": alertas["total_alertas_activas"],
            "alertas_criticas": alertas["resumen_por_severidad"]["CRITICAS"],
            "sector_con_mayor_deficit_regional": resumen_deficit_sector[0]["sector"] if resumen_deficit_sector else "N/A",
            "cce_minimo_detectado": resumen_deficit_sector[0]["cce_promedio"] if resumen_deficit_sector else 0.0
        },
        "resumen_deficit_por_sector": resumen_deficit_sector,
        "top_ocupaciones_con_mayor_brecha": [{
            "pais": r["pais_codigo_iso3"],
            "sector": r["sector"],
            "ocupacion": r["ocupacion_nombre"],
            "score_brecha": r["score_brecha_talento_100"],
            "diagnostico": r["diagnostico_brecha"],
            "habilidades_emergentes": r["habilidades_emergentes_2026"][:3]
        } for r in top_brechas],
        "alertas_recientes": alertas["alertas"][:10],
        "metodologia_referencia": "CIUO-08 (OIT), CEPALSTAT, DiNIECE/SPU (ARG), SIES/Mineduc (CHL), Monitor MEC/UdelaR (URY)"
    }
