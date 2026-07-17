import logging
import warnings
from typing import Dict, Any

class CriticalBlueprintError(Exception):
    """Excepción lanzada cuando falta un archivo crítico que impide generar el blueprint.
    Principalmente cuando no se encuentra la plantilla de Word."""
    pass

class MissingDataTemplateWarning(Warning):
    """Advertencia lanzada cuando no se encuentra la plantilla de Excel.
    El flujo puede continuar, pero se debe notificar."""
    pass

class BlueprintValidator:
    """
    BlueprintValidator verifica que todo el inventario tenga sentido
    para la ejecución de SIEA. Emite un checklist de validación.
    """
    def validate(self, inventory: Dict[str, Any]) -> bool:
        """
        Evalúa el inventario detectado por el Scanner.
        Retorna True si el Blueprint es estructuralmente válido y puede continuar.
        Lanza CriticalBlueprintError si falta un componente insalvable.
        """
        word_target = inventory.get("plantilla_word")
        excel_target = inventory.get("plantilla_excel")
        historicals = inventory.get("informes", [])
        excel_data = inventory.get("excel_actual")

        logging.info("--- Validación del Blueprint ---")
        
        # 1. ¿Existe plantilla Word?
        has_word = bool(word_target)
        logging.info(f"¿Existe plantilla Word? {'SI' if has_word else 'NO'}")
        if not has_word:
            raise CriticalBlueprintError(
                "Falta la plantilla de Word. No se puede generar el informe sin ella."
            )

        # 2. ¿Existe plantilla Excel?
        has_excel = bool(excel_target)
        logging.info(f"¿Existe plantilla Excel? {'SI' if has_excel else 'NO'}")
        if not has_excel:
            warnings.warn(
                "No se encontró una plantilla de Excel (.xlsx).",
                MissingDataTemplateWarning
            )

        # 3. ¿Hay informes históricos?
        has_historicals = len(historicals) > 0
        logging.info(f"¿Hay informes históricos? {'SI' if has_historicals else 'NO'}")

        # 4. ¿Hay Excel actual?
        has_excel_data = bool(excel_data)
        logging.info(f"¿Hay Excel actual? {'SI' if has_excel_data else 'NO'}")

        logging.info("--- Blueprint válido ---")
        return True
