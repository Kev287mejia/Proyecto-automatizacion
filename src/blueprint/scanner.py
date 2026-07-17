import os
import glob
from typing import Dict, Any

class ProjectScanner:
    """
    ProjectScanner es el componente responsable de escanear el directorio
    del proyecto y localizar los archivos clave (plantillas, históricos y datos actuales).
    Su única responsabilidad es responder: ¿Qué archivos existen? ¿Qué tipo son? 
    ¿Cuáles son históricos? ¿Cuál es la plantilla? ¿Cuál es el Excel actual?
    """
    def __init__(self, inputs_dir: str):
        self.inputs_dir = os.path.abspath(inputs_dir)

    def scan(self) -> Dict[str, Any]:
        """
        Retorna un diccionario estructurado con el inventario de la carpeta.
        """
        all_files = os.listdir(self.inputs_dir)
        # Filtrar solo archivos reales, no carpetas ni temporales de Windows
        all_files = [f for f in all_files if os.path.isfile(os.path.join(self.inputs_dir, f)) and not f.startswith("~$")]

        docx_files = [f for f in all_files if f.endswith(".docx")]
        xlsx_files = [f for f in all_files if f.endswith(".xlsx")]
        pdf_files = [f for f in all_files if f.endswith(".pdf")]

        plantillas_word = [f for f in docx_files if "plantilla" in f.lower()]
        plantillas_excel = [f for f in xlsx_files if "plantilla" in f.lower()]

        word_template = plantillas_word[0] if plantillas_word else (docx_files[0] if docx_files else None)
        excel_template = plantillas_excel[0] if plantillas_excel else None

        # El Excel actual (datos) es aquel que no es plantilla
        excel_data = None
        for f in xlsx_files:
            if excel_template and f == excel_template:
                continue
            excel_data = f
            break

        # Históricos: Todos los docx/pdf que no sean la plantilla de Word
        historical_docs = []
        for f in docx_files + pdf_files:
            if word_template and f == word_template:
                continue
            historical_docs.append(f)

        # Construir la respuesta exacta requerida
        inventory = {
            "files_found": all_files,
            "file_types": {
                "docx": len(docx_files),
                "xlsx": len(xlsx_files),
                "pdf": len(pdf_files)
            },
            "word_template": os.path.join(self.inputs_dir, word_template) if word_template else None,
            "excel_template": os.path.join(self.inputs_dir, excel_template) if excel_template else None,
            "excel_data": os.path.join(self.inputs_dir, excel_data) if excel_data else None,
            "historicals": [os.path.join(self.inputs_dir, h) for h in historical_docs]
        }

        return inventory
