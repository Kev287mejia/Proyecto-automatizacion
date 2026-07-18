import pandas as pd
import logging
from typing import Dict
import re

class DatatypeDetector:
    """
    Fase 5: Data Type Detector
    Responsabilidad: Inferir los tipos de datos reales de cada columna
    a partir del contenido crudo, sin depender del nombre de la columna.
    Tipos: Vacío, Booleano, Moneda, Porcentaje, Fecha, Número, Categoría, Texto.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        # Set de valores que solemos interpretar como booleanos
        self.bool_set = {'si', 'sí', 'no', 'true', 'false', 'v', 'f', '1', '0', '1.0', '0.0', 'verdadero', 'falso'}
        self.currency_regex = re.compile(r'[\$€£Q¥]\s*\d+|\d+\s*[\$€£Q¥]')

    def infer(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Calcula una heurística del tipo de dato subyacente para cada columna.
        """
        self.logger.info("Fase 5: Infiriendo tipos de datos lógicos por contenido...")
        inferred = {}
        for col in df.columns:
            inferred[col] = self._detect_type(df[col])
        self.logger.debug(f"Tipos inferidos: {inferred}")
        return inferred

    def _detect_type(self, series: pd.Series) -> str:
        s_notna = series.dropna()
        if len(s_notna) == 0:
            return "Vacío"
            
        total_valid = len(s_notna)
        s_str = s_notna.astype(str).str.strip()
        
        # 1. Booleano
        s_lower = s_str.str.lower()
        bool_ratio = s_lower.isin(self.bool_set).sum() / total_valid
        if bool_ratio >= 0.95:
            return "Booleano"
            
        # 2. Moneda
        currency_ratio = s_str.str.contains(self.currency_regex, regex=True).sum() / total_valid
        if currency_ratio >= 0.8:
            return "Moneda"
            
        # 3. Porcentaje
        percent_ratio = s_str.str.contains('%').sum() / total_valid
        if percent_ratio >= 0.8:
            return "Porcentaje"
            
        # 4. Fecha
        # Excluimos cadenas puramente numéricas para no confundir IDs (ej. 20240101) con fechas
        # A menos que tengan un separador o formato reconocible.
        non_numeric_str = s_str[~s_str.str.isdigit()]
        if len(non_numeric_str) > 0:
            # pd.to_datetime con format mixed suele ser bueno, pero genera warnings, así que confiamos en parseo libre
            parsed_dates = pd.to_datetime(non_numeric_str, errors='coerce')
            date_ratio = parsed_dates.notna().sum() / total_valid
            if date_ratio >= 0.8:
                return "Fecha"
                
        # 5. Número
        # Intentamos cast a float removiendo comas de miles
        def is_numeric(val):
            try:
                float(str(val).replace(',', ''))
                return True
            except ValueError:
                return False
                
        num_ratio = s_str.apply(is_numeric).sum() / total_valid
        if num_ratio >= 0.8:
            return "Número"
            
        # 6. Categoría
        unique_count = s_str.nunique()
        unique_ratio = unique_count / total_valid
        if unique_count <= 15 or (total_valid > 100 and unique_ratio < 0.05):
            return "Categoría"
            
        # 7. Texto (Fallback)
        return "Texto"
