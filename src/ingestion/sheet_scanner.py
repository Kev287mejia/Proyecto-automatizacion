import pandas as pd
from typing import Dict
import logging
from .ingestion_report import IngestionError

class SheetScanner:
    """
    Responsabilidad: Inspeccionar las hojas disponibles y seleccionar/extraer 
    la que contiene la data de interés según políticas (ej. la primera hoja, 
    o una hoja llamada 'Data').
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def scan_and_select(self, workbook: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Escanea el workbook. Por defecto en esta iteración, tomamos la primera hoja.
        Se puede extender para buscar hojas por patrones regex.
        """
        self.logger.info("Escaneando hojas del workbook...")
        if not workbook:
            raise IngestionError("El workbook está completamente vacío (no tiene hojas).")

        sheets = list(workbook.keys())
        self.logger.debug(f"Hojas encontradas: {sheets}")
        
        target_sheet = sheets[0]
        self.logger.info(f"Seleccionando hoja objetivo: '{target_sheet}'")
        
        return workbook[target_sheet]
