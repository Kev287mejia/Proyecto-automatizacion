# Golden Dataset (Muestras de Referencia)

Este directorio (`samples/`) actúa como el "Golden Dataset" para el sistema SIEA. Su propósito es proveer una base de la verdad (*ground truth*) continua para el desarrollo, pruebas y validación del código.

## Estructura de Muestras Requerida

Debes poblar esta carpeta manualmente con los siguientes archivos reales:

1. **Informes Históricos "Perfectos" (Word)**
   - *Cantidad recomendada:* 5 a 10 documentos.
   - *Uso:* Validar la consistencia, el tono corporativo y la narrativa que intentará replicar el *Insight Engine* y ensamblar el *Word Builder*.
   
2. **Reportes Institucionales Definitivos (Excel)**
   - *Cantidad recomendada:* 5 a 10 documentos.
   - *Uso:* Servir como estándar de formato, fórmulas y gráficos para validar visual y funcionalmente lo generado por el *Excel Builder*.

3. **Fuentes de Datos Originales (Excel)**
   - *Cantidad recomendada:* 5 a 10 documentos.
   - *Uso:* Ingresar como input "crudo" para el *Data Extractor* y asegurar que el *Statistics Engine* arroje exactamente la misma matemática que se encuentra en los informes históricos.

## Filosofía de Validación
Esta colección es tan valiosa como el propio código fuente de SIEA. Cualquier mejora en el sistema debe evaluarse empíricamente procesando los datos crudos e intentando acercar los resultados a los informes institucionales definitivos que elaboras manualmente.
