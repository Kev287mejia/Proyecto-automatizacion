import pandas as pd
from dataclasses import dataclass, field
from typing import Mapping

class IngestionError(Exception):
    """Excepción base para errores del Ingestion Engine."""
    pass

@dataclass(frozen=True, slots=True)
class IngestionReport:
    """Diagnóstico detallado del proceso de ingesta tras todos los escaneos."""
    rows_read: int
    columns_detected: tuple[str, ...]
    null_counts: Mapping[str, int]
    dtypes_inferred: Mapping[str, str]
    duration_ms: float
    warnings: tuple[str, ...] = field(default_factory=tuple)

@dataclass(frozen=True, slots=True)
class SSOTContext:
    """
    Single Source of Truth (SSOT).
    Contenedor inmutable de los datos limpios y mapeados al dominio.
    """
    data: pd.DataFrame
    report: IngestionReport
    
    @property
    def is_empty(self) -> bool:
        return self.data.empty
