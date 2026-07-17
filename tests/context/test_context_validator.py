import pytest
from src.context.context_models import AgentContext, ProjectContext, RuntimeContext, WordContext, ExcelContext, MetadataContext, DiagnosticsContext
from src.context.context_validator import ContextValidator, ValidationReport

def test_validator_success():
    ctx = AgentContext(
        project=ProjectContext(project_name="Valid Project"),
        runtime=RuntimeContext(),
        word=WordContext(),
        excel=ExcelContext(),
        metadata=MetadataContext(),
        diagnostics=DiagnosticsContext()
    )
    validator = ContextValidator()
    report = validator.validate(ctx)
    assert isinstance(report, ValidationReport)
    assert report.errors_count == 0
    assert report.score == 100
