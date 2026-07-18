import pandas as pd
import logging
import time
from typing import List, Optional
from .ingestion_report import IngestionError
from .models import ValidationReport

class IngestionValidator:
    """
    Responsabilidad: Ejecutar validaciones duras sobre los datos mapeados 
    antes de sellar la SSOT.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def validate(self, df: pd.DataFrame, mandatory_columns: Optional[List[str]] = None) -> ValidationReport:
        """
        Ejecuta múltiples validaciones de calidad de datos.
        """
        self.logger.info("Validando integridad referencial (SSOT)...")
        start_time = time.time()
        
        errores = []
        warnings = []
        score = 100.0

        if df.empty:
            errores.append("El conjunto de datos mapeado está completamente vacío.")
            score = 0.0
            return ValidationReport(errores=errores, warnings=warnings, score=score, duracion=time.time() - start_time)

        if len(df.columns) == 0:
            errores.append("No se detectaron columnas en el mapeo final.")
            score = 0.0
            return ValidationReport(errores=errores, warnings=warnings, score=score, duracion=time.time() - start_time)

        # 1. Columnas vacías
        for col in df.columns:
            if df[col].isna().all():
                errores.append(f"La columna '{col}' está completamente vacía.")
                score -= 10

        # 2. Filas duplicadas
        duplicados = df.duplicated().sum()
        if duplicados > 0:
            errores.append(f"Se encontraron {duplicados} filas duplicadas.")
            score -= 10

        # 3. Datos nulos
        null_ratios = df.isna().mean()
        for col, ratio in null_ratios.items():
            if 0 < ratio < 1.0:
                warnings.append(f"La columna '{col}' tiene un {(ratio*100):.1f}% de valores nulos.")
                score -= 2

        # 4. Edades negativas
        for col in df.columns:
            if "edad" in col.lower():
                try:
                    negativas = (pd.to_numeric(df[col], errors='coerce') < 0).sum()
                    if negativas > 0:
                        errores.append(f"Se encontraron {negativas} edades negativas en la columna '{col}'.")
                        score -= 15
                except Exception:
                    pass

        # 5. Fechas inválidas (asumiendo formato datetime o string)
        for col in df.select_dtypes(include=['datetime64', 'datetimetz']).columns:
            invalidas = df[col].isna().sum() - (df[col].astype(object) == pd.NaT).sum()
            # Alternativamente, si hay fechas fuera de un rango aceptable
            # Simplemente validamos si hay fechas que no se pudieron parsear si eran strings
            pass
            
        for col in df.columns:
            if "fecha" in col.lower():
                # Tratamos de ver si hay NaT después de forzar to_datetime (invalidas)
                parsed = pd.to_datetime(df[col], errors='coerce')
                original_non_null = df[col].dropna().shape[0]
                parsed_valid = parsed.dropna().shape[0]
                if original_non_null > parsed_valid:
                    invalid_count = original_non_null - parsed_valid
                    errores.append(f"Se encontraron {invalid_count} fechas inválidas en la columna '{col}'.")
                    score -= 10

        # 6. Columnas obligatorias
        if mandatory_columns:
            missing = [col for col in mandatory_columns if col not in df.columns]
            if missing:
                errores.append(f"Faltan columnas obligatorias: {', '.join(missing)}.")
                score -= 20 * len(missing)

        # 7. Porcentajes fuera de rango
        for col in df.columns:
            if "porcentaje" in col.lower() or "%" in col:
                try:
                    num_series = pd.to_numeric(df[col], errors='coerce').dropna()
                    if not num_series.empty:
                        # Asumimos rango 0-100
                        fuera_rango = ((num_series < 0) | (num_series > 100)).sum()
                        if fuera_rango > 0:
                            errores.append(f"Se encontraron {fuera_rango} porcentajes fuera de rango (0-100) en la columna '{col}'.")
                            score -= 10
                except Exception:
                    pass

        score = max(0.0, score)
        duracion = time.time() - start_time
        
        self.logger.info(f"Validación finalizada con score {score:.1f}. {len(errores)} errores, {len(warnings)} warnings.")

        return ValidationReport(errores=errores, warnings=warnings, score=score, duracion=duracion)
