import pandas as pd
import logging
import unicodedata

class EntityMapper:
    """
    Responsabilidad: Traducir el DataFrame genérico al formato canónico (SSOT).
    Estandariza strings, remueve acentos y unifica capitalización para evitar 
    inconsistencias por errores de tipeo.
    Realiza normalización semántica (ej. F, Fem, MUJER -> Femenino).
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        # Diccionario de mapeo semántico. Las claves deben estar normalizadas
        # (mayúsculas y sin acentos) ya que se aplican después de _normalize_string
        self.semantic_mapping = {
            # Sexo
            "F": "Femenino",
            "FEM": "Femenino",
            "FEMENINA": "Femenino",
            "MUJER": "Femenino",
            "M": "Masculino",
            "MASC": "Masculino",
            "MASCULINO": "Masculino",
            "VARON": "Masculino",
            "HOMBRE": "Masculino",
            
            # Etnias
            "MISKITO": "Miskitu",
            "MISKITA": "Miskitu",
            "MISKITU": "Miskitu",
            "MAYANGNA": "Mayangna",
            "SUMU": "Mayangna",
            "MESTIZO": "Mestizo",
            "MESTIZA": "Mestizo",
            "CREOLE": "Creole",
            "KRIOL": "Creole",
            "AFRODESCENDIENTE": "Afrodescendiente",
            
            # Carreras
            "ING SISTEMAS": "Ingeniería en Sistemas",
            "INGENIERIA EN SISTEMAS": "Ingeniería en Sistemas",
            "SISTEMAS": "Ingeniería en Sistemas",
            "ADMINISTRACION": "Administración de Empresas",
            "ADMINISTRACION DE EMPRESAS": "Administración de Empresas",
            "ADMON": "Administración de Empresas",
            "CONTABILIDAD": "Contaduría Pública",
            "CONTADURIA PUBLICA": "Contaduría Pública",
            "DERECHO": "Derecho",
            "MEDICINA": "Medicina",
            
            # Departamentos
            "MGA": "Managua",
            "MANAGUA": "Managua",
            "LEON": "León",
            "CHINANDEGA": "Chinandega",
            "MATAGALPA": "Matagalpa",
            "RACCN": "RACCN",
            "R.A.C.C.N.": "RACCN",
            "COSTA CARIBE NORTE": "RACCN",
            "RACCS": "RACCS",
            "R.A.C.C.S.": "RACCS",
            "COSTA CARIBE SUR": "RACCS",
            
            # Municipios
            "BILWI": "Puerto Cabezas",
            "PUERTO CABEZAS": "Puerto Cabezas",
            "PTO CABEZAS": "Puerto Cabezas",
            "WASPAM": "Waspam",
            "PRINZAPOLKA": "Prinzapolka",
            "ROSITA": "Rosita",
            "BONANZA": "Bonanza",
            "SIUNA": "Siuna",
            
            # Eventos
            "FERIA": "Feria de Salud",
            "FERIA DE LA SALUD": "Feria de Salud",
            "FERIA DE SALUD": "Feria de Salud",
            "JORNADA MEDICA": "Jornada Médica",
            "JORNADA": "Jornada Médica",
            "CAPACITACION": "Capacitación",
            "TALLER": "Taller",
            "CHARLA": "Charla"
        }

    def _normalize_string(self, text: str) -> str:
        """Remueve acentos, convierte a mayúsculas y quita espacios extra."""
        if pd.isna(text) or not isinstance(text, str):
            return text
        
        text = text.strip().upper()
        # Remover acentos/diacríticos
        text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
        return text

    def map_to_ssot(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Estandariza cualquier aspecto final para que coincida con el dominio SSOT.
        Normaliza columnas de tipo string para unificar valores y aplica mapeo semántico.
        """
        self.logger.info("Mapeando DataFrame normalizado a Entidad SSOT y unificando valores...")
        
        # Mapeo y limpieza de valores string en todo el dataframe
        for col in df.columns:
            if df[col].dtype == object or isinstance(df[col].dtype, pd.StringDtype):
                # 1. Normalización básica (mayúsculas, sin acentos, sin espacios extra)
                df[col] = df[col].apply(self._normalize_string)
                # 2. Normalización semántica (mapeo a términos canónicos)
                df[col] = df[col].replace(self.semantic_mapping)
        
        self.logger.info("Mapeo a SSOT completado.")
        return df
