import json

def build_blueprint(project_data: dict, word_data: dict, excel_data: dict) -> dict:
    """
    Une toda la información extraída de los tres módulos anteriores (Scanner, Word, Excel)
    para generar el diccionario final del blueprint.
    """
    
    # Extraemos rutas bases o nombres
    word_template = project_data.get("plantilla_word", "") if project_data else ""
    excel_template = project_data.get("plantilla_excel", "") if project_data else ""

    blueprint = {
        "project": {
            "excel_actual": project_data.get("excel_actual") if project_data else None,
            "informes_historicos": project_data.get("informes", []) if project_data else []
        },
        "word": {
            "template": word_template,
            "sections": word_data.get("sections", []) if word_data else [],
            "styles": word_data.get("styles", {}) if word_data else {},
            "tables": word_data.get("tables", 0) if word_data else 0,
            "headers": word_data.get("headers", False) if word_data else False,
            "footers": word_data.get("footers", False) if word_data else False
        },
        "excel": {
            "template": excel_template,
            "worksheets": excel_data.get("worksheets", []) if excel_data else [],
            "tables": excel_data.get("tables", 0) if excel_data else 0,
            "charts": excel_data.get("charts", 0) if excel_data else 0,
            "styles": excel_data.get("styles", []) if excel_data else [],
            "ranges": excel_data.get("ranges", []) if excel_data else []
        }
    }
    
    return blueprint

def save_blueprint(blueprint_data: dict, output_path: str):
    """
    Guarda el blueprint resultante en un archivo JSON.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(blueprint_data, f, indent=4, ensure_ascii=False)

class BlueprintBuilder:
    """
    Clase contenedora opcional para compatibilidad.
    """
    def build_and_save(self, word_data: dict, excel_data: dict, output_path: str, project_data: dict = None) -> str:
        blueprint = build_blueprint(project_data, word_data, excel_data)
        save_blueprint(blueprint, output_path)
        return output_path
