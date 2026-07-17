# Flujo de Datos (DATA_FLOW) - SIEA

Este documento detalla el ciclo de vida completo de los datos dentro del Sistema Inteligente de Elaboración de Análisis (SIEA). Describe la secuencia exacta de eventos desde la selección de la carpeta de origen por el usuario hasta la generación de los artefactos finales, especificando qué hace cada módulo y qué contratos de datos (archivos/estructuras) intercambian entre sí.

## 1. Inicio: Selección de Carpeta (Input)
El proceso comienza cuando el usuario (o un sistema programado) indica al SIEA la ruta de una carpeta de proyecto para un periodo específico. Esta carpeta actúa como el punto de entrada estandarizado.

**Archivos esperados en la carpeta de entrada:**
- **Datos Mensuales (`.xlsx` o `.csv`):** Los datos crudos operativos del mes.
- **Informes Históricos (`.docx` o `.pdf`):** Documentos de meses anteriores utilizados como base de conocimiento para extraer contexto y tono institucional.
- **Plantilla_Informe (`.docx`):** Plantilla institucional base con marcadores.
- **Plantilla_Reporte (`.xlsx`):** Plantilla institucional pre-formateada.
- **Configuración (`blueprint.json`):** Archivo maestro opcional de configuración del proceso.

---

## 2. Flujo de Ejecución por Módulos

El sistema está dividido en módulos desacoplados (siguiendo Clean Architecture) que se ejecutan en un pipeline secuencial. Cada módulo cumple un propósito específico y pasa un estado (o archivo de datos estructurado) al siguiente.

### Fase 1: Ingestion Controller (Validador e Ingestor)
- **Qué hace:** Verifica que la carpeta seleccionada contenga todos los archivos necesarios. Lee los archivos, valida su integridad (ej. que los Excel no estén corruptos, que las plantillas contengan los marcadores correctos).
- **Archivos que consume:** Carpeta de entrada completa (`blueprint.json`, plantillas, históricos y datos).
- **Qué produce/intercambia:** Si la validación es exitosa, carga los archivos en memoria o en un área temporal (workspace de ejecución) y cede el control al `Data Processor`. Escribe los primeros logs en `execution.log`.

### Fase 2: Data Processor (Extractor y Normalizador)
- **Qué hace:** Abre el archivo de datos mensuales crudos (Excel/CSV), limpia valores nulos o anómalos (Data Cleansing) y estandariza la información. Convierte los datos tabulares en una estructura agnóstica.
- **Archivos que consume:** Datos mensuales crudos.
- **Qué produce/intercambia:** Genera un archivo o estado en memoria llamado `normalized_truth.json` (Datos limpios y estandarizados).

### Fase 3: Statistics Engine (Motor ETL y Matemático)
- **Qué hace:** Toma los datos normalizados y realiza los cálculos estadísticos y de negocio (sumatorias, variaciones porcentuales, detección de picos, agrupaciones).
- **Archivos que consume:** `normalized_truth.json`.
- **Qué produce/intercambia:** 
  1. Produce `statistical_truth.json`: Un diccionario estricto (`StatisticalSummaryDTO`) que contiene todas las métricas procesadas. Este es el contrato de verdad matemática del sistema.
  2. Inyecta temporalmente gráficos renderizados (ej. imágenes `.png`) en el directorio `Graficos/` temporal.

### Fase 4: RAG Engine & Insight Engine (Análisis de IA)
- **Qué hace:** Esta fase gestiona el razonamiento y la creación de la narrativa.
  1. **RAG Engine:** Lee los *Informes Históricos*, los vectoriza y recupera fragmentos clave para entender el tono y el contexto de meses anteriores.
  2. **Insight Engine:** Ensambla un prompt complejo cruzando el contexto recuperado con los números exactos del `statistical_truth.json`. Envía este prompt al LLM Gateway.
- **Archivos que consume:** `statistical_truth.json` y los Informes Históricos.
- **Qué produce/intercambia:** Devuelve un diccionario de narrativas, usualmente llamado `ReportContentDTO`, donde cada clave se mapea a un marcador de la plantilla de Word, y su valor es el texto generado por la IA en tono institucional.

### Fase 5: Document Builders (Ensambladores)
- **Qué hace:** Módulos dedicados (Document Renderers) a la creación física de los archivos ofimáticos finales.
  - **Excel Builder:** Inyecta los datos de `statistical_truth.json` dentro de la *Plantilla_Reporte*.
  - **Word Builder:** Abre la *Plantilla_Informe*, reemplaza los marcadores de texto con el `ReportContentDTO` generado por la IA, e inserta las imágenes del directorio temporal de Gráficos.
- **Archivos que consume:** `statistical_truth.json`, `ReportContentDTO`, gráficos temporales y las plantillas institucionales de entrada.
- **Qué produce/intercambia:** Genera los artefactos ofimáticos finales en memoria y los guarda en la carpeta de salida.

### Fase 6: Quality Assurance (QA) & Audit Logger (Cierre)
- **Qué hace:** Valida que todos los archivos finales existan, no estén corruptos y que no queden marcadores sin reemplazar en el Word. Recolecta toda la telemetría del proceso (tiempo, decisiones, prompts enviados, tokens de IA consumidos).
- **Archivos que consume:** Eventos del sistema emitidos transversalmente durante la ejecución.
- **Qué produce/intercambia:** Persiste la información en disco cerrando el proceso.

---

## 3. Fin: Carpeta de Salida (Output)

Al finalizar la orquestación, el sistema ha transformado las entradas en una carpeta de salida empaquetada. El usuario obtiene los siguientes artefactos finales:

1. **`Informe.docx`**: El documento principal de texto. Contiene el análisis narrativo creado por la IA, cruzado con el contexto histórico, y presentado bajo el esquema de estilos de la plantilla institucional, incluyendo los gráficos del mes.
2. **`Reporte.xlsx`**: El anexo estadístico o reporte de datos. Contiene los datos crudos ya procesados, limpios y consolidados matemáticamente dentro de la plantilla oficial de Excel.
3. **`auditoria.json`**: El comprobante de trazabilidad. Un archivo JSON que documenta qué reglas estadísticas se aplicaron, qué prompts exactos se enviaron al LLM, cuántos tokens se consumieron, alertas de QA y tiempos de ejecución. Garantiza que el proceso no sea una "caja negra".
4. **`execution.log`**: El archivo de bitácora técnica del sistema. Contiene los registros a nivel de aplicación (INFO, WARNING, ERROR, DEBUG) de todos los módulos que intervinieron en la cadena (e.g. "Ingestion Controller inició", "Fallo al conectar con OpenAI", "Reintento 1 de 3"). Utilizado para depuración técnica.
