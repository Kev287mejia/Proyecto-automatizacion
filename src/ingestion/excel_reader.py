import pandas as pd
from pathlib import Path
from typing import Union, Dict
import logging
from .ingestion_report import IngestionError

class ExcelReader:
    """
    Responsabilidad: Cargar el binario de Excel en memoria pura.
    No toma decisiones de hojas ni limpia cabeceras.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def read_workbook(self, filepath: Union[str, Path]) -> Dict[str, pd.DataFrame]:
        """
        Lee el archivo completo, devolviendo un diccionario {nombre_hoja: DataFrame_crudo}.
        Todo se lee como string para preservar integridad absoluta de IDs o fechas.
        """
        path = Path(filepath)
        if not path.is_file():
            raise IngestionError(f"El archivo Excel no existe: {path}")

        try:
            self.logger.info(f"Cargando workbook completo en memoria desde: {path}")
            # sheet_name=None lee TODAS las hojas
            wb = pd.read_excel(path, sheet_name=None, dtype=str)
            return wb
        except Exception as e:
            self.logger.error(f"Fallo al leer el archivo Excel: {e}")
            raise IngestionError(f"Error procesando el Excel {path}: {str(e)}") from e
