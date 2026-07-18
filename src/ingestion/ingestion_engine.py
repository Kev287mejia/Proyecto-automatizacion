import time
import logging
from pathlib import Path
from types import MappingProxyType

from src.context.context_models import AgentContext
from .ingestion_report import SSOTContext, IngestionReport, IngestionError
from .excel_reader import ExcelReader
from .workbook_analyzer import WorkbookAnalyzer
from .worksheet_reader import WorksheetReader
from .header_detector import HeaderDetector
from .datatype_detector import DatatypeDetector
from .row_normalizer import RowNormalizer
from .entity_mapper import EntityMapper
from .ingestion_validator import IngestionValidator
from .truth_exporter import TruthExporter

class IngestionEngine:
    """
    Fachada (Facade) que orquesta todo el pipeline de Ingesta Enterprise.
    """

    def __init__(self):
        # Configurar file handler para asegurar logs/ingestion.log
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        
        # Evitar duplicar handlers si la clase se instancia múltiple veces
        if not any(isinstance(h, logging.FileHandler) and "ingestion.log" in h.baseFilename for h in self.logger.handlers):
            fh = logging.FileHandler(log_dir / "ingestion.log", encoding="utf-8")
            fh.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
        self.reader = ExcelReader()
        self.workbook_analyzer = WorkbookAnalyzer()
        self.worksheet_reader = WorksheetReader()
        self.header_detector = HeaderDetector()
        self.datatype_detector = DatatypeDetector()
        self.row_normalizer = RowNormalizer()
        self.mapper = EntityMapper()
        self.validator = IngestionValidator()
        self.exporter = TruthExporter()

    def run(self, context: AgentContext, output_dir: str = None) -> SSOTContext:
        """
        Ejecuta el pipeline completo y altamente granular de Ingesta.
        """
        start_time = time.time()
        self.logger.info("Iniciando Enterprise Ingestion Engine Pipeline...")

        try:
            raw_path = context.excel.raw_data_path
            
            # Fase 1: Leer archivo físico completo
            workbook = self.reader.read_workbook(raw_path)
            
            # Fase 2: Analizar workbook y extraer metadata de estructura
            workbook_context = self.workbook_analyzer.analyze(raw_path, workbook)
            sheet_name = workbook_context.metadata.target_sheet
            
            # Fase 3: Extraer data de la hoja seleccionada
            worksheet_data = self.worksheet_reader.read(workbook, sheet_name)
            
            # Fase 4: Detectar y limpiar cabeceras
            df_headed = self.header_detector.detect(worksheet_data.valores)
            
            # Fase 5: Inferir tipos lógicos subyacentes
            inferred_types = self.datatype_detector.infer(df_headed)
            
            # Fase 6: Normalizar filas (vacías, strings sucios, auto-cast)
            df_normalized = self.row_normalizer.normalize(df_headed)
            
            # Fase 7: Mapear a SSOT
            df_mapped = self.mapper.map_to_ssot(df_normalized)
            
            # Fase 8: Validar integridad de negocio
            validation_report = self.validator.validate(df_mapped)
            
            # Fase 9: Reporte de ingesta
            duration = time.time() - start_time
            null_counts = df_mapped.isna().sum().sum()
            duplicados = df_mapped.duplicated().sum()
            
            report = IngestionReport(
                archivo=Path(raw_path).name,
                filas=len(df_mapped),
                columnas=len(df_mapped.columns),
                hojas=workbook_context.statistics.sheet_count,
                duplicados=int(duplicados),
                valores_nulos=int(null_counts),
                tiempo=f"{duration:.2f} s"
            )
            
            # Generar el archivo ingestion_report.json
            if not output_dir:
                proj_path = context.runtime.project_path if context.runtime.project_path else "."
                output_dir = Path(proj_path) / "output"
            
            ssot = SSOTContext(data=df_mapped, report=report)
            self.logger.info(f"Ingesta exitosa: {report.filas} filas SSOT selladas en {report.tiempo}")
            
            # Fase 10: Exportar a JSON (Cierre de Ingestion Engine)
            self.exporter.export(ssot, destination_dir=output_dir)
            
            return ssot

        except Exception as e:
            self.logger.error(f"Fallo catastrófico en la ingesta: {e}")
            raise IngestionError(f"Fallo en pipeline de ingesta: {str(e)}") from e
