"""Tests para DTOs y constructores de interfaces."""
import pytest
from pathlib import Path
from src.ingestion.interfaces import ValidationReport, IngestionResult

def test_validation_report_defaults():
    """Verifica los valores por defecto del ValidationReport."""
    report = ValidationReport(is_valid=True)
    assert report.is_valid is True
    assert report.errors == []
    assert report.warnings == []
    assert report.health_score == 100.0
    assert report.processing_time_ms == 0.0

def test_validation_report_custom():
    """Verifica la instanciación de ValidationReport con valores específicos."""
    report = ValidationReport(
        is_valid=False,
        errors=["Error 1"],
        warnings=["Warning 1"],
        health_score=85.5,
        processing_time_ms=120.5
    )
    assert report.is_valid is False
    assert report.errors == ["Error 1"]
    assert report.warnings == ["Warning 1"]
    assert report.health_score == 85.5
    assert report.processing_time_ms == 120.5

def test_ingestion_result():
    """Verifica la instanciación de IngestionResult."""
    val_report = ValidationReport(is_valid=True)
    path = Path("/tmp/output.json")
    
    result = IngestionResult(
        success=True,
        records_processed=100,
        validation_report=val_report,
        output_data_path=path,
        report_path=None
    )
    
    assert result.success is True
    assert result.records_processed == 100
    assert result.validation_report is val_report
    assert result.output_data_path == path
    assert result.report_path is None
