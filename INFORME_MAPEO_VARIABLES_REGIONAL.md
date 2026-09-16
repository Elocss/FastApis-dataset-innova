# INFORME TÉCNICO DE HOMOLOGACIÓN Y MAPEO DE VARIABLES EQUIVALENTES
## Cono Sur: Argentina (ARG), Chile (CHL) y Uruguay (URY)

**Proyecto:** Innova Data Platform – Observatorio de Indicadores y Ocupaciones Regionales  
**Fecha:** Septiembre 2026  
**Estándares de Referencia:** CIUO-08 (OIT), CEPALSTAT (CEPAL), Sistema de Cuentas Nacionales (SCN/ONU), Clasificaciones Estadísticas Nacionales (INDEC, INE Chile, INE Uruguay).

---

## 1. Introducción y Marco de Homologación

La comparabilidad estadística entre países del Cono Sur presenta desafíos debido a diferencias metodológicas en encuestas de hogares, coberturas geográficas, nomenclaturas ocupacionales e institutos estadísticos emisores.

Para resolver estas discrepancias, la plataforma implementa una **Capa de Abstracción y Homologación** estructurada en tres niveles:
1. **Nivel Macroeconómico e Indicadores Clave:** Alineación con estándares internacionales (CEPALSTAT / Banco Mundial / FMI).
2. **Nivel Mercado Laboral y Salarial:** Estandarización sobre directrices de la OIT (ILOSTAT / CIUO-08).
3. **Nivel Ocupaciones y Capital Humano:** Mapeo de perfiles sectoriales a 4 dígitos CIUO-08 con vinculación a registros ministeriales y cámaras sectoriales locales.

```
+-----------------------------------------------------------------------------+
|                      CAPA DE HOMOLOGACIÓN REGIONAL                          |
+------------------------------------+----------------------------------------+
| FUENTES NACIONALES                 | ESTÁNDARES INTERNACIONALES EQUIVALENTES|
| - Argentina: INDEC (EPH, IPC, EMAE)| -> CEPALSTAT / SCN 2008                |
| - Chile: INE (ENE, IPC, IMACEC)    | -> ILOSTAT (SDMX OIT)                  |
| - Uruguay: INE (ECH, IPC, IMACEC)  | -> CIUO-08 / ISCO-08 (OIT)             |
+------------------------------------+----------------------------------------+
                                     |
                                     v
+-----------------------------------------------------------------------------+
|               DATASET CONSOLIDADO UNIFICADO (PROCESSED LAYER)               |
| [pais_codigo_iso3, dimension, indicador_nombre, anio, periodo, valor, ...]  |
+-----------------------------------------------------------------------------+
```

---

## 2. Matriz General de Mapeo de Variables Equivalentes

| Dimensión | Indicador Estandarizado (Plataforma) | Variable / Fuente Argentina (ARG) | Variable / Fuente Chile (CHL) | Variable / Fuente Uruguay (URY) | Unidad de Medida | Frecuencia Base |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **Economía** | `Variación Anual del PIB Real` | Variación del PIB a precios constantes (INDEC / CEPAL) | Variación del PIB a precios del año anterior encadenado (Banco Central de Chile / CEPAL) | Variación del PIB en volumen encadenado (Banco Central del Uruguay / CEPAL) | `%` | Anual |
| **Economía** | `Inflación Anual (IPC acumulado)` | IPC Cobertura Nacional - Variación interanual dic/dic (INDEC) | IPC General Nacional - Variación acumulada 12 meses (INE Chile) | IPC Total País - Variación acumulada interanual (INE Uruguay) | `%` | Anual / Mensual |
| **Demografía**| `Población Total` | Estimaciones y Proyecciones de Población (INDEC / CELADE) | Estimaciones y Proyecciones de Población (INE Chile / CELADE) | Estimaciones y Proyecciones de Población (INE Uruguay / CELADE) | `Millones de hab.` | Anual |
| **Educación** | `Tasa de Finalización de Educación Secundaria` | Población de 20 a 24 años con secundaria completa (EPH INDEC / SITEAL) | Población de 20 a 24 años con educación media completa (CASEN / Mineduc) | Población de 21 a 23 años con educación media superior completa (ECH INE / MEC) | `%` | Anual |
| **Educación** | `Gasto Público en Educación (% del PIB)` | Gasto consolidado en Educación y Cultura / PIB (Ministerio de Economía / CEPAL) | Gasto público total en educación / PIB (Dirección de Presupuestos Dipres / CEPAL) | Gasto público en educación / PIB (Ministerio de Economía y Finanzas / CEPAL) | `% del PIB` | Anual |
| **Empleo** | `Tasa de Desocupación Total` | Tasa de Desocupación Abierta (EPH - INDEC / ILOSTAT) | Tasa de Desocupación Nacional (ENE - INE Chile / ILOSTAT) | Tasa de Desempleo Total País (ECH - INE Uruguay / ILOSTAT) | `% Fuerza de Trabajo` | Anual / Trimestral |
| **Empleo** | `Tasa de Ocupación` | Tasa de Empleo (Ocupados / Población Total) (EPH INDEC) | Tasa de Ocupación (Ocupados / PET) (ENE INE Chile) | Tasa de Empleo (Ocupados / PET) (ECH INE Uruguay) | `% PET / Población` | Anual / Mensual |
| **Empleo** | `Índice de Salario Real` | Índice de Salarios deflactado por IPC (INDEC / OIT base 2018=100) | Índice Nominal de Remuneraciones Real (IR Real INE Chile base 2018=100) | Índice de Salario Real (ISR INE Uruguay base 2018=100) | `Índice (2018=100)` | Anual / Mensual |

---

## 3. Discrepancias Metodológicas y Criterios de Armonización

### 3.1. Mercado Laboral (Encuestas de Hogares)
* **Argentina (EPH - INDEC):**
  * *Cobertura:* 31 Aglomerados Urbanos (~63% de la población del país). No releva áreas rurales sistemáticamente.
  * *Población en Edad de Trabajar (PET):* Desde los 14 años.
  * *Criterio de Armonización:* Se aplica el factor de expansión y ajuste de ILOSTAT para inferir la tasa nacional consolidada y asegurar equivalencia con CHL y URY.
* **Chile (ENE - INE Chile):**
  * *Cobertura:* Nacional continua (urbana y rural).
  * *Población en Edad de Trabajar (PET):* Desde los 15 años.
  * *Criterio de Armonización:* Se homologa directamente con las definiciones internacionales de la OIT (Resolución 19ª CIET).
* **Uruguay (ECH - INE Uruguay):**
  * *Cobertura:* Total País (urbano y localidades rurales de más de 5.000 hab. / todo el territorio desde 2021 continuo).
  * *Población en Edad de Trabajar (PET):* Desde los 14 años.
  * *Criterio de Armonización:* Ajuste a población económicamente activa mayor de 15 años bajo convención OIT.

### 3.2. Medición de Inflación (Índice de Precios al Consumidor - IPC)
* **Argentina:** IPC Nacional con ponderaciones basadas en la ENGHo. Historial de readecuación metodológica post-2016.
* **Chile:** IPC Base 2023=100 (actualización quinquenal según EPF), canasta armonizada a estándares OCDE.
* **Uruguay:** IPC Base Diciembre 2022=100 (INE Uruguay), canasta adaptada al consumo de los hogares urbanos y rurales.
* *Criterio de Homologación:* En la base de datos se almacena la **variación porcentual interanual acumulada a fin de período (dic/dic)** para evitar sesgos de año base.

### 3.3. Nivel Educativo y Finalización Secundaria
* **Argentina:** Título Secundario Completo (Nivel Polimodal o Escuela Secundaria de 5/6 años según jurisdicción).
* **Chile:** Licencia de Educación Media (Científico-Humanista o Técnico-Profesional, 4 años de EM).
* **Uruguay:** Bachillerato Completo / Educación Media Superior (3er año de EMT/EMS, CES / DGETP-UTU).
* *Criterio de Homologación:* Indicador CINE-2011 Nivel 3 (Educación Secundaria Alta / Upper Secondary Education).

---

## 4. Mapeo de Sectores y Ocupaciones Estratégicas (CIUO-08 vs Nomenclaturas Locales)

La plataforma mapea 20 ocupaciones en 5 sectores de alta productividad mediante el estándar **CIUO-08 (Clasificación Internacional Uniforme de Ocupaciones)**:

| Sector | Código CIUO-08 | Denominación Estandarizada | Equivalencia Argentina (CNO / MinCyT) | Equivalencia Chile (CNO-Chile / SENCE) | Equivalencia Uruguay (INE / CUTI) |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **Tecnología** | `2512` | Desarrollador de Software y Aplicaciones | Programador / Analista de Sistemas (CNO 215) | Desarrollador Full-Stack / Ingeniero de Software | Desarrollador de Aplicaciones / Software Engineer |
| **Tecnología** | `2511` | Ingeniero de Datos y Machine Learning | Especialista en Minería de Datos / Data Scientist | Ingeniero de Datos / Arquitecto Big Data | Data Engineer / Especialista en IA |
| **Tecnología** | `2529` | Especialista en Ciberseguridad y Redes | Analista de Seguridad Informática (CERT.ar) | Especialista en Ciberseguridad (CSIRT) | Oficial de Seguridad de la Información (AGESIC) |
| **Tecnología** | `2522` | Arquitecto Cloud y DevOps | Administrador de Infraestructura Cloud | Ingeniero DevOps / Cloud Solutions | Administrador de Sistemas Cloud |
| **Salud** | `2211` | Médico General y Especialista | Médico Clínico / Especialista (MSAL) | Médico Cirujano / Especialista (MINSAL) | Médico General / Especialista (MSP) |
| **Salud** | `2221` | Profesional de Enfermería y Cuidados Críticos | Licenciado en Enfermería | Enfermero Universitario | Licenciado en Enfermería |
| **Salud** | `2262` | Bioquímico y Farmacéutico Clínico | Bioquímico / Farmacéutico Hospitalario | Químico Farmacéutico / Bioquímico | Químico Farmacéutico |
| **Salud** | `3211` | Técnico en Diagnóstico por Imágenes | Técnico Radiólogo / Diagnóstico por Imágenes | Tecnólogo Médico en Radiología | Técnico en Imagenología |
| **Energía** | `2149` | Ingeniero en Energías Renovables | Ingeniero en Energía / Solar / Eólica | Ingeniero Civil en Energías Renovables | Ingeniero en Energía / Generación Renovable |
| **Energía** | `2146` | Ingeniero en Petróleo, Gas y Minería | Ingeniero en Petróleo y Gas (Vaca Muerta) | Ingeniero Civil Metalúrgico / Minas (Cobre/Litio)| Ingeniero Químico / Procesos de Combustible |
| **Energía** | `3113` | Técnico en Redes Inteligentes (Smart Grids) | Técnico Electricista en Redes y Telemetría | Técnico en Transmisión y Redes Eléctricas | Técnico en Redes y Distribución Eléctrica |
| **Energía** | `2149` | Auditor en Eficiencia Energética | Consultor en Gestión de Energía ISO 50001 | Gestor Energético (Agencia Sostenibilidad) | Auditor Energético Certificado (MIEM) |
| **Turismo** | `1411` | Administrador de Servicios Hoteleros | Gerente / Jefe de Operaciones Hoteleras | Administrador Hotelero y Hospitalidad | Gerente de Hotel / Alojamientos |
| **Turismo** | `5113` | Guía Especializado en Ecoturismo | Guía de Turismo de Naturaleza / Parques | Guía de Turismo Aventura (Registro Sernatur) | Guía Turístico Patrimonial y Ecoturismo |
| **Turismo** | `3339` | Coordinador de Turismo Digital (TravelTech)| Gestor Comercial y Operativo OTA | Coordinador de Ventas y Canales Digitales | Operador de Turismo Digital y Canales Web |
| **Turismo** | `3434` | Chef Ejecutivo y Gastronomía Sostenible | Chef Ejecutivo / Jefe de Cocina | Chef / Administrador Gastronómico | Chef / Jefe de Cocina Profesional |
| **Economía del Conocimiento** | `2166` | Diseñador UX/UI y Producto Digital | Diseñador Visual y de Experiencia de Usuario | Diseñador de Interacción y Producto Digital | Diseñador UX/UI |
| **Economía del Conocimiento** | `2421` | Consultor en Transformación Digital | Analista de Procesos de Negocio / Scrum Master| Consultor de Innovación y Procesos | Consultor de Negocios y Transformación Digital |
| **Economía del Conocimiento** | `2131` | Científico en Biotecnología y AgTech | Investigador Biotecnológico (CONICET/INTA) | Investigador en Biotecnología / Bioeconomía | Bioinformático / Investigador (Inst. Pasteur) |
| **Economía del Conocimiento** | `2413` | Analista Financiero Cuantitativo y FinTech | Analista Cuantitativo / Portfolio Manager | Analista de Riesgos y Modelado FinTech | Analista Financiero FinTech / Gestión de Activos |

---

## 5. Esquema de Datos Canónico para Ingesta y Consumo

Todos los datos procesados en la plataforma respetan la estructura canónica en el pipeline:

```json
{
  "pais_codigo_iso3": "ARG | CHL | URY",
  "pais_nombre": "Argentina | Chile | Uruguay",
  "dimension": "Economía | Población | Educación | Empleo | Tecnología | Salud | Energía | Turismo | Economía del Conocimiento",
  "indicador_nombre": "Nombre estandarizado de la métrica u ocupación",
  "anio": 2024,
  "periodo": "Anual | Mensual | Trimestral",
  "valor": 7.60,
  "unidad_medida": "Porcentaje (%) | Millones de hab. | Índice (2018=100) | % del PIB",
  "fuente_oficial": "ILOSTAT / CEPALSTAT / Organismo Nacional",
  "fecha_extraccion": "AAAA-MM-DD"
}
```

---

## 6. Conclusiones y Recomendaciones de Uso

1. **Gobernanza de Datos:** Utilizar siempre el código `pais_codigo_iso3` (ISO 3166-1 alfa-3) y el código `codigo_ciuo08_oit` como llaves de integración primaria.
2. **Comparaciones Temporales:** Para series de inflación y salarios reales, tomar como año base 2018 para mitigar distorsiones de variaciones de precios extremas en la región.
3. **Consumo por API:**
   * Indicadores Macroeconómicos y Laborales: `/api/v1/consolidado/procesar` y `/api/v1/consolidado/descargar`
   * Matriz de Ocupaciones y Sectores: `/api/v1/ocupaciones/catalogo` y `/api/v1/ocupaciones/descargar`
