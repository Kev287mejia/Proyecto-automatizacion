# Estándar Institucional de Reportes Estadísticos (EXCEL_STANDARD)

Este documento define la estructura, formato y estilo obligatorio que debe cumplir cualquier archivo Excel (`Reporte_Estadistico.xlsx`) generado o poblado automáticamente por el motor de transformación de datos del SIEA. Su objetivo es garantizar la calidad, legibilidad y el rigor institucional de la información cuantitativa.

---

## 1. Estructura de Hojas (Worksheets)
Todo reporte estadístico debe contar de forma estandarizada con la siguiente arquitectura de hojas, en este orden:

1. **[Portada]:**
   - Contiene el título oficial del reporte, el periodo analizado, la fecha y hora de generación, y la etiqueta de autoría (generado por SIEA). No debe contener tablas de datos extensas.
2. **[Resumen_Ejecutivo] o [Dashboard]:**
   - Tabla consolidada de los KPIs (Key Performance Indicators) del periodo y su comparativa histórica.
3. **[Datos_Mensuales]:**
   - El dataset principal con el detalle operativo del periodo actual, completamente limpio y tabulado.
4. **[Datos_Historicos] (Opcional/Oculta):**
   - Base de datos acumulativa utilizada para soportar cálculos de variación (MoM, YoY) y gráficos de tendencia.
5. **[Catalogos] / [Parametros] (Oculta):**
   - Contiene las listas de validación, tasas fijas institucionales, o equivalencias de diccionario de datos utilizadas en las fórmulas.

## 2. Tablas y Estructura de Datos
- **Formato Oficial de Tabla:** Todos los datos deben inyectarse dentro de Tablas Oficiales de Excel (formato `ListObject` en la API subyacente).
- **Nomenclatura Técnica:** Las tablas deben poseer un nombre definido claro, sin espacios ni caracteres especiales (ej. `Tbl_Resultados_Julio`).
- **Fila de Totales:** Activar la "Fila de Totales" por defecto en Tablas que contengan métricas sumables o promediables.
- **Filtros Automáticos:** Los encabezados de toda tabla de datos deben poseer los controles de filtro habilitados.

## 3. Encabezados (Headers)
- **Claridad Descriptiva:** Nombres de columna cortos, en estilo Title Case o capitalización institucional (ej. `Zona Operativa`).
- **Unidades Explícitas:** Si una columna representa una métrica, su unidad de medida debe especificarse entre paréntesis en el encabezado (ej. `Presupuesto Ejecutado (USD)`, `Tasa de Éxito (%)`).
- **Inmovilización de Paneles:** Obligatorio fijar la fila superior (encabezados) y la primera columna (llave primaria o identificador principal) para facilitar el desplazamiento.

## 4. Colores y Estilo Visual
Se debe mantener el minimalismo corporativo y evitar la saturación cromática:
- **Encabezados:** Fondo en color institucional primario (ej. Azul Marino HEX #003366), texto en color Blanco y Negrita.
- **Cuerpo de Datos:** Fondo blanco puro. Para tablas muy anchas, se permite el estilo "Bandas de Filas" (Zebra Striping) en tonos grises muy tenues.
- **Semántica de Color (Formato Condicional):** 
  - Alertas/Desviaciones Negativas Críticas: Rojo sobrio (HEX #CC0000).
  - Objetivos Superados: Verde sobrio (HEX #009933).
- **Bordes:** Utilizar bordes grises suaves (HEX #E0E0E0); evitar por completo las cuadrículas negras y gruesas estándar de Excel. Las líneas de cuadrícula generales de la hoja (`Gridlines`) deben desactivarse en la pestaña de vista para un look de reporte limpio.

## 5. Formatos de Número y Celda
- **Alineación:** Textos y categorías alineados a la izquierda. Números, fechas, monedas y porcentajes estrictamente alineados a la derecha. Encabezados centrados.
- **Moneda:** Símbolo monetario correspondiente y separador de miles obligatorios. Mantener estrictamente dos decimales.
- **Porcentajes:** Mostrar con un decimal o dos (ej. `15.5%`), jamás como número crudo (`0.155`).
- **Fechas:** Utilizar el estándar regional oficial o formato corto estándar (ej. `DD/MM/AAAA`).

## 6. Fórmulas y Cálculos
- **Referencias Estructuradas:** Siempre utilizar la notación de columnas de tabla (`=[@[Ingresos]] - [@[Egresos]]`) en lugar de referencias de celda rígidas (`=B2-C2`).
- **Gestión de Errores (Error Handling):** Toda fórmula susceptible de error (divisiones, búsquedas de VLOOKUP/XLOOKUP) debe encapsularse en una función de manejo de errores (`SI.ERROR` o `IFERROR`) para devolver un cero (`0`) o un guion (`"-"`) y mantener el reporte limpio.
- **Sin Valores Mágicos (Hardcoding):** Las constantes globales (tasas de impuestos, metas fijas) no deben escribirse directamente en las fórmulas; deben referenciarse desde la hoja `[Catalogos]`.

## 7. Gráficos (Charts)
- **Minimalismo (Data-Ink Ratio):** Prohibido el uso de gráficos 3D, sombras pesadas o bordes exteriores gruesos. Las líneas de fondo (gridlines) del gráfico deben ser mínimas o eliminarse.
- **Titulaciones:** Cada gráfico debe tener un título conciso que no solo describa el eje, sino el contexto (ej. "Evolución Mensual de Capacitaciones - Q2 2026").
- **Etiquetas de Datos:** Si el gráfico es de barras con menos de 10 elementos, colocar las etiquetas de datos y eliminar el eje Y. Evitar que la lectura visual sea confusa.
- **Paleta Coherente:** El color principal del gráfico debe ser el corporativo. Evitar la paleta multicolor predeterminada de Office a menos que representen múltiples categorías irreconciliables.

## 8. Reglas de Validación de Datos (Data Validation)
- **Integridad Referencial:** Cualquier celda que indique "Estado", "Categoría" o "Departamento" debe estar validada mediante una lista desplegable enlazada a la hoja `[Catalogos]`.
- **Restricción de Tipo:** Si la columna es `Cantidad`, configurar validación numérica para impedir el ingreso de texto.
- **Prevención de Nulos:** Usar Formato Condicional sutil para marcar celdas obligatorias que quedaron vacías por errores en la extracción operativa.

## 9. Errores Comunes Prohibidos (Red Flags)
1. **Celdas Combinadas (Merge & Center):** Estrictamente prohibido su uso dentro de las tablas de datos, ya que destruyen la capacidad de filtrar, ordenar o procesar la tabla mediante scripts posteriores. Si se requiere estética, usar "Centrar en la selección".
2. **Errores Visibles (`#REF!`, `#N/A`, `#¡DIV/0!`):** La presencia de estos valores tras la generación automática se considera un fallo crítico del motor ETL.
3. **Ocultamiento Desordenado:** No se deben ocultar columnas intermedias saltadas dentro del dataset. Si un dato es irrelevante, no se extrae. Si es un cálculo temporal, debe ir a una tabla separada.
4. **Data "Fantasma":** Formatear columnas enteras hasta la fila 1,000,000 hace que el archivo pese megabytes innecesarios. El formato de tabla debe aplicarse estricta y únicamente hasta la última fila poblada.
5. **Reportes "Huérfanos":** Generar un Excel de reporte estadístico donde no se entienda el periodo de estudio ni a qué institución pertenece.
