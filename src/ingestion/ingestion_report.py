import pandas as pd
import json
from dataclasses import dataclass, field, asdict
from typing import Mapping

class IngestionError(Exception):
    """Excepción base para errores del Ingestion Engine."""
    pass

@dataclass(frozen=True, slots=True)
class IngestionReport:
    """Diagnóstico detallado del proceso de ingesta tras todos los escaneos."""
    archivo: str
    filas: int
    columnas: int
    hojas: int
    duplicados: int
    valores_nulos: int
    tiempo: str
    
    def to_json(self, filepath: str = "ingestion_report.json") -> None:
        """Exporta el reporte de ingesta a formato JSON."""
        data = asdict(self)
        # Rename keys to be more readable if needed, but python fields already match requested loosely
        output_data = {
            "Archivo": self.archivo,
            "Filas": self.filas,
            "Columnas": self.columnas,
            "Hojas": self.hojas,
            "Duplicados": self.duplicados,
            "Valores nulos": self.valores_nulos,
            "Tiempo": self.tiempo
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)

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

