import os
from typing import Dict, Any, List
from docx import Document

def analyze_word(file_path: str) -> Dict[str, Any]:
    """
    Analiza una plantilla de Word (.docx) y extrae únicamente su estructura:
    secciones, estilos, tablas, encabezados y pies de página.
    No modifica el archivo.
    """
    if not file_path or not os.path.exists(file_path):
        return {
            "sections": [],
            "styles": {},
            "tables": 0,
            "headers": False,
            "footers": False
        }

    try:
        doc = Document(file_path)
        
        sections_found = []
        styles_found = {}
        
        # Analizar Párrafos para extraer Títulos (Secciones) y Estilos
        for p in doc.paragraphs:
            style_name = p.style.name if p.style else ""
            
            # Identificar secciones a través de los títulos (Headings)
            if style_name.startswith('Heading'):
                text = p.text.strip()
                if text and text not in sections_found:
                    sections_found.append(text)
            
            # Mapear estilos usados
            if style_name:
                style_key = style_name.replace(" ", "")
                if style_key not in styles_found:
                    font_name = p.style.font.name if getattr(p.style, 'font', None) and p.style.font.name else "Calibri"
                    font_size = getattr(p.style, 'font', None)
                    size_pt = font_size.size.pt if font_size and font_size.size else 11
                    
                    styles_found[style_key] = {
                        "font": font_name,
                        "size": int(size_pt)
                    }

        # Analizar Encabezados y Pies de página
        has_headers = False
        has_footers = False
        for section in doc.sections:
            if section.header and any(p.text.strip() for p in section.header.paragraphs):
                has_headers = True
            if section.footer and any(p.text.strip() for p in section.footer.paragraphs):
                has_footers = True

        # Devolver exactamente lo solicitado
        return {
            "sections": sections_found,
            "styles": styles_found,
            "tables": len(doc.tables),
            "headers": has_headers,
            "footers": has_footers
        }
        
    except Exception:
        # En caso de que el archivo no sea un docx válido o esté corrupto
        return {
            "sections": [],
            "styles": {},
            "tables": 0,
            "headers": False,
            "footers": False
        }

class WordAnalyzer:
    """
    Clase contenedora opcional para compatibilidad con el motor anterior.
    """
    def analyze(self, file_path: str) -> Dict[str, Any]:
        return analyze_word(file_path)
