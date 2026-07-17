import logging
from typing import Optional
from .context_models import (
    AgentContext, ProjectContext, WordContext, ExcelContext, 
    RuntimeContext, MetadataContext, DiagnosticsContext
)

class ContextBuilder:
    """
    Este es el corazón del módulo.
    Ensambla los distintos sub-contextos para construir el AgentContext final.
    """
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self._project: Optional[ProjectContext] = None
        self._runtime: Optional[RuntimeContext] = None
        self._word: Optional[WordContext] = None
        self._excel: Optional[ExcelContext] = None
        self._metadata: Optional[MetadataContext] = None
        self._diagnostics: Optional[DiagnosticsContext] = None

    def set_project_context(self, project: ProjectContext) -> 'ContextBuilder':
        self._project = project
        return self

    def set_runtime_context(self, runtime: RuntimeContext) -> 'ContextBuilder':
        self._runtime = runtime
        return self

    def set_word_context(self, word: WordContext) -> 'ContextBuilder':
        self._word = word
        return self

    def set_excel_context(self, excel: ExcelContext) -> 'ContextBuilder':
        self._excel = excel
        return self

    def set_metadata_context(self, metadata: MetadataContext) -> 'ContextBuilder':
        self._metadata = metadata
        return self

    def set_diagnostics_context(self, diagnostics: DiagnosticsContext) -> 'ContextBuilder':
        self._diagnostics = diagnostics
        return self

    def build(self) -> AgentContext:
        """
        Toma todos los sub-contextos y los ensambla en un único AgentContext inmutable.
        """
        self.logger.debug("Ensamblando AgentContext a partir de sub-contextos...")
        
        if not (self._project and self._runtime and self._word and 
                self._excel and self._metadata and self._diagnostics):
            
            missing = []
            if not self._project: missing.append("ProjectContext")
            if not self._runtime: missing.append("RuntimeContext")
            if not self._word: missing.append("WordContext")
            if not self._excel: missing.append("ExcelContext")
            if not self._metadata: missing.append("MetadataContext")
            if not self._diagnostics: missing.append("DiagnosticsContext")
            
            error_msg = f"No se puede construir AgentContext, faltan los siguientes componentes: {', '.join(missing)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        return AgentContext(
            project=self._project,
            runtime=self._runtime,
            word=self._word,
            excel=self._excel,
            metadata=self._metadata,
            diagnostics=self._diagnostics
        )


