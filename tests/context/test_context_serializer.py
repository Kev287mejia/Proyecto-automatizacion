import pytest
import json
from pathlib import Path
from src.context.context_models import AgentContext, ProjectContext
from src.context.context_serializer import ContextSerializer

def test_serializer_to_json(tmp_path):
    ctx = AgentContext(project=ProjectContext(project_name="Test Project"))
    serializer = ContextSerializer()
    
    out_file = tmp_path / "context.json"
    serializer.to_json(ctx, out_file)
    
    assert out_file.exists()
    data = json.loads(out_file.read_text(encoding='utf-8'))
    assert data["project"]["project_name"] == "Test Project"

def test_serializer_to_debug_json(tmp_path):
    ctx = AgentContext(project=ProjectContext(project_name="Debug Project"))
    serializer = ContextSerializer()
    
    out_file = tmp_path / "context.debug.json"
    serializer.to_debug_json(ctx, out_file)
    
    assert out_file.exists()
    content = out_file.read_text(encoding='utf-8')
    assert "Debug Project" in content
    assert "\n" in content  # it's pretty printed
