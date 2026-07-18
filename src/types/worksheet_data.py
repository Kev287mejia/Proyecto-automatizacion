"""
Modelos de dominio inmutables para la extracción cruda de datos de Worksheets.

Este módulo define los Value Objects tipados que representan los datos extraídos
de una hoja de cálculo por la Fase 3B (``WorksheetReader``). Los modelos
capturan la estructura física del contenido sin ninguna interpretación semántica:
no hay tipos inferidos, no hay nombres normalizados, no hay análisis de patrones.

Jerarquía de modelos::

    WorksheetData
    ├── sheet_name (str)
    ├── rows       (Tuple[RowData, ...])    — filas con sus celdas
    ├── column_profiles (Tuple[ColumnProfile, ...])  — resumen por columna
    └── extraction_stats (ExtractionStats)  — métricas del proceso

    RowData
    └── cells (Tuple[CellData, ...])

    CellData
    ├── row_index    (int)   — base-0
    ├── col_index    (int)   — base-0
    ├── raw_value    (Any)   — valor exacto sin castear
    └── is_empty     (bool)

    ColumnProfile
    ├── col_index    (int)
    ├── total_cells  (int)
    ├── empty_cells  (int)
    └── non_empty_cells (int)

    ExtractionStats
    ├── total_rows       (int)
    ├── total_columns    (int)
    ├── empty_rows_skipped (int)
    └── non_empty_rows   (int)

Principios de diseño:
    - ``frozen=True`` + ``slots=True``: inmutabilidad y eficiencia de memoria.
    - Sin pandas, sin numpy, sin dependencias externas.
    - Sin interpretación de tipos: ``raw_value`` es ``Any`` literal.
    - Sin normalización: los valores se almacenan tal como los reporta openpyxl.

Example::

    >>> from src.types.worksheet_data import WorksheetData, RowData, CellData
    >>> cell = CellData(row_index=0, col_index=0, raw_value="Nombre", is_empty=False)
    >>> row = RowData(row_index=0, cells=(cell,))
    >>> ws_data = WorksheetData(
    ...     sheet_name="Datos",
    ...     rows=(row,),
    ...     column_profiles=(),
    ...     extraction_stats=ExtractionStats(1, 1, 0, 1),
    ... )
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Tuple


# ---------------------------------------------------------------------------
# CellData — unidad atómica de dato
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CellData:
    """Representación inmutable de una celda individual.

    Almacena la posición y el valor crudo tal como lo entrega openpyxl,
    sin ninguna transformación ni interpretación de tipo.

    Attributes:
        row_index: Índice de fila base-0 dentro de la hoja extraída
            (no el número de fila de Excel).
        col_index: Índice de columna base-0 dentro de la hoja extraída
            (no la letra de columna de Excel).
        raw_value: Valor exacto de la celda tal como lo retorna openpyxl.
            Puede ser ``str``, ``int``, ``float``, ``datetime``, ``bool``,
            ``None``, o cualquier otro tipo que openpyxl devuelva.
        is_empty: ``True`` si ``raw_value`` es ``None`` o una cadena
            compuesta únicamente de espacios en blanco.
        excel_row: Número de fila en Excel (base-1). ``None`` si no se
            conoce (ej. filas filtradas).
        excel_col: Letra o número de columna en Excel. ``None`` si no se
            conoce.

    Example:
        >>> cell = CellData(
        ...     row_index=0,
        ...     col_index=2,
        ...     raw_value=42,
        ...     is_empty=False,
        ... )
        >>> cell.raw_value
        42
        >>> cell.is_empty
        False
    """

    row_index: int
    col_index: int
    raw_value: Any
    is_empty: bool
    excel_row: Optional[int] = None
    excel_col: Optional[int] = None

    def __repr__(self) -> str:
        return (
            f"CellData(r={self.row_index}, c={self.col_index}, "
            f"val={self.raw_value!r}, empty={self.is_empty})"
        )


# ---------------------------------------------------------------------------
# RowData — fila de celdas
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RowData:
    """Representación inmutable de una fila completa de la hoja.

    Contiene las celdas de la fila en orden de columna, preservando
    posiciones exactas sin descartar celdas vacías intermedias.

    Attributes:
        row_index: Índice de fila base-0 en los datos extraídos.
        cells: Tupla inmutable de ``CellData`` en orden de columna
            (incluyendo celdas vacías entre valores para preservar
            la posición relativa).
        excel_row: Número de fila original en Excel (base-1).
            ``None`` si no aplica.

    Properties:
        cell_count: Total de celdas en la fila.
        non_empty_count: Cantidad de celdas con valor real.
        is_fully_empty: ``True`` si todas las celdas están vacías.
        values: Tupla de los valores crudos en orden de columna.

    Example:
        >>> row = RowData(
        ...     row_index=0,
        ...     cells=(
        ...         CellData(0, 0, "Nombre", False),
        ...         CellData(0, 1, "Edad", False),
        ...     ),
        ... )
        >>> row.values
        ('Nombre', 'Edad')
        >>> row.non_empty_count
        2
    """

    row_index: int
    cells: Tuple[CellData, ...]
    excel_row: Optional[int] = None

    @property
    def cell_count(self) -> int:
        """Total de celdas en la fila (incluyendo vacías).

        Returns:
            Longitud de la tupla ``cells``.
        """
        return len(self.cells)

    @property
    def non_empty_count(self) -> int:
        """Celdas con valor no vacío.

        Returns:
            Cantidad de celdas cuyo ``is_empty`` es ``False``.
        """
        return sum(1 for c in self.cells if not c.is_empty)

    @property
    def is_fully_empty(self) -> bool:
        """Verifica si la fila no contiene ningún valor.

        Returns:
            ``True`` si todas las celdas son vacías.
        """
        return all(c.is_empty for c in self.cells)

    @property
    def values(self) -> Tuple[Any, ...]:
        """Tupla de valores crudos en orden de columna.

        Returns:
            Valores ``raw_value`` de cada celda de la fila.

        Example:
            >>> row.values
            ('Juan', 25, None, 'Managua')
        """
        return tuple(c.raw_value for c in self.cells)


# ---------------------------------------------------------------------------
# ColumnProfile — perfil estadístico por columna
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ColumnProfile:
    """Perfil básico de una columna: solo conteos, sin interpretación.

    Provee métricas de densidad de datos por columna sin inferir tipos,
    normalizar valores ni tomar decisiones semánticas.

    Attributes:
        col_index: Índice de columna base-0.
        total_cells: Total de celdas analizadas en esta columna
            (excluyendo la fila de encabezado si se indica).
        empty_cells: Celdas cuyo valor es ``None`` o cadena en blanco.
        non_empty_cells: Celdas con algún valor real.
        header_value: Valor crudo de la primera fila de esa columna
            (potencial encabezado). ``None`` si la hoja está vacía.

    Properties:
        fill_rate: Tasa de llenado (0.0 - 1.0).
        is_fully_empty: ``True`` si no hay ningún dato en la columna.

    Example:
        >>> col = ColumnProfile(
        ...     col_index=0,
        ...     total_cells=100,
        ...     empty_cells=5,
        ...     non_empty_cells=95,
        ...     header_value="Nombre",
        ... )
        >>> col.fill_rate
        0.95
    """

    col_index: int
    total_cells: int
    empty_cells: int
    non_empty_cells: int
    header_value: Any = None

    @property
    def fill_rate(self) -> float:
        """Proporción de celdas con datos respecto al total.

        Returns:
            ``float`` entre 0.0 y 1.0. Retorna 0.0 si no hay celdas.

        Example:
            >>> ColumnProfile(0, 10, 3, 7).fill_rate
            0.7
        """
        if self.total_cells == 0:
            return 0.0
        return self.non_empty_cells / self.total_cells

    @property
    def is_fully_empty(self) -> bool:
        """``True`` si la columna no tiene ningún dato real.

        Returns:
            ``True`` cuando ``non_empty_cells == 0``.
        """
        return self.non_empty_cells == 0


# ---------------------------------------------------------------------------
# ExtractionStats — métricas del proceso de extracción
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ExtractionStats:
    """Métricas operativas del proceso de extracción de la hoja.

    No interpreta el contenido, solo registra conteos del proceso.

    Attributes:
        total_rows_scanned: Filas totales leídas del worksheet antes de
            cualquier filtrado (incluye filas vacías).
        total_columns: Ancho máximo de columnas detectado en la extracción.
        empty_rows_skipped: Filas descartadas por estar completamente vacías.
        non_empty_rows: Filas con al menos un valor real (incluye encabezado).

    Properties:
        has_data: ``True`` si hay al menos una fila no vacía.

    Example:
        >>> stats = ExtractionStats(
        ...     total_rows_scanned=105,
        ...     total_columns=8,
        ...     empty_rows_skipped=5,
        ...     non_empty_rows=100,
        ... )
        >>> stats.has_data
        True
    """

    total_rows_scanned: int
    total_columns: int
    empty_rows_skipped: int
    non_empty_rows: int

    @property
    def has_data(self) -> bool:
        """Verifica si la extracción produjo algún dato.

        Returns:
            ``True`` si ``non_empty_rows > 0``.
        """
        return self.non_empty_rows > 0


# ---------------------------------------------------------------------------
# WorksheetData — contenedor raíz (output de Fase 3B)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class WorksheetData:
    """Contenedor canónico de los datos extraídos de una hoja — Fase 3B.

    Es el output directo del ``WorksheetReader``. Almacena los datos
    en su forma más cruda posible: sin interpretación de tipos, sin
    normalización, sin análisis de encabezados.

    Este objeto sirve como input para la Fase 4 (Header Detector) y
    Fase 5 (Data Type Detector).

    Attributes:
        sheet_name: Nombre de la hoja de cálculo tal como aparece en Excel.
        rows: Tupla inmutable de ``RowData`` con todas las filas
            no-vacías extraídas, en orden de aparición.
        column_profiles: Tupla inmutable de ``ColumnProfile`` con el
            resumen de densidad de datos por columna.
        extraction_stats: Métricas del proceso de extracción.

    Properties:
        row_count: Número de filas con datos.
        column_count: Número de columnas del dataset.
        cells: Generador de todas las ``CellData`` de todas las filas.
        first_row: Primera fila extraída, o ``None`` si está vacía.
        raw_matrix: Matriz de valores crudos como lista de listas.

    Example:
        >>> ws_data.sheet_name
        'Beneficiarios'
        >>> ws_data.row_count
        101
        >>> ws_data.column_count
        6
        >>> ws_data.first_row.values
        ('Nombre', 'Edad', 'Sexo', 'Municipio', 'Departamento', 'Monto')
    """

    sheet_name: str
    rows: Tuple[RowData, ...]
    column_profiles: Tuple[ColumnProfile, ...]
    extraction_stats: ExtractionStats

    @property
    def row_count(self) -> int:
        """Número de filas de datos (incluyendo potencial encabezado).

        Returns:
            Longitud de la tupla ``rows``.
        """
        return len(self.rows)

    @property
    def column_count(self) -> int:
        """Número de columnas del dataset.

        Returns:
            ``extraction_stats.total_columns``.
        """
        return self.extraction_stats.total_columns

    @property
    def first_row(self) -> Optional[RowData]:
        """Primera fila extraída (candidata a encabezado).

        Returns:
            Primer elemento de ``rows``, o ``None`` si está vacío.

        Example:
            >>> first = ws_data.first_row
            >>> first.values[0] if first else None
            'Nombre'
        """
        return self.rows[0] if self.rows else None

    @property
    def cells(self) -> Tuple[CellData, ...]:
        """Todas las celdas del dataset aplanadas en una tupla.

        Returns:
            Tupla con todas las ``CellData`` de todas las filas,
            en orden de fila y luego de columna.

        Example:
            >>> total = len(ws_data.cells)
            >>> total  # filas x columnas
            606
        """
        return tuple(cell for row in self.rows for cell in row.cells)

    @property
    def raw_matrix(self) -> Tuple[Tuple[Any, ...], ...]:
        """Matriz de valores crudos sin metadatos de posición.

        Returns:
            Tupla de tuplas de valores, preservando ``None`` para vacíos.

        Example:
            >>> matrix = ws_data.raw_matrix
            >>> matrix[0]
            ('Nombre', 'Edad', 'Sexo')
        """
        return tuple(row.values for row in self.rows)

    def get_row(self, index: int) -> Optional[RowData]:
        """Obtiene una fila por índice base-0.

        Args:
            index: Índice de fila en ``rows`` (base-0).

        Returns:
            ``RowData`` en esa posición, o ``None`` si el índice
            está fuera de rango.

        Example:
            >>> ws_data.get_row(0)
            RowData(row_index=0, ...)
        """
        if 0 <= index < len(self.rows):
            return self.rows[index]
        return None

    def get_column_profile(self, col_index: int) -> Optional[ColumnProfile]:
        """Obtiene el perfil de una columna por índice base-0.

        Args:
            col_index: Índice de columna (base-0).

        Returns:
            ``ColumnProfile`` de esa columna, o ``None`` si no existe.
        """
        for profile in self.column_profiles:
            if profile.col_index == col_index:
                return profile
        return None
