from dataclasses import dataclass, field
from typing import Tuple
import pandas as pd



@dataclass(frozen=True, slots=True)
class WorksheetData:
    """
    Datos extraídos crudos de una hoja de cálculo, generado por Fase 3.
    """
    nombre: str
    filas: int
    columnas: int
    valores: pd.DataFrame

@dataclass(frozen=True, slots=True)
class ValidationReport:
    """
    Reporte de validación generado por Fase 8.
    """
    errores: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    score: float = 100.0
    duracion: float = 0.0
