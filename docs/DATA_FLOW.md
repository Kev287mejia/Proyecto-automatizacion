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

### Fase 0: Blueprint Engine
- **Qué hace:** Escanea la carpeta del `Proyecto`, identifica los archivos relevantes (Excel de datos, plantillas, históricos) e infiere los parámetros base.
- **Archivos que consume:** Carpeta de entrada cruda (Proyecto).
- **Qué produce/intercambia:** Genera automáticamente el archivo `blueprint.json`. Elimina la necesidad de configuraciones manuales.

### Fase 1: Context Engine
- **Qué hace:** Lee el `blueprint.json` generado, valida su estructura estrictamente y lo convierte en un contexto maestro en memoria (`AgentContext`). No hace cálculos, no llama IA, no abre ofimática.
- **Archivos que consume:** `blueprint.json`.
- **Qué produce/intercambia:** Objeto `AgentContext` universal para todo el SIEA.

### Fase 2: Ingestion & Normalizer
- **Qué hace:** Basado en las rutas del `AgentContext`, abre el archivo de datos mensuales crudos (Excel/CSV), limpia valores nulos o anómalos (Data Cleansing) y estandariza las columnas.
- **Archivos que consume:** Datos mensuales crudos (indicados por el contexto).
- **Qué produce/intercambia:** Estructuras de datos limpias en memoria.

### Fase 3: Truth Engine & Traceability Engine
- **Qué hace:** Toma los datos normalizados y consolida el estado absoluto del sistema. Simultáneamente, el **Traceability Engine** envuelve cada dato con su linaje exacto (metadatos de procedencia). Cada dato sabe exactamente de dónde salió.
- **Archivos que consume:** Datos en memoria provistos por el Normalizer.
- **Qué produce/intercambia:** Genera un archivo maestro llamado `truth.json`. Este JSON contiene TODA la verdad estructurada y auditable (ej. `{"mujeres": {"value": 140, "trace": {"sheet": "Participantes", "row": 102, "column": "Sexo", "calculated_by": "excel_extractor", "timestamp": "2026-07-17"}}}`). A partir de este momento, **nunca se vuelve a abrir el Excel**. Esto elimina muchísimos errores de lectura concurrente o inconsistencia.

### Fase 4: Statistics Engine
- **Qué hace:** Consume exclusivamente el `truth.json` y realiza los cálculos estadísticos derivados (sumatorias, variaciones porcentuales, crecimiento, detección de picos).
- **Archivos que consume:** `truth.json`.
- **Qué produce/intercambia:** 
  1. Produce `statistical_truth.json`: Un diccionario extendido con todas las métricas calculadas.
  2. Inyecta temporalmente gráficos renderizados (ej. imágenes `.png`) en el directorio temporal.

### Fase 5: Insight Engine (RAG y LLM)
- **Qué hace:** 
  1. **RAG Engine:** Lee los *Informes Históricos*, los vectoriza y recupera contexto.
  2. **Insight Engine:** Ensambla un prompt complejo cruzando el contexto histórico con los números exactos extraídos del `statistical_truth.json` o `truth.json`.
- **Archivos que consume:** `truth.json` / `statistical_truth.json` y los Informes Históricos.
- **Qué produce/intercambia:** Diccionario de narrativas (`ReportContentDTO`).

### Fase 6: Quality Assurance (QA)
- **Qué hace:** Intercepta los resultados del Insight Engine y el Statistics Engine. Valida que las narrativas generadas por la IA no contradigan la matemática de `truth.json` (prevención de alucinaciones) y que la estructura sea correcta.
- **Archivos que consume:** `truth.json` y `ReportContentDTO`.
- **Qué produce/intercambia:** Visto bueno (aprobación) para ensamblar, o lanza excepciones.

### Fase 7: Word Builder & Excel Builder
- **Qué hace:** Módulos dedicados a la creación física de los archivos ofimáticos finales. Solo consumen el JSON maestro y los textos aprobados. No consultan el Excel original.
  - **Excel Builder:** Inyecta los datos calculados dentro de la *Plantilla_Reporte*.
  - **Word Builder:** Abre la *Plantilla_Informe*, reemplaza los marcadores y añade las narrativas e imágenes.
- **Archivos que consume:** `truth.json`, `ReportContentDTO`, gráficos temporales y las plantillas.
- **Qué produce/intercambia:** Genera los artefactos ofimáticos finales en memoria y los guarda en la salida. Persiste además el `auditoria.json` y `execution.log`.

---

## 3. Fin: Carpeta de Salida (Output)

Al finalizar la orquestación, el sistema ha transformado las entradas en una carpeta de salida empaquetada. El usuario obtiene los siguientes artefactos finales:

1. **`Informe.docx`**: El documento principal de texto. Contiene el análisis narrativo creado por la IA, cruzado con el contexto histórico, y presentado bajo el esquema de estilos de la plantilla institucional, incluyendo los gráficos del mes.
2. **`Reporte.xlsx`**: El anexo estadístico o reporte de datos. Contiene los datos crudos ya procesados, limpios y consolidados matemáticamente dentro de la plantilla oficial de Excel.
3. **`auditoria.json`**: El comprobante de trazabilidad. Un archivo JSON que documenta qué reglas estadísticas se aplicaron, qué prompts exactos se enviaron al LLM, cuántos tokens se consumieron, alertas de QA y tiempos de ejecución. Garantiza que el proceso no sea una "caja negra".
4. **`execution.log`**: El archivo de bitácora técnica del sistema. Contiene los registros a nivel de aplicación (INFO, WARNING, ERROR, DEBUG) de todos los módulos que intervinieron en la cadena (e.g. "Ingestion Controller inició", "Fallo al conectar con OpenAI", "Reintento 1 de 3"). Utilizado para depuración técnica.
