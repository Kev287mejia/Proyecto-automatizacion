import pandas as pd
import logging

class RowNormalizer:
    """
    Responsabilidad: Transformar las filas (eliminar vacías, estandarizar texto).
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ejecuta sanitización a nivel de fila y celda.
        """
        self.logger.info("Normalizando filas y limpiando valores...")
        
        # Eliminar filas completamente vacías
        initial_len = len(df)
        df = df.dropna(how='all')
        if len(df) < initial_len:
            self.logger.info(f"Purgadas {initial_len - len(df)} filas vacías.")

        # Limpiar strings (strip)
        for col in df.columns:
            if df[col].dtype == object or isinstance(df[col].dtype, pd.StringDtype):
                df[col] = df[col].apply(lambda x: str(x).strip() if pd.notna(x) else x)
        
        # Consolidar inferencia óptima de pandas
        df = df.convert_dtypes()

        self.logger.info("Normalización de filas finalizada.")
        return df
