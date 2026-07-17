import pandas as pd
import logging
from typing import List
from .ingestion_report import IngestionError

class IngestionValidator:
    """
    Responsabilidad: Ejecutar validaciones duras sobre los datos mapeados 
    antes de sellar la SSOT.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def validate(self, df: pd.DataFrame) -> List[str]:
        """
        Devuelve una lista de advertencias. 
        Si encuentra errores críticos que corrompen el dominio, lanza IngestionError.
        """
        self.logger.info("Validando integridad referencial (SSOT)...")
        warnings = []

        if df.empty:
            raise IngestionError("El conjunto de datos mapeado está completamente vacío.")

        if len(df.columns) == 0:
            raise IngestionError("No se detectaron columnas en el mapeo final.")

        # Verificar exceso de nulos
        null_ratios = df.isna().mean()
        for col, ratio in null_ratios.items():
            if ratio > 0.5:
                warn_msg = f"Columna '{col}' excede 50% de valores nulos ({(ratio*100):.1f}%)."
                self.logger.warning(warn_msg)
                warnings.append(warn_msg)
            if ratio == 1.0:
                raise IngestionError(f"Columna '{col}' está 100% vacía, violando integridad.")

        self.logger.info("Validación SSOT exitosa.")
        return warnings
