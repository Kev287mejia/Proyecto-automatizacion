"""
Interfaces y DTOs para el Ingestion Engine de SIEA.

Este módulo define los contratos (Protocolos y Clases Abstractas) y los 
objetos de transferencia de datos (DTOs) para mantener los componentes
desacoplados siguiendo los principios SOLID y Clean Architecture.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.types.worksheet_data import WorksheetData

# --- DTOs (Data Transfer Objects) ---

@dataclass(slots=True)
class WorkbookHandle:
    """Wrapper enterprise para el workbook con metadata forense."""
    workbook: Any
    source_path: Path
    opened_at: datetime
    checksum: str
    readonly: bool

@dataclass
class ValidationReport:
    """Reporte de validación de los datos ingeridos."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    health_score: float = 100.0
    processing_time_ms: float = 0.0

@dataclass
class IngestionResult:
    """Resultado final del proceso de ingesta."""
    success: bool
    records_processed: int
    validation_report: ValidationReport
    output_data_path: Optional[Path] = None
    report_path: Optional[Path] = None


# --- Interfaces (ABCs) ---

class IExcelReader(ABC):
    """Interfaz para la lectura de archivos Excel."""
    
    @abstractmethod
    def load_workbook(self, file_path: Path) -> WorkbookHandle:
        """
        Carga un archivo Excel y devuelve un objeto WorkbookHandle.
        
        Args:
            file_path (Path): Ruta al archivo Excel.
            
        Returns:
            WorkbookHandle: Wrapper con el workbook y su metadata.
            
        Raises:
            FileNotReadableError: Si el archivo no existe, está corrupto o protegido.
        """
        pass  # pragma: no cover

class IWorkbookAnalyzer(ABC):
    """Interfaz para el análisis de Workbooks."""
    
    @abstractmethod
    def analyze(self, file_path: Path, workbook: Any) -> Any:
        """
        Analiza el workbook sin extraer datos de las celdas, retornando metadata forense.
        
        Args:
            file_path (Path): Ruta del archivo original.
            workbook (Any): Objeto Workbook (ej. de openpyxl).
            
        Returns:
            Any: Un objeto WorkbookContext con la metadata del libro.
            
        Raises:
            InvalidWorkbookError: Si el workbook no se puede analizar.
        """
        pass  # pragma: no cover

class IWorksheetReader(ABC):
    """Interfaz para la extracción de datos de Worksheets — Fase 3B."""

    @abstractmethod
    def extract_data(self, worksheet: Any) -> WorksheetData:
        """Extrae los datos crudos de una hoja de cálculo como ``WorksheetData``.

        La extracción NO interpreta tipos, NO normaliza valores y NO analiza
        encabezados. Produce la representación física más fiel posible del
        contenido de la hoja.

        Args:
            worksheet (Any): Hoja de cálculo (``openpyxl.Worksheet``).

        Returns:
            WorksheetData: Contenedor inmutable con filas, celdas y perfiles
                de columna. Sin ningún análisis semántico.

        Raises:
            DataExtractionError: Si ocurre un error al leer las celdas o si
                la hoja no contiene datos extraíbles.
        """
        pass  # pragma: no cover

class IHeaderDetector(ABC):
    """Interfaz para la detección de encabezados."""
    
    @abstractmethod
    def detect_headers(self, data: List[List[Any]]) -> Dict[str, int]:
        """
        Detecta y mapea los encabezados en los datos crudos.
        
        Args:
            data (List[List[Any]]): Datos crudos de la hoja.
            
        Returns:
            Dict[str, int]: Diccionario mapeando el nombre del encabezado a su índice de columna.
            
        Raises:
            HeaderDetectionError: Si no se detectan encabezados válidos.
        """
        pass  # pragma: no cover

class IDataTypeDetector(ABC):
    """Interfaz para la inferencia de tipos de datos."""
    
    @abstractmethod
    def infer_types(self, data: List[List[Any]], headers: Dict[str, int]) -> Dict[str, type]:
        """
        Infiere los tipos de datos para cada columna.
        
        Args:
            data (List[List[Any]]): Datos crudos.
            headers (Dict[str, int]): Mapeo de encabezados.
            
        Returns:
            Dict[str, type]: Diccionario mapeando el nombre de la columna a su tipo de dato inferido.
        """
        pass  # pragma: no cover

class IRowNormalizer(ABC):
    """Interfaz para la normalización de filas a esquema JSON."""
    
    @abstractmethod
    def normalize_row(self, row: List[Any], headers: Dict[str, int], types: Dict[str, type]) -> Dict[str, Any]:
        """
        Normaliza una fila de datos crudos a un diccionario tipado.
        
        Args:
            row (List[Any]): Fila de datos crudos.
            headers (Dict[str, int]): Mapeo de encabezados.
            types (Dict[str, type]): Tipos inferidos.
            
        Returns:
            Dict[str, Any]: Registro normalizado.
            
        Raises:
            DataNormalizationError: Si la fila no puede ser normalizada.
        """
        pass  # pragma: no cover

class IEntityMapper(ABC):
    """Interfaz para la normalización semántica de entidades."""
    
    @abstractmethod
    def map_entity(self, field_name: str, value: Any) -> Any:
        """
        Mapea un valor a su representación semántica normalizada (ej. "M" -> "Masculino").
        
        Args:
            field_name (str): Nombre del campo/entidad.
            value (Any): Valor original.
            
        Returns:
            Any: Valor normalizado semánticamente.
        """
        pass  # pragma: no cover

class IIngestionValidator(ABC):
    """Interfaz para la validación de los datos normalizados."""
    
    @abstractmethod
    def validate(self, records: List[Dict[str, Any]]) -> ValidationReport:
        """
        Valida una lista de registros normalizados contra las reglas de negocio.
        
        Args:
            records (List[Dict[str, Any]]): Lista de registros normalizados.
            
        Returns:
            ValidationReport: Reporte de validación.
        """
        pass  # pragma: no cover

class IIngestionReport(ABC):
    """Interfaz para la generación del reporte de ingesta."""
    
    @abstractmethod
    def generate_report(self, result: IngestionResult, output_path: Path) -> None:
        """
        Genera y guarda el reporte final de ingesta en disco.
        
        Args:
            result (IngestionResult): Resultado del proceso.
            output_path (Path): Ruta donde guardar el reporte.
        """
        pass  # pragma: no cover

class IIngestionEngine(ABC):
    """Interfaz principal del Ingestion Engine."""
    
    @abstractmethod
    def run(self, file_path: Path) -> IngestionResult:
        """
        Ejecuta el pipeline completo de ingesta.
        
        Args:
            file_path (Path): Ruta del archivo Excel origen.
            
        Returns:
            IngestionResult: Resultado final del pipeline.
        """
        pass  # pragma: no cover
