import pandas as pd
import logging

class RowNormalizer:
    """
    Fase 6: Row Normalizer
    Responsabilidad: Transformar las filas y convertir la estructura de columnas 
    en un formato uniforme (claves en minúscula).
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ejecuta sanitización a nivel de fila y celda.
        """
        self.logger.info("Normalizando filas y limpiando valores...")
        
        if df.empty:
            return df
            
        # Eliminar filas completamente vacías
        initial_len = len(df)
        df = df.dropna(how='all').copy()
        if len(df) < initial_len:
            self.logger.info(f"Purgadas {initial_len - len(df)} filas vacías.")

        # Estandarizar nombres de columnas (minúsculas, reemplazar espacios) para que 
        # al exportar a JSON los keys tengan formato uniforme, ej: {"nombre": "...", "edad": 21}
        df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]

        # Limpiar strings (strip)
        for col in df.columns:
            if df[col].dtype == object or isinstance(df[col].dtype, pd.StringDtype):
                df[col] = df[col].apply(lambda x: str(x).strip() if pd.notna(x) else x)
        
        # Consolidar inferencia óptima de pandas
        df = df.convert_dtypes()

        self.logger.info("Normalización de filas finalizada.")
        return df

    def to_records(self, df: pd.DataFrame) -> list:
        """
        Convierte cada fila en una estructura uniforme de diccionario.
        Ejemplo: {"nombre": "...", "sexo": "Femenino", "edad": 21}
        """
        # Reemplazamos <NA> de pandas con None para diccionarios puros de Python
        df_clean = df.replace({pd.NA: None})
        # Tambien convertimos float NaN a None
        df_clean = df_clean.where(pd.notnull(df_clean), None)
        return df_clean.to_dict(orient="records")
