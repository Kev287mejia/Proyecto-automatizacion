import pytest
import json
from pathlib import Path
from src.context.context_loader import ContextLoader, ContextResolutionError

def test_loader_success(tmp_path):
    blueprint_file = tmp_path / "blueprint.json"
    blueprint_file.write_text(json.dumps({"project": {"project_name": "Test"}}))
    
    loader = ContextLoader()
    data = loader.load_blueprint(blueprint_file)
    assert data["project"]["project_name"] == "Test"

def test_loader_file_not_found():
    loader = ContextLoader()
    with pytest.raises(ContextResolutionError):
        loader.load_blueprint(Path("non_existent.json"))

def test_loader_invalid_json(tmp_path):
    blueprint_file = tmp_path / "blueprint.json"
    blueprint_file.write_text("invalid json")
    
    loader = ContextLoader()
    with pytest.raises(ContextResolutionError):
        loader.load_blueprint(blueprint_file)
