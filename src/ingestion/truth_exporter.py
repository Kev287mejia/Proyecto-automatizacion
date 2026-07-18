import json
import logging
from pathlib import Path
from typing import Union
from .ingestion_report import SSOTContext, IngestionError

class TruthExporter:
    """
    Responsabilidad: Serializar la Single Source of Truth (SSOT) hacia un 
    archivo físico JSON para que otros motores puedan consumirla.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def export(self, context: SSOTContext, destination_dir: Union[str, Path]) -> Path:
        """
        Exporta el DataFrame de SSOT a un archivo JSON estructurado (normalized_truth.json)
        y opcionalmente un archivo de reporte de auditoría (ingestion_report.json).
        """
        dest_path = Path(destination_dir)
        
        if not dest_path.exists():
            self.logger.info(f"Creando directorio de destino: {dest_path}")
            dest_path.mkdir(parents=True, exist_ok=True)
            
        truth_file_path = dest_path / "normalized_truth.json"
        report_file_path = dest_path / "ingestion_report.json"
        
        self.logger.info(f"Exportando SSOT a: {truth_file_path}")
        
        try:
            # Exportar datos a JSON (orient="records" es ideal para APIs y otros motores)
            # Para manejar datetime types correctamente y evitar que el JSON falle al exportar Pandas:
            context.data.assign(**context.data.select_dtypes(['datetime', 'datetimetz']).astype(str)).to_json(truth_file_path, orient="records", force_ascii=False, indent=2)
            
            # Exportar reporte de ingesta para trazabilidad
            context.report.to_json(str(report_file_path))
                
            self.logger.info(f"Reporte de ingesta exportado a: {report_file_path}")
            
            return truth_file_path
            
        except Exception as e:
            self.logger.error(f"Fallo al exportar el SSOT a JSON: {e}")
            raise IngestionError(f"Error escribiendo normalized_truth.json: {str(e)}") from e
