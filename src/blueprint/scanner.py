import os
import logging
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass, field

# -------------------------------------------------------------------------
# Exceptions
# -------------------------------------------------------------------------

class ScannerError(Exception):
    """Excepción base para errores relacionados con el escaneo del proyecto."""
    pass

class DirectoryNotFoundError(ScannerError):
    """El directorio objetivo no existe o no es accesible."""
    pass

# -------------------------------------------------------------------------
# Domain Models
# -------------------------------------------------------------------------

@dataclass(frozen=True)
class ProjectInventory:
    """
    Representa el inventario clasificado de un proyecto.
    El estado es inmutable para asegurar la integridad de los datos en el flujo.
    """
    excel_actual: Optional[str] = None
    plantilla_word: Optional[str] = None
    plantilla_excel: Optional[str] = None
    informes: List[str] = field(default_factory=list)
    carpetas_auxiliares: List[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        """Verifica si el inventario está completamente vacío."""
        return not any([
            self.excel_actual,
            self.plantilla_word,
            self.plantilla_excel,
            self.informes,
            self.carpetas_auxiliares
        ])

# -------------------------------------------------------------------------
# Interface Layer
# -------------------------------------------------------------------------

class IProjectScanner(ABC):
    """
    Contrato base para cualquier escáner de proyecto.
    Respeta el principio de Inversión de Dependencias.
    """
    @abstractmethod
    def scan(self) -> ProjectInventory:
        """Realiza el escaneo y devuelve el inventario clasificado."""
        pass

# -------------------------------------------------------------------------
# Infrastructure Layer
# -------------------------------------------------------------------------

class LocalProjectScanner(IProjectScanner):
    """
    Implementación concreta que escanea el sistema de archivos local.
    Responsabilidad Única: Leer disco local y clasificar.
    """
    def __init__(self, inputs_dir: str):
        self.inputs_dir = os.path.abspath(inputs_dir)
        self.logger = logging.getLogger(self.__class__.__name__)

    def scan(self) -> ProjectInventory:
        """
        Escanea el directorio local y clasifica los recursos.
        """
        self.logger.debug(f"Iniciando escaneo en: {self.inputs_dir}")

        if not os.path.exists(self.inputs_dir):
            self.logger.error(f"El directorio no existe: {self.inputs_dir}")
            raise DirectoryNotFoundError(f"Directorio no encontrado: {self.inputs_dir}")

        try:
            items = os.listdir(self.inputs_dir)
        except PermissionError as e:
            self.logger.error(f"Sin permisos para leer el directorio: {self.inputs_dir}")
            raise ScannerError(f"Error de permisos al leer {self.inputs_dir}: {e}")

        # Clasificadores en memoria
        carpetas_auxiliares = []
        docx_files = []
        xlsx_files = []
        pdf_files = []

        # Separar en carpetas y archivos
        for item in items:
            item_path = os.path.join(self.inputs_dir, item)
            
            # Ignorar temporales de sistema o archivos ocultos de Office
            if item.startswith("~$") or item.startswith("."):
                continue

            if os.path.isdir(item_path):
                carpetas_auxiliares.append(item_path)
            elif os.path.isfile(item_path):
                ext = item.lower()
                if ext.endswith(".docx"):
                    docx_files.append(item_path)
                elif ext.endswith(".xlsx"):
                    xlsx_files.append(item_path)
                elif ext.endswith(".pdf"):
                    pdf_files.append(item_path)

        # Determinar plantillas (por convención de nombre)
        plantilla_word = next((f for f in docx_files if "plantilla" in os.path.basename(f).lower()), None)
        # Fallback: si no hay "plantilla" literal pero hay un docx y ningún histórico evidente
        if not plantilla_word and docx_files:
            # Si solo hay uno, asumimos que es la plantilla
            plantilla_word = docx_files[0]

        plantilla_excel = next((f for f in xlsx_files if "plantilla" in os.path.basename(f).lower()), None)

        # Extraer Excel Actual (datos puros, excluyendo plantilla)
        excel_actual = None
        for f in xlsx_files:
            if f != plantilla_excel:
                excel_actual = f
                break

        # Extraer Históricos (docx/pdf que no son la plantilla)
        informes = []
        for f in docx_files + pdf_files:
            if f != plantilla_word:
                informes.append(f)

        inventory = ProjectInventory(
            excel_actual=excel_actual,
            plantilla_word=plantilla_word,
            plantilla_excel=plantilla_excel,
            informes=informes,
            carpetas_auxiliares=carpetas_auxiliares
        )

        self.logger.debug(f"Escaneo finalizado. Inventario: {inventory}")
        return inventory

# -------------------------------------------------------------------------
# Factory / Facade Helper (Opcional, para no romper compatibilidad rápida)
# -------------------------------------------------------------------------
def scan_project(inputs_dir: str) -> dict:
    """
    Función de conveniencia para compatibilidad hacia atrás temporal.
    Se recomienda usar LocalProjectScanner directamente.
    """
    scanner = LocalProjectScanner(inputs_dir)
    try:
        inv = scanner.scan()
        return {
            "excel_actual": inv.excel_actual,
            "informes": inv.informes,
            "plantilla_word": inv.plantilla_word,
            "plantilla_excel": inv.plantilla_excel,
            "carpetas_auxiliares": inv.carpetas_auxiliares
        }
    except DirectoryNotFoundError:
        # Para compatibilidad con tests viejos que esperaban un dict vacio si no existia
        return {
            "excel_actual": None,
            "informes": [],
            "plantilla_word": None,
            "plantilla_excel": None,
            "carpetas_auxiliares": []
        }
