"""Tests para las excepciones del dominio."""
import pytest
from src.ingestion.exceptions import (
    IngestionError,
    FileNotReadableError,
    InvalidWorkbookError,
    InvalidWorksheetError,
    HeaderDetectionError,
    DataExtractionError,
    DataNormalizationError,
    EntityMappingError,
    ValidationError,
    ConfigurationError
)

def test_exception_hierarchy():
    """Verifica que todas las excepciones heredan de IngestionError."""
    exceptions = [
        FileNotReadableError,
        InvalidWorkbookError,
        InvalidWorksheetError,
        HeaderDetectionError,
        DataExtractionError,
        DataNormalizationError,
        EntityMappingError,
        ValidationError,
        ConfigurationError
    ]
    
    for exc_class in exceptions:
        assert issubclass(exc_class, IngestionError)

def test_exception_instantiation():
    """Verifica que las excepciones pueden ser instanciadas con un mensaje."""
    msg = "Test error message"
    exc = ValidationError(msg)
    
    assert isinstance(exc, IngestionError)
    assert str(exc) == msg
