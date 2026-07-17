# Blueprint Arquitectónico: Sistema Inteligente de Elaboración de Análisis (SIEA)

## 1. Objetivo del Blueprint
Establecer la arquitectura fundacional y las directrices técnicas para la construcción del SIEA, garantizando un diseño basado en **Clean Architecture**. Este documento sirve como la única fuente de verdad (Single Source of Truth) para la orquestación del flujo de trabajo automatizado, asegurando que el sistema sea escalable, mantenible y desacoplado de tecnologías específicas de infraestructura o modelos de IA particulares.

## 2. Responsabilidades
El Blueprint define las siguientes responsabilidades principales para el sistema:
- **Orquestación de Flujo:** Coordinar de forma secuencial y determinista la lectura, procesamiento, análisis y generación de artefactos.
- **Aislamiento del Dominio:** Asegurar que la lógica de negocio (reglas de análisis estadístico y redacción de informes) esté aislada de los detalles de implementación (APIs de LLM, librerías de ofimática).
- **Trazabilidad:** Garantizar que cada transformación de datos y decisión generada por IA sea auditable.
- **Resiliencia:** Gestionar proactivamente fallos en la ingesta de archivos o indisponibilidad de servicios de IA.

## 3. Entradas (Inputs)
El sistema espera recibir un directorio o paquete de ejecución que contenga los siguientes elementos estructurados:
1. **Excel del mes:** Archivo de datos operativos crudos (`.xlsx` o `.csv`) correspondientes al periodo a analizar.
2. **Informes históricos:** Documentos previos (`.docx` o `.pdf`) utilizados como base de conocimiento (RAG) para extraer contexto, tono institucional y estilos de redacción históricos.
3. **Plantilla institucional de Word:** Documento (`.docx`) con marcadores, estilos y estructura oficial para el informe final.
4. **Plantilla institucional de Excel:** Documento (`.xlsx`) pre-formateado donde se inyectarán los datos procesados para el reporte final.

## 4. Salidas (Outputs)
Tras una ejecución exitosa, el sistema producirá en un directorio de salida aislado:
1. `Informe_Final.docx`: Documento narrativo completo, combinando el análisis de la IA con el formato de la plantilla institucional.
2. `Reporte_Estadistico.xlsx`: Datos del mes consolidados, limpios y calculados, insertados en la plantilla oficial.
3. `Graficos/`: Directorio que contiene las visualizaciones generadas (ej. `.png`, `.svg`) listas para ser consumidas o insertadas.
4. `auditoria.json`: Archivo estructurado con la trazabilidad completa del proceso (tiempos, prompts enviados al LLM, tokens consumidos, reglas aplicadas).
5. `execution.log`: Registro técnico detallado (logs a nivel de sistema) para depuración y monitoreo.

## 5. Flujo de Procesamiento
El procesamiento sigue un pipeline unidireccional y secuencial:
1. **Fase de Ingesta y Validación:** Lectura de las entradas, verificación de integridad de archivos y validación de esquemas/marcadores en plantillas.
2. **Fase de Extracción y Limpieza:** Parseo del Excel del mes. Limpieza de datos nulos o anómalos.
3. **Fase de Transformación (ETL):** Cálculo de métricas estadísticas. Generación del `Reporte_Estadistico.xlsx` y renderizado de imágenes en el directorio `Graficos/`.
4. **Fase de Análisis de IA:**
   - Vectorización y recuperación (RAG) de informes históricos.
   - Construcción de prompts contextuales inyectando métricas del mes y contexto histórico.
   - Ejecución del modelo fundacional (LLM) para obtener texto analítico estructurado.
5. **Fase de Ensamblado (Document Generation):** Inyección del texto generado por IA y los gráficos en la Plantilla institucional de Word.
6. **Fase de Finalización:** Cierre de procesos, guardado de `auditoria.json` y consolidación de `execution.log`.

## 6. Componentes (Clean Architecture)
- **Ingestion Controller (Adaptador):** Interfaz de entrada para leer el sistema de archivos o recibir el payload.
- **Data Processor (Caso de Uso):** Contiene la lógica pura para cruzar datos, calcular variaciones y estructurar la información.
- **Context Analyzer / RAG Engine (Caso de Uso):** Gestiona el procesamiento de lenguaje natural de los históricos.
- **LLM Gateway (Puerto/Adaptador):** Abstracción (Interfaz) que encapsula la comunicación con la API de IA (OpenAI, Gemini, Anthropic, etc.).
- **Document Renderer (Puerto/Adaptador):** Interfaz responsable de interactuar con librerías específicas (ej. `python-docx`, `openpyxl`) para generar los archivos.
- **Audit Logger (Infraestructura):** Observador transversal que recolecta eventos para la auditoría.

## 7. Contratos entre módulos (Interfaces)
- **`IDataExtractor` -> `DataProcessor`:** Retorna un DTO estandarizado con series de tiempo y metadatos operativos, agnóstico a la estructura del Excel original.
- **`DataProcessor` -> `AIAnalyzer`:** Se comunican mediante un JSON estricto (`StatisticalSummaryDTO`) que contiene exclusivamente hallazgos cuantitativos (ej. incrementos porcentuales, anomalías detectadas).
- **`AIAnalyzer` -> `DocumentRenderer`:** Envía un diccionario estructurado (`ReportContentDTO`) donde las llaves corresponden exactamente a los marcadores/placeholders de la plantilla Word.

## 8. blueprint.json esperado
Archivo de configuración base que guía la ejecución del orquestador:
```json
{
  "project_id": "SIEA_PROD_01",
  "execution_month": "2026-07",
  "inputs": {
    "raw_data_excel": "./inputs/datos_mensuales.xlsx",
    "historical_docs": "./inputs/historicos/",
    "word_template": "./templates/institucional.docx",
    "excel_template": "./templates/estadisticas.xlsx"
  },
  "outputs": {
    "destination_folder": "./outputs/2026-07/",
    "generate_charts": true
  },
  "ai_settings": {
    "temperature": 0.2,
    "max_tokens": 4096,
    "historical_context_weight": 0.7
  }
}
```

## 9. Casos de error
- **MissingFilesError:** Falta de archivos obligatorios en el directorio de entrada. Detiene la ejecución.
- **TemplateMismatchError:** Los marcadores esperados por el sistema no existen en las plantillas provistas. Retorna un reporte de marcadores faltantes.
- **DataQualityError:** El Excel del mes contiene formatos corruptos o columnas faltantes. Se registra en `auditoria.json` y se aborta el paso.
- **LLMTimeout/ConnectionError:** Fallo en el servicio de IA. El sistema debe reintentar con backoff exponencial. Si falla definitivamente, genera los reportes numéricos pero deja los campos narrativos vacíos con un tag de error.

## 10. Estrategia de validación
- **Pruebas Unitarias:** Cobertura >80% en los módulos de transformación de datos (Data Processor).
- **Validación de Esquema:** Uso de Pydantic para asegurar que todos los DTOs y el `blueprint.json` cumplen su contrato.
- **Mocking de IA:** Las pruebas de integración del pipeline deben mockear el `LLM Gateway` para evitar costos y latencia, asegurando un comportamiento determinista durante CI/CD.
- **Auditoría Post-Ejecución:** Un script validador debe asegurar que los archivos declarados en `outputs` existan físicamente y no estén corruptos.

## 11. Criterios de calidad
- **Agnosticismo Tecnológico:** El sistema no debe depender de un LLM específico (OpenAI o Gemini) ni de un formato estricto que no pueda adaptarse mediante puertos.
- **Determinismo Estilístico:** Ajustar la IA (temperatura baja, system prompts fuertes) para que reportes con datos similares generen narrativas consistentes en tono institucional.
- **Inmutabilidad de Entrada:** El sistema bajo ninguna circunstancia debe modificar, sobreescribir o bloquear los archivos de entrada (Excel original e Históricos).
- **Rendimiento:** El proceso de generación End-to-End no debe superar los 5 minutos para un paquete mensual típico.

## 12. Qué NO debe hacer el Blueprint
- **NO debe incluir código fuente:** Este documento es una guía arquitectónica y de contrato, no un manual de implementación de librerías.
- **NO debe tener Interfaz de Usuario (UI):** SIEA en esta capa opera puramente en backend/CLI como un motor de procesamiento.
- **NO debe entrenar modelos de IA (Fine-tuning):** El sistema utiliza inferencia basada en contexto (RAG/Few-shot), no re-entrena pesos del modelo fundacional.
- **NO es un sistema de almacenamiento a largo plazo:** El sistema toma inputs, genera outputs y descarta estados intermedios. El almacenamiento a largo plazo es responsabilidad del sistema que invoca al SIEA.
