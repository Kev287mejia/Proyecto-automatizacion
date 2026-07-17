import time
import logging
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, List
from .context_models import AgentContext
from .context_loader import ContextResolutionError

class Severity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass(frozen=True)
class ValidationIssue:
    code: str
    severity: Severity
    message: str
    suggestion: str

@dataclass(frozen=True)
class ValidationReport:
    issues: tuple[ValidationIssue, ...]
    duration_ms: float

    @property
    def warnings_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.WARNING)

    @property
    def criticals_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.CRITICAL)

    @property
    def errors_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.ERROR)

    @property
    def infos_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.INFO)

    @property
    def score(self) -> int:
        """Puntuación sobre 100 basada en severidades. Penaliza duro errores y críticos."""
        total = 100 - (self.criticals_count * 100) - (self.errors_count * 50) - (self.warnings_count * 5)
        return max(0, total)

class ValidationRule(Protocol):
    def validate(self, context: AgentContext) -> List[ValidationIssue]:
        """Retorna una lista de problemas encontrados. Retorna [] si es válido."""
        ...

class ProjectNameRule:
    def validate(self, context: AgentContext) -> List[ValidationIssue]:
        if not context.project.project_name or context.project.project_name == "Desconocido":
            return [ValidationIssue(
                code="CTX-001",
                severity=Severity.ERROR,
                message="El nombre del proyecto (project_name) no está definido.",
                suggestion="Define un nombre válido en 'project_name' en el blueprint.json."
            )]
        return []

class TemplateExistsRule:
    def validate(self, context: AgentContext) -> List[ValidationIssue]:
        if context.word.template_path:
            path = Path(context.word.template_path)
            if not path.exists():
                return [ValidationIssue(
                    code="CTX-002",
                    severity=Severity.ERROR,
                    message=f"La plantilla de Word no existe en: {path}",
                    suggestion="Asegúrate de que 'template_path' en 'word' apunte a un archivo .docx real."
                )]
        return []

class ExcelTemplateExistsRule:
    def validate(self, context: AgentContext) -> List[ValidationIssue]:
        if context.excel.template_path:
            path = Path(context.excel.template_path)
            if not path.exists():
                return [ValidationIssue(
                    code="CTX-003",
                    severity=Severity.ERROR,
                    message=f"La plantilla de Excel no existe en: {path}",
                    suggestion="Asegúrate de que 'template_path' en 'excel' apunte a un archivo .xlsx real."
                )]
        return []

class ContextValidator:
    """Validador principal que orquesta un sistema de reglas independientes y genera un Reporte."""
    
    def __init__(self, rules: List[ValidationRule] = None) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.rules = rules or [
            ProjectNameRule(),
            TemplateExistsRule(),
            ExcelTemplateExistsRule()
        ]

    def validate(self, context: AgentContext) -> ValidationReport:
        """
        Itera sobre todas las reglas configuradas y compila un reporte.
        """
        self.logger.debug(f"Ejecutando {len(self.rules)} reglas de validación...")
        start_time = time.perf_counter()
        
        all_issues: List[ValidationIssue] = []
        for rule in self.rules:
            issues = rule.validate(context)
            all_issues.extend(issues)

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        report = ValidationReport(
            issues=tuple(all_issues),
            duration_ms=duration_ms
        )

        for issue in report.issues:
            log_msg = f"[{issue.code}] {issue.message} -> Sugerencia: {issue.suggestion}"
            if issue.severity == Severity.CRITICAL:
                self.logger.critical(log_msg)
            elif issue.severity == Severity.ERROR:
                self.logger.error(log_msg)
            elif issue.severity == Severity.WARNING:
                self.logger.warning(log_msg)
            else:
                self.logger.info(log_msg)

        self.logger.info(f"Validación completada en {report.duration_ms:.2f}ms. "
                         f"Score: {report.score}/100. "
                         f"Críticos: {report.criticals_count}. Errores: {report.errors_count}. Warnings: {report.warnings_count}.")

        return report

