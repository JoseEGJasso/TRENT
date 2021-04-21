# TRENT

TRENT es un software de manipulación de imágenes como proyecto para la materia de Proceso Digital de Imágenes. Sus actuales funciones constan de aplicar filtros con distintos tonos de grises, modificar el brillo, aplicar un filtro de mosaico así como funciones para abrir y guardar las imágenes modificadas. Es importante mencionar que el programa **solo** abre imágenes de formato jpg, jpeg y png y al ser modificadas, estas deben ser guardadas en un archivo de su mismo formato. La versión de este software no está optimizada por lo cual para aplicar un filtro en una imagen muy grande se podrían tener tiempos de espera prolongados.

## Ejecución
- ### Windows
    Para ejecutar en Windows solo basta ejecutar el archivo ``` dist/windows/TRENT.exe```
- ### Linux / MacOs
    Para ejecutar en Linux o MacOs se debe abrir una terminal y ejecutar el archivo dentro de la carpeta ```linux-macos```, es decir:

    ``` 
                                        $ ./.../dist/linux-macos/TRENT    
    ```
## Novedades
* ### v.1.1
    - Se agregan los filtros inverso y alto contraste
    - Se agregan los siguientes filtros de convolucion:
        - Blur suave
        - Blur fuerte
        - Motion Blur
        - Encontrar bordes
        - Sharpen
        - Emboss
    - Optimización en el guardado de la imagen usando arreglos de numpy
* ### v.2.0
    - Optimización en los filtros al recorrer la imagen usando Cython disminuyendo el tiempo de procesamiento de los filtros