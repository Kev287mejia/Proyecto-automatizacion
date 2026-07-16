import os
import sys
import shutil
import logging
from datetime import datetime

# Añadir el directorio raíz 'SIEA' al path para poder importar los submódulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.blueprint.report_blueprint import BlueprintExtractor
from src.builders.excel_builder import ExcelReportBuilder
from src.builders.word_builder import WordReportBuilder

class PackageBuilder:
    def __init__(self, input_folder: str, output_folder: str):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.log_file = os.path.join(self.output_folder, "log.txt")
        
        # Asegurar que las carpetas existan
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            
        self._setup_logging()

    def _setup_logging(self):
        """Configura el logging para escribir tanto en consola como en log.txt"""
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # Limpiar handlers anteriores
        if logger.hasHandlers():
            logger.handlers.clear()
            
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # File Handler
        fh = logging.FileHandler(self.log_file, encoding='utf-8')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
        # Console Handler
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    def run_pipeline(self):
        logging.info("==================================================")
        logging.info(f"Iniciando Pipeline SIEA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Carpeta Entrada: {self.input_folder}")
        logging.info(f"Carpeta Salida: {self.output_folder}")
        logging.info("==================================================")
        
        try:
            # 1. Blueprint Extractor (Analizar plantillas de entrada)
            logging.info("Paso 1: Analizando plantillas estructurales...")
            extractor = BlueprintExtractor(self.input_folder)
            extractor.extract_excel("Plantilla_Reporte.xlsx", "excel_blueprint.json")
            extractor.extract_word("Plantilla_Informe.docx", "word_blueprint.json")
            
            # Copiar los blueprints generados a la salida (por propósitos de auditoría)
            shutil.copy2(os.path.join(self.input_folder, "excel_blueprint.json"), os.path.join(self.output_folder, "excel_blueprint.json"))
            shutil.copy2(os.path.join(self.input_folder, "word_blueprint.json"), os.path.join(self.output_folder, "word_blueprint.json"))
            logging.info("✔ Blueprints generados y copiados.")

            # 2. Análisis y Estadística (Simulado por ahora: copiaremos assembled_report.json a la salida)
            logging.info("Paso 2: Ejecutando motores de análisis...")
            # En un entorno real, aquí se llama a StatisticsEngine e InsightEngine.
            # Por ahora simularemos inyectando el assembled_report.json en la salida
            assembled_path_in = os.path.join(self.input_folder, "assembled_report.json")
            assembled_path_out = os.path.join(self.output_folder, "assembled_report.json")
            if os.path.exists(assembled_path_in):
                shutil.copy2(assembled_path_in, assembled_path_out)
                logging.info("✔ Datos procesados (Simulado).")
            else:
                logging.warning("No se encontró assembled_report.json en la entrada. Se utilizarán datos vacíos.")

            # 3. Excel Builder
            logging.info("Paso 3: Construyendo Reporte en Excel...")
            # Copiamos la plantilla a la salida para no alterar la original
            plantilla_excel_in = os.path.join(self.input_folder, "Plantilla_Reporte.xlsx")
            plantilla_excel_out = os.path.join(self.output_folder, "Plantilla_Reporte.xlsx")
            shutil.copy2(plantilla_excel_in, plantilla_excel_out)
            
            excel_builder = ExcelReportBuilder(self.output_folder)
            excel_builder.build_report(
                template_name="Plantilla_Reporte.xlsx",
                blueprint_name="excel_blueprint.json",
                data_name="assembled_report.json",
                output_name="Reporte_Final.xlsx"
            )
            # Limpiamos la plantilla temporal
            os.remove(plantilla_excel_out)
            logging.info("✔ Reporte Excel completado.")

            # 4. Word Builder
            logging.info("Paso 4: Construyendo Documento Word...")
            # Copiamos la plantilla a la salida
            plantilla_word_in = os.path.join(self.input_folder, "Plantilla_Informe.docx")
            plantilla_word_out = os.path.join(self.output_folder, "Plantilla_Informe.docx")
            shutil.copy2(plantilla_word_in, plantilla_word_out)
            
            word_builder = WordReportBuilder(self.output_folder)
            word_builder.build_report(
                template_name="Plantilla_Informe.docx",
                assembled_data_name="assembled_report.json",
                output_name="Informe_Final.docx"
            )
            # Limpiamos la plantilla temporal
            os.remove(plantilla_word_out)
            logging.info("✔ Documento Word completado.")

            logging.info("==================================================")
            logging.info("Pipeline completado exitosamente. Documentos listos para revisión.")
            
        except Exception as e:
            logging.error(f"Error crítico en el Pipeline: {str(e)}")

if __name__ == "__main__":
    import locale
    # Intentar configurar el locale a español para los nombres de los meses
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except:
        pass

    # Determinar el mes y año actual (o se podría pasar como parámetro)
    ahora = datetime.now()
    anio_str = ahora.strftime("%Y")
    mes_str = ahora.strftime("%m_%B").capitalize() # ej. 07_Julio

    base_dir = r"C:\Users\LENOVO X1 YOGA\Videos\AUTOMATIZACION"
    in_folder = os.path.join(base_dir, "Entrada_Junio")
    
    # Crear una estructura jerárquica: AUTOMATIZACION / REPORTES_HISTORICOS / 2026 / 07_Julio
    historico_dir = os.path.join(base_dir, "REPORTES_HISTORICOS")
    out_folder = os.path.join(historico_dir, anio_str, mes_str)
    
    orchestrator = PackageBuilder(input_folder=in_folder, output_folder=out_folder)
    orchestrator.run_pipeline()
