import pandas as pd
import logging

class HeaderDetector:
    """
    Responsabilidad: Encontrar la fila real que contiene las cabeceras.
    Elimina filas superiores "basura" (títulos, logos) y purga columnas 
    fantasmas (Unnamed).
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def detect(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        En esta primera versión, asumiremos que pandas encontró la cabecera en la fila 0.
        Sin embargo, eliminaremos columnas "fantasmas" y espacios en los nombres.
        """
        self.logger.info("Detectando y limpiando cabeceras...")
        
        # 1. Purga de columnas fantasmas completamente vacías
        cols_to_drop = [col for col in df.columns if str(col).startswith("Unnamed") and df[col].isna().all()]
        if cols_to_drop:
            self.logger.debug(f"Purgando columnas fantasmas: {cols_to_drop}")
            df = df.drop(columns=cols_to_drop)

        # 2. Limpieza de nombres de cabecera
        df.columns = [str(col).strip().lower() for col in df.columns]
        
        self.logger.info(f"Cabeceras limpias detectadas: {len(df.columns)} columnas.")
        return df
