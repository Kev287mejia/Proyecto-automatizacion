import os
import pytest
from src.blueprint.scanner import LocalProjectScanner, DirectoryNotFoundError, ProjectInventory

def test_local_project_scanner_empty_dir(tmp_path):
    """Prueba que el escáner maneje correctamente un directorio vacío."""
    scanner = LocalProjectScanner(str(tmp_path))
    inventory = scanner.scan()
    
    assert isinstance(inventory, ProjectInventory)
    assert inventory.is_empty() is True

def test_local_project_scanner_nonexistent_dir():
    """Prueba que el escáner lance la excepción correcta si no existe el directorio."""
    scanner = LocalProjectScanner("/ruta/falsa/que/no/existe/123")
    with pytest.raises(DirectoryNotFoundError):
        scanner.scan()

def test_local_project_scanner_happy_path(tmp_path):
    """Prueba un escenario de éxito con plantillas, históricos y carpetas auxiliares."""
    
    # Crear estructura mock
    (tmp_path / "Plantilla_Informe.docx").touch()
    (tmp_path / "Plantilla_Datos.xlsx").touch()
    (tmp_path / "Datos_Julio.xlsx").touch()
    (tmp_path / "Historico_Mayo.docx").touch()
    (tmp_path / "Historico_Junio.pdf").touch()
    
    # Carpeta auxiliar
    aux_folder = tmp_path / "Imagenes"
    aux_folder.mkdir()
    
    # Archivos basura (ocultos o temporales)
    (tmp_path / "~$Plantilla_Informe.docx").touch()
    (tmp_path / ".DS_Store").touch()

    # Ejecutar escáner
    scanner = LocalProjectScanner(str(tmp_path))
    inventory = scanner.scan()

    assert inventory.is_empty() is False
    
    # Validar Plantillas
    assert inventory.plantilla_word is not None
    assert "Plantilla_Informe.docx" in inventory.plantilla_word
    
    assert inventory.plantilla_excel is not None
    assert "Plantilla_Datos.xlsx" in inventory.plantilla_excel
    
    # Validar Excel Actual
    assert inventory.excel_actual is not None
    assert "Datos_Julio.xlsx" in inventory.excel_actual
    
    # Validar Históricos
    assert len(inventory.informes) == 2
    assert any("Historico_Mayo.docx" in f for f in inventory.informes)
    assert any("Historico_Junio.pdf" in f for f in inventory.informes)
    
    # Validar Carpetas auxiliares
    assert len(inventory.carpetas_auxiliares) == 1
    assert "Imagenes" in inventory.carpetas_auxiliares[0]
    
    # Validar Ignorados (temporales y ocultos)
    all_values = str(inventory)
    assert "~$" not in all_values
    assert ".DS_Store" not in all_values

def test_local_project_scanner_fallback_word(tmp_path):
    """Prueba que asuma el único docx como plantilla si no tiene la palabra 'plantilla'."""
    (tmp_path / "Unico_Reporte.docx").touch()
    
    scanner = LocalProjectScanner(str(tmp_path))
    inventory = scanner.scan()
    
    assert inventory.plantilla_word is not None
    assert "Unico_Reporte.docx" in inventory.plantilla_word
    assert len(inventory.informes) == 0
