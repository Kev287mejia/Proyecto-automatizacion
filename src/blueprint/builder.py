import json
import os
import logging

class BlueprintBuilder:
    """
    BlueprintBuilder ensambla las piezas obtenidas de los analizadores, 
    construye el diccionario final y genera el archivo blueprint.json en disco.
    """
    def build_and_save(self, word_data: dict, excel_data: dict, output_path: str) -> str:
        # Aquí se podrían inyectar parámetros pasados al engine,
        # pero por ahora inicializamos con valores por defecto acordados.
        blueprint_data = {
            "project": {
                "client": "Por definir",
                "report_type": "Por definir"
            },
            "word": word_data if word_data else {
                "template": "",
                "sections": [],
                "styles": {},
                "metrics": {}
            },
            "excel": excel_data if excel_data else {
                "template": "",
                "worksheets": [],
                "metrics": {}
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(blueprint_data, f, indent=4, ensure_ascii=False)
            
        logging.info(f"Blueprint generado exitosamente en: {output_path}")
        return output_path
