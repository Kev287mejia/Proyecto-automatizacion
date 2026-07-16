# SIEA - Sistema Institucional de Evaluación Académica

**Área de Innovación y Emprendimiento**

SIEA es una plataforma de automatización documental y análisis de datos orientada a la generación desatendida de reportes corporativos e informes ejecutivos. Diseñada con una arquitectura de separación de responsabilidades (Clean Architecture), la herramienta permite ingerir grandes volúmenes de datos crudos y transformarlos en inteligencia de negocios estructurada a través de un flujo *Blueprint-Driven*.

## Arquitectura del Sistema

El proyecto abstrae por completo la lógica de negocio del formato de presentación final, garantizando que los datos y el diseño institucional no se acoplen de forma rígida. La orquestación sigue un patrón `Extractor -> Processor -> Builder`.

### Módulos Principales

*   **Blueprint Engine (`src/blueprint/`)**: Motor de ingeniería inversa que analiza plantillas institucionales (Word y Excel) preexistentes y extrae un mapa estructural (JSON). Esto asegura que el software trabaje sobre lienzos preaprobados, conservando tipografías, colores, cálculos nativos y dimensiones corporativas exactas.
*   **Builders (`src/builders/`)**: Inyectores de información especializados y aislados del diseño visual.
    *   `word_builder.py`: Implementa inyección dinámica a través de marcadores de posición (`{{variables}}`) a nivel de párrafos manipulando la estructura XML subyacente (vía `python-docx`).
    *   `excel_builder.py`: Inyecta tensores de datos matriciales en hojas designadas por el *Blueprint*, respetando estrictamente las fórmulas iterativas y los gráficos pre-configurados (vía `openpyxl`).
*   **Orquestador (`src/export/package_builder.py`)**: Cerebro de automatización que gestiona el ciclo de vida del reporte. Controla la ingesta de la carpeta de trabajo, enruta los datos a los motores de procesamiento, orquesta los *Builders* de forma secuencial y despliega la salida en una bóveda histórica jerárquica auditada (ej. `REPORTES_HISTORICOS/YYYY/MM_Mes/`).
*   **Analysis Engines (`src/analysis/`)**: Capa de abstracción matemática encargada de procesar los datos duros, generar el archivo de estado o verdad estadística (`statistical_truth.json`) y procesar *insights* de alto nivel.

## Estructura del Código

```text
SIEA/
├── src/
│   ├── blueprint/          # Extracción de esquemas JSON desde plantillas físicas
│   ├── analysis/           # Motores de modelado estadístico e inferencia
│   ├── builders/           # Generación de binarios inyectados (.xlsx, .docx)
│   ├── templates/          # Gestor de integridad de documentos base
│   └── export/             # Package Builder / Orquestador de pipeline
└── README.md
```

## Flujo de Orquestación

1.  **Ingesta Transaccional**: El sistema captura datos crudos (`.csv`, `.xlsx`) y carga los modelos de plantillas base.
2.  **Mapeo Topológico**: El *Blueprint Engine* resuelve las ubicaciones de inyección exactas en el modelo de objetos del documento.
3.  **Procesamiento Analítico**: Conversión de registros brutos en hallazgos matemáticos estructurados.
4.  **Inyección y Compilación**: Construcción en paralelo de la matriz de validación (Excel) y la narrativa ejecutiva (Word).
5.  **Despliegue y Auditoría**: Consolidación de archivos finales, generación del log transaccional y clasificación automatizada en el histórico del servidor.

## Uso del Orquestador

Para disparar el pipeline de compilación documental:

```bash
python -m src.export.package_builder
```

El script registrará la estampa de tiempo actual y generará una carpeta autocontenida lista para distribución ejecutiva.

---
*Desarrollado desde cero para transformar procesamiento operativo mecánico en automatización estratégica escalable.*
