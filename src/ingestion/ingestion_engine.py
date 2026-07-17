import time
import logging
from types import MappingProxyType

from src.context.context_models import AgentContext
from .ingestion_report import SSOTContext, IngestionReport, IngestionError
from .excel_reader import ExcelReader
from .sheet_scanner import SheetScanner
from .header_detector import HeaderDetector
from .datatype_detector import DatatypeDetector
from .row_normalizer import RowNormalizer
from .entity_mapper import EntityMapper
from .ingestion_validator import IngestionValidator

class IngestionEngine:
    """
    Fachada (Facade) que orquesta todo el pipeline de Ingesta Enterprise.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.reader = ExcelReader()
        self.scanner = SheetScanner()
        self.header_detector = HeaderDetector()
        self.datatype_detector = DatatypeDetector()
        self.row_normalizer = RowNormalizer()
        self.mapper = EntityMapper()
        self.validator = IngestionValidator()

    def run(self, context: AgentContext) -> SSOTContext:
        """
        Ejecuta el pipeline completo y altamente granular de Ingesta.
        """
        start_time = time.time()
        self.logger.info("Iniciando Enterprise Ingestion Engine Pipeline...")

        try:
            raw_path = context.excel.raw_data_path
            
            # 1. Leer archivo físico completo
            workbook = self.reader.read_workbook(raw_path)
            
            # 2. Escanear y seleccionar hoja
            df_raw = self.scanner.scan_and_select(workbook)
            
            # 3. Detectar y limpiar cabeceras
            df_headed = self.header_detector.detect(df_raw)
            
            # 4. Inferir tipos lógicos subyacentes
            inferred_types = self.datatype_detector.infer(df_headed)
            
            # 5. Normalizar filas (vacías, strings sucios, auto-cast)
            df_normalized = self.row_normalizer.normalize(df_headed)
            
            # 6. Mapear a SSOT
            df_mapped = self.mapper.map_to_ssot(df_normalized)
            
            # 7. Validar integridad de negocio
            warnings = self.validator.validate(df_mapped)
            
            # 8. Reporte y cierre
            duration = (time.time() - start_time) * 1000
            null_counts = df_mapped.isna().sum().to_dict()
            
            report = IngestionReport(
                rows_read=len(df_mapped),
                columns_detected=tuple(df_mapped.columns.tolist()),
                null_counts=MappingProxyType(null_counts),
                dtypes_inferred=MappingProxyType(inferred_types),
                duration_ms=duration,
                warnings=tuple(warnings)
            )
            
            self.logger.info(f"Ingesta exitosa: {report.rows_read} filas SSOT selladas en {duration:.1f}ms")
            
            return SSOTContext(data=df_mapped, report=report)

        except Exception as e:
            self.logger.error(f"Fallo catastrófico en la ingesta: {e}")
            raise IngestionError(f"Fallo en pipeline de ingesta: {str(e)}") from e
