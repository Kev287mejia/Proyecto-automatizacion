"""
Lector de datos crudos de Worksheets — Fase 3B del SIEA Ingestion Engine.

Responsabilidad única:
    Extraer el contenido celda-a-celda de una hoja de cálculo openpyxl y
    encapsularlo en un ``WorksheetData`` inmutable.

El módulo expone:
    - ``WorksheetReader``: Implementación concreta de ``IWorksheetReader``.

Lo que SÍ hace esta fase:
    - Itera filas con ``iter_rows(values_only=False)`` para preservar índices.
    - Detecta celdas vacías (``None`` y strings en blanco).
    - Descarta filas completamente vacías y contabiliza las omitidas.
    - Construye perfiles de densidad por columna (``ColumnProfile``).
    - Registra métricas del proceso en ``ExtractionStats``.
    - Emite logging granular a nivel DEBUG/INFO/WARNING/ERROR.

Lo que NO hace esta fase:
    - No infiere tipos de datos.
    - No detecta encabezados.
    - No normaliza valores.
    - No interpreta el significado semántico de ningún valor.
    - No modifica la hoja de cálculo.
    - No usa pandas.

Example::

    >>> import openpyxl
    >>> from pathlib import Path
    >>> from src.ingestion.worksheet_reader import WorksheetReader
    >>>
    >>> wb = openpyxl.load_workbook("datos.xlsx")
    >>> ws = wb["Beneficiarios"]
    >>> reader = WorksheetReader()
    >>> ws_data = reader.extract_data(ws)
    >>> print(ws_data.row_count)
    101
    >>> print(ws_data.first_row.values)
    ('Nombre', 'Edad', 'Sexo', 'Municipio')
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from src.ingestion.exceptions import DataExtractionError
from src.ingestion.interfaces import IWorksheetReader
from src.types.worksheet_data import (
    CellData,
    ColumnProfile,
    ExtractionStats,
    RowData,
    WorksheetData,
)

# ---------------------------------------------------------------------------
# Logger del módulo
# ---------------------------------------------------------------------------

_logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Implementación principal
# ---------------------------------------------------------------------------


class WorksheetReader(IWorksheetReader):
    """Lector forense de datos crudos de un Worksheet openpyxl.

    Implementa ``IWorksheetReader`` siguiendo el principio de Responsabilidad
    Única (SRP): extrae datos físicos de la hoja sin interpretarlos.

    Design Decisions:
        - Usa ``iter_rows(values_only=False)`` para tener acceso al índice de
          celda (``cell.row``, ``cell.column``) y así preservar la posición
          exacta en el modelo ``CellData``.
        - Las filas completamente vacías se descartan y se contabilizan en
          ``ExtractionStats.empty_rows_skipped``.
        - Las celdas vacías intermedias se CONSERVAN en ``RowData.cells``
          para preservar la posición relativa de las columnas.
        - Los perfiles de columna se calculan en un único pase sobre las
          filas ya procesadas (no re-itera sobre el worksheet).

    Stateless:
        La clase no guarda estado entre llamadas; puede reutilizarse
        para múltiples hojas sin efecto secundario.

    Example::

        >>> reader = WorksheetReader()
        >>> ws_data = reader.extract_data(ws)
        >>> ws_data.column_count
        6
    """

    # -----------------------------------------------------------------------
    # Interfaz pública
    # -----------------------------------------------------------------------

    def extract_data(self, worksheet: Any) -> WorksheetData:
        """Extrae todos los datos crudos de la hoja como ``WorksheetData``.

        Itera las filas de la hoja con ``iter_rows``, construye ``CellData``
        para cada celda, agrupa en ``RowData``, descarta filas vacías, y
        computa perfiles de columna en un único pase adicional sobre las
        filas ya construidas.

        Args:
            worksheet: Objeto ``openpyxl.worksheet.worksheet.Worksheet``
                (modo normal o read-only).

        Returns:
            ``WorksheetData`` inmutable con:
            - ``rows``: filas no-vacías con sus celdas.
            - ``column_profiles``: densidad por columna.
            - ``extraction_stats``: métricas del proceso.

        Raises:
            DataExtractionError: Si la hoja no puede ser leída, o si tras
                el filtrado no quedan filas con datos.

        Example::

            >>> ws_data = reader.extract_data(ws)
            >>> ws_data.sheet_name
            'Beneficiarios'
        """
        sheet_name: str = getattr(worksheet, "title", "UNKNOWN")
        _logger.info("Iniciando extracción de datos de hoja: '%s'", sheet_name)

        try:
            rows_data, total_scanned, empty_skipped = self._extract_rows(worksheet)
        except DataExtractionError:
            raise
        except Exception as exc:
            _logger.error(
                "Error inesperado al extraer datos de '%s': %s", sheet_name, exc
            )
            raise DataExtractionError(
                f"Fallo al extraer datos de la hoja '{sheet_name}': {exc}"
            ) from exc

        if not rows_data:
            _logger.warning(
                "La hoja '%s' no contiene filas con datos extraíbles.", sheet_name
            )
            raise DataExtractionError(
                f"La hoja '{sheet_name}' no contiene datos extraíbles."
            )

        # Ancho máximo real de columnas
        max_cols = max((row.cell_count for row in rows_data), default=0)

        # Perfiles de columna — pase único sobre las filas ya construidas
        column_profiles = self._build_column_profiles(rows_data, max_cols)

        stats = ExtractionStats(
            total_rows_scanned=total_scanned,
            total_columns=max_cols,
            empty_rows_skipped=empty_skipped,
            non_empty_rows=len(rows_data),
        )

        ws_data = WorksheetData(
            sheet_name=sheet_name,
            rows=tuple(rows_data),
            column_profiles=tuple(column_profiles),
            extraction_stats=stats,
        )

        _logger.info(
            "Extracción completada: hoja='%s', filas=%d, columnas=%d, "
            "filas_vacías_omitidas=%d",
            sheet_name,
            stats.non_empty_rows,
            stats.total_columns,
            stats.empty_rows_skipped,
        )
        return ws_data

    # -----------------------------------------------------------------------
    # Métodos privados — helpers de extracción
    # -----------------------------------------------------------------------

    def _extract_rows(
        self, worksheet: Any
    ) -> Tuple[List[RowData], int, int]:
        """Itera el worksheet y construye la lista de ``RowData``.

        Descarta filas completamente vacías y lleva conteo de ellas.

        Args:
            worksheet: Objeto ``openpyxl.Worksheet``.

        Returns:
            Tupla ``(filas_con_datos, total_filas_escaneadas, filas_vacías_omitidas)``.

        Raises:
            DataExtractionError: Si ``iter_rows`` falla.
        """
        rows_data: List[RowData] = []
        total_scanned = 0
        empty_skipped = 0
        row_idx = 0  # índice base-0 de las filas de datos (sin contar vacías)

        for raw_row in worksheet.iter_rows(values_only=False):
            total_scanned += 1
            cells = self._build_cells(raw_row, row_idx)

            row_data = RowData(
                row_index=row_idx,
                cells=tuple(cells),
                excel_row=raw_row[0].row if raw_row else None,
            )

            if row_data.is_fully_empty:
                empty_skipped += 1
                _logger.debug(
                    "Fila Excel %s omitida (completamente vacía).",
                    row_data.excel_row,
                )
                continue

            rows_data.append(row_data)
            row_idx += 1

        _logger.debug(
            "Filas escaneadas=%d, no-vacías=%d, vacías omitidas=%d",
            total_scanned,
            len(rows_data),
            empty_skipped,
        )
        return rows_data, total_scanned, empty_skipped

    @staticmethod
    def _build_cells(raw_row: Tuple[Any, ...], row_idx: int) -> List[CellData]:
        """Construye la lista de ``CellData`` para una fila.

        Preserva celdas vacías intermedias para mantener la posición
        relativa de columnas.

        Args:
            raw_row: Tupla de objetos ``openpyxl.Cell`` de una fila.
            row_idx: Índice base-0 de la fila en los datos de salida.

        Returns:
            Lista de ``CellData`` en orden de columna.
        """
        cells: List[CellData] = []
        for col_idx, cell in enumerate(raw_row):
            raw_value = cell.value
            is_empty = raw_value is None or (
                isinstance(raw_value, str) and raw_value.strip() == ""
            )
            cells.append(
                CellData(
                    row_index=row_idx,
                    col_index=col_idx,
                    raw_value=raw_value,
                    is_empty=is_empty,
                    excel_row=cell.row,
                    excel_col=cell.column,
                )
            )
        return cells

    @staticmethod
    def _build_column_profiles(
        rows: List[RowData], max_cols: int
    ) -> List[ColumnProfile]:
        """Construye perfiles de densidad para cada columna.

        Recorre las filas ya construidas en un único pase y acumula
        conteos por columna. La primera fila se usa como ``header_value``
        potencial sin interpretarla como encabezado formal.

        Args:
            rows: Filas de datos ya filtradas (sin vacías).
            max_cols: Número máximo de columnas a perfilar.

        Returns:
            Lista de ``ColumnProfile`` ordenada por ``col_index``.
        """
        if not rows or max_cols == 0:
            return []

        # Acumuladores: col_index -> {total, empty, non_empty}
        totals: Dict[int, int] = {i: 0 for i in range(max_cols)}
        empties: Dict[int, int] = {i: 0 for i in range(max_cols)}

        # Header potencial: primera fila
        header_values: Dict[int, Any] = {}
        first_row = rows[0]
        for cell in first_row.cells:
            header_values[cell.col_index] = cell.raw_value

        # Pase único sobre filas de datos (excluye primera fila del conteo)
        data_rows = rows[1:] if len(rows) > 1 else []
        for row in data_rows:
            for cell in row.cells:
                ci = cell.col_index
                if ci in totals:
                    totals[ci] += 1
                    if cell.is_empty:
                        empties[ci] += 1

        profiles: List[ColumnProfile] = []
        for col_idx in range(max_cols):
            total = totals.get(col_idx, 0)
            empty = empties.get(col_idx, 0)
            profiles.append(
                ColumnProfile(
                    col_index=col_idx,
                    total_cells=total,
                    empty_cells=empty,
                    non_empty_cells=total - empty,
                    header_value=header_values.get(col_idx),
                )
            )

        _logger.debug(
            "Perfiles de columna construidos: %d columnas",
            len(profiles),
        )
        return profiles
