# TRENT

TRENT es un software de manipulación de imágenes como proyecto para la materia de Proceso Digital de Imágenes. Sus actuales funciones constan de aplicar filtros con distintos tonos de grises, modificar el brillo, aplicar un filtro de mosaico, etc. así como funciones para abrir y guardar las imágenes modificadas. Es importante mencionar que el programa **solo** abre imágenes de formato jpg, jpeg y png y al ser modificadas, estas deben ser guardadas en un archivo de su mismo formato. La versión de este software no está optimizada por lo cual para aplicar un filtro en una imagen muy grande se podrían tener tiempos de espera prolongados.

<div id="ejecucion"></div>

## Ejecución

- ### Windows
    Para ejecutar en Windows hay que descargar la carpeta ``` dist/windows/TRENT/``` y ejecutar el archivo ``` TRENT.exe``` dentro de esa carpeta. 
    **Importante:** El archivo ``` TRENT.exe``` solo puede ejecutarse dentro de la carpeta ``` dist/windows/TRENT/``` , si se mueve a otra parte el programa no funcionará.
- ### Linux / MacOs
    Para ejecutar en Linux o MacOs se debe abrir una terminal y ejecutar el archivo dentro de la carpeta ```linux-macos```, es decir:

    ``` 
                                        $ ./.../dist/linux-macos/TRENT    
    ```
## Novedades
* ### v.2.3
    - Se crea un nuevo filtro que convierte la imagen en una imagen recursiva a tonos de gris y a color
    - Se agrega una barra de progreso a cada filtro
* ### v.2.2
    - Se crea un nuevo filtro que aplica una marca de agua personalizada en una imagen
    - Se modifica la forma de ejecutar el programa en Windows (ver detalles en la sección [Ejecución](#ejecucion))
* ### v.2.1
    - Se agregan los siguientes filtros de conversión de una imagen a texto:
        - Solo letra M a color
        - Solo letra M con tono gris
        - 16 letras simulando 256 tonos
        - 16 letras simulando 256 tonos a color
        - 16 letras simulando con tono gris
        - Texto personalizado
        - Fichas de domino blancas
        - Fichas de domino negras
        - Cartas de naipes
* ### v.2.0
    - Optimización en los filtros al recorrer la imagen usando Cython, lo que mejora el tiempo de aplicación de los filtros considerablemente.
* ### v.1.1
    - Se agregan los filtros inverso y alto contraste
    - Se agregan los siguientes filtros de convolucion:
        - Blur suave
        - Blur fuerte
        - Motion Blur
        - Encontrar bordes
        - Sharpen
        - Emboss
    - Optimización en el procesamiento de la imagen utilizando arreglos de numpy``