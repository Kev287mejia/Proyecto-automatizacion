import json
import logging
from pathlib import Path
from dataclasses import asdict
from typing import Union, Any
from .context_models import AgentContext

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

class ContextSerializer:
    """Responsable de serializar el AgentContext para auditoría y depuración."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def _to_dict(self, context: AgentContext) -> dict[str, Any]:
        """Convierte el contexto inmutable en un diccionario estándar."""
        # asdict maneja las dataclasses, tuplas y mappings automáticamente
        return asdict(context)

    def to_json(self, context: AgentContext, output_path: Union[str, Path], pretty: bool = False) -> Path:
        """Exporta el contexto a formato JSON."""
        path = Path(output_path)
        data = self._to_dict(context)
        
        with path.open('w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=4, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)
                
        self.logger.info(f"Contexto serializado en JSON: {path}")
        return path

    def to_yaml(self, context: AgentContext, output_path: Union[str, Path]) -> Path:
        """Exporta el contexto a formato YAML si PyYAML está instalado."""
        if not HAS_YAML:
            self.logger.error("PyYAML no está instalado. Ejecuta 'pip install pyyaml'.")
            raise ImportError("PyYAML es requerido para exportar a YAML.")
            
        path = Path(output_path)
        data = self._to_dict(context)
        
        with path.open('w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            
        self.logger.info(f"Contexto serializado en YAML: {path}")
        return path

    def to_debug_json(self, context: AgentContext, output_path: Union[str, Path]) -> Path:
        """Exporta un JSON indentado y listo para depuración (equivalente a to_json pretty=True)."""
        return self.to_json(context, output_path, pretty=True)
