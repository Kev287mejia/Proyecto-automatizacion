from dataclasses import dataclass, field
from typing import Any, Mapping

@dataclass(frozen=True, slots=True)
class ProjectContext:
    """Metadatos generales del proyecto."""
    project_name: str = "Desconocido"
    client: str = "Desconocido"
    report_type: str = "Desconocido"
    period: str = "Desconocido"

@dataclass(frozen=True, slots=True)
class WordContext:
    """Contexto de la plantilla y artefactos de Word."""
    template_path: str = ""
    sections: tuple[str, ...] = field(default_factory=tuple)
    styles: Mapping[str, Any] = field(default_factory=dict)
    tables_count: int = 0
    has_headers: bool = False
    has_footers: bool = False

@dataclass(frozen=True, slots=True)
class ExcelContext:
    """Contexto de los datos crudos y la plantilla de Excel."""
    raw_data_path: str = ""
    template_path: str = ""
    worksheets: tuple[str, ...] = field(default_factory=tuple)
    tables_count: int = 0
    charts_count: int = 0
    ranges: tuple[str, ...] = field(default_factory=tuple)

@dataclass(frozen=True, slots=True)
class RuntimeContext:
    """Configuración de la ejecución actual, sistema y motor."""
    os_name: str = ""
    python_version: str = ""
    date: str = ""
    time: str = ""
    timezone: str = ""
    user: str = ""
    project_path: str = ""

@dataclass(frozen=True, slots=True)
class MetadataContext:
    """Contexto adicional de metadatos del proceso y trazabilidad."""
    client: str = ""
    period: str = ""
    
    # Control de Versiones
    context_version: str = "1.0"
    schema_version: str = "2026.1"
    siea_version: str = "1.0.0"
    blueprint_version: str = ""
    
    # Fingerprints (SHA-256)
    blueprint_hash: str = ""
    template_hash: str = ""
    excel_hash: str = ""
    config_hash: str = ""
    
    tags: tuple[str, ...] = field(default_factory=tuple)
    custom_fields: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class DiagnosticsContext:
    """Contexto de diagnóstico para auditoría y telemetría."""
    warnings: tuple[str, ...] = field(default_factory=tuple)
    errors: tuple[str, ...] = field(default_factory=tuple)
    execution_time_ms: int = 0

@dataclass(frozen=True, slots=True)
class AgentContext:
    """
    Contexto universal de ejecución para todo el SIEA.
    Este es el objeto más importante del proyecto y será recibido
    por todos los motores (Statistics, Insight, Word, Excel).
    Es completamente inmutable.
    """
    project: ProjectContext = field(default_factory=ProjectContext)
    runtime: RuntimeContext = field(default_factory=RuntimeContext)
    word: WordContext = field(default_factory=WordContext)
    excel: ExcelContext = field(default_factory=ExcelContext)
    metadata: MetadataContext = field(default_factory=MetadataContext)
    diagnostics: DiagnosticsContext = field(default_factory=DiagnosticsContext)

