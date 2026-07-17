# Roadmap del Proyecto SIEA

Este documento traza la hoja de ruta general para la construcción, pruebas y despliegue del Sistema de Informes (SIEA).

## Fase 1: Diseñar la Base (Actual)
- ✅ Estructura de directorios base.
- ✅ Documentación Core (`BLUEPRINT.md`, `DATA_FLOW.md`).
- ✅ Definición de Estándares (`WORD_STANDARD.md`, `EXCEL_STANDARD.md`).
- ✅ Setup del Golden Dataset (`samples/`).
- ✅ Creación de la prueba de concepto del *Blueprint Engine*.

## Fase 2: Desarrollo de Motores Core (Siguiente)
- Construcción del **Data Extractor** y **Normalizador**.
- Implementación del **Statistics Engine** para cálculos matemáticos estructurados.

## Fase 3: Integración de IA y Generación
- Desarrollo del **Insight Engine** (conexión con LLMs para generación narrativa).
- Desarrollo de los **Builders** (Word Builder y Excel Builder) para ensamblar los documentos finales.

## Fase 4: Aseguramiento de Calidad y Refinamiento
- Implementación de **QA Engine**.
- Pruebas exhaustivas contra el Golden Dataset.
- Refinamiento de Prompts y lógicas de validación.
