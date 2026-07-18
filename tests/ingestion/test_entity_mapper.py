import pytest
import pandas as pd
from src.ingestion.entity_mapper import EntityMapper

def test_entity_mapper_gender():
    mapper = EntityMapper()
    df = pd.DataFrame({
        "sexo": ["F", "Fem", "Femenina", "MUJER", "Mujer", "M", "MASCULINO"]
    })
    
    mapped_df = mapper.map_to_ssot(df)
    
    assert mapped_df["sexo"].tolist() == ["Femenino", "Femenino", "Femenino", "Femenino", "Femenino", "MASCULINO", "MASCULINO"]

def test_entity_mapper_location():
    mapper = EntityMapper()
    df = pd.DataFrame({
        "municipio": ["Bilwi", "Puerto Cabezas", "PUERTO CABEZAS", "Managua"]
    })
    
    mapped_df = mapper.map_to_ssot(df)
    
    assert mapped_df["municipio"].tolist() == ["Puerto Cabezas", "Puerto Cabezas", "Puerto Cabezas", "MANAGUA"]

def test_entity_mapper_normalization():
    mapper = EntityMapper()
    df = pd.DataFrame({
        "nombre": [" áéíóú ", "María", "José"]
    })
    
    mapped_df = mapper.map_to_ssot(df)
    
    assert mapped_df["nombre"].tolist() == ["AEIOU", "MARIA", "JOSE"]
