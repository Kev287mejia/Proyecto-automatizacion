import pytest
from dataclasses import FrozenInstanceError
from src.context.context_models import ProjectContext, AgentContext

def test_project_context_is_immutable():
    ctx = ProjectContext(project_name="Test")
    with pytest.raises(FrozenInstanceError):
        ctx.project_name = "Mutated"

def test_agent_context_instantiation():
    ctx = AgentContext()
    assert ctx.project.project_name == "Desconocido"
