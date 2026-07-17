import pytest
import pandas as pd
from pathlib import Path
from src.context.context_models import AgentContext, ExcelContext
from src.ingestion.ingestion_engine import IngestionEngine

@pytest.fixture
def dirty_excel(tmp_path):
    """Genera un archivo Excel sucio para pruebas de integración."""
    df = pd.DataFrame({
        "Unnamed: 0": [None, None, None, None],
        "  ID Empleado ": ["001 ", "002", None, "004"],
        "EDAD": [25, 30, None, 40],
        "Fecha Ingreso": ["2023-01-01", "2023-02-01", None, "2023-04-01"]
    })
    
    # Añadir filas completamente vacías al final
    df.loc[4] = [None, None, None, None]
    
    file_path = tmp_path / "dirty_data.xlsx"
    df.to_excel(file_path, index=False)
    return file_path

def test_ingestion_integration_pipeline(dirty_excel):
    # Mockear un AgentContext que apunte al archivo temporal
    context = AgentContext(
        excel=ExcelContext(
            raw_data_path=str(dirty_excel),
            template_path=""
        )
    )
    
    orchestrator = IngestionEngine()
    ssot_context = orchestrator.run(context)
    
    # Assertions on Data
    df_clean = ssot_context.data
    
    # - Column "Unnamed: 0" dropped
    assert "Unnamed: 0" not in df_clean.columns
    # - Headers cleaned
    assert "id empleado" in df_clean.columns
    # - Empty row dropped (originally 5 rows, rows 2 and 4 are completely empty, should be 3 now)
    assert len(df_clean) == 3
    # - Strings stripped
    assert df_clean.iloc[0]["id empleado"] == "001"
    
    # Assertions on Report
    report = ssot_context.report
    assert report.rows_read == 3
    assert len(report.columns_detected) == 3
    assert report.duration_ms > 0
