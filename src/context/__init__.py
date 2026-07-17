import inspect
import hashlib
from pathlib import Path
from types import MappingProxyType
from typing import Union, Dict, Any, Type, TypeVar

from .context_models import (
    AgentContext, ProjectContext, WordContext, ExcelContext, 
    RuntimeContext, MetadataContext, DiagnosticsContext
)
from .context_loader import ContextLoader, ContextResolutionError
from .context_builder import ContextBuilder
from .context_validator import ContextValidator
from .context_serializer import ContextSerializer

T = TypeVar('T')

def _calculate_sha256(filepath: Union[str, Path]) -> str:
    """Calcula el hash SHA256 de un archivo para auditoría y trazabilidad."""
    path = Path(filepath)
    if not path.is_file():
        return ""
    hasher = hashlib.sha256()
    try:
        with path.open('rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return ""

def _instantiate_dataclass(cls: Type[T], data: Dict[str, Any]) -> T:
    """Helper para instanciar dataclasses ignorando claves no reconocidas e imponiendo inmutabilidad profunda."""
    if not isinstance(data, dict):
        data = {}
    valid_keys = {f.name for f in inspect.fields(cls)} if hasattr(cls, '__dataclass_fields__') else set()
    filtered_data = {}
    
    for k, v in data.items():
        if k in valid_keys:
            if isinstance(v, list):
                filtered_data[k] = tuple(v)
            elif isinstance(v, dict):
                filtered_data[k] = MappingProxyType(v)
            else:
                filtered_data[k] = v
                
    return cls(**filtered_data)

def build_context(blueprint_path: Union[str, Path]) -> AgentContext:
    """
    Orquestador principal del módulo Context.
    Flujo: Blueprint -> Loader -> Builder -> Validator -> AgentContext
    """
    # 1. Loader lee y parsea el archivo
    loader = ContextLoader()
    raw_dict = loader.load_blueprint(blueprint_path)

    # 1.5 Calculamos Fingerprints (SHA256) para auditoría empresarial
    metadata_dict = raw_dict.get('metadata', {})
    
    # Hash del blueprint mismo
    if not metadata_dict.get('blueprint_hash'):
        metadata_dict['blueprint_hash'] = _calculate_sha256(blueprint_path)
        
    # Hash de la plantilla Word
    word_template = raw_dict.get('word', {}).get('template_path')
    if word_template and not metadata_dict.get('template_hash'):
        metadata_dict['template_hash'] = _calculate_sha256(word_template)

    # Hash de la plantilla Excel
    excel_template = raw_dict.get('excel', {}).get('template_path')
    if excel_template and not metadata_dict.get('excel_hash'):
        metadata_dict['excel_hash'] = _calculate_sha256(excel_template)

    # 2. Builder ensambla los sub-contextos
    builder = ContextBuilder()
    
    # Instanciamos ignorando campos extras y forzando inmutabilidad en colecciones
    builder.set_project_context(_instantiate_dataclass(ProjectContext, raw_dict.get('project', {})))
    builder.set_runtime_context(_instantiate_dataclass(RuntimeContext, raw_dict.get('runtime', {})))
    builder.set_word_context(_instantiate_dataclass(WordContext, raw_dict.get('word', {})))
    builder.set_excel_context(_instantiate_dataclass(ExcelContext, raw_dict.get('excel', {})))
    builder.set_metadata_context(_instantiate_dataclass(MetadataContext, metadata_dict))
    builder.set_diagnostics_context(_instantiate_dataclass(DiagnosticsContext, raw_dict.get('diagnostics', {})))
    
    context = builder.build()

    # 3. Validator evalúa el contexto ensamblado y genera un reporte
    validator = ContextValidator()
    report = validator.validate(context)

    if report.errors_count > 0 or report.criticals_count > 0:
        error_msgs = "\n".join(f"- [{i.code}] {i.message}" for i in report.issues if i.severity.name in ("ERROR", "CRITICAL"))
        raise ContextResolutionError(
            f"Contexto inconsistente. Puntaje: {report.score}/100. Errores detectados:\n{error_msgs}"
        )

    return context

__all__ = [
    "build_context",
    "AgentContext",
    "ProjectContext",
    "WordContext",
    "ExcelContext",
    "RuntimeContext",
    "MetadataContext",
    "DiagnosticsContext",
    "ContextBuilder",
    "ContextValidator",
    "ContextSerializer",
    "ContextResolutionError"
]
