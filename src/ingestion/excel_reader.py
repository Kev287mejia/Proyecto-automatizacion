"""
Infraestructura de lectura de archivos Excel para el Ingestion Engine.
"""
from pathlib import Path
from typing import Any
import openpyxl
from openpyxl.utils.exceptions import InvalidFileException
import zipfile
import hashlib
from datetime import datetime, timezone

from src.ingestion.interfaces import IExcelReader, WorkbookHandle
from src.ingestion.exceptions import FileNotReadableError


class ExcelReader(IExcelReader):
    """
    Implementación concreta de IExcelReader utilizando openpyxl.
    Su única responsabilidad es abrir el archivo de forma segura y
    retornar el workbook sin interpretar sus datos.
    """

    def load_workbook(self, file_path: Path) -> WorkbookHandle:
        """
        Carga un archivo Excel (.xlsx, .xlsm) y retorna un objeto WorkbookHandle.
        Abre el archivo en modo 'data_only=True' para leer los valores finales,
        no las fórmulas, y 'read_only=True' para asegurar optimización y
        que no modificamos el original.
        
        Args:
            file_path (Path): Ruta al archivo Excel.
            
        Returns:
            WorkbookHandle: Wrapper con el workbook y metadata forense.
            
        Raises:
            FileNotReadableError: Si el archivo no existe, no es un formato válido,
                                  está corrupto o protegido.
        """
        if not file_path.exists():
            raise FileNotReadableError(f"El archivo no existe: {file_path}")
            
        if not file_path.is_file():
            raise FileNotReadableError(f"La ruta no es un archivo válido: {file_path}")
            
        if file_path.suffix.lower() not in ['.xlsx', '.xlsm']:
            raise FileNotReadableError(f"Formato no soportado. Se esperaba .xlsx o .xlsm: {file_path}")

        try:
            # Calcular checksum antes de abrir
            checksum = self._calculate_checksum(file_path)
            
            workbook = openpyxl.load_workbook(
                filename=str(file_path),
                data_only=True,
                read_only=True
            )
            
            return WorkbookHandle(
                workbook=workbook,
                source_path=file_path,
                opened_at=datetime.now(timezone.utc),
                checksum=checksum,
                readonly=True
            )
        except InvalidFileException as e:
            raise FileNotReadableError(f"Archivo Excel inválido o corrupto: {e}")
        except zipfile.BadZipFile as e:
            raise FileNotReadableError(f"Archivo dañado o protegido con contraseña (BadZipFile): {e}")
        except Exception as e:
            raise FileNotReadableError(f"Error inesperado al leer el archivo Excel: {e}")

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calcula el hash SHA-256 del archivo."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
