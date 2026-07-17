import os
import logging

from .scanner import LocalProjectScanner as ProjectScanner, scan_project
from .word_analyzer import WordAnalyzer
from .excel_analyzer import ExcelAnalyzer
from .builder import BlueprintBuilder
from .validator import BlueprintValidator, CriticalBlueprintError

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

class BlueprintEngine:
    """
    Orquestador principal que coordina el Scanner, los Analyzers, el Validator
    y el Builder para generar el blueprint.json final.
    """
    def __init__(self, inputs_dir: str):
        self.inputs_dir = os.path.abspath(inputs_dir)
        self.scanner = ProjectScanner(self.inputs_dir)
        self.validator = BlueprintValidator()
        self.word_analyzer = WordAnalyzer()
        self.excel_analyzer = ExcelAnalyzer()
        self.builder = BlueprintBuilder()

    def generate_blueprint(self, output_name: str = "blueprint.json"):
        logging.info(f"Iniciando Blueprint Engine en directorio: {self.inputs_dir}")
        
        # 1. Escanear el proyecto
        # Usamos compatibilidad con diccionarios temporalmente para no romper validator.py/builder.py
        inventory = scan_project(self.inputs_dir)

        # 2. Validar que todo tenga sentido
        self.validator.validate(inventory)

        # 3. Extraer información (Analyzers)
        word_target = inventory.get("plantilla_word")
        excel_target = inventory.get("plantilla_excel")
        
        word_data = None
        if word_target:
            logging.info(f"Analizando Word: {os.path.basename(word_target)}")
            word_data = self.word_analyzer.analyze(word_target)
            
        excel_data = None
        if excel_target:
            logging.info(f"Analizando Excel: {os.path.basename(excel_target)}")
            excel_data = self.excel_analyzer.analyze(excel_target)

        # 4. Construir JSON y Guardarlo en disco (Builder)
        output_path = os.path.join(self.inputs_dir, output_name)
        self.builder.build_and_save(word_data, excel_data, output_path, inventory)

        return output_path

__all__ = ["BlueprintEngine", "CriticalBlueprintError"]
