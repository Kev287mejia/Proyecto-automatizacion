"""
Modelos de dominio inmutables para el análisis estructural de Workbooks.

Este módulo define los Value Objects tipados (dataclasses frozen) que representan
el contexto forense de un archivo Excel, producido exclusivamente por la Fase 3A
(WorkbookAnalyzer). Ningún modelo aquí contiene lógica de negocio; son contenedores
de datos puros siguiendo el principio de Inmutabilidad (SOLID - SRP).

Jerarquía de modelos:
    WorkbookContext
    ├── WorkbookStatistics    (métricas cuantitativas del libro)
    ├── WorkbookProtection    (estado de seguridad del libro)
    ├── WorkbookMetadata      (metadatos del libro)
    └── Tuple[WorksheetMetadata, ...]  (metadata por hoja)

Nota:
    Todos los modelos usan ``frozen=True`` para garantizar inmutabilidad en runtime
    y ``slots=True`` para optimizar el uso de memoria.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


# ---------------------------------------------------------------------------
# Modelo de hoja individual
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class WorksheetMetadata:
    """Metadata estructural de una hoja de cálculo individual.

    Contiene únicamente información forense obtenida de la estructura del
    workbook sin leer ni interpretar contenido de celdas.

    Attributes:
        name: Nombre de la hoja tal como aparece en la pestaña.
        is_hidden: ``True`` si la hoja tiene estado ``'hidden'`` o ``'veryHidden'``.
        dimensions: Rango de celdas pre-calculado por Excel (ej. ``'A1:Z100'``).
            Cadena vacía si la hoja no tiene dimensiones registradas.
        has_tables: ``True`` si la hoja contiene al menos una tabla estructurada.
        has_charts: ``True`` si la hoja contiene al menos un gráfico embebido.
        has_filters: ``True`` si la hoja tiene un auto-filtro activo.
        tables: Tupla inmutable con los nombres de las tablas estructuradas.
        chart_count: Cantidad total de gráficos en la hoja.

    Example:
        >>> meta = WorksheetMetadata(
        ...     name="Datos",
        ...     is_hidden=False,
        ...     dimensions="A1:D100",
        ...     has_tables=True,
        ...     has_charts=False,
        ...     has_filters=True,
        ...     tables=("Tabla1",),
        ...     chart_count=0,
        ... )
        >>> meta.name
        'Datos'
    """

    name: str
    is_hidden: bool
    dimensions: str
    has_tables: bool
    has_charts: bool
    has_filters: bool
    tables: Tuple[str, ...]
    chart_count: int = 0


# ---------------------------------------------------------------------------
# Modelo de protección del libro
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class WorkbookProtection:
    """Estado de protección de seguridad del workbook.

    Attributes:
        is_protected: ``True`` si la estructura del libro está bloqueada
            (``lockStructure`` activo en la configuración de seguridad).
        lock_structure: Alias explícito de ``is_protected`` para claridad semántica.
        lock_windows: ``True`` si las ventanas del libro están bloqueadas.

    Example:
        >>> prot = WorkbookProtection(
        ...     is_protected=True,
        ...     lock_structure=True,
        ...     lock_windows=False,
        ... )
        >>> prot.is_protected
        True
    """

    is_protected: bool
    lock_structure: bool = False
    lock_windows: bool = False


# ---------------------------------------------------------------------------
# Modelo de estadísticas del libro
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class WorkbookStatistics:
    """Métricas cuantitativas del workbook extraídas del sistema de archivos y estructura.

    Attributes:
        approx_size_bytes: Tamaño en bytes del archivo en disco.
            Valor 0 si el archivo no existe o no es accesible.
        sheet_count: Total de hojas en el workbook (visibles + ocultas).
        hidden_sheet_count: Cantidad de hojas con estado ``'hidden'`` o ``'veryHidden'``.
        visible_sheet_count: Cantidad de hojas visibles (calculado automáticamente).

    Example:
        >>> stats = WorkbookStatistics(
        ...     approx_size_bytes=102400,
        ...     sheet_count=5,
        ...     hidden_sheet_count=1,
        ... )
        >>> stats.visible_sheet_count
        4
    """

    approx_size_bytes: int
    sheet_count: int
    hidden_sheet_count: int

    @property
    def visible_sheet_count(self) -> int:
        """Cantidad de hojas visibles.

        Returns:
            Diferencia entre el total de hojas y las hojas ocultas.
        """
        return self.sheet_count - self.hidden_sheet_count


# ---------------------------------------------------------------------------
# Modelo de metadata del libro
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class WorkbookMetadata:
    """Metadata de identificación y navegación del workbook.

    Attributes:
        file_name: Nombre del archivo con extensión (ej. ``'datos_2024.xlsx'``).
        active_sheet: Nombre de la hoja activa cuando el libro fue guardado.
        target_sheet: Hoja candidata heurística para extracción de datos.
            Determinada por el analizador como la primera hoja visible con
            dimensiones aparentes de datos reales.
        named_ranges: Tupla inmutable con los nombres de rangos nombrados
            definidos en el libro.

    Example:
        >>> meta = WorkbookMetadata(
        ...     file_name="reporte.xlsx",
        ...     active_sheet="Hoja1",
        ...     target_sheet="Datos",
        ...     named_ranges=("RANGO_ACTIVOS", "RANGO_PASIVOS"),
        ... )
        >>> meta.file_name
        'reporte.xlsx'
    """

    file_name: str
    active_sheet: str
    target_sheet: str
    named_ranges: Tuple[str, ...]


# ---------------------------------------------------------------------------
# Modelo raíz: contexto completo del workbook
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class WorkbookContext:
    """Contexto forense completo de un archivo Excel generado por la Fase 3A.

    Agrega todos los modelos de metadata en un único Value Object inmutable.
    Este objeto es el output canónico del ``WorkbookAnalyzer`` y sirve como
    input para las fases posteriores del pipeline de ingesta.

    Attributes:
        statistics: Métricas cuantitativas del workbook.
        protection: Estado de seguridad y protección del libro.
        metadata: Metadatos de identificación y navegación.
        sheets: Tupla inmutable con la metadata de cada hoja individual.

    Example:
        >>> context = WorkbookContext(
        ...     statistics=WorkbookStatistics(102400, 3, 1),
        ...     protection=WorkbookProtection(False),
        ...     metadata=WorkbookMetadata("datos.xlsx", "Hoja1", "Datos", ()),
        ...     sheets=(WorksheetMetadata("Datos", False, "A1:D100", False, False, False, (), 0),),
        ... )
        >>> context.metadata.file_name
        'datos.xlsx'
        >>> len(context.sheets)
        1
    """

    statistics: WorkbookStatistics
    protection: WorkbookProtection
    metadata: WorkbookMetadata
    sheets: Tuple[WorksheetMetadata, ...]

    def get_sheet(self, name: str) -> WorksheetMetadata | None:
        """Busca y retorna la metadata de una hoja por nombre.

        Args:
            name: Nombre exacto de la hoja a buscar.

        Returns:
            ``WorksheetMetadata`` de la hoja encontrada, o ``None`` si no existe.

        Example:
            >>> sheet = context.get_sheet("Datos")
            >>> sheet.name if sheet else None
            'Datos'
        """
        for sheet in self.sheets:
            if sheet.name == name:
                return sheet
        return None

    def get_visible_sheets(self) -> Tuple[WorksheetMetadata, ...]:
        """Retorna solo las hojas que no están ocultas.

        Returns:
            Tupla con las hojas visibles del workbook.

        Example:
            >>> visible = context.get_visible_sheets()
            >>> all(not s.is_hidden for s in visible)
            True
        """
        return tuple(s for s in self.sheets if not s.is_hidden)
