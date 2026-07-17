import os
from typing import Dict, Any, List
import openpyxl

def analyze_excel(file_path: str) -> Dict[str, Any]:
    """
    Analiza una plantilla de Excel (.xlsx) y extrae únicamente su estructura:
    hojas, tablas, gráficos, estilos (colores predominantes) y rangos nombrados.
    No modifica el archivo.
    """
    if not file_path or not os.path.exists(file_path):
        return {
            "worksheets": [],
            "tables": 0,
            "charts": 0,
            "styles": [],
            "ranges": []
        }

    try:
        wb = openpyxl.load_workbook(file_path, data_only=False)
        
        worksheets_found = []
        tables_count = 0
        charts_count = 0
        styles_found = set()
        ranges_found = []

        # 1. Extraer rangos nombrados
        if hasattr(wb, 'defined_names'):
            for dn in wb.defined_names.definedName:
                ranges_found.append(dn.name)

        # 2. Iterar por cada hoja
        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            
            if sheet.sheet_state != 'visible':
                continue
                
            worksheets_found.append(sheet_name)
            
            if hasattr(sheet, 'tables'):
                tables_count += len(sheet.tables)
                
            if hasattr(sheet, '_charts'):
                charts_count += len(sheet._charts)
                
            # Muestreo rápido de colores para estilos (solo las primeras 50 filas)
            for row in sheet.iter_rows(min_row=1, max_row=50):
                for cell in row:
                    if getattr(cell, 'fill', None) and cell.fill.fill_type == "solid":
                        color_val = getattr(cell.fill.start_color, 'rgb', None)
                        if color_val and isinstance(color_val, str) and color_val != "00000000":
                            styles_found.add(color_val)

        return {
            "worksheets": worksheets_found,
            "tables": tables_count,
            "charts": charts_count,
            "styles": list(styles_found),
            "ranges": ranges_found
        }
        
    except Exception:
        return {
            "worksheets": [],
            "tables": 0,
            "charts": 0,
            "styles": [],
            "ranges": []
        }

class ExcelAnalyzer:
    """
    Clase contenedora opcional para compatibilidad.
    """
    def analyze(self, file_path: str) -> Dict[str, Any]:
        return analyze_excel(file_path)
