"""
Analizador de la estructura del Workbook — Fase 3A del SIEA Ingestion Engine.

Responsabilidad única:
    Detectar y retornar la metadata estructural completa de un archivo Excel
    sin leer filas, interpretar columnas, modificar el libro, ni usar pandas.

El módulo expone:
    - ``WorkbookAnalyzer``: Implementación concreta de ``IWorkbookAnalyzer``.

Detección forense:
    - Nombre del archivo y tamaño en disco.
    - Cantidad total de hojas, hojas ocultas y hoja activa.
    - Tablas estructuradas (``ListObject``) por hoja.
    - Gráficos embebidos por hoja.
    - Auto-filtros activos.
    - Rangos nombrados del libro.
    - Dimensiones pre-calculadas por Excel (``ws.dimensions``).
    - Protección de estructura del libro.
    - Hoja target heurística para extracción posterior.

Limitaciones explícitas (No hace):
    - No itera filas ni celdas.
    - No usa ``ws.values``, ``ws.iter_rows``, ni ``ws.iter_cols``.
    - No usa pandas.
    - No modifica el workbook.
    - No hace cálculos sobre el contenido de las celdas.

Example:
    >>> from pathlib import Path
    >>> import openpyxl
    >>> from src.ingestion.workbook_analyzer import WorkbookAnalyzer
    >>>
    >>> wb = openpyxl.load_workbook("datos.xlsx", read_only=True)
    >>> analyzer = WorkbookAnalyzer()
    >>> context = analyzer.analyze(Path("datos.xlsx"), wb)
    >>> print(context.metadata.target_sheet)
    'Datos'
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, List

from src.ingestion.exceptions import InvalidWorkbookError
from src.ingestion.interfaces import IWorkbookAnalyzer
from src.types.workbook_context import (
    WorkbookContext,
    WorkbookMetadata,
    WorkbookProtection,
    WorkbookStatistics,
    WorksheetMetadata,
)

# ---------------------------------------------------------------------------
# Logger del módulo (nombre calificado para configuración granular)
# ---------------------------------------------------------------------------

_logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Implementación principal
# ---------------------------------------------------------------------------


class WorkbookAnalyzer(IWorkbookAnalyzer):
    """Analizador forense de la estructura de un Workbook openpyxl.

    Implementa ``IWorkbookAnalyzer`` siguiendo el principio de Responsabilidad
    Única (SRP): únicamente analiza estructura, nunca lee datos.

    Design Decisions:
        - Método ``analyze`` como punto de entrada principal.
        - Método ``get_valid_sheets`` como helper público para facilitar el
          testeo y la reutilización en otras fases.
        - Toda detección se hace sobre propiedades de metadata de openpyxl
          (``ws.dimensions``, ``ws.tables``, ``ws._charts``, etc.) sin acceder
          a celdas de datos.

    Args:
        (no constructor dependencies — stateless service)

    Example:
        >>> analyzer = WorkbookAnalyzer()
        >>> context = analyzer.analyze(Path("file.xlsx"), workbook)
        >>> context.statistics.sheet_count
        3
    """

    # -----------------------------------------------------------------------
    # Interfaz pública
    # -----------------------------------------------------------------------

    def analyze(self, file_path: Path, workbook: Any) -> WorkbookContext:
        """Analiza la estructura forense completa del workbook.

        Extrae toda la metadata estructural disponible sin acceder al contenido
        de las celdas. La detección se basa exclusivamente en propiedades de
        openpyxl que representan metadata pre-calculada por Excel.

        Args:
            file_path: Ruta al archivo ``.xlsx`` / ``.xlsm`` en disco.
                Usada para obtener nombre de archivo y tamaño.
            workbook: Objeto ``openpyxl.Workbook`` ya abierto (puede ser
                read-only o en modo normal).

        Returns:
            ``WorkbookContext`` inmutable con toda la información estructural.

        Raises:
            InvalidWorkbookError: Si el workbook no tiene hojas, si todas las
                hojas están ocultas, o si ocurre un error inesperado de openpyxl
                durante la inspección de la estructura.

        Example:
            >>> context = analyzer.analyze(Path("reporte.xlsx"), wb)
            >>> context.metadata.file_name
            'reporte.xlsx'
            >>> context.statistics.sheet_count
            4
        """
        _logger.info("Iniciando análisis forense de workbook: %s", file_path.name)

        if not workbook.sheetnames:
            _logger.error("El workbook '%s' no contiene ninguna hoja.", file_path.name)
            raise InvalidWorkbookError(
                f"El workbook '{file_path.name}' no contiene hojas."
            )

        # 1. Tamaño en disco (no lectura de contenido)
        approx_size = self._get_file_size(file_path)

        # 2. Metadata de hojas — sin tocar contenido de celdas
        sheets_meta, hidden_count = self._analyze_sheets(workbook)

        # 3. Hoja activa
        active_sheet = workbook.active.title if workbook.active else ""
        _logger.debug("Hoja activa: '%s'", active_sheet)

        # 4. Hoja target heurística
        target_sheet = self._resolve_target_sheet(
            sheets_meta=sheets_meta,
            active_sheet=active_sheet,
            workbook=workbook,
        )

        # 5. Rangos nombrados
        named_ranges = self._extract_named_ranges(workbook)

        # 6. Protección del libro
        protection = self._extract_protection(workbook)

        context = WorkbookContext(
            statistics=WorkbookStatistics(
                approx_size_bytes=approx_size,
                sheet_count=len(workbook.sheetnames),
                hidden_sheet_count=hidden_count,
            ),
            protection=protection,
            metadata=WorkbookMetadata(
                file_name=file_path.name,
                active_sheet=active_sheet,
                target_sheet=target_sheet,
                named_ranges=tuple(named_ranges),
            ),
            sheets=tuple(sheets_meta),
        )

        _logger.info(
            "Análisis completado: %d hojas (%d ocultas), target='%s', "
            "protegido=%s, rangos_nombrados=%d",
            context.statistics.sheet_count,
            context.statistics.hidden_sheet_count,
            target_sheet,
            protection.is_protected,
            len(named_ranges),
        )
        return context

    def get_valid_sheets(self, workbook: Any) -> List[Any]:
        """Retorna las hojas del workbook que son visibles y contienen datos.

        Útil como helper para fases posteriores del pipeline que necesiten
        saber cuáles hojas son candidatas para extracción.

        Args:
            workbook: Objeto ``openpyxl.Workbook`` ya abierto.

        Returns:
            Lista de objetos ``Worksheet`` que son visibles y tienen
            dimensiones distintas de una sola celda vacía.

        Raises:
            InvalidWorkbookError: Si no existe ninguna hoja visible con datos.

        Example:
            >>> valid = analyzer.get_valid_sheets(wb)
            >>> [ws.title for ws in valid]
            ['Datos', 'Resumen']
        """
        valid = []
        for name in workbook.sheetnames:
            ws = workbook[name]
            if ws.sheet_state != "hidden" and ws.sheet_state != "veryHidden":
                dims = getattr(ws, "dimensions", "") or ""
                max_row = getattr(ws, "max_row", 0) or 0
                max_col = getattr(ws, "max_column", 0) or 0
                # Hoja con contenido real: dimensiones distintas a A1:A1 vacío
                # o con más de 1 fila / columna según openpyxl
                if (dims and dims != "A1:A1") or max_row > 1 or max_col > 1:
                    valid.append(ws)

        if not valid:
            _logger.warning(
                "No se encontraron hojas visibles con datos en el workbook."
            )
            raise InvalidWorkbookError(
                "El workbook no contiene hojas visibles con datos."
            )

        _logger.debug(
            "Hojas válidas encontradas: %s",
            [ws.title for ws in valid],
        )
        return valid

    # -----------------------------------------------------------------------
    # Métodos privados — helpers de análisis
    # -----------------------------------------------------------------------

    @staticmethod
    def _get_file_size(file_path: Path) -> int:
        """Obtiene el tamaño del archivo en bytes desde el sistema de archivos.

        Args:
            file_path: Ruta al archivo en disco.

        Returns:
            Tamaño en bytes, o ``0`` si el archivo no es accesible.
        """
        try:
            return os.path.getsize(file_path) if file_path.exists() else 0
        except OSError as exc:
            _logger.warning(
                "No se pudo obtener el tamaño de '%s': %s", file_path, exc
            )
            return 0

    def _analyze_sheets(
        self, workbook: Any
    ) -> tuple[List[WorksheetMetadata], int]:
        """Extrae la metadata estructural de cada hoja sin leer datos.

        Itera sobre los nombres de hojas y construye ``WorksheetMetadata``
        accediendo únicamente a propiedades de estructura de openpyxl.

        Args:
            workbook: Objeto ``openpyxl.Workbook``.

        Returns:
            Tupla ``(lista_de_WorksheetMetadata, conteo_de_hojas_ocultas)``.

        Raises:
            InvalidWorkbookError: Si una hoja no puede ser inspeccionada.
        """
        sheets_meta: List[WorksheetMetadata] = []
        hidden_count = 0

        for sheet_name in workbook.sheetnames:
            try:
                ws = workbook[sheet_name]
                meta = self._inspect_worksheet(ws)
                sheets_meta.append(meta)
                if meta.is_hidden:
                    hidden_count += 1
                _logger.debug(
                    "Hoja '%s': hidden=%s, dims='%s', tablas=%d, gráficos=%d, filtros=%s",
                    meta.name,
                    meta.is_hidden,
                    meta.dimensions,
                    len(meta.tables),
                    meta.chart_count,
                    meta.has_filters,
                )
            except Exception as exc:
                _logger.error(
                    "Error al inspeccionar la hoja '%s': %s", sheet_name, exc
                )
                raise InvalidWorkbookError(
                    f"No se pudo analizar la hoja '{sheet_name}': {exc}"
                ) from exc

        return sheets_meta, hidden_count

    @staticmethod
    def _inspect_worksheet(ws: Any) -> WorksheetMetadata:
        """Construye la metadata de una hoja a partir de sus propiedades estructurales.

        No accede al contenido de celdas. Solo usa:
        - ``ws.sheet_state``
        - ``ws.dimensions``
        - ``ws.tables``
        - ``ws._charts``
        - ``ws.auto_filter``

        Args:
            ws: Objeto ``openpyxl.worksheet.worksheet.Worksheet``.

        Returns:
            ``WorksheetMetadata`` con toda la información estructural disponible.
        """
        # Estado de visibilidad
        sheet_state = getattr(ws, "sheet_state", "visible")
        is_hidden = sheet_state in ("hidden", "veryHidden")

        # Dimensiones pre-calculadas (no lectura de celdas)
        dimensions = getattr(ws, "dimensions", "") or ""

        # Tablas estructuradas (ListObjects en terminología Excel)
        tables_dict = getattr(ws, "tables", {}) or {}
        table_names = tuple(tables_dict.keys()) if tables_dict else ()
        has_tables = len(table_names) > 0

        # Gráficos embebidos
        charts = getattr(ws, "_charts", []) or []
        chart_count = len(charts)
        has_charts = chart_count > 0

        # Auto-filtro activo
        auto_filter = getattr(ws, "auto_filter", None)
        has_filters = (
            auto_filter is not None
            and getattr(auto_filter, "ref", None) is not None
        )

        return WorksheetMetadata(
            name=ws.title,
            is_hidden=is_hidden,
            dimensions=dimensions,
            has_tables=has_tables,
            has_charts=has_charts,
            has_filters=has_filters,
            tables=table_names,
            chart_count=chart_count,
        )

    @staticmethod
    def _resolve_target_sheet(
        sheets_meta: List[WorksheetMetadata],
        active_sheet: str,
        workbook: Any,
    ) -> str:
        """Determina heurísticamente la hoja más probable para extracción de datos.

        Estrategia de selección (en orden de prioridad):
        1. Primera hoja visible con dimensiones distintas de ``'A1:A1'``.
        2. Primera hoja visible con más de 1 fila o columna según openpyxl.
        3. Hoja activa si es visible.
        4. Primera hoja visible en la lista.

        Args:
            sheets_meta: Lista de metadata de hojas ya inspeccionadas.
            active_sheet: Nombre de la hoja activa del workbook.
            workbook: Objeto ``openpyxl.Workbook`` (para leer ``max_row``/``max_column``).

        Returns:
            Nombre de la hoja target.

        Raises:
            InvalidWorkbookError: Si no hay ninguna hoja visible.
        """
        # Prioridad 1 y 2: dimensiones o tamaño aparente
        for meta in sheets_meta:
            if meta.is_hidden:
                continue
            ws = workbook[meta.name]
            max_row = getattr(ws, "max_row", 0) or 0
            max_col = getattr(ws, "max_column", 0) or 0
            dims = meta.dimensions

            if (dims and dims != "A1:A1") or max_row > 1 or max_col > 1:
                _logger.debug("Target sheet por dimensiones: '%s'", meta.name)
                return meta.name

        # Prioridad 3: hoja activa visible
        for meta in sheets_meta:
            if meta.name == active_sheet and not meta.is_hidden:
                _logger.debug(
                    "Target sheet por hoja activa: '%s'", meta.name
                )
                return meta.name

        # Prioridad 4: primera hoja visible
        for meta in sheets_meta:
            if not meta.is_hidden:
                _logger.debug(
                    "Target sheet por primera visible (fallback): '%s'", meta.name
                )
                return meta.name

        raise InvalidWorkbookError(
            "El workbook no contiene hojas visibles para determinar el target."
        )

    @staticmethod
    def _extract_named_ranges(workbook: Any) -> List[str]:
        """Extrae los nombres de rangos nombrados definidos en el libro.

        Args:
            workbook: Objeto ``openpyxl.Workbook``.

        Returns:
            Lista de nombres de rangos nombrados. Lista vacía si no hay ninguno
            o si la versión de openpyxl no soporta la API.
        """
        named_ranges: List[str] = []
        try:
            defined_names = getattr(workbook, "defined_names", None)
            if defined_names is None:
                return named_ranges

            # openpyxl < 3.1: defined_names.definedName
            # openpyxl >= 3.1: defined_names es iterable directamente
            if hasattr(defined_names, "definedName"):
                named_ranges = [dn.name for dn in defined_names.definedName]
            elif hasattr(defined_names, "__iter__"):
                named_ranges = [
                    dn.name
                    for dn in defined_names
                    if hasattr(dn, "name")
                ]
        except Exception as exc:  # noqa: BLE001
            _logger.warning("No se pudieron extraer rangos nombrados: %s", exc)

        _logger.debug("Rangos nombrados detectados: %s", named_ranges)
        return named_ranges

    @staticmethod
    def _extract_protection(workbook: Any) -> WorkbookProtection:
        """Extrae el estado de protección de la estructura del workbook.

        Args:
            workbook: Objeto ``openpyxl.Workbook``.

        Returns:
            ``WorkbookProtection`` con los flags de seguridad detectados.
        """
        security = getattr(workbook, "security", None)
        if security is None:
            return WorkbookProtection(
                is_protected=False,
                lock_structure=False,
                lock_windows=False,
            )

        lock_structure = bool(getattr(security, "lockStructure", False))
        lock_windows = bool(getattr(security, "lockWindows", False))
        is_protected = lock_structure or lock_windows

        _logger.debug(
            "Protección del workbook: is_protected=%s, "
            "lock_structure=%s, lock_windows=%s",
            is_protected,
            lock_structure,
            lock_windows,
        )
        return WorkbookProtection(
            is_protected=is_protected,
            lock_structure=lock_structure,
            lock_windows=lock_windows,
        )
