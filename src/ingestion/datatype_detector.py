import pandas as pd
import logging
from typing import Dict

class DatatypeDetector:
    """
    Responsabilidad: Inferir los tipos de datos reales de cada columna
    a partir del contenido crudo.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def infer(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Calcula una heurística del tipo de dato subyacente.
        (Ej: string, numeric, date)
        """
        self.logger.info("Infiriendo tipos de datos de las columnas...")
        inferred = {}
        for col in df.columns:
            # Heurística simple: intentamos convertir a numérico. 
            # Si más del 80% es numérico, lo marcamos como 'numeric'.
            s_notna = df[col].dropna()
            if len(s_notna) == 0:
                inferred[col] = "unknown"
                continue
                
            is_num_ratio = s_notna.astype(str).str.isnumeric().mean()
            if is_num_ratio > 0.8:
                inferred[col] = "numeric"
            else:
                inferred[col] = "string"
                
        self.logger.debug(f"Tipos inferidos: {inferred}")
        return inferred
