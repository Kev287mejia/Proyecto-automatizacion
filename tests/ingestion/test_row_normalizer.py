import pytest
import pandas as pd
from src.ingestion.row_normalizer import RowNormalizer

def test_row_normalizer_removes_empty_rows():
    normalizer = RowNormalizer()
    df = pd.DataFrame({
        'Nombre': ['Alice', None, 'Charlie'],
        'Edad': [25, None, 30]
    })
    
    normalized = normalizer.normalize(df)
    assert len(normalized) == 2
    assert 'nombre' in normalized.columns

def test_row_normalizer_cleans_strings_and_lowercases_cols():
    normalizer = RowNormalizer()
    df = pd.DataFrame({
        'Nombre': [' Alice ', 'Bob '],
        'Sexo': ['Femenino ', ' Masculino']
    })
    
    normalized = normalizer.normalize(df)
    # Check lowercase column names
    assert 'nombre' in normalized.columns
    assert 'sexo' in normalized.columns
    
    # Check stripped strings
    assert normalized['nombre'].iloc[0] == 'Alice'
    assert normalized['sexo'].iloc[0] == 'Femenino'

def test_row_normalizer_to_records():
    normalizer = RowNormalizer()
    df = pd.DataFrame({
        'Nombre': ['Alice'],
        'Edad': [25],
        'Municipio': ['Bilwi']
    })
    
    # We pass the df through normalize, then get records
    normalized = normalizer.normalize(df)
    records = normalizer.to_records(normalized)
    assert isinstance(records, list)
    assert len(records) == 1
    assert records[0] == {'nombre': 'Alice', 'edad': 25, 'municipio': 'Bilwi'}
