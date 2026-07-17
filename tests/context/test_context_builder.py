import pytest
from src.context.context_models import ProjectContext, RuntimeContext, WordContext, ExcelContext, MetadataContext, DiagnosticsContext
from src.context.context_builder import ContextBuilder

def test_builder_success():
    builder = ContextBuilder()
    builder.set_project_context(ProjectContext())
    builder.set_runtime_context(RuntimeContext())
    builder.set_word_context(WordContext())
    builder.set_excel_context(ExcelContext())
    builder.set_metadata_context(MetadataContext())
    builder.set_diagnostics_context(DiagnosticsContext())
    
    context = builder.build()
    assert context is not None
    assert context.project.project_name == "Desconocido"

def test_builder_missing_component():
    builder = ContextBuilder()
    builder.set_project_context(ProjectContext())
    # Missing others
    with pytest.raises(ValueError):
        builder.build()
