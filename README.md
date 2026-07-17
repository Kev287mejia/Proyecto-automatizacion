# SIEA - Sistema Institucional de Evaluación Académica

**Área de Innovación y Emprendimiento**

SIEA es una plataforma de automatización documental y análisis de datos orientada a la generación desatendida de reportes corporativos e informes ejecutivos. Diseñada con una arquitectura de separación de responsabilidades (Clean Architecture), la herramienta permite ingerir grandes volúmenes de datos crudos y transformarlos en inteligencia de negocios estructurada a través de un flujo *Blueprint-Driven*.

## Arquitectura del Sistema: Pipeline SIEA

El proyecto abstrae por completo la lógica de negocio del formato de presentación final, garantizando que los datos y el diseño institucional no se acoplen de forma rígida. El flujo de ejecución secuencial garantiza una Única Fuente de Verdad (Single Source of Truth) en cada etapa:

```text
Project (Carpeta de Trabajo)
       ↓
Blueprint Engine (Scanner, Analyzers, Validator, Builder)
       ↓
blueprint.json (Artefacto en disco)
       ↓
Context Engine (Inferencia de metadatos de negocio)
       ↓
AgentContext (Objeto inmutable en memoria)
       ↓
Processing (Capa Analítica)
       ├── Data Extractor (Ingesta cruda de Excel)
       ├── Data Normalizer (Limpieza y estandarización)
       ├── Truth Engine (Generación de Verdad Estadística Inmutable)
       └── Insight Engine (Generación de lenguaje natural)
       ↓
Word Builder (Inyección de insights en Word)
       ↓
Excel Builder (Inyección de datos en Excel)
       ↓
QA Engine (Auditoría final del resultado)
```

### Módulos Principales

*   **Blueprint Engine**: Motor de ingeniería inversa que analiza plantillas institucionales (Word y Excel) preexistentes y extrae un mapa estructural estático (`blueprint.json`).
*   **Context Engine**: Traduce el blueprint estático en un contexto de negocio vivo (`AgentContext`), deduciendo periodos, metadatos y manteniendo la estructura visual en memoria.
*   **Processing Module**: El cerebro analítico del sistema, estructurado para garantizar la inmutabilidad de los datos:
    *   `Data Extractor`: Sabe *cómo* y *de dónde* leer, pero no analiza.
    *   `Data Normalizer`: Estandariza nulos, formatos de fechas y tipos de datos.
    *   **`Truth Engine`**: Consolida todos los cálculos en un "Estado de la Verdad" matemático inmutable. Todos los módulos posteriores confían ciegamente en este nodo. No es solo estadística, es el acta notarial de los datos del periodo.
    *   `Insight Engine`: Transforma los números del *Truth Engine* en conclusiones ejecutivas digeribles y narrativas.
*   **Builders**: Inyectores especializados que toman los insights y los vacían en las plantillas sin alterar su diseño nativo.
*   **QA Engine**: Validador final que garantiza que los reportes generados cumplen con las directrices de la institución.

## Uso del Orquestador

Para disparar el pipeline de compilación documental:

```bash
python -m src.export.package_builder
```

---
*Desarrollado desde cero para transformar procesamiento operativo mecánico en automatización estratégica escalable.*
