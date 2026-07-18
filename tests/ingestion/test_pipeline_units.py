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
    assert list(cleaned.columns) == ["Nombre", "Edad"]

def test_detector_infer_types():
    # Expandimos las columnas para que todas tengan 20 filas (excepto Vacío que será 20 None)
    df = pd.DataFrame({
        "col1": [None] * 20,
        "col2": ["si", "NO"] * 10,
        "col3": ["$100", "€200"] * 10,
        "col4": ["15%", "20.5%"] * 10,
        "col5": ["2023-01-01", "2024-02-15"] * 10,
        "col6": ["10", "1,500.50"] * 10,
        "col7": ["A", "B"] * 10,
        "col8": [f"Unic_{i}" for i in range(20)]
    })
    
    detector = DatatypeDetector()
    types = detector.infer(df)
    
    assert types["col1"] == "Vacío"
    assert types["col2"] == "Booleano"
    assert types["col3"] == "Moneda"
    assert types["col4"] == "Porcentaje"
    assert types["col5"] == "Fecha"
    assert types["col6"] == "Número"
    assert types["col7"] == "Categoría"
    assert types["col8"] == "Texto"

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
