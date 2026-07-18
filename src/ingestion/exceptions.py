"""
Excepciones personalizadas para el Ingestion Engine de SIEA.

Este módulo define la jerarquía de errores de dominio, garantizando
que las fallas del sistema se manejen de forma estructurada y predecible.
"""

class IngestionError(Exception):
    """Excepción base para todos los errores del Ingestion Engine."""
    pass

class FileNotReadableError(IngestionError):
    """Lanzada cuando el archivo Excel no puede ser leído (no existe, corrupto, protegido)."""
    pass

class InvalidWorkbookError(IngestionError):
    """Lanzada cuando el workbook no cumple los requisitos (ej. sin hojas válidas)."""
    pass

class InvalidWorksheetError(IngestionError):
    """Lanzada cuando una hoja específica no tiene el formato esperado."""
    pass

class HeaderDetectionError(IngestionError):
    """Lanzada cuando no se pueden detectar o identificar los encabezados obligatorios."""
    pass

class DataExtractionError(IngestionError):
    """Lanzada cuando ocurre un error al extraer datos de las celdas."""
    pass

class DataNormalizationError(IngestionError):
    """Lanzada cuando una fila no puede ser normalizada al esquema JSON."""
    pass

class EntityMappingError(IngestionError):
    """Lanzada cuando falla la normalización semántica de una entidad."""
    pass

class ValidationError(IngestionError):
    """Lanzada cuando los datos extraídos no superan las reglas de validación."""
    pass

class ConfigurationError(IngestionError):
    """Lanzada cuando hay un error en la configuración del motor de ingesta."""
    pass
