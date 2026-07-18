import pandas as pd
import logging
import unicodedata

class HeaderDetector:
    """
    Fase 4: Header Detector
    Descubre automáticamente las cabeceras estándar (Nombre, Edad, Sexo, etc.),
    tolerando cambios de posición, mayúsculas/minúsculas y alias comunes (ej. Genero -> Sexo).
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Diccionario de alias (en minúsculas y sin acentos) mapeando al nombre canónico
        self.aliases = {
            'nombre': 'Nombre',
            'nombres': 'Nombre',
            'nombre completo': 'Nombre',
            'edad': 'Edad',
            'sexo': 'Sexo',
            'genero': 'Sexo',
            'municipio': 'Municipio',
            'departamento': 'Departamento',
            'carrera': 'Carrera',
            'programa': 'Programa',
            'fecha': 'Fecha',
            'evento': 'Evento'
        }

    def _normalize_string(self, text: str) -> str:
        """Remueve acentos, convierte a minúsculas y quita espacios extra."""
        if pd.isna(text) or not isinstance(text, str):
            return ""
        text = text.strip().lower()
        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

    def detect(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Escanea las filas para encontrar las cabeceras.
        Limpia columnas vacías y renombra a los campos estándar si detecta alias.
        """
        self.logger.info("Fase 4: Detectando y normalizando cabeceras...")
        
        if df.empty:
            return df

        # Buscar la fila de cabecera en las primeras 20 filas
        search_limit = min(20, len(df))
        best_row_idx = -1
        
        # Consideramos la densidad como el número de celdas no nulas y que no sean "Unnamed: X"
        def calculate_density(row: pd.Series) -> int:
            valid_cells = 0
            for val in row:
                if pd.notna(val) and not (isinstance(val, str) and str(val).startswith("Unnamed")):
                    valid_cells += 1
            return valid_cells

        current_cols = pd.Series(df.columns)
        max_density = calculate_density(current_cols)

        for i in range(search_limit):
            row_density = calculate_density(df.iloc[i])
            if row_density > max_density:
                max_density = row_density
                best_row_idx = i

        self.logger.info(f"Fila base de cabeceras en índice: {best_row_idx} (Densidad: {max_density})")

        if best_row_idx >= 0:
            new_header = df.iloc[best_row_idx].copy()
            new_header = new_header.fillna(pd.Series([f"col_{j}" for j in range(len(new_header))]))
            df.columns = new_header
            df = df.iloc[best_row_idx + 1:].reset_index(drop=True)
            
        # 1. Purga de columnas fantasmas
        cols_to_drop = []
        for col in df.columns:
            if (str(col).startswith("Unnamed") or str(col).startswith("col_") or pd.isna(col)) and df[col].isna().all():
                cols_to_drop.append(col)
                
        if cols_to_drop:
            self.logger.debug(f"Purgando columnas fantasmas: {cols_to_drop}")
            df = df.drop(columns=cols_to_drop)

        # 2. Renombrar cabeceras usando alias
        new_columns = []
        detected_canonical = []
        
        for col in df.columns:
            norm_col = self._normalize_string(str(col))
            if norm_col in self.aliases:
                canonical_name = self.aliases[norm_col]
                new_columns.append(canonical_name)
                detected_canonical.append(canonical_name)
            else:
                new_columns.append(str(col).strip().lower())
                
        df.columns = new_columns
        
        self.logger.info(f"Cabeceras canónicas detectadas: {detected_canonical}")
        return df
