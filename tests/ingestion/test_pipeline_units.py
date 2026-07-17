import pytest
import pandas as pd
from src.ingestion.header_detector import HeaderDetector
from src.ingestion.datatype_detector import DatatypeDetector
from src.ingestion.row_normalizer import RowNormalizer
from src.ingestion.ingestion_validator import IngestionValidator
from src.ingestion.ingestion_report import IngestionError

def test_detector_cleans_unnamed():
    df = pd.DataFrame({
        "Unnamed: 0": [None, None],
        " Nombre ": ["A", "B"],
        "EDAD": [10, 20]
    })
    
    detector = HeaderDetector()
    cleaned = detector.detect(df)
    
    # Should drop Unnamed with all NaNs and normalize names
    assert "Unnamed: 0" not in cleaned.columns
    assert list(cleaned.columns) == ["nombre", "edad"]

def test_detector_infer_types():
    df = pd.DataFrame({
        "nombre": ["A", "B"],
        "edad": ["10", "20"]
    })
    detector = DatatypeDetector()
    types = detector.infer(df)
    assert types["edad"] == "numeric"
    assert types["nombre"] == "string"

def test_normalizer_cleans_whitespace():
    df = pd.DataFrame({
        "nombre": [" A ", "B "],
        "edad": [10, 20]
    })
    normalizer = RowNormalizer()
    normalized = normalizer.normalize(df)
    assert normalized["nombre"].tolist() == ["A", "B"]

def test_normalizer_drops_empty_rows():
    df = pd.DataFrame({
        "nombre": ["A", None, "B"],
        "edad": [10, None, 20]
    })
    normalizer = RowNormalizer()
    normalized = normalizer.normalize(df)
    assert len(normalized) == 2

def test_validator_raises_on_empty():
    df = pd.DataFrame()
    validator = IngestionValidator()
    with pytest.raises(IngestionError, match="vacío"):
        validator.validate(df)

def test_validator_warns_on_high_nulls(caplog):
    df = pd.DataFrame({
        "nombre": ["A", "B", "C"],
        "telefono": ["123", None, None] # 66% nulls
    })
    validator = IngestionValidator()
    warnings = validator.validate(df)
    assert len(warnings) == 1
    assert "telefono" in warnings[0]
