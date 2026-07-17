# Blueprint Engine Specification (SIEA)

## 1. Visión General y Responsabilidades
El **Blueprint Engine** es el componente fundamental (Tier 1) de la arquitectura SIEA. Actúa como el "analista estructural", inspeccionando los archivos provistos por el usuario (plantillas e históricos) para mapear el terreno antes de que cualquier extracción de datos o generación de IA ocurra.

**Responsabilidades Únicas:**
1. **Descubrimiento:** Leer el directorio raíz del proyecto para identificar activos clave (Plantillas Word/Excel, Documentos Históricos).
2. **Mapeo Estructural:** Extraer la jerarquía de secciones, marcadores y tipografías del documento Word; enumerar hojas, conteo de tablas y gráficos del Excel.
3. **Generación del Contrato:** Emitir un documento `blueprint.json` estandarizado que servirá como fuente de verdad y contrato de interfaces para los motores subsecuentes (Data Extractor, Statistics Engine, Insight Engine, Builders).

---

## 2. Entradas y Salidas

### Entradas Esperadas (Inputs)
- **Directorio del Proyecto**: Carpeta montada que contiene:
  - `Plantilla_*.docx`: Plantilla base con estilos y jerarquía esperada.
  - `Plantilla_*.xlsx`: Plantilla base con hojas y tablas pre-formateadas.
  - `Informe_*.docx` (Opcional): Informes previos para inferencia de contexto.

### Salidas (Outputs)
- **`blueprint.json`**: Archivo JSON estandarizado en la raíz del directorio del proyecto o en una carpeta oculta de procesamiento (`.siea/`).
- **Blueprint Event Logs**: Logs estructurados indicando éxito, advertencias de secciones faltantes o fallos críticos de validación.

---

## 3. Estructura del Contrato (`blueprint.json`)
El diseño del JSON debe ser determinista, legible y fácil de parsear por Pydantic u otras librerías de validación de esquemas en Python.

```json
{
  "metadata": {
    "schema_version": "1.0",
    "generated_at": "2026-07-17T10:00:00Z",
    "project_path": "/absolute/path/to/project"
  },
  "word_template": {
    "detected_file": "Plantilla_Informe.docx",
    "structure": [
      {
        "level": 1,
        "name": "Resumen Ejecutivo",
        "expected_elements": ["paragraphs"]
      },
      {
        "level": 1,
        "name": "Resultados",
        "expected_elements": ["table", "chart", "paragraphs"]
      }
    ],
    "styles": {
      "Heading1": {
        "font_family": "Arial",
        "font_size_pt": 18,
        "is_bold": true
      },
      "Normal": {
        "font_family": "Calibri",
        "font_size_pt": 11,
        "is_bold": false
      }
    }
  },
  "excel_template": {
    "detected_file": "Plantilla_Reporte.xlsx",
    "worksheets": [
      {
        "name": "Resumen",
        "tables_detected": 2,
        "charts_detected": 1
      },
      {
        "name": "Demografia_Sexo",
        "tables_detected": 1,
        "charts_detected": 1
      }
    ]
  },
  "historical_context": {
    "files_detected": [
      "Informe_Abril.docx",
      "Informe_Mayo.docx"
    ]
  }
}
```

---

## 4. Reglas de Validación y Lógica de Negocio

### 4.1 Tolerancia a Fallos y Degadación Elegante
- **Si no hay Word:** El sistema debe lanzar una excepción `CriticalBlueprintError`, abortando la cadena, ya que no se puede generar el informe final sin plantilla.
- **Si no hay Excel:** Lanza un `MissingDataTemplateWarning`. Si los datos se suministran por otra vía, el flujo puede continuar (aunque se marca en el log).
- **Si no hay Históricos:** El JSON se genera indicando un arreglo vacío en `historical_context`. El pipeline degrada de modo que el *Insight Engine* no comparará métricas cualitativas con el pasado.

### 4.2 Lógica de Extracción Word
- Solo se consideran secciones (nodos raíz) aquellos párrafos que cuenten con estilos predefinidos (Ej. `Heading 1`, `Heading 2`).
- Las variables inyectables (`{{VAR}}`) encontradas dentro del Word deben ser mapeadas temporalmente, aunque su resolución competa al Builder.

### 4.3 Lógica de Extracción Excel
- Se ignoran las hojas ocultas nativamente por Excel (ej. macros, datos raw escondidos de fábrica) a menos que se fuerce por configuración.
- El conteo de tablas se basa en tablas estructuradas de Excel (`ListObjects`). Tablas implícitas (rangos de datos sin formato tabla) requerirán validación heurística.

---

## 5. Criterios de Calidad (NFRs - Non-Functional Requirements)

1. **Rendimiento:** La inspección de documentos no debe tardar más de 3 segundos por documento (para archivos < 20MB).
2. **Determinismo:** Ejecutar el Engine 10 veces sobre la misma carpeta debe generar un JSON con exactamente los mismos *hashes* lógicos estructurales.
3. **Desacoplamiento:** El motor no debe ejecutar operaciones matemáticas (Statistics Engine) ni de NLP (Insight Engine). Su única tarea es *declarar qué existe* en las plantillas, no evaluar su contenido de negocio.
