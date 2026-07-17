import json
import logging
from typing import Dict, Any, Union
from pathlib import Path

class ContextResolutionError(Exception):
    """Excepción lanzada si el blueprint.json es inaccesible o corrupto."""
    pass

class ContextLoader:
    """Responsable exclusivamente de la lectura del archivo blueprint.json y su conversión a objetos Python."""
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    def load_blueprint(self, blueprint_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Verifica la existencia del archivo, lo lee y lo convierte a un diccionario Python.
        No valida el contenido ni lo modifica.
        """
        path = Path(blueprint_path)
        
        if not path.exists() or not path.is_file():
            self.logger.error(f"El archivo Blueprint no existe o no es un archivo en: {path}")
            raise ContextResolutionError(f"No se encontró el Blueprint: {path}")

        try:
            with path.open('r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            self.logger.error(f"Error al decodificar el Blueprint JSON: {e}")
            raise ContextResolutionError(f"Formato JSON inválido en el Blueprint: {e}")
        except Exception as e:
            self.logger.error(f"Error inesperado al leer el Blueprint: {e}")
            raise ContextResolutionError(f"Error al leer el Blueprint: {e}")

